"""
Unit tests for OrderManager - Trading order placement and management functionality.

Tests comprehensive order management including:
- Market order placement
- Limit order placement with price controls  
- Order cancellation and modification
- Order status tracking
- Bracket order handling (entry + stop + target)

All tests use mocked IBKR API to avoid external dependencies.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from ibkr_mcp_server.trading.order_management import OrderManager
from ibkr_mcp_server.utils import ValidationError, ConnectionError
from ib_async import IB, Stock, Order, Trade, MarketOrder, LimitOrder, StopOrder


@pytest.fixture
def enabled_trading_settings():
    """Fixture to enable trading in enhanced_validators"""
    with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
        mock_settings.enable_trading = True
        mock_settings.enable_stop_loss_orders = True
        mock_settings.ibkr_is_paper = True
        mock_settings.max_order_size = 1000
        mock_settings.max_order_value_usd = 50000.0  # Increased for tests
        mock_settings.max_stop_loss_orders = 25
        mock_settings.max_trail_percent = 25.0
        mock_settings.supported_forex_pairs = ["EURUSD", "GBPUSD", "USDJPY"]
        mock_settings.supported_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD"]
        mock_settings.allowed_account_prefixes = ["DU", "DUH"]
        yield mock_settings


@pytest.fixture
def mock_ib():
    """Mock IB client with common order methods."""
    ib = Mock(spec=IB)
    ib.isConnected = Mock(return_value=True)
    ib.qualifyContractsAsync = AsyncMock()
    ib.placeOrder = Mock()
    ib.cancelOrder = Mock()
    ib.reqOpenOrdersAsync = AsyncMock(return_value=[])
    # Add client mock with getReqId method
    ib.client = Mock()
    ib.client.getReqId = Mock(return_value=12345)
    return ib


@pytest.fixture
def enabled_trading_settings():
    """Fixture to enable trading in enhanced_validators"""
    with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
        mock_settings.enable_trading = True
        mock_settings.enable_forex_trading = True
        mock_settings.enable_international_trading = True
        mock_settings.enable_stop_loss_orders = True
        mock_settings.ibkr_is_paper = True
        mock_settings.max_order_size = 1000  # Allow large test orders
        mock_settings.max_order_value_usd = 100000.0  # Allow large test values
        mock_settings.max_daily_orders = 1000  # Allow many test orders
        mock_settings.max_stop_loss_orders = 100  # Allow many test stop losses
        mock_settings.supported_forex_pairs = ["EURUSD", "GBPUSD", "USDJPY"]
        mock_settings.supported_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD"]
        mock_settings.allowed_account_prefixes = ["DU", "DUH"]
        yield mock_settings


@pytest.fixture
def order_manager(mock_ib, enabled_trading_settings):
    """Create OrderManager with mocked IB client and enhanced settings."""
    manager = OrderManager(mock_ib)
    return manager


@pytest.fixture
def sample_stock_contract():
    """Sample stock contract for testing."""
    contract = Stock("AAPL", "SMART", "USD")
    contract.conId = 265598  # Apple's contract ID
    return contract


@pytest.fixture
def sample_trade():
    """Sample trade object for testing."""
    trade = Mock(spec=Trade)
    trade.order = Mock(spec=Order)
    trade.order.orderId = 12345
    trade.order.action = "BUY"
    trade.order.totalQuantity = 100
    trade.order.orderType = "MKT"
    trade.orderStatus = Mock()
    trade.contract = Mock()
    trade.contract.symbol = "AAPL"
    trade.orderStatus.status = "Submitted"
    return trade


class TestOrderManagerInitialization:
    """Test OrderManager initialization and basic functionality."""
    
    def test_order_manager_initialization(self, mock_ib):
        """Test OrderManager initializes correctly."""
        manager = OrderManager(mock_ib)
        
        assert manager.ib == mock_ib
        assert hasattr(manager, 'validator')
        assert hasattr(manager, 'active_orders')
        assert hasattr(manager, 'bracket_orders')
        assert isinstance(manager.active_orders, dict)
        assert isinstance(manager.bracket_orders, dict)
    
    def test_connection_check(self, order_manager, mock_ib):
        """Test connection validation."""
        # Test connected case
        mock_ib.isConnected.return_value = True
        order_manager._ensure_connected()  # Should not raise
        
        # Test disconnected case
        mock_ib.isConnected.return_value = False
        with pytest.raises(ConnectionError):
            order_manager._ensure_connected()
    
    def test_contract_creation(self, order_manager):
        """Test contract creation for different asset types."""
        # Test stock contract
        stock_contract = order_manager._create_contract("AAPL", "SMART", "USD")
        assert stock_contract.symbol == "AAPL"
        assert stock_contract.exchange == "SMART"
        assert stock_contract.currency == "USD"
        
        # Test forex contract (IBKR Forex expects pair format like EURUSD)
        forex_contract = order_manager._create_contract("EURUSD", "IDEALPRO", "USD")
        assert forex_contract.symbol == "EUR"  # Base currency
        assert forex_contract.currency == "USD"  # Quote currency


class TestMarketOrderPlacement:
    """Test market order placement functionality."""
    
    @pytest.mark.asyncio
    async def test_place_market_order_success(self, order_manager, mock_ib, sample_stock_contract, sample_trade):
        """Test successful market order placement."""
        # Setup mocks
        mock_ib.qualifyContractsAsync.return_value = [sample_stock_contract]
        mock_ib.placeOrder.return_value = sample_trade
        
        # Place market order
        result = await order_manager.place_market_order(
            symbol="AAPL",
            action="BUY", 
            quantity=100
        )
        
        # Verify result
        assert result['success'] == True
        assert result['order_id'] == 12345
        assert result['symbol'] == "AAPL"
        assert result['action'] == "BUY"
        assert result['quantity'] == 100
        assert result['order_type'] == "MKT"
        assert result['status'] == "Submitted"
        assert 'timestamp' in result
        
        # Verify order is tracked
        assert 12345 in order_manager.active_orders
        order_info = order_manager.active_orders[12345]
        assert order_info['symbol'] == "AAPL"
        assert order_info['status'] == "Submitted"
    
    @pytest.mark.asyncio
    async def test_place_market_order_invalid_parameters(self, order_manager):
        """Test market order with invalid parameters."""
        # Test invalid action
        result = await order_manager.place_market_order(
            symbol="AAPL",
            action="INVALID",
            quantity=100
        )
        assert result['success'] == False
        assert 'error' in result
        
        # Test negative quantity
        result = await order_manager.place_market_order(
            symbol="AAPL", 
            action="BUY",
            quantity=-100
        )
        assert result['success'] == False
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_place_market_order_connection_error(self, order_manager, mock_ib):
        """Test market order placement when disconnected."""
        mock_ib.isConnected.return_value = False
        
        result = await order_manager.place_market_order(
            symbol="AAPL",
            action="BUY",
            quantity=100
        )
        
        assert result['success'] == False
        assert 'error' in result
        assert 'connected' in result['error'].lower()  # Changed from 'connection' to match actual error message


class TestLimitOrderPlacement:
    """Test limit order placement functionality."""
    
    @pytest.mark.asyncio
    async def test_place_limit_order_success(self, order_manager, mock_ib, sample_stock_contract, sample_trade):
        """Test successful limit order placement."""
        # Setup mocks
        sample_trade.order.orderType = "LMT"
        sample_trade.order.lmtPrice = 150.0
        sample_trade.order.tif = "DAY"
        
        mock_ib.qualifyContractsAsync.return_value = [sample_stock_contract]
        mock_ib.placeOrder.return_value = sample_trade
        
        # Place limit order
        result = await order_manager.place_limit_order(
            symbol="AAPL",
            action="BUY",
            quantity=100,
            price=150.0,
            time_in_force="DAY"
        )
        
        # Verify result
        assert result['success'] == True
        assert result['order_id'] == 12345
        assert result['symbol'] == "AAPL"
        assert result['action'] == "BUY"
        assert result['quantity'] == 100
        assert result['price'] == 150.0
        assert result['order_type'] == "LMT"
        assert result['time_in_force'] == "DAY"
        assert result['status'] == "Submitted"
    
    @pytest.mark.asyncio
    async def test_place_limit_order_different_tif(self, order_manager, mock_ib, sample_stock_contract, sample_trade):
        """Test limit order with different time-in-force values."""
        mock_ib.qualifyContractsAsync.return_value = [sample_stock_contract]
        mock_ib.placeOrder.return_value = sample_trade
        
        # Test GTC order
        result = await order_manager.place_limit_order(
            symbol="AAPL",
            action="BUY",
            quantity=100,
            price=150.0,
            time_in_force="GTC"
        )
        
        assert result['success'] == True
        assert result['time_in_force'] == "GTC"


class TestOrderCancellation:
    """Test order cancellation functionality."""
    
    @pytest.mark.asyncio
    async def test_cancel_order_success(self, order_manager, mock_ib, sample_trade):
        """Test successful order cancellation."""
        # Add order to tracking first
        order_id = 12345
        order_manager.active_orders[order_id] = {
            'order_id': order_id,
            'symbol': 'AAPL',
            'status': 'Submitted',
            'trade': sample_trade
        }
        
        # Cancel order
        result = await order_manager.cancel_order(order_id)
        
        # Verify result
        assert result['success'] == True
        assert result['order_id'] == order_id
        assert result['status'] == 'Cancelled'
        assert 'timestamp' in result
        
        # Verify order removed from tracking
        assert order_id not in order_manager.active_orders
    
    @pytest.mark.asyncio
    async def test_cancel_order_not_found(self, order_manager, mock_ib):
        """Test cancelling non-existent order."""
        mock_ib.reqOpenOrdersAsync.return_value = []
        
        result = await order_manager.cancel_order(99999)
        
        assert result['success'] == False
        assert 'error' in result
        assert 'not found' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_cancel_order_found_in_open_orders(self, order_manager, mock_ib, sample_trade):
        """Test cancelling order found in IBKR open orders."""
        sample_trade.order.orderId = 12345
        mock_ib.reqOpenOrdersAsync.return_value = [sample_trade]
        
        result = await order_manager.cancel_order(12345)
        
        assert result['success'] == True
        assert result['order_id'] == 12345
        mock_ib.cancelOrder.assert_called_once()


class TestOrderModification:
    """Test order modification functionality."""
    
    @pytest.mark.asyncio
    async def test_modify_order_quantity(self, order_manager, mock_ib, sample_stock_contract):
        """Test modifying order quantity."""
        # Setup existing order
        order_id = 12345
        original_order = Mock()
        original_order.orderId = order_id
        original_order.action = "BUY"
        original_order.totalQuantity = 100
        original_order.orderType = "LMT"
        original_order.lmtPrice = 150.0
        original_order.tif = "DAY"
        
        order_manager.active_orders[order_id] = {
            'order_id': order_id,
            'symbol': 'AAPL',
            'order': original_order,
            'contract': sample_stock_contract,
            'status': 'Submitted'
        }
        
        # Mock placeOrder for modification
        modified_trade = Mock()
        modified_trade.order = original_order
        mock_ib.placeOrder.return_value = modified_trade
        
        # Modify quantity
        result = await order_manager.modify_order(order_id, quantity=150)
        
        # Verify result
        assert result['success'] == True
        assert result['order_id'] == order_id
        assert result['status'] == 'Modified'
        assert 'modifications' in result
        assert result['modifications']['quantity'] == 150
    
    @pytest.mark.asyncio
    async def test_modify_order_price(self, order_manager, mock_ib, sample_stock_contract):
        """Test modifying order price."""
        # Setup existing limit order
        order_id = 12345
        original_order = Mock()
        original_order.orderId = order_id
        original_order.action = "BUY"
        original_order.totalQuantity = 100
        original_order.orderType = "LMT"
        original_order.lmtPrice = 150.0
        original_order.tif = "DAY"
        
        order_manager.active_orders[order_id] = {
            'order_id': order_id,
            'symbol': 'AAPL',
            'order': original_order,
            'contract': sample_stock_contract,
            'status': 'Submitted'
        }
        
        modified_trade = Mock()
        modified_trade.order = original_order
        mock_ib.placeOrder.return_value = modified_trade
        
        # Modify price
        result = await order_manager.modify_order(order_id, price=155.0)
        
        assert result['success'] == True
        assert result['modifications']['price'] == 155.0
    
    @pytest.mark.asyncio
    async def test_modify_order_not_found(self, order_manager):
        """Test modifying non-existent order."""
        result = await order_manager.modify_order(99999, quantity=150)
        
        assert result['success'] == False
        assert 'error' in result
        assert 'not found' in result['error'].lower()


class TestOrderStatus:
    """Test order status tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_get_order_status_tracked_order(self, order_manager):
        """Test getting status of tracked order."""
        # Add order to tracking
        order_id = 12345
        order_manager.active_orders[order_id] = {
            'order_id': order_id,
            'symbol': 'AAPL',
            'exchange': 'SMART',
            'currency': 'USD',
            'order': Mock(action="BUY", totalQuantity=100, orderType="MKT"),
            'status': 'Submitted',
            'timestamp': '2024-01-15T14:30:00Z',
            'fills': []
        }
        
        result = await order_manager.get_order_status(order_id)
        
        assert result['success'] == True
        assert result['order_id'] == order_id
        assert result['symbol'] == 'AAPL'
        assert result['status'] == 'Submitted'
    
    @pytest.mark.asyncio
    async def test_get_order_status_from_ibkr(self, order_manager, mock_ib, sample_trade):
        """Test getting status from IBKR when not tracked locally."""
        sample_trade.order.orderId = 12345
        sample_trade.contract.symbol = "AAPL"
        sample_trade.orderStatus.status = "Working"
        
        mock_ib.reqOpenOrdersAsync.return_value = [sample_trade]
        
        result = await order_manager.get_order_status(12345)
        
        assert result['success'] == True
        assert result['order_id'] == 12345
        assert result['symbol'] == "AAPL"
        assert result['status'] == "Working"
    
    @pytest.mark.asyncio
    async def test_get_order_status_not_found(self, order_manager, mock_ib):
        """Test getting status of non-existent order."""
        mock_ib.reqOpenOrdersAsync.return_value = []
        
        result = await order_manager.get_order_status(99999)
        
        assert result['success'] == False
        assert 'error' in result
        assert 'not found' in result['error'].lower()


