"""IBKR Client with advanced trading capabilities."""

import asyncio
import logging
from typing import Dict, List, Optional, Union
from decimal import Decimal

from ib_async import IB, Stock, util
from .config import settings
from .utils import rate_limit, retry_on_failure, safe_float, safe_int, ValidationError, ConnectionError as IBKRConnectionError


class IBKRClient:
    """Enhanced IBKR client with multi-account and short selling support."""
    
    def __init__(self):
        self.ib: Optional[IB] = None
        self.logger = logging.getLogger(__name__)
        
        # Connection settings
        self.host = settings.ibkr_host
        self.port = settings.ibkr_port
        self.client_id = settings.ibkr_client_id
        self.max_reconnect_attempts = settings.max_reconnect_attempts
        self.reconnect_delay = settings.reconnect_delay
        self.reconnect_attempts = 0
        
        # Account management
        self.accounts: List[str] = []
        self.current_account: Optional[str] = settings.ibkr_default_account
        
        # Connection state
        self._connected = False
        self._connecting = False
    
    @retry_on_failure(max_attempts=3)
    async def connect(self) -> bool:
        """Establish connection and discover accounts."""
        if self._connected and self.ib and self.ib.isConnected():
            return True
        
        if self._connecting:
            # Wait for ongoing connection attempt
            while self._connecting:
                await asyncio.sleep(0.1)
            return self._connected
        
        self._connecting = True
        
        try:
            self.ib = IB()
            
            self.logger.info(f"Connecting to IBKR at {self.host}:{self.port}...")
            await self.ib.connectAsync(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=10
            )
            
            # Setup event handlers
            self.ib.disconnectedEvent += self._on_disconnect
            self.ib.errorEvent += self._on_error
            
            # Wait for connection to stabilize
            await asyncio.sleep(2)
            
            # Discover accounts
            self.accounts = self.ib.managedAccounts()
            if self.accounts:
                if not self.current_account or self.current_account not in self.accounts:
                    self.current_account = self.accounts[0]
                
                self.logger.info(f"Connected to IBKR. Accounts: {self.accounts}")
                self.logger.info(f"Current account: {self.current_account}")
            else:
                self.logger.warning("No managed accounts found")
            
            self._connected = True
            self.reconnect_attempts = 0
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to IBKR: {e}")
            raise IBKRConnectionError(f"Connection failed: {e}")
        finally:
            self._connecting = False
    
    async def disconnect(self):
        """Clean disconnection."""
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
            self._connected = False
            self.logger.info("IBKR disconnected")
    
    def _on_disconnect(self):
        """Handle disconnection with automatic reconnection."""
        self._connected = False
        self.logger.warning("IBKR disconnected, scheduling reconnection...")
        asyncio.create_task(self._reconnect())
    
    def _on_error(self, reqId, errorCode, errorString, contract):
        """Centralized error logging."""
        # Don't log certain routine messages as errors
        if errorCode in [2104, 2106, 2158]:  # Market data warnings
            self.logger.debug(f"IBKR Info {errorCode}: {errorString}")
        else:
            self.logger.error(f"IBKR Error {errorCode}: {errorString} (reqId: {reqId})")
    
    async def _reconnect(self):
        """Background reconnection task."""
        try:
            await asyncio.sleep(self.reconnect_delay)
            await self.connect()
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected and self.ib is not None and self.ib.isConnected()
    
    def switch_account(self, account_id: str) -> bool:
        """Switch to a different account."""
        if account_id in self.accounts:
            self.current_account = account_id
            self.logger.info(f"Switched to account: {account_id}")
            return True
        else:
            self.logger.error(f"Account {account_id} not found. Available: {self.accounts}")
            return False
    
    def get_accounts(self) -> Dict[str, Union[str, List[str]]]:
        """Get available accounts."""
        return {
            "current_account": self.current_account,
            "available_accounts": self.accounts
        }
    
    @rate_limit(calls_per_second=1.0)
    async def get_portfolio(self, account: Optional[str] = None) -> List[Dict]:
        """Get portfolio positions."""
        if not self.is_connected():
            raise IBKRConnectionError("IBKR not connected")
        
        account = account or self.current_account
        
        try:
            positions = await self.ib.reqPositionsAsync()
            
            portfolio = []
            for pos in positions:
                if not account or pos.account == account:
                    portfolio.append(self._serialize_position(pos))
            
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Portfolio request failed: {e}")
            raise RuntimeError(f"IBKR API error: {str(e)}")
    
    @rate_limit(calls_per_second=1.0)
    async def get_account_summary(self, account: Optional[str] = None) -> List[Dict]:
        """Get account summary."""
        if not self.is_connected():
            raise IBKRConnectionError("IBKR not connected")
        
        account = account or self.current_account or "All"
        
        try:
            summary_tags = [
                'TotalCashValue', 'NetLiquidation', 'UnrealizedPnL', 'RealizedPnL',
                'GrossPositionValue', 'BuyingPower', 'EquityWithLoanValue',
                'PreviousDayEquityWithLoanValue', 'FullInitMarginReq', 'FullMaintMarginReq'
            ]
            
            account_values = await self.ib.reqAccountSummaryAsync(account, ','.join(summary_tags))
            
            return [self._serialize_account_value(av) for av in account_values]
            
        except Exception as e:
            self.logger.error(f"Account summary request failed: {e}")
            raise RuntimeError(f"IBKR API error: {str(e)}")
    
    @rate_limit(calls_per_second=0.5)
    async def get_shortable_shares(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get short selling information for multiple symbols."""
        if not self.is_connected():
            raise IBKRConnectionError("IBKR not connected")
        
        results = {}
        
        for symbol in symbols:
            try:
                contract = Stock(symbol, 'SMART', 'USD')
                
                # Qualify the contract
                qualified_contracts = await self.ib.reqContractDetailsAsync(contract)
                if not qualified_contracts:
                    results[symbol] = {"error": "Contract not found"}
                    continue
                
                qualified_contract = qualified_contracts[0].contract
                
                # Request shortable shares
                shortable_shares = await self.ib.reqShortableSharesAsync(qualified_contract)
                
                # Get current market data
                ticker = self.ib.reqMktData(qualified_contract, '', False, False)
                await asyncio.sleep(1.5)  # Wait for market data
                
                results[symbol] = {
                    "symbol": symbol,
                    "shortable_shares": shortable_shares if shortable_shares != -1 else "Unlimited",
                    "current_price": safe_float(ticker.last or ticker.close),
                    "bid": safe_float(ticker.bid),
                    "ask": safe_float(ticker.ask),
                    "contract_id": qualified_contract.conId
                }
                
                # Clean up ticker
                self.ib.cancelMktData(qualified_contract)
                
            except Exception as e:
                results[symbol] = {"error": str(e)}
                self.logger.error(f"Error getting shortable shares for {symbol}: {e}")
        
        return results
    
    @rate_limit(calls_per_second=0.5)
    async def get_margin_requirements(self, symbols: List[str], account: Optional[str] = None) -> Dict[str, Dict]:
        """Get margin requirements for symbols."""
        if not self.is_connected():
            raise IBKRConnectionError("IBKR not connected")
        
        account = account or self.current_account
        results = {}
        
        for symbol in symbols:
            try:
                contract = Stock(symbol, 'SMART', 'USD')
                
                # Qualify contract
                qualified_contracts = await self.ib.reqContractDetailsAsync(contract)
                if not qualified_contracts:
                    results[symbol] = {"error": "Contract not found"}
                    continue
                
                contract_details = qualified_contracts[0]
                qualified_contract = contract_details.contract
                
                # Create what-if order for margin calculation
                from ib_async import Order
                order = Order()
                order.account = account
                order.action = 'SELL'  # Short position
                order.totalQuantity = 100
                order.orderType = 'MKT'
                
                try:
                    margin_info = await self.ib.whatIfOrderAsync(qualified_contract, order)
                    
                    results[symbol] = {
                        "symbol": symbol,
                        "init_margin": safe_float(margin_info.initMarginChange),
                        "maint_margin": safe_float(margin_info.maintMarginChange),
                        "equity_with_loan": safe_float(margin_info.equityWithLoanChange),
                        "commission": safe_float(margin_info.commission),
                        "min_tick": safe_float(contract_details.minTick),
                        "long_name": contract_details.longName
                    }
                except Exception as margin_error:
                    results[symbol] = {
                        "symbol": symbol,
                        "error": f"Margin calculation failed: {str(margin_error)}",
                        "min_tick": safe_float(contract_details.minTick),
                        "long_name": contract_details.longName,
                        "note": "Enable margin trading for detailed calculations"
                    }
                
            except Exception as e:
                results[symbol] = {"error": str(e)}
                self.logger.error(f"Error getting margin info for {symbol}: {e}")
        
        return results
    
    def _serialize_position(self, position) -> Dict:
        """Convert Position to serializable dict."""
        return {
            "symbol": position.contract.symbol,
            "secType": position.contract.secType,
            "exchange": position.contract.exchange,
            "position": safe_float(position.position),
            "avgCost": safe_float(position.avgCost),
            "marketPrice": safe_float(getattr(position, 'marketPrice', 0)),
            "marketValue": safe_float(getattr(position, 'marketValue', 0)),
            "unrealizedPNL": safe_float(getattr(position, 'unrealizedPNL', 0)),
            "realizedPNL": safe_float(getattr(position, 'realizedPNL', 0)),
            "account": position.account
        }
    
    def _serialize_account_value(self, account_value) -> Dict:
        """Convert AccountValue to serializable dict."""
        return {
            "tag": account_value.tag,
            "value": account_value.value,
            "currency": account_value.currency,
            "account": account_value.account
        }


# Global client instance
ibkr_client = IBKRClient()
