"""Stop loss order management for IBKR MCP Server."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import defaultdict

from ib_async import IB, Stock, Forex, Order, StopOrder, StopLimitOrder, MarketOrder, LimitOrder
from ib_async import Trade, OrderStatus

from ..utils import safe_float, safe_int, ValidationError
from ..enhanced_validators import StopLossValidator


class StopLossManager:
    """Manages stop loss orders with comprehensive monitoring and validation."""
    
    def __init__(self, ib_client: IB):
        self.ib = ib_client
        self.validator = StopLossValidator()
        self.logger = logging.getLogger(__name__)
        
        # Order tracking
        self.active_stops = {}  # order_id -> order_info
        self.bracket_orders = {}  # parent_order_id -> bracket_info
        
        # Monitoring
        self.order_states = defaultdict(list)  # Track state changes
        self.monitoring_active = False
    
    async def place_stop_loss(self, symbol: str, exchange: str = "SMART", 
                             currency: str = "USD", action: str = "SELL",
                             quantity: int = 100, stop_price: float = 0.0,
                             order_type: str = "STP", **kwargs) -> Dict:
        """Place stop loss order with comprehensive validation."""
        try:
            if not self.ib or not self.ib.isConnected():
                raise ConnectionError("Not connected to IBKR")
            
            # Validate inputs
            self.validator.validate_stop_loss_order({
                'symbol': symbol,
                'exchange': exchange,
                'currency': currency,
                'action': action,
                'quantity': quantity,
                'stop_price': stop_price,
                'order_type': order_type,
                **kwargs
            })
            
            # Create contract
            contract = self._create_contract(symbol, exchange, currency)
            
            # Qualify contract
            qualified = await self.ib.qualifyContractsAsync(contract)
            if not qualified:
                raise ValidationError(f"Could not qualify contract for {symbol}")
            
            contract = qualified[0]
            
            # Create stop loss order
            order = self._create_stop_loss_order(action, quantity, stop_price, order_type, **kwargs)
            
            # Additional validation with qualified contract
            self._validate_order_with_contract(order, contract)
            
            # Place order
            trade = self.ib.placeOrder(contract, order)
            
            # Track the order
            order_info = {
                'order_id': order.orderId,
                'symbol': symbol,
                'exchange': exchange,
                'currency': currency,
                'contract': contract,
                'order': order,
                'trade': trade,
                'order_type': order_type,
                'created_time': datetime.now(timezone.utc),
                'status': 'Submitted',
                'fills': []
            }
            
            self.active_stops[order.orderId] = order_info
            
            # Start monitoring if not already active
            if not self.monitoring_active:
                asyncio.create_task(self.monitor_orders())
            
            return {
                "order_id": order.orderId,
                "symbol": symbol,
                "exchange": exchange,
                "currency": currency,
                "action": action,
                "quantity": quantity,
                "stop_price": stop_price,
                "order_type": order_type,
                "status": "Submitted",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Stop loss placement failed: {e}")
            raise
    
    def _create_contract(self, symbol: str, exchange: str, currency: str):
        """Create appropriate contract based on exchange."""
        if exchange.upper() == 'IDEALPRO':
            from ib_async import Forex
            return Forex(symbol)
        else:
            return Stock(symbol, exchange, currency)
    
    def _create_stop_loss_order(self, action: str, quantity: int, stop_price: float, 
                               order_type: str, **kwargs) -> Order:
        """Create stop loss order based on type."""
        if order_type == "STP":
            order = StopOrder(action, quantity, stop_price)
        elif order_type == "STP LMT":
            limit_price = kwargs.get('limit_price')
            if limit_price is None:
                # Default limit price slightly away from stop price
                offset = 0.01 if action == 'SELL' else -0.01
                limit_price = stop_price + offset
            order = StopLimitOrder(action, quantity, stop_price, limit_price)
        elif order_type == "TRAIL":
            order = Order()
            order.action = action
            order.totalQuantity = quantity
            order.orderType = 'TRAIL'
            
            # Set trailing parameters
            if 'trail_amount' in kwargs:
                order.auxPrice = kwargs['trail_amount']
            elif 'trail_percent' in kwargs:
                order.trailPercent = kwargs['trail_percent']
            else:
                raise ValidationError("Trailing stop requires either trail_amount or trail_percent")
        else:
            raise ValidationError(f"Unsupported stop loss order type: {order_type}")
        
        # Set common attributes
        order.tif = kwargs.get('time_in_force', 'GTC')
        order.outsideRth = kwargs.get('outside_rth', True)
        order.transmit = True
        
        return order
    
    def _validate_order_with_contract(self, order: Order, contract) -> None:
        """Additional validation with qualified contract."""
        # Check minimum quantity constraints
        if hasattr(contract, 'minSize') and contract.minSize:
            if order.totalQuantity < contract.minSize:
                raise ValidationError(f"Order quantity {order.totalQuantity} below minimum {contract.minSize}")
        
        # Forex-specific validations
        if contract.secType == 'CASH':  # Forex
            if order.totalQuantity < 25000:  # Standard forex minimum
                raise ValidationError(f"Forex order minimum is 25,000 units, got {order.totalQuantity}")
    
    async def get_stop_losses(self, account: str = None, symbol: str = None, 
                             status: str = "active") -> List[Dict]:
        """Get existing stop loss orders with filtering."""
        try:
            if status == "active":
                orders = list(self.active_stops.values())
            else:
                # Get all orders from IBKR
                if status == "open":
                    ibkr_orders = await self.ib.reqOpenOrdersAsync()
                else:
                    ibkr_orders = await self.ib.reqAllOpenOrdersAsync()
                
                # Convert to our format
                orders = []
                for order in ibkr_orders:
                    if order.orderType in ['STP', 'STP LMT', 'TRAIL']:
                        order_info = self._convert_ibkr_order_to_info(order)
                        orders.append(order_info)
            
            # Apply filters
            filtered_orders = []
            for order_info in orders:
                if symbol and order_info.get('symbol', '').upper() != symbol.upper():
                    continue
                if account and order_info.get('account', '') != account:
                    continue
                
                filtered_orders.append(self._format_stop_loss_info(order_info))
            
            return filtered_orders
            
        except Exception as e:
            self.logger.error(f"Failed to get stop losses: {e}")
            raise
    
    def _convert_ibkr_order_to_info(self, ibkr_order) -> Dict:
        """Convert IBKR order to our internal format."""
        contract = ibkr_order.contract if hasattr(ibkr_order, 'contract') else None
        
        return {
            'order_id': ibkr_order.orderId,
            'symbol': contract.symbol if contract else 'Unknown',
            'exchange': contract.exchange if contract else 'Unknown',
            'currency': contract.currency if contract else 'Unknown',
            'order': ibkr_order,
            'order_type': ibkr_order.orderType,
            'status': getattr(ibkr_order, 'orderState', {}).get('status', 'Unknown'),
            'created_time': datetime.now(timezone.utc),  # Approximation
            'fills': []
        }
    
    def _format_stop_loss_info(self, order_info: Dict) -> Dict:
        """Format order info for API response."""
        order = order_info.get('order')
        
        result = {
            "order_id": order_info.get('order_id'),
            "symbol": order_info.get('symbol'),
            "exchange": order_info.get('exchange'),
            "currency": order_info.get('currency'),
            "action": order.action if order else 'Unknown',
            "quantity": order.totalQuantity if order else 0,
            "order_type": order_info.get('order_type'),
            "status": order_info.get('status', 'Unknown'),
            "created_time": order_info.get('created_time', datetime.now(timezone.utc)).isoformat(),
            "fills": order_info.get('fills', [])
        }
        
        # Add order-specific details
        if order:
            if hasattr(order, 'auxPrice') and order.auxPrice:
                if order.orderType == 'STP':
                    result["stop_price"] = order.auxPrice
                elif order.orderType == 'TRAIL':
                    result["trail_amount"] = order.auxPrice
            
            if hasattr(order, 'lmtPrice') and order.lmtPrice:
                result["limit_price"] = order.lmtPrice
            
            if hasattr(order, 'trailPercent') and order.trailPercent:
                result["trail_percent"] = order.trailPercent
            
            result["time_in_force"] = getattr(order, 'tif', 'Unknown')
            result["outside_rth"] = getattr(order, 'outsideRth', False)
        
        return result
    
    async def modify_stop_loss(self, order_id: int, **modifications) -> Dict:
        """Modify existing stop loss order."""
        try:
            if order_id not in self.active_stops:
                raise ValidationError(f"Stop loss order {order_id} not found in active orders")
            
            order_info = self.active_stops[order_id]
            original_order = order_info['order']
            
            # Create modified order
            modified_order = Order()
            modified_order.orderId = order_id
            modified_order.action = original_order.action
            modified_order.totalQuantity = modifications.get('quantity', original_order.totalQuantity)
            modified_order.orderType = original_order.orderType
            
            # Apply modifications based on order type
            if original_order.orderType == 'STP':
                modified_order.auxPrice = modifications.get('stop_price', original_order.auxPrice)
            elif original_order.orderType == 'STP LMT':
                modified_order.auxPrice = modifications.get('stop_price', original_order.auxPrice)
                modified_order.lmtPrice = modifications.get('limit_price', original_order.lmtPrice)
            elif original_order.orderType == 'TRAIL':
                if 'trail_amount' in modifications:
                    modified_order.auxPrice = modifications['trail_amount']
                elif 'trail_percent' in modifications:
                    modified_order.trailPercent = modifications['trail_percent']
                else:
                    modified_order.auxPrice = getattr(original_order, 'auxPrice', None)
                    modified_order.trailPercent = getattr(original_order, 'trailPercent', None)
            
            modified_order.tif = modifications.get('time_in_force', original_order.tif)
            modified_order.outsideRth = modifications.get('outside_rth', original_order.outsideRth)
            modified_order.transmit = True
            
            # Place modified order
            contract = order_info['contract']
            trade = self.ib.placeOrder(contract, modified_order)
            
            # Update tracking
            order_info['order'] = modified_order
            order_info['trade'] = trade
            
            return {
                "order_id": order_id,
                "status": "Modified",
                "modifications": modifications,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Stop loss modification failed: {e}")
            raise
    
    async def cancel_stop_loss(self, order_id: int) -> Dict:
        """Cancel existing stop loss order."""
        try:
            if order_id in self.active_stops:
                order_info = self.active_stops[order_id]
                order = order_info['order']
            else:
                # Try to find in IBKR open orders
                open_orders = await self.ib.reqOpenOrdersAsync()
                order = None
                for o in open_orders:
                    if o.orderId == order_id:
                        order = o
                        break
                
                if not order:
                    raise ValidationError(f"Order {order_id} not found")
            
            # Cancel the order
            self.ib.cancelOrder(order)
            
            # Remove from tracking
            if order_id in self.active_stops:
                del self.active_stops[order_id]
            
            return {
                "order_id": order_id,
                "status": "Cancelled",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Stop loss cancellation failed: {e}")
            raise
    
    async def monitor_orders(self):
        """Monitor stop loss orders for status changes."""
        self.monitoring_active = True
        self.logger.info("Started stop loss order monitoring")
        
        try:
            while self.monitoring_active and self.active_stops:
                await asyncio.sleep(2)  # Check every 2 seconds
                
                # Get current order statuses
                for order_id, order_info in list(self.active_stops.items()):
                    try:
                        trade = order_info.get('trade')
                        if trade and hasattr(trade, 'orderStatus'):
                            status = trade.orderStatus.status
                            
                            # Update status if changed
                            if order_info.get('status') != status:
                                old_status = order_info.get('status')
                                order_info['status'] = status
                                
                                self.logger.info(f"Order {order_id} status changed: {old_status} -> {status}")
                                
                                # Track state change
                                self.order_states[order_id].append({
                                    'timestamp': datetime.now(timezone.utc),
                                    'old_status': old_status,
                                    'new_status': status
                                })
                                
                                # Handle filled/cancelled orders
                                if status in ['Filled', 'Cancelled']:
                                    self._handle_completed_order(order_id, order_info, status)
                    
                    except Exception as e:
                        self.logger.error(f"Error monitoring order {order_id}: {e}")
                
        except Exception as e:
            self.logger.error(f"Order monitoring error: {e}")
        finally:
            self.monitoring_active = False
            self.logger.info("Stopped stop loss order monitoring")
    
    def _handle_completed_order(self, order_id: int, order_info: Dict, status: str):
        """Handle completed (filled/cancelled) orders."""
        try:
            # Log completion
            self.logger.info(f"Stop loss order {order_id} completed with status: {status}")
            
            # Update final status
            order_info['completed_time'] = datetime.now(timezone.utc)
            order_info['final_status'] = status
            
            # Move from active to completed (keep for history)
            # Don't delete immediately - let it age out or be cleaned up later
            
        except Exception as e:
            self.logger.error(f"Error handling completed order {order_id}: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status and statistics."""
        return {
            "monitoring_active": self.monitoring_active,
            "active_orders": len(self.active_stops),
            "total_state_changes": sum(len(changes) for changes in self.order_states.values()),
            "order_ids": list(self.active_stops.keys())
        }
    
    def stop_monitoring(self):
        """Stop order monitoring."""
        self.monitoring_active = False
        self.logger.info("Stop loss order monitoring stopped")
    
    def clear_completed_orders(self, older_than_hours: int = 24):
        """Clear completed orders older than specified hours."""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (older_than_hours * 3600)
        
        orders_to_remove = []
        for order_id, order_info in self.active_stops.items():
            if (order_info.get('final_status') in ['Filled', 'Cancelled'] and
                order_info.get('completed_time') and
                order_info['completed_time'].timestamp() < cutoff_time):
                orders_to_remove.append(order_id)
        
        for order_id in orders_to_remove:
            del self.active_stops[order_id]
            if order_id in self.order_states:
                del self.order_states[order_id]
        
        self.logger.info(f"Cleared {len(orders_to_remove)} completed orders")
        return len(orders_to_remove)