class TestBracketOrders:
    """Test bracket order functionality."""
    
    @pytest.mark.asyncio
    async def test_place_bracket_order_success(self, order_manager, mock_ib, sample_stock_contract):
        """Test successful bracket order placement."""
        # Mock bracket order creation
        with patch.object(order_manager, '_create_bracket_orders') as mock_create:
            parent_order = Mock()
            parent_order.orderId = 12345
            stop_order = Mock()
            stop_order.orderId = 12346  
            target_order = Mock()
            target_order.orderId = 12347
            
            mock_create.return_value = (parent_order, stop_order, target_order)
            
            # Mock trades
            parent_trade = Mock()
            parent_trade.order = parent_order
            stop_trade = Mock()
            stop_trade.order = stop_order
            target_trade = Mock()
            target_trade.order = target_order
            
            mock_ib.qualifyContractsAsync.return_value = [sample_stock_contract]
            mock_ib.placeOrder.side_effect = [parent_trade, stop_trade, target_trade]
            
            # Place bracket order
            result = await order_manager.place_bracket_order(
                symbol="AAPL",
                action="BUY",
                quantity=100,
                entry_price=150.0,
                stop_price=145.0,
                target_price=160.0
            )
            
            # Verify result
            assert result['success'] == True
            assert result['parent_order_id'] == 12345
            assert result['stop_order_id'] == 12346
            assert result['target_order_id'] == 12347
            assert result['symbol'] == "AAPL"
            assert result['action'] == "BUY"
            assert result['quantity'] == 100
            assert result['entry_price'] == 150.0
            assert result['stop_price'] == 145.0
            assert result['target_price'] == 160.0
            
            # Verify bracket tracking
            assert 12345 in order_manager.bracket_orders
            bracket_info = order_manager.bracket_orders[12345]
            assert bracket_info['stop_order_id'] == 12346
            assert bracket_info['target_order_id'] == 12347
    
    def test_create_bracket_orders(self, order_manager, mock_ib):
        """Test bracket order creation logic."""
        # Mock getReqId for order IDs
        mock_ib.client.getReqId.side_effect = [12345, 12346, 12347]
        
        parent_order, stop_order, target_order = order_manager._create_bracket_orders(
            action="BUY",
            quantity=100,
            entry_price=150.0,
            stop_price=145.0,
            target_price=160.0
        )
        
        # Verify parent order
        assert parent_order.action == "BUY"
        assert parent_order.totalQuantity == 100
        assert parent_order.lmtPrice == 150.0
        assert parent_order.transmit == False
        
        # Verify stop order
        assert stop_order.action == "SELL"  # Opposite of parent
        assert stop_order.totalQuantity == 100
        assert stop_order.auxPrice == 145.0
        assert stop_order.parentId == 12345
        assert stop_order.transmit == False
        
        # Verify target order
        assert target_order.action == "SELL"  # Opposite of parent
        assert target_order.totalQuantity == 100
        assert target_order.lmtPrice == 160.0
        assert target_order.parentId == 12345
        assert target_order.transmit == True


