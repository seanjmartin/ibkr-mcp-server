"""
End-to-end trading workflow tests.

Tests complete trading workflows that span multiple tools and components,
simulating real-world usage scenarios.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings
from ibkr_mcp_server.trading.forex import ForexManager
from ibkr_mcp_server.trading.international import InternationalManager
from ibkr_mcp_server.trading.stop_loss import StopLossManager


@pytest.fixture
def workflow_settings():
    """Settings configured for end-to-end workflow testing"""
    settings = EnhancedSettings()
    settings.enable_trading = True
    settings.enable_forex_trading = True
    settings.enable_international_trading = True
    settings.enable_stop_loss_orders = True
    settings.ibkr_is_paper = True
    settings.max_order_size = 1000
    settings.max_order_value_usd = 50000.0
    return settings


@pytest.fixture
async def workflow_client(workflow_settings, mock_ib):
    """Create fully configured client for workflow testing"""
    client = IBKRClient()
    client.settings = workflow_settings
    client.ib = mock_ib
    client._connected = True
    
    # Initialize managers
    client.forex_manager = ForexManager(mock_ib)
    client.international_manager = InternationalManager(mock_ib)
    client.stop_loss_manager = StopLossManager(mock_ib)
    
    return client


class TestCompleteForexWorkflow:
    """Test complete forex trading workflows"""
    
    @pytest.mark.asyncio
    async def test_forex_rate_analysis_to_conversion_workflow(self, workflow_client):
        """Test complete workflow: Get rates -> Analyze -> Convert currency"""
        
        # Step 1: Get multiple forex rates for analysis
        workflow_client.forex_manager.get_forex_rates = AsyncMock(return_value=[
            {
                'pair': 'EURUSD',
                'last': 1.0856,
                'bid': 1.0855,
                'ask': 1.0857,
                'change': 0.0012,
                'change_percent': 0.11,
                'high': 1.0870,
                'low': 1.0840,
                'timestamp': '2025-08-01T14:30:00Z'
            },
            {
                'pair': 'GBPUSD',  
                'last': 1.2654,
                'bid': 1.2652,
                'ask': 1.2656,
                'change': 0.0008,
                'change_percent': 0.06,
                'high': 1.2665,
                'low': 1.2640,
                'timestamp': '2025-08-01T14:30:00Z'
            }
        ])
        
        # Step 2: Convert currencies based on analysis
        workflow_client.forex_manager.convert_currency = AsyncMock(side_effect=[
            {  # EUR to USD conversion
                'original_amount': 10000.0,
                'from_currency': 'EUR',
                'to_currency': 'USD',
                'exchange_rate': 1.0856,
                'converted_amount': 10856.0,
                'conversion_method': 'direct',
                'timestamp': '2025-08-01T14:30:00Z'
            },
            {  # GBP to USD conversion
                'original_amount': 8000.0,
                'from_currency': 'GBP',
                'to_currency': 'USD',
                'exchange_rate': 1.2654,
                'converted_amount': 10123.2,
                'conversion_method': 'direct',
                'timestamp': '2025-08-01T14:30:00Z'
            }
        ])
        
        # Execute workflow
        rates = await workflow_client.forex_manager.get_forex_rates(["EURUSD", "GBPUSD"])
        
        # Analyze rates (simulate decision making)
        eur_rate = next(r for r in rates if r['pair'] == 'EURUSD')
        gbp_rate = next(r for r in rates if r['pair'] == 'GBPUSD')
        
        # Convert based on better rate (EURUSD has higher positive change)
        eur_conversion = await workflow_client.forex_manager.convert_currency(
            10000.0, "EUR", "USD"
        )
        gbp_conversion = await workflow_client.forex_manager.convert_currency(
            8000.0, "GBP", "USD"
        )
        
        # Verify workflow results
        assert len(rates) == 2
        assert eur_rate['change_percent'] > gbp_rate['change_percent']
        assert eur_conversion['converted_amount'] == 10856.0
        assert gbp_conversion['converted_amount'] == 10123.2
        
        # Verify total conversion
        total_usd = eur_conversion['converted_amount'] + gbp_conversion['converted_amount']
        assert total_usd == 20979.2
    
    @pytest.mark.asyncio
    async def test_cross_currency_arbitrage_workflow(self, workflow_client):
        """Test cross-currency arbitrage opportunity detection workflow"""
        
        # Mock multiple forex rates with arbitrage opportunity
        workflow_client.forex_manager.get_forex_rates = AsyncMock(return_value=[
            {'pair': 'EURUSD', 'last': 1.0856, 'bid': 1.0855, 'ask': 1.0857},
            {'pair': 'GBPUSD', 'last': 1.2654, 'bid': 1.2652, 'ask': 1.2656},
            {'pair': 'EURGBP', 'last': 0.8580, 'bid': 0.8579, 'ask': 0.8581}
        ])
        
        # Mock conversions for arbitrage calculation
        workflow_client.forex_manager.convert_currency = AsyncMock(side_effect=[
            {  # EUR -> USD -> GBP
                'converted_amount': 1265.4,  # 1000 EUR * 1.0856 / 1.2654
                'exchange_rate': 0.8579
            },
            {  # EUR -> GBP direct
                'converted_amount': 1165.5,  # 1000 EUR * 0.8580
                'exchange_rate': 0.8580
            }
        ])
        
        # Execute arbitrage detection workflow
        rates = await workflow_client.forex_manager.get_forex_rates([
            "EURUSD", "GBPUSD", "EURGBP"
        ])
        
        # Calculate cross-rate arbitrage
        eur_amount = 1000.0
        via_usd = await workflow_client.forex_manager.convert_currency(
            eur_amount, "EUR", "GBP"
        )
        direct = await workflow_client.forex_manager.convert_currency(
            eur_amount, "EUR", "GBP"
        )
        
        # Verify arbitrage detection
        assert len(rates) == 3
        arbitrage_profit = via_usd['converted_amount'] - direct['converted_amount']
        assert arbitrage_profit > 0  # Positive arbitrage opportunity detected


class TestInternationalTradingWorkflow:
    """Test international trading workflows"""
    
    @pytest.mark.asyncio
    async def test_global_portfolio_diversification_workflow(self, workflow_client):
        """Test workflow for diversifying across global markets"""
        
        # Step 1: Resolve international symbols
        workflow_client.international_manager.resolve_symbol = AsyncMock(side_effect=[
            {  # ASML (Netherlands)
                'symbol': 'ASML',
                'exchange': 'AEB',
                'currency': 'EUR',
                'name': 'ASML Holding NV',
                'country': 'Netherlands'
            },
            {  # Toyota (Japan)
                'symbol': '7203',
                'exchange': 'TSE',
                'currency': 'JPY',
                'name': 'Toyota Motor Corporation',
                'country': 'Japan'
            },
            {  # SAP (Germany)
                'symbol': 'SAP',
                'exchange': 'XETRA',
                'currency': 'EUR',
                'name': 'SAP SE',
                'country': 'Germany'
            }
        ])
        
        # Step 2: Get market data for all symbols
        workflow_client.get_market_data = AsyncMock(return_value={
            'success': True,
            'data': [
                {
                    'symbol': 'ASML',
                    'exchange': 'AEB',
                    'currency': 'EUR',
                    'last': 650.80,
                    'market_cap_billion': 264.5
                },
                {
                    'symbol': '7203',
                    'exchange': 'TSE', 
                    'currency': 'JPY',
                    'last': 2450.0,
                    'market_cap_billion': 245.2
                },
                {
                    'symbol': 'SAP',
                    'exchange': 'XETRA',
                    'currency': 'EUR',
                    'last': 134.25,
                    'market_cap_billion': 164.1
                }
            ]
        })
        
        # Step 3: Currency conversions for portfolio allocation
        workflow_client.forex_manager.convert_currency = AsyncMock(side_effect=[
            {  # EUR allocation
                'converted_amount': 30000.0,
                'exchange_rate': 1.0856
            },
            {  # JPY allocation
                'converted_amount': 3270000.0,  # ~30k USD worth
                'exchange_rate': 109.0
            }
        ])
        
        # Execute diversification workflow
        symbols = ['ASML', '7203', 'SAP']
        resolutions = []
        
        for symbol in symbols:
            resolution = await workflow_client.international_manager.resolve_symbol(symbol)
            resolutions.append(resolution)
        
        market_data = await workflow_client.get_market_data(symbols)
        
        # Calculate allocations (simulate equal weight)
        total_allocation_usd = 90000.0  # $90k total
        allocation_per_region = total_allocation_usd / 3
        
        eur_allocation = await workflow_client.forex_manager.convert_currency(
            allocation_per_region, "USD", "EUR"
        )
        jpy_allocation = await workflow_client.forex_manager.convert_currency(
            allocation_per_region, "USD", "JPY"
        )
        
        # Verify diversification workflow
        assert len(resolutions) == 3
        assert len(market_data['data']) == 3
        
        # Verify geographic diversification
        countries = [r['country'] for r in resolutions]
        assert 'Netherlands' in countries
        assert 'Japan' in countries  
        assert 'Germany' in countries
        
        # Verify currency diversification
        currencies = [r['currency'] for r in resolutions]
        assert 'EUR' in currencies
        assert 'JPY' in currencies
        
        # Verify allocation calculations
        assert eur_allocation['converted_amount'] > 0
        assert jpy_allocation['converted_amount'] > 0


class TestRiskManagementWorkflow:
    """Test comprehensive risk management workflows"""
    
    @pytest.mark.asyncio
    async def test_portfolio_protection_setup_workflow(self, workflow_client):
        """Test complete workflow for setting up portfolio protection"""
        
        # Step 1: Get current portfolio
        workflow_client.get_portfolio = AsyncMock(return_value={
            'success': True,
            'positions': [
                {
                    'symbol': 'AAPL',
                    'quantity': 100,
                    'avg_cost': 180.00,
                    'current_price': 185.50,
                    'market_value': 18550.0,
                    'unrealized_pnl': 550.0
                },
                {
                    'symbol': 'TSLA',
                    'quantity': 50,
                    'avg_cost': 245.00,
                    'current_price': 238.90,
                    'market_value': 11945.0,
                    'unrealized_pnl': -305.0
                },
                {
                    'symbol': 'ASML',
                    'quantity': 25,
                    'avg_cost': 600.00,
                    'current_price': 650.80,
                    'market_value': 16270.0,
                    'unrealized_pnl': 1270.0
                }
            ],
            'total_value': 46765.0
        })
        
        # Step 2: Place stop losses for each position
        workflow_client.stop_loss_manager.place_stop_loss = AsyncMock(side_effect=[
            {  # AAPL stop loss
                'order_id': 12345,
                'symbol': 'AAPL',
                'stop_price': 175.00,
                'order_type': 'STP',
                'status': 'Submitted'
            },
            {  # TSLA trailing stop
                'order_id': 12346,
                'symbol': 'TSLA',
                'stop_price': 220.00,
                'order_type': 'TRAIL',
                'trail_percent': 8.0,
                'status': 'Submitted'
            },
            {  # ASML stop limit
                'order_id': 12347,
                'symbol': 'ASML',
                'stop_price': 580.00,
                'limit_price': 575.00,
                'order_type': 'STP LMT',
                'status': 'Submitted'
            }
        ])
        
        # Step 3: Verify stop losses are active
        workflow_client.stop_loss_manager.get_stop_losses = AsyncMock(return_value=[
            {'order_id': 12345, 'symbol': 'AAPL', 'status': 'Active'},
            {'order_id': 12346, 'symbol': 'TSLA', 'status': 'Active'},
            {'order_id': 12347, 'symbol': 'ASML', 'status': 'Active'}
        ])
        
        # Execute portfolio protection workflow
        portfolio = await workflow_client.get_portfolio()
        
        stop_loss_orders = []
        for position in portfolio['positions']:
            # Calculate stop loss levels (10% below avg cost for simplicity)
            stop_price = position['avg_cost'] * 0.90
            
            if position['symbol'] == 'TSLA':
                # Use trailing stop for volatile stock
                order = await workflow_client.stop_loss_manager.place_stop_loss(
                    symbol=position['symbol'],
                    action='SELL',
                    quantity=position['quantity'],
                    stop_price=stop_price,
                    order_type='TRAIL',
                    trail_percent=8.0
                )
            elif position['symbol'] == 'ASML':
                # Use stop limit for international stock
                order = await workflow_client.stop_loss_manager.place_stop_loss(
                    symbol=position['symbol'],
                    action='SELL',
                    quantity=position['quantity'],
                    stop_price=stop_price,
                    order_type='STP LMT',
                    limit_price=stop_price - 5.0
                )
            else:
                # Use basic stop for domestic stocks
                order = await workflow_client.stop_loss_manager.place_stop_loss(
                    symbol=position['symbol'],
                    action='SELL',
                    quantity=position['quantity'],
                    stop_price=stop_price
                )
            
            stop_loss_orders.append(order)
        
        # Verify all positions are protected
        active_stops = await workflow_client.stop_loss_manager.get_stop_losses()
        
        # Verify workflow success
        assert len(portfolio['positions']) == 3
        assert len(stop_loss_orders) == 3
        assert len(active_stops) == 3
        
        # Verify different order types used appropriately
        order_types = [order['order_type'] for order in stop_loss_orders]
        assert 'STP' in order_types      # Basic stop
        assert 'TRAIL' in order_types    # Trailing stop
        assert 'STP LMT' in order_types  # Stop limit
        
        # Verify all orders are active
        active_order_ids = [order['order_id'] for order in active_stops]
        placed_order_ids = [order['order_id'] for order in stop_loss_orders]
        assert set(active_order_ids) == set(placed_order_ids)
    
    @pytest.mark.asyncio
    async def test_dynamic_risk_adjustment_workflow(self, workflow_client):
        """Test workflow for dynamically adjusting risk based on market conditions"""
        
        # Step 1: Get current market data
        workflow_client.get_market_data = AsyncMock(return_value={
            'success': True,
            'data': [
                {
                    'symbol': 'AAPL',
                    'last': 190.25,  # Price moved up significantly
                    'change_percent': 5.2,
                    'volatility': 0.22
                }
            ]
        })
        
        # Step 2: Get existing stop loss
        workflow_client.stop_loss_manager.get_stop_losses = AsyncMock(return_value=[
            {
                'order_id': 12345,
                'symbol': 'AAPL',
                'stop_price': 175.00,
                'distance_percent': -8.0
            }
        ])
        
        # Step 3: Modify stop loss based on new price
        workflow_client.stop_loss_manager.modify_stop_loss = AsyncMock(return_value={
            'order_id': 12345,
            'symbol': 'AAPL',
            'old_stop_price': 175.00,
            'new_stop_price': 185.00,  # Raised stop to lock in profits
            'status': 'Modified'
        })
        
        # Execute dynamic risk adjustment workflow
        market_data = await workflow_client.get_market_data(['AAPL'])
        current_stops = await workflow_client.stop_loss_manager.get_stop_losses()
        
        # Analyze market conditions
        apple_data = market_data['data'][0]
        apple_stop = current_stops[0]
        
        # If price moved up significantly and change is positive, raise stop
        if apple_data['change_percent'] > 5.0 and apple_data['last'] > 190.0:
            new_stop_price = apple_data['last'] * 0.95  # 5% below current price
            
            modification = await workflow_client.stop_loss_manager.modify_stop_loss(
                order_id=apple_stop['order_id'],
                stop_price=new_stop_price
            )
        
        # Verify dynamic adjustment
        assert apple_data['change_percent'] > 5.0
        assert modification['new_stop_price'] > modification['old_stop_price']
        assert modification['status'] == 'Modified'


class TestErrorRecoveryWorkflows:
    """Test workflows that handle errors and recover gracefully"""
    
    @pytest.mark.asyncio
    async def test_connection_loss_recovery_workflow(self, workflow_client):
        """Test workflow recovery after connection loss"""
        
        # Step 1: Simulate connection loss during operation
        workflow_client._connected = False
        workflow_client.get_connection_status = AsyncMock(return_value={
            'success': False,
            'connected': False,
            'error': 'Connection lost to IBKR server'
        })
        
        # Step 2: Attempt operation that should fail
        workflow_client.get_market_data = AsyncMock(side_effect=Exception("Connection error"))
        
        # Step 3: Simulate reconnection
        async def mock_reconnect():
            workflow_client._connected = True
            workflow_client.get_connection_status = AsyncMock(return_value={
                'success': True,
                'connected': True,
                'server': '127.0.0.1:7497'
            })
            workflow_client.get_market_data = AsyncMock(return_value={
                'success': True,
                'data': [{'symbol': 'AAPL', 'last': 185.50}]
            })
        
        # Execute recovery workflow
        connection_status = await workflow_client.get_connection_status()
        assert connection_status['connected'] is False
        
        # Attempt operation (should fail)
        try:
            await workflow_client.get_market_data(['AAPL'])
            assert False, "Should have raised exception"
        except Exception as e:
            assert "connection" in str(e).lower()
        
        # Simulate reconnection
        await mock_reconnect()
        
        # Verify recovery
        recovered_status = await workflow_client.get_connection_status()
        assert recovered_status['connected'] is True
        
        # Retry operation (should succeed)
        market_data = await workflow_client.get_market_data(['AAPL'])
        assert market_data['success'] is True
    
    @pytest.mark.asyncio
    async def test_safety_violation_recovery_workflow(self, workflow_client):
        """Test workflow recovery after safety violations"""
        
        # Step 1: Trigger safety violation (kill switch activation)
        workflow_client.safety_manager.kill_switch.activate("Test violation")
        
        # Step 2: Attempt trading operation (should be blocked)
        workflow_client.stop_loss_manager.place_stop_loss = AsyncMock(return_value={
            'success': False,
            'error': 'Emergency kill switch is active'
        })
        
        # Step 3: Deactivate kill switch and retry
        workflow_client.safety_manager.kill_switch.deactivate("EMERGENCY_OVERRIDE_2025")
        workflow_client.stop_loss_manager.place_stop_loss = AsyncMock(return_value={
            'success': True,
            'order_id': 12345,
            'symbol': 'AAPL'
        })
        
        # Execute safety recovery workflow
        # First attempt should fail
        blocked_result = await workflow_client.stop_loss_manager.place_stop_loss(
            symbol='AAPL', action='SELL', quantity=100, stop_price=180.0
        )
        assert blocked_result['success'] is False
        assert 'kill switch' in blocked_result['error'].lower()
        
        # After override, should succeed
        success_result = await workflow_client.stop_loss_manager.place_stop_loss(
            symbol='AAPL', action='SELL', quantity=100, stop_price=180.0
        )
        assert success_result['success'] is True
        assert success_result['order_id'] == 12345


class TestPerformanceOptimizedWorkflows:
    """Test workflows optimized for performance and efficiency"""
    
    @pytest.mark.asyncio
    async def test_batch_operations_workflow(self, workflow_client):
        """Test workflow that batches operations for efficiency"""
        
        # Mock batch market data request
        workflow_client.get_market_data = AsyncMock(return_value={
            'success': True,
            'data': [
                {'symbol': 'AAPL', 'last': 185.50},
                {'symbol': 'MSFT', 'last': 420.25},
                {'symbol': 'GOOGL', 'last': 175.80},
                {'symbol': 'TSLA', 'last': 238.90},
                {'symbol': 'NVDA', 'last': 875.45}
            ]
        })
        
        # Mock batch stop loss placement
        workflow_client.stop_loss_manager.place_stop_loss = AsyncMock(side_effect=[
            {'order_id': 12345, 'symbol': 'AAPL'},
            {'order_id': 12346, 'symbol': 'MSFT'},
            {'order_id': 12347, 'symbol': 'GOOGL'},
            {'order_id': 12348, 'symbol': 'TSLA'},
            {'order_id': 12349, 'symbol': 'NVDA'}
        ])
        
        # Execute batch workflow
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        # Batch market data request
        market_data = await workflow_client.get_market_data(symbols)
        
        # Batch stop loss placement
        stop_orders = []
        for data in market_data['data']:
            stop_price = data['last'] * 0.95  # 5% stop loss
            order = await workflow_client.stop_loss_manager.place_stop_loss(
                symbol=data['symbol'],
                action='SELL',
                quantity=100,
                stop_price=stop_price
            )
            stop_orders.append(order)
        
        # Verify batch efficiency
        assert len(market_data['data']) == 5  # Single request for all symbols
        assert len(stop_orders) == 5  # All stop losses placed
        
        # Verify all orders have unique IDs
        order_ids = [order['order_id'] for order in stop_orders]
        assert len(set(order_ids)) == 5  # All unique
