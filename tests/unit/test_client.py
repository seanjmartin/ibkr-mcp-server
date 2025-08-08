"""
Unit tests for IBKR MCP Server Client order history functionality.

Simple tests to validate the MCP tool handlers work correctly with the client methods.
"""
import pytest
import pytest_asyncio
import json
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings


@pytest.mark.unit
class TestOrderHistoryMethods:
    """Test completed orders and executions functionality"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock enhanced settings for testing"""
        settings = EnhancedSettings()
        settings.enable_trading = True
        settings.ibkr_is_paper = True
        return settings
        
    @pytest.fixture
    def mock_ib(self):
        """Mock IB client with common methods"""
        ib = Mock()
        ib.isConnected = Mock(return_value=True)
        ib.reqCompletedOrdersAsync = AsyncMock()
        ib.reqExecutionsAsync = AsyncMock()
        return ib
        
    @pytest_asyncio.fixture
    async def ibkr_client(self, mock_settings, mock_ib):
        """Create IBKR client with mocked dependencies"""
        client = IBKRClient()
        client.settings = mock_settings
        client.ib = mock_ib
        client._connected = True
        client.current_account = "DU123456"
        # Mock _ensure_connected to return True
        client._ensure_connected = AsyncMock(return_value=True)
        return client
    
    @pytest.mark.asyncio
    async def test_get_completed_orders_empty_response(self, ibkr_client):
        """Test get_completed_orders with no completed orders"""
        # Mock empty response (common in paper trading)
        ibkr_client.ib.reqCompletedOrdersAsync.return_value = []
        
        result = await ibkr_client.get_completed_orders()
        
        # Client returns List[Dict] directly
        assert isinstance(result, list)
        assert len(result) == 0
        
    @pytest.mark.asyncio
    async def test_get_completed_orders_timeout_handling(self, ibkr_client):
        """Test timeout handling for IBKR API hanging issue"""
        # Mock timeout scenario with asyncio.wait_for wrapper
        async def mock_timeout(*args, **kwargs):
            raise asyncio.TimeoutError("Request timed out")
        
        with patch('asyncio.wait_for', side_effect=mock_timeout):
            result = await ibkr_client.get_completed_orders()
            
            # Should return empty list on timeout (as per implementation)
            assert isinstance(result, list)
            assert len(result) == 0
        
    @pytest.mark.asyncio
    async def test_get_executions_empty_response(self, ibkr_client):
        """Test get_executions with no executions"""
        # Mock empty execution response
        ibkr_client.ib.reqExecutionsAsync.return_value = []
        
        result = await ibkr_client.get_executions()
        
        # Client returns List[Dict] directly
        assert isinstance(result, list)
        assert len(result) == 0
        
    @pytest.mark.asyncio
    async def test_get_executions_basic_functionality(self, ibkr_client):
        """Test get_executions basic call structure"""
        # Mock the basic call succeeds without complex data validation
        ibkr_client.ib.reqExecutionsAsync.return_value = []
        
        # Test that the method can be called with different parameters
        result1 = await ibkr_client.get_executions()
        result2 = await ibkr_client.get_executions(account="DU123456")
        result3 = await ibkr_client.get_executions(symbol="AAPL")
        
        # All should return empty lists
        assert isinstance(result1, list)
        assert isinstance(result2, list) 
        assert isinstance(result3, list)
        assert len(result1) == 0
        assert len(result2) == 0
        assert len(result3) == 0
        
    @pytest.mark.asyncio
    async def test_methods_are_callable(self, ibkr_client):
        """Test that both methods exist and are callable"""
        # Test method existence
        assert hasattr(ibkr_client, 'get_completed_orders')
        assert hasattr(ibkr_client, 'get_executions')
        assert callable(ibkr_client.get_completed_orders)
        assert callable(ibkr_client.get_executions)
        
        # Test they can be called (with empty mock responses)
        ibkr_client.ib.reqCompletedOrdersAsync.return_value = []
        ibkr_client.ib.reqExecutionsAsync.return_value = []
        
        orders_result = await ibkr_client.get_completed_orders()
        executions_result = await ibkr_client.get_executions()
        
        assert isinstance(orders_result, list)
        assert isinstance(executions_result, list)
        
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, ibkr_client):
        """Test error handling when not connected"""
        # Mock connection failure
        ibkr_client._ensure_connected = AsyncMock(return_value=False)
        
        with pytest.raises(Exception):  # Should raise some connection error
            await ibkr_client.get_completed_orders()
            
        with pytest.raises(Exception):  # Should raise some connection error
            await ibkr_client.get_executions()