class TestOrderManagerUtilities:
    """Test utility methods and order tracking."""
    
    def test_get_active_orders(self, order_manager):
        """Test getting all active orders."""
        # Add sample orders
        order_manager.active_orders[12345] = {
            'order_id': 12345,
            'symbol': 'AAPL',
            'order': Mock(action="BUY", totalQuantity=100),
            'status': 'Submitted'
        }
        order_manager.active_orders[12346] = {
            'order_id': 12346,
            'symbol': 'MSFT',
            'order': Mock(action="SELL", totalQuantity=50),
            'status': 'Working'
        }
        
        active_orders = order_manager.get_active_orders()
        
        assert len(active_orders) == 2
        assert 12345 in active_orders
        assert 12346 in active_orders
        assert active_orders[12345]['symbol'] == 'AAPL'
        assert active_orders[12346]['symbol'] == 'MSFT'
    
    def test_get_bracket_orders(self, order_manager):
        """Test getting all bracket orders."""
        # Add sample bracket order
        order_manager.bracket_orders[12345] = {
            'parent_order_id': 12345,
            'stop_order_id': 12346,
            'target_order_id': 12347,
            'symbol': 'AAPL',
            'status': 'Submitted'
        }
        
        bracket_orders = order_manager.get_bracket_orders()
        
        assert len(bracket_orders) == 1
        assert 12345 in bracket_orders
        assert bracket_orders[12345]['symbol'] == 'AAPL'
        assert bracket_orders[12345]['stop_order_id'] == 12346
    
    def test_cleanup_completed_orders(self, order_manager):
        """Test cleanup of completed orders."""
        # Add orders with different statuses
        order_manager.active_orders[12345] = {
            'order_id': 12345,
            'symbol': 'AAPL',
            'status': 'Filled'  # Completed
        }
        order_manager.active_orders[12346] = {
            'order_id': 12346, 
            'symbol': 'MSFT',
            'status': 'Working'  # Active
        }
        order_manager.active_orders[12347] = {
            'order_id': 12347,
            'symbol': 'GOOGL', 
            'status': 'Cancelled'  # Completed
        }
        
        # Cleanup
        order_manager.cleanup_completed_orders()
        
        # Verify only active orders remain
        assert len(order_manager.active_orders) == 1
        assert 12346 in order_manager.active_orders
        assert 12345 not in order_manager.active_orders
        assert 12347 not in order_manager.active_orders
    
    def test_format_order_info(self, order_manager):
        """Test order information formatting."""
        order = Mock()
        order.action = "BUY"
        order.totalQuantity = 100
        order.orderType = "LMT"
        order.lmtPrice = 150.0
        order.tif = "DAY"
        
        order_info = {
            'order_id': 12345,
            'symbol': 'AAPL',
            'exchange': 'SMART',
            'currency': 'USD',
            'order': order,
            'status': 'Submitted',
            'timestamp': '2024-01-15T14:30:00Z',
            'fills': []
        }
        
        formatted = order_manager._format_order_info(order_info)
        
        assert formatted['order_id'] == 12345
        assert formatted['symbol'] == 'AAPL'
        assert formatted['action'] == "BUY"
        assert formatted['quantity'] == 100
        assert formatted['order_type'] == "LMT"
        assert formatted['price'] == 150.0
        assert formatted['time_in_force'] == "DAY"
        assert formatted['status'] == 'Submitted'


