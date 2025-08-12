"""
Unit tests for IBKR MCP Server MCP Tools - Complete Coverage.

Tests all 23 MCP tools and infrastructure:
- Core tool infrastructure (4 tests)
- Portfolio & account tools (5 tests)
- Market data tools (2 tests) 
- Forex & currency tools (2 tests)
- Risk management tools (4 tests)
- Order management tools (6 tests)
- Order history tools (3 tests)
- Documentation & error handling (4 tests)

Total: 30 unit tests for complete MCP tools coverage
"""
import pytest
import pytest_asyncio
import json
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import MCP tools and infrastructure
from ibkr_mcp_server.tools import (
    safe_trading_operation,
    list_tools,
    call_tool
)
from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings


@pytest.mark.unit
class TestMCPToolInfrastructure:
    """Test core MCP tool infrastructure (4 tests)"""
    
    @pytest.mark.asyncio
    async def test_safe_trading_operation_success(self):
        """Test safety wrapper for successful operation"""
        # Mock safety manager
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            # Mock successful operation
            async def mock_operation():
                return {"success": True, "data": "test"}
            
            result = await safe_trading_operation("test", {}, mock_operation)
            
            assert result["success"] is True
            assert "data" in result
    
    @pytest.mark.asyncio
    async def test_safe_trading_operation_failure(self):
        """Test safety wrapper for failed operation"""
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": False,
                "warnings": [],
                "errors": ["Test safety violation"]
            }
            
            async def mock_operation():
                return {"success": True, "data": "test"}
            
            result = await safe_trading_operation("test", {}, mock_operation)
            
            assert result["success"] is False
            assert "Safety validation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_tools_count(self):
        """Test tool list returns all 23 tools"""
        tools = await list_tools()
        
        assert isinstance(tools, list)
        # Should have 23 tools
        assert len(tools) == 23
        
        # Check for key tools - Tool objects have .name attribute
        tool_names = [tool.name for tool in tools]
        assert "get_portfolio" in tool_names
        assert "get_market_data" in tool_names
        assert "place_stop_loss" in tool_names
        assert "get_forex_rates" in tool_names
    
    @pytest.mark.asyncio
    async def test_call_tool_dispatcher(self):
        """Test call_tool routing to correct handlers"""
        # Mock client
        mock_client = Mock()
        mock_client.get_portfolio = AsyncMock(return_value=[])
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_portfolio", {})
            
            assert isinstance(result, list)  # MCP response format


