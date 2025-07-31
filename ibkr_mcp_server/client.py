"""IBKR Client with advanced trading capabilities."""

import asyncio
import logging
from typing import Dict, List, Optional, Union
from decimal import Decimal

from ib_async import IB, Stock, util
from .enhanced_config import EnhancedSettings
settings = EnhancedSettings()
from .utils import rate_limit, retry_on_failure, safe_float, safe_int, ValidationError, ConnectionError as IBKRConnectionError
from .trading import ForexManager, InternationalManager, StopLossManager


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
        
        # Trading managers (initialized after connection)
        self.forex_manager = None
        self.international_manager = None
        self.stop_loss_manager = None
    
    @property
    def is_paper(self) -> bool:
        """Check if this is a paper trading connection."""
        return self.port in [7497, 4002]  # Common paper trading ports
    
    async def _ensure_connected(self) -> bool:
        """Ensure IBKR connection is active, reconnect if needed."""
        if self.is_connected():
            return True
        
        try:
            await self.connect()
            return self.is_connected()
        except Exception as e:
            self.logger.error(f"Failed to ensure connection: {e}")
            return False
    
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
            
            # Initialize trading managers
            self._initialize_trading_managers()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to IBKR: {e}")
            raise IBKRConnectionError(f"Connection failed: {e}")
        finally:
            self._connecting = False
    
    def _initialize_trading_managers(self):
        """Initialize trading managers after successful connection."""
        try:
            self.forex_manager = ForexManager(self.ib)
            self.international_manager = InternationalManager(self.ib)
            self.stop_loss_manager = StopLossManager(self.ib)
            self.logger.info("Trading managers initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize trading managers: {e}")
    
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
    
    @rate_limit(calls_per_second=1.0)
    async def get_portfolio(self, account: Optional[str] = None) -> List[Dict]:
        """Get portfolio positions."""
        try:
            if not await self._ensure_connected():
                raise ConnectionError("Not connected to IBKR")
            
            account = account or self.current_account
            
            positions = await self.ib.reqPositionsAsync()
            
            portfolio = []
            for pos in positions:
                if not account or pos.account == account:
                    portfolio.append(self._serialize_position(pos))
            
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Portfolio request failed: {e}")
            raise RuntimeError(f"IBKR API error: {str(e)}")
    
    @rate_limit(calls_per_second=2.0)
    async def get_market_data(self, symbols: str) -> List[Dict]:
        """Get real-time market quotes for symbols."""
        try:
            if not await self._ensure_connected():
                raise ConnectionError("Not connected to IBKR")
            
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
            contracts = []
            
            # Create stock contracts
            for symbol in symbol_list:
                stock = Stock(symbol, 'SMART', 'USD')
                contracts.append(stock)
            
            # Qualify contracts first
            qualified = await self.ib.qualifyContractsAsync(*contracts)
            
            if not qualified:
                return [{"error": "No valid contracts found"}]
            
            # Get tickers
            tickers = await self.ib.reqTickersAsync(*qualified)
            
            results = []
            for ticker in tickers:
                results.append({
                    "symbol": ticker.contract.symbol,
                    "last": safe_float(ticker.last),
                    "bid": safe_float(ticker.bid),
                    "ask": safe_float(ticker.ask),
                    "close": safe_float(ticker.close),
                    "volume": safe_int(ticker.volume),
                    "contract_id": ticker.contract.conId
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Market data request failed: {e}")
            raise RuntimeError(f"IBKR API error: {str(e)}")
    
    @rate_limit(calls_per_second=1.0)
    async def get_account_summary(self, account: Optional[str] = None) -> List[Dict]:
        """Get account summary."""
        try:
            if not await self._ensure_connected():
                raise ConnectionError("Not connected to IBKR")
            
            account = account or self.current_account or "All"
            
            summary_tags = [
                'TotalCashValue', 'NetLiquidation', 'UnrealizedPnL', 'RealizedPnL',
                'GrossPositionValue', 'BuyingPower', 'EquityWithLoanValue',
                'PreviousDayEquityWithLoanValue', 'FullInitMarginReq', 'FullMaintMarginReq'
            ]
            
            account_values = await self.ib.reqAccountSummaryAsync()
            
            return [self._serialize_account_value(av) for av in account_values]
            
        except Exception as e:
            self.logger.error(f"Account summary request failed: {e}")
            raise RuntimeError(f"IBKR API error: {str(e)}")
    
    # Short selling method removed - reqShortableSharesAsync not available in ib-async 2.0.1
    # Use get_market_data() for basic quote information instead

    @retry_on_failure(max_attempts=2)
    async def get_margin_requirements(self, symbol: str, account: str = None) -> Dict:
        """Get margin requirements for a symbol."""
        try:
            if not await self._ensure_connected():
                raise ConnectionError("Not connected to IBKR")
                
            # Create contract
            contract = Stock(symbol, 'SMART', 'USD')
            await self.ib.qualifyContractsAsync(contract)
            
            if not contract.conId:
                return {"error": f"Invalid symbol: {symbol}"}
            
            # Get margin requirements - simplified for now
            # Note: IBKR API doesn't provide direct margin requirements
            # This would typically require additional market data subscriptions
            margin_info = {
                "symbol": symbol,
                "contract_id": contract.conId,
                "exchange": contract.exchange,
                "margin_requirement": "Market data subscription required",
                "note": "Use TWS for detailed margin calculations"
            }
            
            return margin_info
            
        except Exception as e:
            self.logger.error(f"Error getting margin info for {symbol}: {e}")
            return {"error": str(e)}

    # short_selling_analysis removed - depends on non-existent get_shortable_shares method
    
    async def switch_account(self, account_id: str) -> Dict:
        """Switch to a different IBKR account."""
        try:
            if account_id not in self.accounts:
                self.logger.error(f"Account {account_id} not found. Available: {self.accounts}")
                return {
                    "success": False,
                    "message": f"Account {account_id} not found",
                    "current_account": self.current_account,
                    "available_accounts": self.accounts
                }
            
            self.current_account = account_id
            self.logger.info(f"Switched to account: {account_id}")
            
            return {
                "success": True,
                "message": f"Switched to account: {account_id}",
                "current_account": self.current_account,
                "available_accounts": self.accounts
            }
            
        except Exception as e:
            self.logger.error(f"Error switching account: {e}")
            return {"success": False, "error": str(e)}

    async def get_accounts(self) -> Dict[str, Union[str, List[str]]]:
        """Get available accounts information."""
        try:
            if not await self._ensure_connected():
                await self.connect()
            
            return {
                "current_account": self.current_account,
                "available_accounts": self.accounts,
                "connected": self.is_connected(),
                "paper_trading": self.is_paper
            }
            
        except Exception as e:
            self.logger.error(f"Error getting accounts: {e}")
            return {"error": str(e)}

    async def get_connection_status(self) -> Dict:
        """Check IBKR TWS/Gateway connection status and account information."""
        try:
            is_connected = self.is_connected()
            
            result = {
                "connected": is_connected,
                "paper_trading": self.is_paper,
                "client_id": settings.ibkr_client_id,
                "host": settings.ibkr_host,
                "port": settings.ibkr_port
            }
            
            if is_connected:
                result.update({
                    "current_account": self.current_account,
                    "available_accounts": self.accounts,
                    "total_accounts": len(self.accounts) if self.accounts else 0,
                    "server_version": getattr(self.ib, 'serverVersion', 'unknown'),
                    "connection_time": str(getattr(self.ib, 'connectedAt', 'unknown'))
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting connection status: {e}")
            return {
                "connected": False,
                "error": str(e),
                "paper_trading": self.is_paper,
                "client_id": settings.ibkr_client_id,
                "host": settings.ibkr_host,
                "port": settings.ibkr_port
            }
    
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



    # ============ FOREX TRADING METHODS ============
    
    async def get_forex_rates(self, currency_pairs: str) -> List[Dict]:
        """Get real-time forex rates."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.forex_manager:
            raise ValidationError("Forex manager not initialized")
        
        return await self.forex_manager.get_forex_rates(currency_pairs)
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        """Convert currency using live forex rates."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.forex_manager:
            raise ValidationError("Forex manager not initialized")
        
        return await self.forex_manager.convert_currency(amount, from_currency, to_currency)

    # ============ INTERNATIONAL TRADING METHODS ============
    
    async def get_international_market_data(self, symbols: str, auto_detect: bool = True) -> List[Dict]:
        """Get market data for international stocks."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.international_manager:
            raise ValidationError("International manager not initialized")
        
        return await self.international_manager.get_international_market_data(symbols, auto_detect)
    
    async def resolve_international_symbol(self, symbol: str, exchange: str = None, currency: str = None) -> Dict:
        """Resolve international symbol with comprehensive information."""
        if not self.international_manager:
            raise ValidationError("International manager not initialized")
        
        return self.international_manager.resolve_symbol(symbol, exchange, currency)

    # ============ STOP LOSS MANAGEMENT METHODS ============
    
    async def place_stop_loss(self, symbol: str, exchange: str = "SMART", 
                             currency: str = "USD", action: str = "SELL",
                             quantity: int = 100, stop_price: float = 0.0,
                             order_type: str = "STP", **kwargs) -> Dict:
        """Place stop loss order."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.stop_loss_manager:
            raise ValidationError("Stop loss manager not initialized")
        
        return await self.stop_loss_manager.place_stop_loss(
            symbol, exchange, currency, action, quantity, stop_price, order_type, **kwargs
        )
    
    async def get_stop_losses(self, account: str = None, symbol: str = None, 
                             status: str = "active") -> List[Dict]:
        """Get existing stop loss orders."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.stop_loss_manager:
            raise ValidationError("Stop loss manager not initialized")
        
        return await self.stop_loss_manager.get_stop_losses(account, symbol, status)
    
    async def modify_stop_loss(self, order_id: int, **modifications) -> Dict:
        """Modify existing stop loss order."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.stop_loss_manager:
            raise ValidationError("Stop loss manager not initialized")
        
        return await self.stop_loss_manager.modify_stop_loss(order_id, **modifications)
    
    async def cancel_stop_loss(self, order_id: int) -> Dict:
        """Cancel existing stop loss order."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        if not self.stop_loss_manager:
            raise ValidationError("Stop loss manager not initialized")
        
        return await self.stop_loss_manager.cancel_stop_loss(order_id)


# Global client instance
ibkr_client = IBKRClient()