class TestOrderValidation:
    """Test order parameter validation."""
    
    @pytest.mark.asyncio
    async def test_invalid_symbol(self, order_manager):
        """Test validation with invalid symbol."""
        result = await order_manager.place_market_order(
            symbol="",  # Empty symbol
            action="BUY",
            quantity=100
        )
        
        assert result['success'] == False
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_invalid_action(self, order_manager):
        """Test validation with invalid action."""
        result = await order_manager.place_market_order(
            symbol="AAPL",
            action="INVALID",
            quantity=100
        )
        
        assert result['success'] == False
        assert 'error' in result
    
    @pytest.mark.asyncio 
    async def test_zero_quantity(self, order_manager):
        """Test validation with zero quantity."""
        result = await order_manager.place_market_order(
            symbol="AAPL",
            action="BUY",
            quantity=0
        )
        
        assert result['success'] == False
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_negative_price(self, order_manager):
        """Test validation with negative price."""
        result = await order_manager.place_limit_order(
            symbol="AAPL",
            action="BUY", 
            quantity=100,
            price=-150.0  # Negative price
        )
        
        assert result['success'] == False
        assert 'error' in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_order_manager_complex_scenarios(enabled_trading_settings):
    """Test complex multi-order scenarios and interactions"""
    # Setup comprehensive test environment
    mock_ib = Mock()
    mock_ib.isConnected.return_value = True
    mock_ib.nextOrderId.return_value = 10001
    
    # Use enhanced settings with increased limits for testing
    with patch('ibkr_mcp_server.trading.order_management.OrderValidator') as mock_validator_class:
        # Create a mock validator that accepts all orders
        mock_validator = Mock()
        mock_validator.validate_order_placement = Mock()  # Doesn't raise exceptions
        mock_validator_class.return_value = mock_validator
        
        order_manager = OrderManager(mock_ib)
    
    # Setup mock contract
    mock_contract = Mock()
    mock_contract.symbol = 'AAPL'
    mock_contract.exchange = 'SMART'
    mock_contract.currency = 'USD'
    mock_contract.minSize = None
    mock_contract.multiplier = 1
    
    # Fix: Make qualifyContractsAsync return an awaitable (AsyncMock)
    async def mock_qualify_contracts_async(contract):
        return [mock_contract]
    
    mock_ib.qualifyContractsAsync = AsyncMock(side_effect=mock_qualify_contracts_async)
    
    # Setup order tracking
    placed_orders = []
    order_id_counter = 10001
    
    def mock_place_order(contract, order):
        nonlocal order_id_counter
        order.orderId = order_id_counter
        order_id_counter += 1
        mock_trade = Mock()
        mock_trade.order = order
        mock_trade.contract = contract
        placed_orders.append({
            'order_id': order.orderId,
            'symbol': contract.symbol,
            'action': order.action,
            'quantity': order.totalQuantity,
            'order_type': order.orderType
        })
        return mock_trade
    
    mock_ib.placeOrder.side_effect = mock_place_order
    
    # Test complex scenario: Multiple related orders
    with patch('ib_async.MarketOrder') as mock_market_order, \
         patch('ib_async.LimitOrder') as mock_limit_order:
        
        # Configure order mocks
        mock_market_order.side_effect = lambda action, quantity: Mock(
            action=action, 
            totalQuantity=quantity, 
            orderType='MKT', 
            orderId=None
        )
        mock_limit_order.side_effect = lambda action, quantity, price: Mock(
            action=action, 
            totalQuantity=quantity, 
            lmtPrice=price,
            orderType='LMT', 
            orderId=None
        )
        
        # Scenario 1: Place initial market order
        result1 = await order_manager.place_market_order(
            symbol="AAPL",
            action="BUY",
            quantity=100
        )
        
        # Scenario 2: Place limit order as follow-up
        result2 = await order_manager.place_limit_order(
            symbol="AAPL", 
            action="SELL",
            quantity=50,
            price=185.0
        )
        
        # Scenario 3: Place another limit order with different parameters
        result3 = await order_manager.place_limit_order(
            symbol="AAPL",
            action="SELL", 
            quantity=25,
            price=190.0,
            time_in_force="GTC"
        )
    
    # Verify all orders were successful
    assert result1['success'] == True
    assert result2['success'] == True  
    assert result3['success'] == True
    
    # Verify order sequencing and tracking
    assert len(placed_orders) == 3
    
    # Verify first order (market buy)
    order1 = placed_orders[0]
    assert order1['symbol'] == 'AAPL'
    assert order1['action'] == 'BUY'
    assert order1['quantity'] == 100
    assert order1['order_type'] == 'MKT'
    
    # Verify second order (limit sell partial)
    order2 = placed_orders[1]
    assert order2['symbol'] == 'AAPL'
    assert order2['action'] == 'SELL'
    assert order2['quantity'] == 50
    assert order2['order_type'] == 'LMT'
    
    # Verify third order (limit sell with GTC)
    order3 = placed_orders[2]
    assert order3['symbol'] == 'AAPL'
    assert order3['action'] == 'SELL'
    assert order3['quantity'] == 25
    assert order3['order_type'] == 'LMT'
    
    # Verify order IDs are unique and sequential
    order_ids = [order['order_id'] for order in placed_orders]
    assert len(set(order_ids)) == 3  # All unique
    assert order_ids == [10001, 10002, 10003]  # Sequential
    
    # Test order management scenarios
    # Scenario 4: Modify an existing order
    modify_result = await order_manager.modify_order(
        order_id=10002,
        quantity=75,  # Increase quantity
        price=187.0   # Adjust price
    )
    assert modify_result['success'] == True
    assert modify_result['order_id'] == 10002
    
    # Scenario 5: Cancel an order
    cancel_result = await order_manager.cancel_order(order_id=10003)
    assert cancel_result['success'] == True
    assert cancel_result['order_id'] == 10003
    
    # Scenario 6: Get order status
    status_result = await order_manager.get_order_status(order_id=10001)
    assert status_result['success'] == True
    assert status_result['order_id'] == 10001
    
    # Test error handling in complex scenarios
    # Scenario 7: Try to modify non-existent order
    error_result = await order_manager.modify_order(
        order_id=99999,  # Non-existent
        quantity=100
    )
    assert error_result['success'] == False
    assert 'error' in error_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
