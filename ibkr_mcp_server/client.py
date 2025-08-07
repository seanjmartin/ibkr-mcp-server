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
        self._reconnect_task = None
        
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
        # Cancel any pending reconnect task
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            self._reconnect_task = None
            
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
            self._connected = False
            self.logger.info("IBKR disconnected")
    
    def _on_disconnect(self):
        """Handle disconnection with automatic reconnection."""
        self._connected = False
        self.logger.warning("IBKR disconnected, scheduling reconnection...")
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect())
    
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
        except asyncio.CancelledError:
            # Task was cancelled, which is expected during shutdown
            self.logger.debug("Reconnection task cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected and self.ib is not None and self.ib.isConnected()
    
    @rate_limit(calls_per_second=1.0)
    async def get_portfolio(self, account: Optional[str] = None) -> List[Dict]:
        """Get portfolio positions using subscription model (avoids hanging reqPositionsAsync)."""
        try:
            if not await self._ensure_connected():
                raise ConnectionError("Not connected to IBKR")
            
            account = account or self.current_account
            
            # Use subscription model instead of hanging reqPositionsAsync()
            self.logger.debug(f"Subscribing to account updates for portfolio data: {account}")
            
            # Use the client directly to avoid event loop conflicts
            self.ib.client.reqAccountUpdates(True, account)
            
            # Wait for initial data to arrive
            await asyncio.sleep(3.0)
            
            # Get portfolio from cached data
            portfolio_items = self.ib.portfolio()
            
            # Unsubscribe to clean up
            self.ib.client.reqAccountUpdates(False, account)
            
            # Convert to our format, filtering by account if needed
            portfolio = []
            for item in portfolio_items:
                if not account or item.account == account:
                    portfolio.append(self._serialize_portfolio_item(item))
            
            self.logger.debug(f"Retrieved {len(portfolio)} portfolio positions")
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Portfolio request failed: {e}")
            # Ensure we clean up subscription on error
            try:
                self.ib.client.reqAccountUpdates(False, account or self.current_account)
            except:
                pass
            raise RuntimeError(f"IBKR API error: {str(e)}")
    
    @rate_limit(calls_per_second=2.0)
    async def get_market_data(self, symbols: str, auto_detect: bool = True) -> List[Dict]:
        """Get real-time market quotes for US and international symbols with intelligent auto-detection."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        # Use international manager for all symbols (handles US + international intelligently)
        if not self.international_manager:
            raise ValidationError("International manager not initialized")
        
        return await self.international_manager.get_international_market_data(symbols, auto_detect)
    
    @rate_limit(calls_per_second=1.0)
    async def get_account_summary(self, account: Optional[str] = None) -> List[Dict]:
        """Get account summary using subscription model (avoids hanging reqAccountSummaryAsync)."""
        try:
            if not await self._ensure_connected():
                raise ConnectionError("Not connected to IBKR")
            
            account = account or self.current_account
            
            # Use subscription model instead of hanging reqAccountSummaryAsync()
            self.logger.debug(f"Subscribing to account updates for summary data: {account}")
            
            # Use the client directly to avoid event loop conflicts
            self.ib.client.reqAccountUpdates(True, account)
            
            # Wait for initial data to arrive
            await asyncio.sleep(3.0)
            
            # Get account values from cached data
            account_values = self.ib.accountValues()
            
            # Unsubscribe to clean up
            self.ib.client.reqAccountUpdates(False, account)
            
            # Filter to desired tags for summary and convert to our format
            summary_tags = {
                'TotalCashValue', 'NetLiquidation', 'UnrealizedPnL', 'RealizedPnL',
                'GrossPositionValue', 'BuyingPower', 'EquityWithLoanValue',
                'PreviousDayEquityWithLoanValue', 'FullInitMarginReq', 'FullMaintMarginReq'
            }
            
            summary_values = []
            for av in account_values:
                if not account or av.account == account:
                    if av.tag in summary_tags:
                        summary_values.append(self._serialize_account_value(av))
            
            self.logger.debug(f"Retrieved {len(summary_values)} account summary values")
            return summary_values
            
        except Exception as e:
            self.logger.error(f"Account summary request failed: {e}")
            # Ensure we clean up subscription on error
            try:
                self.ib.client.reqAccountUpdates(False, account or self.current_account)
            except:
                pass
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
                "client_id": self.client_id,
                "host": self.host,
                "port": self.port
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
                "client_id": self.client_id,
                "host": self.host,
                "port": self.port
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
    
    def _serialize_portfolio_item(self, item) -> Dict:
        """Convert PortfolioItem to serializable dict (from subscription model)."""
        return {
            "symbol": item.contract.symbol,
            "secType": item.contract.secType,
            "exchange": item.contract.exchange,
            "position": safe_float(item.position),
            "avgCost": safe_float(item.averageCost),
            "marketPrice": safe_float(item.marketPrice),
            "marketValue": safe_float(item.marketValue),
            "unrealizedPNL": safe_float(item.unrealizedPNL),
            "realizedPNL": safe_float(item.realizedPNL),
            "account": item.account
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

    async def get_open_orders(self, account: str = None) -> List[Dict]:
        """Get all open/pending orders from IBKR."""
        if not await self._ensure_connected():
            raise IBKRConnectionError("Not connected to IBKR")
        
        try:
            # Get all open orders from IBKR
            open_orders = await self.ib.reqOpenOrdersAsync()
            
            orders_list = []
            for order_state in open_orders:
                if hasattr(order_state, 'order') and hasattr(order_state, 'contract'):
                    order = order_state.order
                    contract = order_state.contract
                    
                    order_info = {
                        "order_id": order.orderId,
                        "symbol": contract.symbol,
                        "exchange": getattr(contract, 'exchange', 'Unknown'),
                        "currency": getattr(contract, 'currency', 'Unknown'),
                        "action": order.action,
                        "quantity": order.totalQuantity,
                        "order_type": order.orderType,
                        "status": getattr(order_state, 'orderStatus', {}).get('status', 'Unknown'),
                        "filled": getattr(order_state, 'orderStatus', {}).get('filled', 0),
                        "remaining": getattr(order_state, 'orderStatus', {}).get('remaining', order.totalQuantity),
                        "avg_fill_price": getattr(order_state, 'orderStatus', {}).get('avgFillPrice', 0),
                        "last_fill_price": getattr(order_state, 'orderStatus', {}).get('lastFillPrice', 0),
                        "time_in_force": order.tif,
                        "account": getattr(order_state, 'orderStatus', {}).get('account', account or 'Unknown')
                    }
                    
                    # Add order-type specific info
                    if order.orderType == 'LMT':
                        order_info["limit_price"] = order.lmtPrice
                    elif order.orderType in ['STP', 'STP LMT']:
                        order_info["stop_price"] = order.auxPrice
                    
                    orders_list.append(order_info)
            
            return orders_list
            
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            return []

    async def get_completed_orders(self, account: str = None) -> List[Dict]:
        """Get completed orders from IBKR."""
        try:
            if not await self._ensure_connected():
                raise IBKRConnectionError("Not connected to IBKR")

            # Use timeout to handle IBKR API hanging issue with completed orders
            # When there are no completed orders, the API may not send completion callback
            try:
                completed_orders = await asyncio.wait_for(
                    self.ib.reqCompletedOrdersAsync(apiOnly=False),
                    timeout=5.0  # 5 second timeout
                )
            except asyncio.TimeoutError:
                self.logger.warning("reqCompletedOrdersAsync timed out - likely no completed orders")
                completed_orders = []  # Return empty list when timeout occurs
            
            # Filter by account if specified
            if account:
                completed_orders = [order for order in completed_orders if hasattr(order, 'account') and order.account == account]
            
            results = []
            for order in completed_orders:
                order_data = {
                    "order_id": order.orderId,
                    "symbol": getattr(order.contract, 'symbol', 'Unknown'),
                    "exchange": getattr(order.contract, 'exchange', 'Unknown'),
                    "currency": getattr(order.contract, 'currency', 'Unknown'),
                    "action": order.action,
                    "quantity": order.totalQuantity,
                    "order_type": order.orderType,
                    "limit_price": getattr(order, 'lmtPrice', None),
                    "aux_price": getattr(order, 'auxPrice', None),
                    "time_in_force": order.tif,
                    "status": getattr(order, 'orderState', {}).get('status', 'Unknown') if hasattr(order, 'orderState') else 'Unknown',
                    "filled": getattr(order, 'filled', 0),
                    "remaining": getattr(order, 'remaining', order.totalQuantity),
                    "avg_fill_price": getattr(order, 'avgFillPrice', 0),
                    "commission": getattr(order, 'commission', 0),
                    "account": getattr(order, 'account', 'Unknown'),
                    "order_ref": getattr(order, 'orderRef', ''),
                    "client_id": getattr(order, 'clientId', self.client_id)
                }
                results.append(order_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting completed orders: {e}")
            raise IBKRConnectionError(f"Failed to get completed orders: {str(e)}")

    async def get_executions(self, account: str = None, symbol: str = None, days_back: int = 7) -> List[Dict]:
        """Get trade executions from IBKR."""
        try:
            if not await self._ensure_connected():
                raise IBKRConnectionError("Not connected to IBKR")

            # Create execution filter
            from ib_async import ExecutionFilter
            exec_filter = ExecutionFilter()
            
            if account:
                exec_filter.account = account
            if symbol:
                exec_filter.symbol = symbol
            
            # Get executions
            executions = await self.ib.reqExecutionsAsync(exec_filter)
            
            results = []
            for execution_detail in executions:
                execution = execution_detail.execution
                contract = execution_detail.contract
                
                execution_data = {
                    "execution_id": execution.execId,
                    "order_id": execution.orderId,
                    "client_id": execution.clientId,
                    "symbol": contract.symbol,
                    "exchange": contract.exchange,
                    "currency": contract.currency,
                    "security_type": contract.secType,
                    "side": execution.side,
                    "shares": execution.shares,
                    "price": safe_float(execution.price),
                    "perm_id": execution.permId,
                    "liquidation": execution.liquidation,
                    "cumulative_quantity": execution.cumQty,
                    "average_price": safe_float(execution.avgPrice),
                    "order_ref": execution.orderRef,
                    "ev_rule": execution.evRule,
                    "ev_multiplier": safe_float(execution.evMultiplier),
                    "model_code": execution.modelCode,
                    "last_liquidity": execution.lastLiquidity,
                    "time": execution.time,
                    "account": execution.acctNumber
                }
                results.append(execution_data)
            
            # Sort by time (most recent first)
            results.sort(key=lambda x: x['time'], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting executions: {e}")
            raise IBKRConnectionError(f"Failed to get executions: {str(e)}")


# Global client instance
ibkr_client = IBKRClient()
