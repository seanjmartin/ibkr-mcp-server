"""
Integration tests for MCP tools functionality.

Tests the complete integration of MCP tools with the underlying trading managers
and safety framework, ensuring that tools work correctly end-to-end.
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings
from ibkr_mcp_server.tools import call_tool
from mcp.types import TextContent


@pytest.fixture
def mock_enabled_settings():
    """Mock settings with all trading features enabled for integration testing"""
    settings = EnhancedSettings()
    settings.enable_trading = True
    settings.enable_forex_trading = True
    settings.enable_international_trading = True
    settings.enable_stop_loss_orders = True
    settings.ibkr_is_paper = True
    return settings


@pytest.fixture
def enabled_ibkr_client(mock_enabled_settings, mock_ib):
    """Create IBKR client with all features enabled for integration testing"""
    client = IBKRClient()
    client.settings = mock_enabled_settings
    client.ib = mock_ib
    client._connected = True
    
    # Mock the _initialize_trading_managers method to avoid async issues
    client._initialize_trading_managers = AsyncMock()
    
    return client


class TestForexToolsIntegration:
    """Test forex-related MCP tools integration"""
    
    @pytest.mark.asyncio
    async def test_get_forex_rates_tool_integration(self, enabled_ibkr_client):
        """Test get_forex_rates MCP tool with full integration"""
        # Mock the client method
        enabled_ibkr_client.get_forex_rates = AsyncMock(return_value={
            'success': True,
            'rates': [
                {
                    'pair': 'EURUSD',
                    'last': 1.0856,
                    'bid': 1.0855,
                    'ask': 1.0857,
                    'change': 0.0012,
                    'change_percent': 0.11,
                    'timestamp': '2025-08-01T14:30:00Z'
                }
            ]
        })
        
        # Mock client reference in tools module
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
                mock_safety.rate_limiter.check_rate_limit.return_value = True
                
                result = await call_tool("get_forex_rates", {"currency_pairs": "EURUSD"})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert 'rates' in response_data
        assert len(response_data['rates']) == 1
        assert response_data['rates'][0]['pair'] == 'EURUSD'
    
    @pytest.mark.asyncio
    async def test_convert_currency_tool_integration(self, enabled_ibkr_client):
        """Test convert_currency MCP tool with full integration"""
        # Mock the client method
        enabled_ibkr_client.convert_currency = AsyncMock(return_value={
            'success': True,
            'conversion': {
                'original_amount': 1000.0,
                'from_currency': 'EUR',
                'to_currency': 'USD',
                'exchange_rate': 1.0856,
                'converted_amount': 1085.6,
                'timestamp': '2025-08-01T14:30:00Z'
            }
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            result = await call_tool("convert_currency", {
                "amount": 1000.0,
                "from_currency": "EUR",
                "to_currency": "USD"
            })
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert response_data['conversion']['original_amount'] == 1000.0
        assert response_data['conversion']['converted_amount'] == 1085.6
    
    @pytest.mark.asyncio
    async def test_forex_tools_error_handling(self, enabled_ibkr_client):
        """Test forex tools handle errors gracefully"""
        # Mock an error in the client
        enabled_ibkr_client.get_forex_rates = AsyncMock(
            side_effect=Exception("Connection error")
        )
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
                mock_safety.rate_limiter.check_rate_limit.return_value = True
                
                result = await call_tool("get_forex_rates", {"currency_pairs": "INVALID"})
        
        assert len(result) == 1
        assert "Error getting forex rates" in result[0].text
        assert "connection error" in result[0].text.lower()


class TestMarketDataToolsIntegration:
    """Test market data MCP tools integration"""
    
    @pytest.mark.asyncio
    async def test_get_market_data_tool_integration(self, enabled_ibkr_client):
        """Test get_market_data MCP tool with full integration"""
        # Mock the client method
        enabled_ibkr_client.get_market_data = AsyncMock(return_value={
            'success': True,
            'data': [
                {
                    'symbol': 'AAPL',
                    'exchange': 'SMART',
                    'currency': 'USD',
                    'last': 185.50,
                    'bid': 185.48,
                    'ask': 185.52,
                    'change': 2.15,
                    'change_percent': 1.17,
                    'volume': 45678900,
                    'timestamp': '2025-08-01T14:30:00Z'
                }
            ]
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
                mock_safety.rate_limiter.check_rate_limit.return_value = True
                
                result = await call_tool("get_market_data", {"symbols": "AAPL"})
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert 'data' in response_data
        assert len(response_data['data']) == 1
        assert response_data['data'][0]['symbol'] == 'AAPL'
    
    @pytest.mark.asyncio
    async def test_resolve_international_symbol_integration(self, enabled_ibkr_client):
        """Test resolve_international_symbol MCP tool integration"""
        # Mock the client method
        enabled_ibkr_client.resolve_international_symbol = AsyncMock(return_value={
            'success': True,
            'resolution': {
                'symbol': 'ASML',
                'exchange': 'AEB',
                'currency': 'EUR',
                'name': 'ASML Holding NV',
                'country': 'Netherlands',
                'alternatives': [
                    {'exchange': 'NASDAQ', 'currency': 'USD', 'symbol': 'ASML'}
                ]
            }
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            result = await call_tool("resolve_international_symbol", {"symbol": "ASML"})
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert response_data['resolution']['symbol'] == 'ASML'
        assert response_data['resolution']['exchange'] == 'AEB'


class TestStopLossToolsIntegration:
    """Test stop loss MCP tools integration"""
    
    @pytest.mark.asyncio
    async def test_place_stop_loss_tool_integration(self, enabled_ibkr_client):
        """Test place_stop_loss MCP tool with full integration"""
        # Mock the client method
        enabled_ibkr_client.place_stop_loss = AsyncMock(return_value={
            'success': True,
            'order': {
                'order_id': 12345,
                'symbol': 'AAPL',
                'action': 'SELL',
                'quantity': 100,
                'stop_price': 180.00,
                'order_type': 'STP',
                'status': 'Submitted',
                'timestamp': '2025-08-01T14:30:00Z'
            }
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safe_trading_operation') as mock_safe_op:
                mock_safe_op.return_value = {
                    'success': True,
                    'order': {
                        'order_id': 12345,
                        'symbol': 'AAPL',
                        'stop_price': 180.00
                    }
                }
                
                result = await call_tool("place_stop_loss", {
                    "symbol": "AAPL",
                    "action": "SELL",
                    "quantity": 100,
                    "stop_price": 180.00
                })
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert response_data['order']['order_id'] == 12345
    
    @pytest.mark.asyncio
    async def test_get_stop_losses_tool_integration(self, enabled_ibkr_client):
        """Test get_stop_losses MCP tool integration"""
        # Mock the client method
        enabled_ibkr_client.get_stop_losses = AsyncMock(return_value={
            'success': True,
            'orders': [
                {
                    'order_id': 12345,
                    'symbol': 'AAPL',
                    'quantity': 100,
                    'stop_price': 180.00,
                    'status': 'Active',
                    'distance_percent': -2.5
                }
            ]
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            result = await call_tool("get_stop_losses", {})
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert 'orders' in response_data
        assert len(response_data['orders']) == 1
        assert response_data['orders'][0]['order_id'] == 12345


class TestPortfolioToolsIntegration:
    """Test portfolio management MCP tools integration"""
    
    @pytest.mark.asyncio
    async def test_get_portfolio_tool_integration(self, enabled_ibkr_client):
        """Test get_portfolio MCP tool integration"""
        # Mock the client method
        enabled_ibkr_client.get_portfolio = AsyncMock(return_value={
            'success': True,
            'positions': [
                {
                    'symbol': 'AAPL',
                    'quantity': 100,
                    'market_value': 18550.0,
                    'avg_cost': 180.00,
                    'unrealized_pnl': 550.0,
                    'unrealized_pnl_percent': 3.06
                }
            ],
            'total_value': 98450.75,
            'available_cash': 51230.45
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            result = await call_tool("get_portfolio", {})
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert 'positions' in response_data
        assert len(response_data['positions']) == 1
        assert response_data['positions'][0]['symbol'] == 'AAPL'
    
    @pytest.mark.asyncio
    async def test_get_connection_status_tool_integration(self, enabled_ibkr_client):
        """Test get_connection_status MCP tool integration"""
        # Mock the client method
        enabled_ibkr_client.get_connection_status = AsyncMock(return_value={
            'success': True,
            'connected': True,
            'server': '127.0.0.1:7497',
            'account': 'DU123456',
            'account_type': 'Paper Trading'
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            result = await call_tool("get_connection_status", {})
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is True
        assert response_data['connected'] is True
        assert response_data['account'] == 'DU123456'


class TestMCPToolsErrorHandling:
    """Test error handling across all MCP tools"""
    
    @pytest.mark.asyncio
    async def test_tools_handle_rate_limiting(self, enabled_ibkr_client):
        """Test that tools handle rate limiting properly"""
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
                # Mock rate limit exceeded
                mock_safety.rate_limiter.check_rate_limit.return_value = False
                
                result = await call_tool("get_market_data", {"symbols": "AAPL"})
        
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data['success'] is False
        assert 'rate limit' in response_data['error'].lower()
    
    @pytest.mark.asyncio
    async def test_tools_handle_invalid_parameters(self, enabled_ibkr_client):
        """Test that tools validate parameters and handle invalid inputs"""
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            # Test invalid tool name
            result = await call_tool("invalid_tool", {})
            assert len(result) == 1
            assert "Unknown tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_safety_framework_integration(self, enabled_ibkr_client):
        """Test that tools integrate properly with safety framework"""
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safe_trading_operation') as mock_safe_op:
                # Mock safety violation
                mock_safe_op.side_effect = Exception("Safety validation failed")
                
                result = await call_tool("place_stop_loss", {
                    "symbol": "AAPL",
                    "action": "SELL",
                    "quantity": 100,
                    "stop_price": 180.00
                })
        
        assert len(result) == 1
        assert "Error placing stop loss" in result[0].text
        assert "Safety validation failed" in result[0].text


class TestMCPToolsIntegrationWorkflows:
    """Test complete workflows using multiple MCP tools"""
    
    @pytest.mark.asyncio
    async def test_forex_trading_workflow(self, enabled_ibkr_client):
        """Test complete forex trading workflow using multiple tools"""
        # Mock client methods
        enabled_ibkr_client.get_forex_rates = AsyncMock(return_value={
            'success': True,
            'rates': [{'pair': 'EURUSD', 'last': 1.0856, 'bid': 1.0855, 'ask': 1.0857}]
        })
        
        enabled_ibkr_client.convert_currency = AsyncMock(return_value={
            'success': True,
            'conversion': {
                'original_amount': 1000.0,
                'converted_amount': 1085.6,
                'exchange_rate': 1.0856
            }
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
                mock_safety.rate_limiter.check_rate_limit.return_value = True
                
                # Execute workflow
                rates_result = await call_tool("get_forex_rates", {"currency_pairs": "EURUSD"})
                conversion_result = await call_tool("convert_currency", {
                    "amount": 1000.0,
                    "from_currency": "EUR",
                    "to_currency": "USD"
                })
        
        # Verify workflow success
        rates_data = json.loads(rates_result[0].text)
        conversion_data = json.loads(conversion_result[0].text)
        
        assert rates_data['success'] is True
        assert conversion_data['success'] is True
        assert conversion_data['conversion']['exchange_rate'] == 1.0856
    
    @pytest.mark.asyncio
    async def test_portfolio_protection_workflow(self, enabled_ibkr_client):
        """Test portfolio protection workflow"""
        # Mock portfolio data
        enabled_ibkr_client.get_portfolio = AsyncMock(return_value={
            'success': True,
            'positions': [
                {'symbol': 'AAPL', 'quantity': 100, 'avg_cost': 180.00}
            ]
        })
        
        with patch('ibkr_mcp_server.tools.ibkr_client', enabled_ibkr_client):
            with patch('ibkr_mcp_server.tools.safe_trading_operation') as mock_safe_op:
                mock_safe_op.return_value = {
                    'success': True,
                    'order': {'order_id': 12345, 'symbol': 'AAPL'}
                }
                
                # Execute workflow
                portfolio_result = await call_tool("get_portfolio", {})
                stop_loss_result = await call_tool("place_stop_loss", {
                    "symbol": "AAPL",
                    "action": "SELL",
                    "quantity": 100,
                    "stop_price": 170.00
                })
        
        # Verify workflow success
        portfolio_data = json.loads(portfolio_result[0].text)
        stop_loss_data = json.loads(stop_loss_result[0].text)
        
        assert portfolio_data['success'] is True
        assert stop_loss_data['success'] is True
        assert stop_loss_data['order']['symbol'] == 'AAPL'
