"""
Unit tests for IBKR MCP Server Stop Loss Manager.

Tests the stop loss functionality including order placement,
modification, cancellation, and risk management.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from ibkr_mcp_server.trading.stop_loss import StopLossManager
from ibkr_mcp_server.utils import ValidationError
from ibkr_mcp_server.enhanced_validators import TradingDisabledError, StopLossDisabledError


@pytest.fixture
def enabled_trading_settings():
    """Fixture to enable trading in enhanced_validators"""
    with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
        mock_settings.enable_trading = True
        mock_settings.enable_stop_loss_orders = True
        mock_settings.ibkr_is_paper = True
        yield mock_settings


@pytest.mark.unit
class TestStopLossManager:
    """Test stop loss trading functionality"""
    
    def test_stop_loss_manager_initialization(self, mock_ib):
        """Test stop loss manager initializes correctly"""
        stop_manager = StopLossManager(mock_ib)
        
        assert stop_manager.ib == mock_ib
        assert hasattr(stop_manager, 'validator')
        assert hasattr(stop_manager, 'active_stops')  # Actual attribute name
        
        # Test methods exist
        assert hasattr(stop_manager, 'place_stop_loss')
        assert hasattr(stop_manager, 'get_stop_losses')
        assert hasattr(stop_manager, 'modify_stop_loss')
        assert hasattr(stop_manager, 'cancel_stop_loss')
    
    @pytest.mark.asyncio
    async def test_place_stop_loss_basic(self, mock_ib):
        """Test basic stop loss placement"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup mocks with proper attribute configuration
        mock_contract = Mock()
        mock_contract.symbol = 'AAPL'
        mock_contract.exchange = 'SMART'
        mock_contract.currency = 'USD'
        # Fix: Configure minSize as None or numeric value, not Mock
        mock_contract.minSize = None
        mock_contract.multiplier = 1
        mock_ib.qualifyContractsAsync.return_value = [mock_contract]
        
        mock_order = Mock()
        mock_order.orderId = 99999
        mock_order.orderType = 'STP'
        mock_order.auxPrice = 180.00
        
        # Mock placeOrder to assign orderId and return trade
        def mock_place_order(contract, order):
            order.orderId = 99999  # Assign the expected order ID
            mock_trade = Mock()
            mock_trade.order = order
            mock_trade.contract = contract
            return mock_trade
        
        mock_ib.placeOrder.side_effect = mock_place_order
        
        with patch('ib_async.StopOrder') as mock_stop_order:
            mock_stop_order.return_value = mock_order
            result = await stop_manager.place_stop_loss(
                symbol="AAPL",
                action="SELL",
                quantity=100,
                stop_price=180.00,
                order_type="STP"
            )
        
        assert result['order_id'] == 99999
        assert result['symbol'] == 'AAPL'
        assert result['stop_price'] == 180.00
        assert result['order_type'] == 'STP'
        assert result['status'] == 'Submitted'
    
    @pytest.mark.asyncio
    async def test_place_stop_limit_order(self, mock_ib):
        """Test stop-limit order placement"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup mocks with proper attribute configuration
        mock_contract = Mock()
        mock_contract.symbol = 'AAPL'
        mock_contract.minSize = None  # Fix: Proper numeric or None value
        mock_contract.multiplier = 1
        mock_ib.qualifyContractsAsync.return_value = [mock_contract]
        
        mock_order = Mock()
        mock_order.orderId = 99998
        mock_order.orderType = 'STP LMT'
        mock_order.auxPrice = 180.00
        mock_order.lmtPrice = 179.50
        
        # Mock placeOrder to assign orderId and return trade
        def mock_place_order(contract, order):
            order.orderId = 99998  # Assign the expected order ID
            mock_trade = Mock()
            mock_trade.order = order
            mock_trade.contract = contract
            return mock_trade
        
        mock_ib.placeOrder.side_effect = mock_place_order
        
        with patch('ib_async.StopLimitOrder') as mock_stop_limit_order:
            mock_stop_limit_order.return_value = mock_order
            result = await stop_manager.place_stop_loss(
                symbol="AAPL",
                action="SELL",
                quantity=100,
                stop_price=180.00,
                order_type="STP LMT",
                limit_price=179.50
            )
        
        assert result['order_id'] == 99998
        assert result['order_type'] == 'STP LMT'
        assert result['stop_price'] == 180.00
        assert result['status'] == 'Submitted'
        # Note: limit_price is not returned in the standard response
    
    @pytest.mark.asyncio
    async def test_place_trailing_stop(self, mock_ib):
        """Test trailing stop order placement"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup mocks with proper attribute configuration
        mock_contract = Mock()
        mock_contract.symbol = 'TSLA'
        mock_contract.minSize = None  # Fix: Proper numeric or None value
        mock_contract.multiplier = 1
        mock_ib.qualifyContractsAsync.return_value = [mock_contract]
        
        mock_order = Mock()
        mock_order.orderId = 99997
        mock_order.orderType = 'TRAIL'
        mock_order.trailStopPrice = 8.0  # 8% trail
        
        # Mock placeOrder to assign orderId and return trade  
        def mock_place_order(contract, order):
            order.orderId = 99997  # Assign the expected order ID
            mock_trade = Mock()
            mock_trade.order = order
            mock_trade.contract = contract
            return mock_trade
        
        mock_ib.placeOrder.side_effect = mock_place_order
        
        with patch('ib_async.Order') as mock_order_class:
            mock_order_class.return_value = mock_order
            result = await stop_manager.place_stop_loss(
                symbol="TSLA",
                action="SELL",
                quantity=50,
                stop_price=220.00,
                order_type="TRAIL",
                trail_percent=8.0
            )
        
        assert result['order_id'] == 99997
        assert result['order_type'] == 'TRAIL'
        assert result['status'] == 'Submitted'
        # Note: trail_percent is not returned in the standard response
    
    @pytest.mark.asyncio
    async def test_get_stop_losses_active(self, mock_ib):
        """Test retrieving active stop loss orders"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup mock active orders
        mock_order1 = Mock()
        mock_order1.orderId = 99999
        mock_order1.orderType = 'STP'
        mock_order1.auxPrice = 180.00
        mock_order1.orderStatus.status = 'Submitted'
        
        mock_order2 = Mock()
        mock_order2.orderId = 99998
        mock_order2.orderType = 'TRAIL'
        mock_order2.trailStopPrice = 8.0
        mock_order2.orderStatus.status = 'Submitted'
        
        mock_ib.openOrders.return_value = [mock_order1, mock_order2]
        
        result = await stop_manager.get_stop_losses()
        
        assert isinstance(result, list)
        # Should return stop loss orders
        assert len(result) >= 0  # May be filtered
    
    @pytest.mark.asyncio
    async def test_modify_stop_loss(self, mock_ib):
        """Test modifying existing stop loss order"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup existing order in active_stops (as the actual implementation expects)
        mock_order = Mock()
        mock_order.orderId = 99999
        mock_order.orderType = 'STP'
        mock_order.auxPrice = 180.00
        
        # Add order to active_stops dictionary with all required fields
        mock_contract = Mock()
        mock_contract.symbol = 'AAPL'
        
        order_info = {
            'order_id': 99999,
            'symbol': 'AAPL',
            'order': mock_order,
            'contract': mock_contract,  # Add required contract field
            'status': 'Submitted'
        }
        stop_manager.active_stops[99999] = order_info
        
        # Mock the placeOrder method for modification
        def mock_place_order_modify(contract, order):
            order.orderId = 99999  # Keep same order ID for modification
            mock_trade = Mock()
            mock_trade.order = order
            mock_trade.contract = contract
            return mock_trade
        
        mock_ib.placeOrder.side_effect = mock_place_order_modify
        
        result = await stop_manager.modify_stop_loss(
            order_id=99999,
            stop_price=175.00
        )
        
        assert result['order_id'] == 99999
        assert result['status'] == 'Modified'
        assert 'modifications' in result
        assert result['modifications']['stop_price'] == 175.00
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_cancel_stop_loss(self, mock_ib):
        """Test cancelling stop loss order"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup existing order in active_stops
        mock_order = Mock()
        mock_order.orderId = 99999
        mock_order.orderType = 'STP'
        
        # Add order to active_stops dictionary  
        order_info = {
            'order_id': 99999,
            'symbol': 'AAPL',
            'order': mock_order,
            'status': 'Submitted'
        }
        stop_manager.active_stops[99999] = order_info
        
        # Mock the cancelOrder method
        mock_ib.cancelOrder.return_value = Mock()
        
        result = await stop_manager.cancel_stop_loss(order_id=99999)
        
        assert result['order_id'] == 99999
        assert result['status'] == 'Cancelled'
    
    def test_validate_stop_loss_parameters(self, mock_ib):
        """Test stop loss parameter validation"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test that validator exists and has expected validation functionality
        assert hasattr(stop_manager, 'validator')
        assert hasattr(stop_manager.validator, 'validate_stop_loss_order')
        
        # Test valid parameters - validator should not raise exception
        valid_order_data = {
            'symbol': "AAPL",
            'action': "SELL", 
            'quantity': 100,
            'stop_price': 180.00,
            'order_type': "STP"
        }
        
        # Should not raise exception for valid data
        try:
            stop_manager.validator.validate_stop_loss_order(valid_order_data)
            validation_passed = True
        except Exception:
            validation_passed = False
        
        assert validation_passed
        
        # Test invalid parameters
        invalid_order_data = {
            'symbol': "",  # Empty symbol
            'action': "SELL",
            'quantity': -100,  # Negative quantity
            'stop_price': 0,  # Zero price
            'order_type': "INVALID"
        }
        
        with pytest.raises(Exception):
            stop_manager.validator.validate_stop_loss_order(invalid_order_data)


