"""Order management for IBKR MCP Server - Core trading functionality.

This module provides comprehensive order management including:
- Market order placement
- Limit order placement with price controls
- Order cancellation
- Order modification  
- Order status tracking
- Bracket order handling (entry + stop + target)

All operations include comprehensive validation and error handling.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

from ib_async import IB, Stock, Forex, Order, MarketOrder, LimitOrder, StopOrder
from ib_async import BracketOrder, Trade, OrderStatus, Contract

from ..utils import safe_float, safe_int, ValidationError, ConnectionError
from ..enhanced_validators import OrderValidator


class OrderManager:
    """Manages all order types with comprehensive validation and tracking."""
    
    def __init__(self, ib_client: IB):
        self.ib = ib_client
        self.validator = OrderValidator()
        self.logger = logging.getLogger(__name__)
        
        # Order tracking
        self.active_orders = {}  # order_id -> order_info
        self.bracket_orders = {}  # parent_order_id -> bracket_info
        
        # Order state monitoring
        self.order_states = defaultdict(list)  # Track state changes
        self.fill_tracking = {}  # order_id -> fill_info
        
        self.logger.info("OrderManager initialized")
    
    def _ensure_connected(self):
        """Ensure IBKR connection is active."""
        if not self.ib or not self.ib.isConnected():
            raise ConnectionError("Not connected to IBKR")
    
    def _create_contract(self, symbol: str, exchange: str = "SMART", 
                        currency: str = "USD") -> Contract:
        """Create appropriate contract based on symbol and exchange."""
        if exchange == "IDEALPRO":
            # Forex contract - symbol should be pair like "EURUSD"
            if len(symbol) == 6:
                # Full pair format
                return Forex(pair=symbol)
            else:
                # Single currency format - convert to pair
                return Forex(symbol=symbol, currency=currency)
        else:
            # Stock contract
            return Stock(symbol, exchange, currency)
    
    async def _qualify_contract(self, contract: Contract) -> Contract:
        """Qualify contract with IBKR."""
        qualified = await self.ib.qualifyContractsAsync(contract)
        if not qualified:
            raise ValidationError(f"Could not qualify contract for {contract.symbol}")
        return qualified[0]
    
    def _format_order_info(self, order_info: Dict) -> Dict:
        """Format order info for API response."""
        order = order_info.get('order')
        return {
            'order_id': order_info.get('order_id'),
            'symbol': order_info.get('symbol'),
            'exchange': order_info.get('exchange', 'SMART'),
            'currency': order_info.get('currency', 'USD'),
            'action': order.action if order else None,
            'quantity': order.totalQuantity if order else None,
            'order_type': order.orderType if order else None,
            'price': getattr(order, 'lmtPrice', None) if order else None,
            'stop_price': getattr(order, 'auxPrice', None) if order else None,
            'time_in_force': order.tif if order else None,
            'status': order_info.get('status', 'Unknown'),
            'fills': order_info.get('fills', []),
            'timestamp': order_info.get('timestamp')
        }
    
    # ============ MARKET ORDER PLACEMENT ============
    
    async def place_market_order(self, symbol: str, action: str, quantity: int,
                               exchange: str = "SMART", currency: str = "USD",
                               **kwargs) -> Dict:
        """Place market order with immediate execution."""
        try:
            self._ensure_connected()
            
            # Validate inputs
            order_data = {
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'exchange': exchange,
                'currency': currency,
                'order_type': 'MKT'
            }
            self.validator.validate_order_data(order_data)
            
            # Create and qualify contract
            contract = self._create_contract(symbol, exchange, currency)
            qualified_contract = await self._qualify_contract(contract)
            
            # Create market order
            order = MarketOrder(action, quantity)
            
            # Place order
            trade = self.ib.placeOrder(qualified_contract, order)
            order_id = trade.order.orderId
            
            # Track order
            order_info = {
                'order_id': order_id,
                'symbol': symbol,
                'exchange': exchange,
                'currency': currency,
                'order': trade.order,
                'contract': qualified_contract,
                'trade': trade,
                'status': 'Submitted',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'fills': []
            }
            self.active_orders[order_id] = order_info
            
            return {
                'success': True,
                'order_id': order_id,
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'order_type': 'MKT',
                'exchange': exchange,
                'currency': currency,
                'status': 'Submitted',
                'timestamp': order_info['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ============ LIMIT ORDER PLACEMENT ============
    
    async def place_limit_order(self, symbol: str, action: str, quantity: int,
                              price: float, exchange: str = "SMART", 
                              currency: str = "USD", time_in_force: str = "DAY",
                              **kwargs) -> Dict:
        """Place limit order with price control."""
        try:
            self._ensure_connected()
            
            # Validate inputs
            order_data = {
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'price': price,
                'exchange': exchange,
                'currency': currency,
                'time_in_force': time_in_force,
                'order_type': 'LMT'
            }
            self.validator.validate_order_data(order_data)
            
            # Create and qualify contract
            contract = self._create_contract(symbol, exchange, currency)
            qualified_contract = await self._qualify_contract(contract)
            
            # Create limit order
            order = LimitOrder(action, quantity, price)
            order.tif = time_in_force
            
            # Place order
            trade = self.ib.placeOrder(qualified_contract, order)
            order_id = trade.order.orderId
            
            # Track order
            order_info = {
                'order_id': order_id,
                'symbol': symbol,
                'exchange': exchange,
                'currency': currency,
                'order': trade.order,
                'contract': qualified_contract,
                'trade': trade,
                'status': 'Submitted',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'fills': []
            }
            self.active_orders[order_id] = order_info
            
            return {
                'success': True,
                'order_id': order_id,
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'price': price,
                'order_type': 'LMT',
                'time_in_force': time_in_force,
                'exchange': exchange,
                'currency': currency,
                'status': 'Submitted',
                'timestamp': order_info['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ============ ORDER CANCELLATION ============
    
    async def cancel_order(self, order_id: int) -> Dict:
        """Cancel existing order."""
        try:
            self._ensure_connected()
            
            # Check if order exists in our tracking
            found_trade = None
            if order_id not in self.active_orders:
                # Try to find order in IBKR open orders
                open_orders = await self.ib.reqOpenOrdersAsync()
                for trade in open_orders:
                    if trade.order.orderId == order_id:
                        found_trade = trade
                        break
                
                if not found_trade:
                    raise ValidationError(f"Order {order_id} not found")
            
            # Cancel the order
            if order_id in self.active_orders:
                order_info = self.active_orders[order_id]
                trade = order_info.get('trade')
                if trade:
                    self.ib.cancelOrder(trade.order)
                else:
                    # Fallback - create order object for cancellation
                    from ib_async import Order as IBOrder
                    order = IBOrder()
                    order.orderId = order_id
                    self.ib.cancelOrder(order)
            elif found_trade:
                # Cancel order found in IBKR open orders
                self.ib.cancelOrder(found_trade.order)
            
            # Remove from tracking and update status
            if order_id in self.active_orders:
                self.active_orders[order_id]['status'] = 'Cancelled'
                cancelled_order = self.active_orders.pop(order_id)
            else:
                cancelled_order = {'order_id': order_id}
            
            return {
                'success': True,
                'order_id': order_id,
                'status': 'Cancelled',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ============ ORDER MODIFICATION ============
    
    async def modify_order(self, order_id: int, **modifications) -> Dict:
        """Modify existing order parameters."""
        try:
            self._ensure_connected()
            
            # Validate modification parameters
            self.validator.validate_order_modification(order_id, modifications)
            
            # Check if order exists
            if order_id not in self.active_orders:
                raise ValidationError(f"Order {order_id} not found")
            
            order_info = self.active_orders[order_id]
            original_order = order_info['order']
            contract = order_info['contract']
            
            # Create modified order (copy of original)
            modified_order = Order()
            modified_order.orderId = order_id
            modified_order.action = original_order.action
            modified_order.totalQuantity = original_order.totalQuantity
            modified_order.orderType = original_order.orderType
            modified_order.tif = original_order.tif
            
            # Copy original prices
            if hasattr(original_order, 'lmtPrice'):
                modified_order.lmtPrice = original_order.lmtPrice
            if hasattr(original_order, 'auxPrice'):
                modified_order.auxPrice = original_order.auxPrice
            
            # Apply modifications
            applied_modifications = {}
            
            if 'quantity' in modifications:
                modified_order.totalQuantity = modifications['quantity']
                applied_modifications['quantity'] = modifications['quantity']
            
            if 'price' in modifications:
                if modified_order.orderType == 'LMT':
                    modified_order.lmtPrice = modifications['price']
                    applied_modifications['price'] = modifications['price']
                elif modified_order.orderType == 'STP':
                    modified_order.auxPrice = modifications['price']
                    applied_modifications['price'] = modifications['price']
            
            if 'time_in_force' in modifications:
                modified_order.tif = modifications['time_in_force']
                applied_modifications['time_in_force'] = modifications['time_in_force']
            
            # Place modified order (IBKR will update existing order)
            trade = self.ib.placeOrder(contract, modified_order)
            
            # Update tracking
            order_info['order'] = modified_order
            order_info['trade'] = trade
            order_info['status'] = 'Modified'
            order_info['modifications'] = applied_modifications
            order_info['modified_timestamp'] = datetime.now(timezone.utc).isoformat()
            
            return {
                'success': True,
                'order_id': order_id,
                'status': 'Modified',
                'modifications': applied_modifications,
                'timestamp': order_info['modified_timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"Error modifying order {order_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ============ ORDER STATUS TRACKING ============
    
    async def get_order_status(self, order_id: int) -> Dict:
        """Get detailed order status and execution information."""
        try:
            self._ensure_connected()
            
            # Check our tracking first
            if order_id in self.active_orders:
                order_info = self.active_orders[order_id]
                return {
                    'success': True,
                    **self._format_order_info(order_info)
                }
            
            # If not in our tracking, check IBKR directly
            open_orders = await self.ib.reqOpenOrdersAsync()
            for trade in open_orders:
                if trade.order.orderId == order_id:
                    # Create temporary order info for formatting
                    temp_order_info = {
                        'order_id': order_id,
                        'symbol': trade.contract.symbol,
                        'exchange': getattr(trade.contract, 'exchange', 'SMART'),
                        'currency': getattr(trade.contract, 'currency', 'USD'),
                        'order': trade.order,
                        'status': trade.orderStatus.status,
                        'fills': []
                    }
                    
                    return {
                        'success': True,
                        **self._format_order_info(temp_order_info)
                    }
            
            # Order not found
            raise ValidationError(f"Order {order_id} not found")
            
        except Exception as e:
            self.logger.error(f"Error getting order status for {order_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ============ BRACKET ORDER PLACEMENT ============
    
    async def place_bracket_order(self, symbol: str, action: str, quantity: int,
                                entry_price: float, stop_price: float, 
                                target_price: float, exchange: str = "SMART",
                                currency: str = "USD", **kwargs) -> Dict:
        """Place bracket order with entry, stop, and target."""
        try:
            self._ensure_connected()
            
            # Validate inputs
            order_data = {
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'entry_price': entry_price,
                'stop_price': stop_price,
                'target_price': target_price,
                'exchange': exchange,
                'currency': currency,
                'order_type': 'BRACKET'
            }
            self.validator.validate_order_data(order_data)
            
            # Create and qualify contract
            contract = self._create_contract(symbol, exchange, currency)
            qualified_contract = await self._qualify_contract(contract)
            
            # Create bracket orders
            parent_order, stop_order, target_order = self._create_bracket_orders(
                action, quantity, entry_price, stop_price, target_price
            )
            
            # Place parent order (entry)
            parent_trade = self.ib.placeOrder(qualified_contract, parent_order)
            parent_order_id = parent_trade.order.orderId
            
            # Place child orders (stop and target)
            stop_trade = self.ib.placeOrder(qualified_contract, stop_order)
            target_trade = self.ib.placeOrder(qualified_contract, target_order)
            
            # Track all orders
            bracket_info = {
                'parent_order_id': parent_order_id,
                'stop_order_id': stop_order.orderId,
                'target_order_id': target_order.orderId,
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'entry_price': entry_price,
                'stop_price': stop_price,
                'target_price': target_price,
                'status': 'Submitted',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            self.bracket_orders[parent_order_id] = bracket_info
            
            # Track individual orders too
            for order_id, trade, order_type in [
                (parent_order_id, parent_trade, 'ENTRY'),
                (stop_order.orderId, stop_trade, 'STOP'),
                (target_order.orderId, target_trade, 'TARGET')
            ]:
                order_info = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'exchange': exchange,
                    'currency': currency,
                    'order': trade.order,
                    'contract': qualified_contract,
                    'trade': trade,
                    'order_type_detail': order_type,
                    'bracket_parent': parent_order_id,
                    'status': 'Submitted',
                    'timestamp': bracket_info['timestamp'],
                    'fills': []
                }
                self.active_orders[order_id] = order_info
            
            return {
                'success': True,
                'parent_order_id': parent_order_id,
                'stop_order_id': stop_order.orderId,
                'target_order_id': target_order.orderId,
                'symbol': symbol,
                'action': action.upper(),
                'quantity': quantity,
                'entry_price': entry_price,
                'stop_price': stop_price,
                'target_price': target_price,
                'exchange': exchange,
                'currency': currency,
                'status': 'Submitted',
                'timestamp': bracket_info['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"Error placing bracket order: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _create_bracket_orders(self, action: str, quantity: int, 
                             entry_price: float, stop_price: float,
                             target_price: float) -> Tuple[Order, Order, Order]:
        """Create the three orders for a bracket order."""
        # Generate order IDs (IBKR will assign actual IDs)
        parent_id = self.ib.client.getReqId()
        stop_id = self.ib.client.getReqId()
        target_id = self.ib.client.getReqId()
        
        # Parent order (entry limit order)
        parent_order = LimitOrder(action, quantity, entry_price)
        parent_order.orderId = parent_id
        parent_order.transmit = False  # Don't transmit until children are set
        
        # Stop loss order
        stop_action = 'SELL' if action == 'BUY' else 'BUY'
        stop_order = StopOrder(stop_action, quantity, stop_price)
        stop_order.orderId = stop_id
        stop_order.parentId = parent_id
        stop_order.transmit = False
        
        # Target profit order  
        target_action = 'SELL' if action == 'BUY' else 'BUY'
        target_order = LimitOrder(target_action, quantity, target_price)
        target_order.orderId = target_id
        target_order.parentId = parent_id
        target_order.transmit = True  # Transmit all orders
        
        return parent_order, stop_order, target_order
    
    # ============ UTILITY METHODS ============
    
    def get_active_orders(self) -> Dict[int, Dict]:
        """Get all active orders."""
        return {
            order_id: self._format_order_info(order_info) 
            for order_id, order_info in self.active_orders.items()
        }
    
    def get_bracket_orders(self) -> Dict[int, Dict]:
        """Get all bracket orders."""
        return self.bracket_orders.copy()
    
    def cleanup_completed_orders(self) -> None:
        """Remove completed/cancelled orders from tracking."""
        completed_statuses = ['Filled', 'Cancelled', 'ApiCancelled', 'Inactive']
        completed_orders = [
            order_id for order_id, order_info in self.active_orders.items()
            if order_info.get('status') in completed_statuses
        ]
        
        for order_id in completed_orders:
            self.active_orders.pop(order_id, None)
        
        self.logger.info(f"Cleaned up {len(completed_orders)} completed orders")