@pytest.mark.unit
class TestMCPPortfolioAccountTools:
    """Test portfolio & account MCP tools (5 tests)"""
    
    @pytest.fixture
    def mock_client(self):
        """Mock IBKR client for testing"""
        client = Mock()
        client.get_portfolio = AsyncMock(return_value=[])
        client.get_account_summary = AsyncMock(return_value={})
        client.switch_account = AsyncMock(return_value={"success": True})
        client.get_accounts = AsyncMock(return_value={"accounts": []})
        client.get_connection_status = AsyncMock(return_value={"connected": True})
        return client
    
    @pytest.mark.asyncio
    async def test_get_portfolio_tool(self, mock_client):
        """Test get_portfolio MCP tool wrapper"""
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_portfolio", {})
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_portfolio.assert_called_once_with(None)
    
    @pytest.mark.asyncio
    async def test_get_account_summary_tool(self, mock_client):
        """Test get_account_summary MCP tool wrapper"""
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_account_summary", {})
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_account_summary.assert_called_once_with(None)
    
    @pytest.mark.asyncio
    async def test_switch_account_tool(self, mock_client):
        """Test switch_account MCP tool wrapper"""
        arguments = {"account_id": "DU123456"}
        
        # Mock safety manager to allow operation
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("switch_account", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_get_accounts_tool(self, mock_client):
        """Test get_accounts MCP tool wrapper"""
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_accounts", {})
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_accounts.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_connection_status_tool(self, mock_client):
        """Test get_connection_status MCP tool wrapper"""
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_connection_status", {})
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_connection_status.assert_called_once()


@pytest.mark.unit
class TestMCPMarketDataTools:
    """Test market data MCP tools (2 tests)"""
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.get_market_data = AsyncMock(return_value={"symbol": "AAPL"})
        client.resolve_international_symbol = AsyncMock(return_value={"symbol": "ASML"})
        return client
    
    @pytest.mark.asyncio
    async def test_get_market_data_tool(self, mock_client):
        """Test get_market_data MCP tool wrapper"""
        arguments = {"symbols": "AAPL", "auto_detect": True}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_market_data", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_market_data.assert_called_once_with("AAPL", True)
    
    @pytest.mark.asyncio
    async def test_resolve_international_symbol_tool(self, mock_client):
        """Test resolve_international_symbol MCP tool wrapper"""
        arguments = {"symbol": "ASML"}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("resolve_international_symbol", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.resolve_international_symbol.assert_called_once()


@pytest.mark.unit
class TestMCPForexCurrencyTools:
    """Test forex & currency MCP tools (2 tests)"""
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.get_forex_rates = AsyncMock(return_value=[{"pair": "EURUSD"}])
        client.convert_currency = AsyncMock(return_value={"converted": 1085.6})
        return client
    
    @pytest.mark.asyncio
    async def test_get_forex_rates_tool(self, mock_client):
        """Test get_forex_rates MCP tool wrapper"""
        arguments = {"currency_pairs": "EURUSD"}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_forex_rates", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_forex_rates.assert_called_once_with("EURUSD")
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_convert_currency_tool(self, mock_client):
        """Test convert_currency MCP tool wrapper"""
        arguments = {"amount": 1000.0, "from_currency": "EUR", "to_currency": "USD"}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("convert_currency", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.convert_currency.assert_called_once_with(1000.0, "EUR", "USD")


@pytest.mark.unit
class TestMCPRiskManagementTools:
    """Test risk management MCP tools (4 tests)"""
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.place_stop_loss = AsyncMock(return_value={"order_id": 123})
        client.get_stop_losses = AsyncMock(return_value=[])
        client.modify_stop_loss = AsyncMock(return_value={"success": True})
        client.cancel_stop_loss = AsyncMock(return_value={"success": True})
        return client
    
    @pytest.mark.asyncio
    async def test_place_stop_loss_tool(self, mock_client):
        """Test place_stop_loss MCP tool wrapper"""
        arguments = {
            "symbol": "AAPL",
            "action": "SELL", 
            "quantity": 100,
            "stop_price": 180.0
        }
        
        # Mock safety framework
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("place_stop_loss", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_get_stop_losses_tool(self, mock_client):
        """Test get_stop_losses MCP tool wrapper"""
        arguments = {}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_stop_losses", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_stop_losses.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_modify_stop_loss_tool(self, mock_client):
        """Test modify_stop_loss MCP tool wrapper"""
        arguments = {"order_id": 123, "stop_price": 185.0}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("modify_stop_loss", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_cancel_stop_loss_tool(self, mock_client):
        """Test cancel_stop_loss MCP tool wrapper"""
        arguments = {"order_id": 123}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("cancel_stop_loss", arguments)
            
            assert isinstance(result, list)  # MCP response


@pytest.mark.unit
class TestMCPOrderManagementTools:
    """Test order management MCP tools (6 tests)"""
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.place_market_order = AsyncMock(return_value={"order_id": 124})
        client.place_limit_order = AsyncMock(return_value={"order_id": 125})
        client.cancel_order = AsyncMock(return_value={"success": True})
        client.modify_order = AsyncMock(return_value={"success": True})
        client.get_order_status = AsyncMock(return_value={"status": "Filled"})
        client.place_bracket_order = AsyncMock(return_value={"parent_id": 126})
        return client
    
    @pytest.mark.asyncio
    async def test_place_market_order_tool(self, mock_client):
        """Test place_market_order MCP tool wrapper"""
        arguments = {"symbol": "AAPL", "action": "BUY", "quantity": 100}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("place_market_order", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_place_limit_order_tool(self, mock_client):
        """Test place_limit_order MCP tool wrapper"""
        arguments = {"symbol": "MSFT", "action": "BUY", "quantity": 50, "price": 400.0}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("place_limit_order", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_cancel_order_tool(self, mock_client):
        """Test cancel_order MCP tool wrapper"""
        arguments = {"order_id": 123}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("cancel_order", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_modify_order_tool(self, mock_client):
        """Test modify_order MCP tool wrapper"""
        arguments = {"order_id": 123, "quantity": 150}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("modify_order", arguments)
            
            assert isinstance(result, list)  # MCP response
    
    @pytest.mark.asyncio
    async def test_get_order_status_tool(self, mock_client):
        """Test get_order_status MCP tool wrapper"""
        arguments = {"order_id": 123}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_order_status", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_order_status.assert_called_once_with(123)
    
    @pytest.mark.asyncio
    async def test_place_bracket_order_tool(self, mock_client):
        """Test place_bracket_order MCP tool wrapper"""
        arguments = {
            "symbol": "GOOGL",
            "action": "BUY",
            "quantity": 10,
            "entry_price": 2750.0,
            "stop_price": 2650.0,
            "target_price": 2850.0
        }
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety, \
             patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": True,
                "warnings": [],
                "errors": []
            }
            
            result = await call_tool("place_bracket_order", arguments)
            
            assert isinstance(result, list)  # MCP response


@pytest.mark.unit
class TestMCPOrderHistoryTools:
    """Test order history MCP tools (3 tests)"""
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.get_open_orders = AsyncMock(return_value=[])
        client.get_completed_orders = AsyncMock(return_value=[])
        client.get_executions = AsyncMock(return_value=[])
        return client
    
    @pytest.mark.asyncio
    async def test_get_open_orders_tool(self, mock_client):
        """Test get_open_orders MCP tool wrapper"""
        arguments = {}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_open_orders", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_open_orders.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_completed_orders_tool(self, mock_client):
        """Test get_completed_orders MCP tool wrapper"""
        arguments = {}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_completed_orders", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_completed_orders.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_executions_tool(self, mock_client):
        """Test get_executions MCP tool wrapper"""
        arguments = {"symbol": "AAPL", "days_back": 30}
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_executions", arguments)
            
            assert isinstance(result, list)  # MCP response
            mock_client.get_executions.assert_called_once()


@pytest.mark.unit
class TestMCPDocumentationAndErrorHandling:
    """Test documentation & error handling (4 tests)"""
    
    @pytest.mark.asyncio
    async def test_get_tool_documentation_tool(self):
        """Test get_tool_documentation MCP tool wrapper"""
        arguments = {"tool_or_category": "forex"}
        
        result = await call_tool("get_tool_documentation", arguments)
        
        assert isinstance(result, list)  # MCP response
        # Should contain documentation content
        text_content = result[0]
        assert "forex" in text_content.text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self):
        """Test MCP tool parameter validation"""
        # Test missing required parameters - should return error in TextContent, not raise exception
        result = await call_tool("get_market_data", {})  # Missing symbols parameter
        
        assert isinstance(result, list)  # MCP response format
        assert len(result) > 0
        text_content = result[0]
        assert hasattr(text_content, 'text')
        # Should contain error message about missing symbols parameter
        assert "error" in text_content.text.lower()
        assert "symbols" in text_content.text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_error_responses(self):
        """Test MCP tool error response formatting"""
        # Mock client that raises exception
        mock_client = Mock()
        mock_client.get_portfolio = AsyncMock(side_effect=Exception("Test error"))
        
        with patch('ibkr_mcp_server.tools.ibkr_client', mock_client):
            result = await call_tool("get_portfolio", {})
            
            # Should return MCP error response
            assert isinstance(result, list)
            text_content = result[0]
            assert "error" in text_content.text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_safety_integration(self):
        """Test MCP tools integration with safety framework"""
        # Test with safety blocking
        arguments = {"symbol": "AAPL", "action": "BUY", "quantity": 100}
        
        with patch('ibkr_mcp_server.tools.safety_manager') as mock_safety:
            mock_safety.validate_trading_operation.return_value = {
                "is_safe": False,
                "warnings": [],
                "errors": ["Trading disabled for safety"]
            }
            
            result = await call_tool("place_market_order", arguments)
            
            # Should return safety error
            assert isinstance(result, list)
            text_content = result[0]
            assert "safety" in text_content.text.lower()