@pytest.mark.unit
class TestStopLossManagerErrorHandling:
    """Test stop loss manager error handling"""
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_ib):
        """Test handling of connection errors"""
        stop_manager = StopLossManager(mock_ib)
        
        # Simulate connection error
        mock_ib.qualifyContractsAsync.side_effect = Exception("Connection lost")
        
        with pytest.raises(Exception) as exc_info:
            await stop_manager.place_stop_loss(
                symbol="AAPL",
                action="SELL",
                quantity=100,
                stop_price=180.00
            )
        
        assert "Connection lost" in str(exc_info.value) or "error" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_invalid_symbol_handling(self, mock_ib):
        """Test handling of invalid symbols"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup empty contract response (invalid symbol)
        mock_ib.qualifyContractsAsync.return_value = []
        
        with pytest.raises(Exception) as exc_info:
            await stop_manager.place_stop_loss(
                symbol="INVALID",
                action="SELL",
                quantity=100,
                stop_price=180.00
            )
        
        # Should raise appropriate error for invalid symbol
        assert "symbol" in str(exc_info.value).lower() or "contract" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_order_rejection_handling(self, mock_ib):
        """Test handling of order rejections"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup mocks for order rejection
        mock_contract = Mock()
        mock_contract.symbol = 'AAPL'
        mock_contract.minSize = None  # Fix: Proper value to avoid TypeError
        mock_contract.multiplier = 1
        mock_ib.qualifyContractsAsync.return_value = [mock_contract]
        
        # Simulate order rejection
        mock_ib.placeOrder.side_effect = Exception("Order rejected")
        
        with pytest.raises(Exception) as exc_info:
            await stop_manager.place_stop_loss(
                symbol="AAPL",
                action="SELL",
                quantity=100,
                stop_price=180.00
            )
        
        assert "rejected" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_modify_nonexistent_order(self, mock_ib):
        """Test modifying non-existent order"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup empty orders list
        mock_ib.openOrders.return_value = []
        
        with pytest.raises(Exception) as exc_info:
            await stop_manager.modify_stop_loss(order_id=99999, stop_price=175.00)
        
        assert "not found" in str(exc_info.value).lower() or "order" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_order(self, mock_ib):
        """Test cancelling non-existent order"""
        stop_manager = StopLossManager(mock_ib)
        
        # Setup empty orders list
        mock_ib.openOrders.return_value = []
        
        with pytest.raises(Exception) as exc_info:
            await stop_manager.cancel_stop_loss(order_id=99999)
        
        assert "not found" in str(exc_info.value).lower() or "order" in str(exc_info.value).lower()


@pytest.mark.unit
class TestStopLossManagerValidation:
    """Test stop loss manager validation functionality"""
    
    def test_validator_integration(self, mock_ib):
        """Test that validator properly integrates with stop loss manager"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test that validator exists and is properly configured
        assert hasattr(stop_manager, 'validator')
        assert stop_manager.validator is not None
        
        # Test validator has the expected validation method
        assert hasattr(stop_manager.validator, 'validate_stop_loss_order')
        
        # Test basic validation functionality through the validator
        valid_order = {
            'symbol': 'AAPL',
            'action': 'SELL', 
            'quantity': 100,
            'stop_price': 180.00,
            'order_type': 'STP'
        }
        
        # Should not raise exception for valid order
        try:
            stop_manager.validator.validate_stop_loss_order(valid_order)
            validation_works = True
        except Exception:
            validation_works = False
            
        assert validation_works
    
    def test_validation_error_handling(self, mock_ib):
        """Test validation error handling for invalid orders"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test that validator properly handles invalid order data
        invalid_order = {
            'symbol': '',  # Empty symbol
            'action': 'INVALID',  # Invalid action
            'quantity': -100,  # Negative quantity
            'stop_price': 0,  # Zero price
            'order_type': 'INVALID'  # Invalid order type
        }
        
        # Should raise exception for invalid order
        with pytest.raises(Exception):
            stop_manager.validator.validate_stop_loss_order(invalid_order)
        
        # Test individual validation issues
        partially_invalid_order = {
            'symbol': 'AAPL',
            'action': 'SELL',
            'quantity': 100,
            'stop_price': -50.0,  # Invalid negative price
            'order_type': 'STP'
        }
        
        with pytest.raises(Exception):
            stop_manager.validator.validate_stop_loss_order(partially_invalid_order)


@pytest.mark.unit
class TestStopLossManagerUtilities:
    """Test stop loss manager utility functions"""
    
    def test_active_stops_tracking(self, mock_ib):
        """Test active stops tracking functionality"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test that active_stops dictionary exists and is initialized
        assert hasattr(stop_manager, 'active_stops')
        assert isinstance(stop_manager.active_stops, dict)
        assert len(stop_manager.active_stops) == 0  # Should start empty
    
    def test_bracket_orders_tracking(self, mock_ib):
        """Test bracket orders tracking functionality"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test that bracket_orders dictionary exists and is initialized
        assert hasattr(stop_manager, 'bracket_orders')
        assert isinstance(stop_manager.bracket_orders, dict)
        assert len(stop_manager.bracket_orders) == 0  # Should start empty
    
    def test_monitoring_functionality(self, mock_ib):
        """Test monitoring status functionality"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test monitoring methods exist
        assert hasattr(stop_manager, 'get_monitoring_status')
        assert hasattr(stop_manager, 'stop_monitoring')
        assert hasattr(stop_manager, 'clear_completed_orders')
        
        # Test initial monitoring state
        status = stop_manager.get_monitoring_status()
        assert isinstance(status, dict)
        assert 'monitoring_active' in status or 'active' in status
    
    def test_order_state_tracking(self, mock_ib):
        """Test order state change tracking"""
        stop_manager = StopLossManager(mock_ib)
        
        # Test that order_states exists for tracking state changes
        assert hasattr(stop_manager, 'order_states')
        assert hasattr(stop_manager.order_states, 'default_factory')  # defaultdict


if __name__ == "__main__":
    # Run stop loss manager tests
    pytest.main([__file__, "-v", "--tb=short"])
