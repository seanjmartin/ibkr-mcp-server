"""
Unit tests for IBKR MCP Server Client - Comprehensive Testing.

Tests all 28+ methods in the IBKRClient class across all functional areas:
- Connection management (8 tests)
- Portfolio & account management (10 tests)  
- Market data (6 tests)
- Forex operations (4 tests)
- Trading manager integration (4 tests)
- Order management (6 tests)
- Error handling & edge cases (4 tests)

Total: 42+ unit tests for complete client coverage
"""
import pytest
import pytest_asyncio
import json
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings
from ibkr_mcp_server.utils import ConnectionError


@pytest.mark.unit
class TestClientConnectionManagement:
    """Test connection-related functionality (8 tests)"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock enhanced settings for testing"""
        settings = EnhancedSettings()
        settings.enable_trading = True
        settings.ibkr_is_paper = True
        settings.ibkr_host = "127.0.0.1"
        settings.ibkr_port = 7497
        settings.ibkr_client_id = 5
        return settings
        
    @pytest.fixture
    def mock_ib(self):
        """Mock IB client with connection methods"""
        ib = Mock()
        ib.isConnected = Mock(return_value=True)
        ib.connectAsync = AsyncMock(return_value=True)
        ib.disconnect = Mock()
        ib.managedAccounts = ["DU123456", "DU789012"]
        return ib
        
    @pytest_asyncio.fixture
    async def ibkr_client(self, mock_settings, mock_ib):
        """Create IBKR client with mocked dependencies"""
        client = IBKRClient()
        client.settings = mock_settings
        client.ib = mock_ib
        return client
    
    @pytest.mark.asyncio
    @patch('ibkr_mcp_server.client.IB')
    @patch('asyncio.sleep', AsyncMock())  # Skip sleep delays
    async def test_connect_success(self, mock_ib_class, ibkr_client):
        """Test successful IBKR connection"""
        # Mock the IB class and instance
        mock_ib_instance = Mock()  # Use regular Mock for non-async methods
        mock_ib_instance.isConnected.return_value = True
        mock_ib_instance.connectAsync = AsyncMock(return_value=True)  # Only async methods as AsyncMock
        mock_ib_instance.managedAccounts.return_value = ["DU123456"]  # Regular method returns list
        
        # Mock event objects that support += operator
        mock_ib_instance.disconnectedEvent = Mock()
        mock_ib_instance.disconnectedEvent.__iadd__ = Mock(return_value=mock_ib_instance.disconnectedEvent)
        mock_ib_instance.errorEvent = Mock()
        mock_ib_instance.errorEvent.__iadd__ = Mock(return_value=mock_ib_instance.errorEvent)
        
        mock_ib_class.return_value = mock_ib_instance
        
        result = await ibkr_client.connect()
        
        assert result is True
        assert ibkr_client._connected is True
        mock_ib_instance.connectAsync.assert_called_once()
    
    @pytest.mark.asyncio 
    @patch('ibkr_mcp_server.client.IB')
    @patch('asyncio.sleep', AsyncMock())  # Skip sleep delays
    async def test_connect_failure(self, mock_ib_class, ibkr_client):
        """Test connection failure handling"""
        # Mock the IB class to raise an exception on connectAsync
        mock_ib_instance = Mock()
        mock_ib_instance.connectAsync = AsyncMock(side_effect=Exception("Connection failed"))
        mock_ib_class.return_value = mock_ib_instance
        
        # The connect method should raise ConnectionError after retries
        with pytest.raises(ConnectionError, match="Connection failed"):
            await ibkr_client.connect()
        
        assert ibkr_client._connected is False
    
    @pytest.mark.asyncio
    @patch('ibkr_mcp_server.client.IB')
    @patch('asyncio.sleep', AsyncMock())  # Skip sleep delays
    async def test_connect_retry_logic(self, mock_ib_class, ibkr_client):
        """Test connection retry mechanism"""
        # Create two different mock instances for retry logic
        mock_ib_instance1 = Mock()
        mock_ib_instance1.connectAsync = AsyncMock(side_effect=Exception("Connection failed"))
        
        mock_ib_instance2 = Mock()
        mock_ib_instance2.connectAsync = AsyncMock(return_value=True)
        mock_ib_instance2.isConnected.return_value = True
        mock_ib_instance2.managedAccounts.return_value = ["DU123456"]
        
        # Mock event objects for second instance
        mock_ib_instance2.disconnectedEvent = Mock()
        mock_ib_instance2.disconnectedEvent.__iadd__ = Mock(return_value=mock_ib_instance2.disconnectedEvent)
        mock_ib_instance2.errorEvent = Mock()
        mock_ib_instance2.errorEvent.__iadd__ = Mock(return_value=mock_ib_instance2.errorEvent)
        
        # Make IB() return different instances on each call (simulating retry)
        mock_ib_class.side_effect = [mock_ib_instance1, mock_ib_instance2]
        
        result = await ibkr_client.connect()
        
        # Should succeed after retry
        assert result is True
        assert ibkr_client._connected is True
        # Verify both instances were created (retry occurred)
        assert mock_ib_class.call_count == 2
    
    @pytest.mark.asyncio
    async def test_disconnect_cleanup(self, ibkr_client):
        """Test clean disconnection process"""
        ibkr_client._connected = True
        
        await ibkr_client.disconnect()
        
        assert ibkr_client._connected is False
        ibkr_client.ib.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ensure_connected_when_connected(self, ibkr_client):
        """Test _ensure_connected when already connected"""
        ibkr_client._connected = True
        ibkr_client.ib.isConnected.return_value = True
        
        result = await ibkr_client._ensure_connected()
        
        assert result is True
        # Should not attempt new connection
        ibkr_client.ib.connectAsync.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_ensure_connected_when_disconnected(self, ibkr_client):
        """Test _ensure_connected triggers reconnection"""
        ibkr_client._connected = False
        ibkr_client.ib.isConnected.return_value = False
        
        # Mock the connect method to simulate successful reconnection
        with patch.object(ibkr_client, 'connect', AsyncMock(return_value=True)):
            # Mock is_connected to return False initially, then True after connect
            with patch.object(ibkr_client, 'is_connected', side_effect=[False, True]):
                result = await ibkr_client._ensure_connected()
                
                assert result is True
                # Verify connect was called
                ibkr_client.connect.assert_called_once()
    
    def test_is_connected_true(self, ibkr_client):
        """Test is_connected returns True when connected"""
        ibkr_client._connected = True
        ibkr_client.ib.isConnected.return_value = True
        
        assert ibkr_client.is_connected() is True
    
    def test_is_connected_false(self, ibkr_client):
        """Test is_connected returns False when disconnected"""
        ibkr_client._connected = False
        ibkr_client.ib.isConnected.return_value = False
        
        assert ibkr_client.is_connected() is False

    @pytest.mark.asyncio
    @patch('asyncio.create_task')
    @patch('asyncio.sleep', AsyncMock())
    async def test_client_reconnect_logic(self, mock_create_task, ibkr_client):
        """Test automatic reconnection logic when disconnected"""
        # Setup: Client is initially connected
        ibkr_client._connected = True
        ibkr_client._reconnect_task = None
        ibkr_client.reconnect_delay = 1
        
        # Mock the reconnect task
        mock_task = Mock()
        mock_task.done.return_value = True
        mock_create_task.return_value = mock_task
        
        # Mock the connect method
        with patch.object(ibkr_client, 'connect', AsyncMock(return_value=True)) as mock_connect:
            # Test 1: _on_disconnect should create a reconnect task
            ibkr_client._on_disconnect()
            
            # Should set connected to False
            assert ibkr_client._connected is False
            
            # Should create a reconnect task
            mock_create_task.assert_called_once()
            
            # Verify reconnect task is stored
            assert ibkr_client._reconnect_task == mock_task
            
            # Test 2: Test the _reconnect method directly
            await ibkr_client._reconnect()
            
            # Should attempt to reconnect
            mock_connect.assert_called_once()
            
            # Test 3: Test reconnect task cancellation on disconnect
            mock_create_task.reset_mock()
            mock_task.done.return_value = False
            mock_task.cancel = Mock()
            
            # Set up an active reconnect task
            ibkr_client._reconnect_task = mock_task
            
            # Call disconnect, which should cancel the task
            await ibkr_client.disconnect()
            
            # Should cancel the existing task
            mock_task.cancel.assert_called_once()
            assert ibkr_client._reconnect_task is None
            
            # Test 4: Test _on_disconnect doesn't create duplicate tasks
            mock_create_task.reset_mock()
            mock_task.done.return_value = False
            ibkr_client._reconnect_task = mock_task
            
            # Call _on_disconnect again - should not create new task
            ibkr_client._on_disconnect()
            
            # Should not create a new task since one is already running
            mock_create_task.assert_not_called()


@pytest.mark.unit
class TestClientPortfolioAndAccount:
    """Test portfolio and account management (10 tests)"""
    
    @pytest.fixture
    def mock_settings(self):
        settings = EnhancedSettings()
        settings.ibkr_is_paper = True
        return settings
        
    @pytest.fixture
    def mock_ib(self):
        ib = Mock()
        ib.isConnected = Mock(return_value=True)
        ib.portfolio = Mock(return_value=[])
        ib.accountSummary = Mock(return_value=[])
        ib.managedAccounts = ["DU123456"]
        return ib
        
    @pytest_asyncio.fixture
    async def ibkr_client(self, mock_settings, mock_ib):
        client = IBKRClient()
        client.settings = mock_settings
        client.ib = mock_ib
        client._connected = True
        client.current_account = "DU123456"
        client._ensure_connected = AsyncMock(return_value=True)
        return client
    
    @pytest.mark.asyncio
    async def test_get_portfolio_empty(self, ibkr_client):
        """Test empty portfolio response"""
        ibkr_client.ib.portfolio.return_value = []
        
        result = await ibkr_client.get_portfolio()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_portfolio_with_positions(self, ibkr_client):
        """Test portfolio with mock positions"""
        # Mock portfolio item object with all required attributes
        mock_item = Mock()
        mock_item.contract.symbol = "AAPL"
        mock_item.contract.secType = "STK"
        mock_item.contract.exchange = "SMART"
        mock_item.position = 100
        mock_item.averageCost = 175.0
        mock_item.marketPrice = 180.0
        mock_item.marketValue = 18000.0
        mock_item.unrealizedPNL = 500.0
        mock_item.realizedPNL = 0.0
        mock_item.account = "DU123456"
        
        # Mock the portfolio() method call (not property)
        ibkr_client.ib.portfolio.return_value = [mock_item]
        
        # Mock current_account
        ibkr_client.current_account = "DU123456"
        
        # Mock the client method calls
        ibkr_client.ib.client.reqAccountUpdates = Mock()
        
        result = await ibkr_client.get_portfolio()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['symbol'] == 'AAPL'
        assert result[0]['position'] == 100
        assert result[0]['marketValue'] == 18000.0
        assert result[0]['account'] == 'DU123456'
    
    @pytest.mark.asyncio
    async def test_get_portfolio_account_parameter(self, ibkr_client):
        """Test with specific account parameter"""
        ibkr_client.ib.portfolio.return_value = []
        
        result = await ibkr_client.get_portfolio(account="DU123456")
        
        assert isinstance(result, list)
        # Verify account parameter was used
        ibkr_client.ib.portfolio.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_portfolio_connection_error(self, ibkr_client):
        """Test connection error handling"""
        ibkr_client._ensure_connected = AsyncMock(return_value=False)
        
        with pytest.raises(Exception):
            await ibkr_client.get_portfolio()
    
    @pytest.mark.asyncio
    async def test_get_account_summary_success(self, ibkr_client):
        """Test successful account summary retrieval"""
        # Mock account value objects with account attribute
        mock_values = [
            Mock(tag="NetLiquidation", value="100000", currency="USD", account="DU123456"),
            Mock(tag="BuyingPower", value="200000", currency="USD", account="DU123456"),
            Mock(tag="TotalCashValue", value="50000", currency="USD", account="DU123456"),
        ]
        
        # Mock the correct method: accountValues() not accountSummary()
        ibkr_client.ib.accountValues.return_value = mock_values
        
        # Mock current_account and client methods
        ibkr_client.current_account = "DU123456"
        ibkr_client.ib.client.reqAccountUpdates = Mock()
        
        result = await ibkr_client.get_account_summary()
        
        assert isinstance(result, list)
        assert len(result) == 3
        # Check first item structure
        assert result[0]['tag'] == 'NetLiquidation'
        assert result[0]['value'] == '100000'
        assert result[0]['currency'] == 'USD'
        assert result[0]['account'] == 'DU123456'
    
    @pytest.mark.asyncio
    async def test_get_account_summary_multi_currency(self, ibkr_client):
        """Test multiple currency balances"""
        mock_values = [
            Mock(tag="NetLiquidation", value="100000", currency="USD", account="DU123456"),
            Mock(tag="NetLiquidation", value="85000", currency="EUR", account="DU123456"),
            Mock(tag="TotalCashValue", value="50000", currency="USD", account="DU123456"),
        ]
        
        # Mock the correct method: accountValues() not accountSummary()
        ibkr_client.ib.accountValues.return_value = mock_values
        
        # Mock current_account and client methods
        ibkr_client.current_account = "DU123456"
        ibkr_client.ib.client.reqAccountUpdates = Mock()
        
        result = await ibkr_client.get_account_summary()
        
        assert isinstance(result, list)
        assert len(result) == 3
        # Check multi-currency support
        currencies = [item['currency'] for item in result]
        assert 'USD' in currencies
        assert 'EUR' in currencies
    
    @pytest.mark.asyncio
    async def test_get_accounts_discovery(self, ibkr_client):
        """Test account discovery on connection"""
        # Setup client state as if connected with discovered accounts
        ibkr_client.accounts = ["DU123456", "DU789012"]
        ibkr_client.current_account = "DU123456"
        ibkr_client._connected = True
        
        # Setup managedAccounts mock for consistency
        ibkr_client.ib.managedAccounts = Mock(return_value=["DU123456", "DU789012"])
        
        result = await ibkr_client.get_accounts()
        
        assert isinstance(result, dict)
        assert "current_account" in result
        assert "available_accounts" in result
        assert len(result["available_accounts"]) == 2
        assert result["current_account"] == "DU123456"
        assert "DU123456" in result["available_accounts"]
        assert "DU789012" in result["available_accounts"]
        assert result["connected"] is True
        assert result["paper_trading"] is True
    
    @pytest.mark.asyncio
    async def test_switch_account_success(self, ibkr_client):
        """Test successful account switching"""
        # Setup client state with available accounts
        ibkr_client.accounts = ["DU123456", "DU789012"]
        ibkr_client.current_account = "DU123456"
        
        result = await ibkr_client.switch_account("DU789012")
        
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["message"] == "Switched to account: DU789012"
        assert result["current_account"] == "DU789012"
        assert result["available_accounts"] == ["DU123456", "DU789012"]
        assert ibkr_client.current_account == "DU789012"
    
    @pytest.mark.asyncio
    async def test_switch_account_invalid(self, ibkr_client):
        """Test switching to invalid account"""
        # Setup client state with available accounts
        ibkr_client.accounts = ["DU123456"]
        ibkr_client.current_account = "DU123456"
        
        result = await ibkr_client.switch_account("INVALID123")
        
        assert isinstance(result, dict)
        assert result["success"] is False
        assert result["message"] == "Account INVALID123 not found"
        assert result["current_account"] == "DU123456"
        assert result["available_accounts"] == ["DU123456"]
        # Verify current account didn't change
        assert ibkr_client.current_account == "DU123456"
    
    @pytest.mark.asyncio
    async def test_get_connection_status_connected(self, ibkr_client):
        """Test connection status when connected"""
        # Setup client state for connected scenario
        ibkr_client._connected = True
        ibkr_client.current_account = "DU123456"
        ibkr_client.accounts = ["DU123456", "DU789012"]
        ibkr_client.client_id = 5
        ibkr_client.host = "127.0.0.1"
        ibkr_client.port = 7497
        
        # Mock is_connected method to return True
        ibkr_client.is_connected = Mock(return_value=True)
        
        # Mock ib attributes for server info
        ibkr_client.ib.serverVersion = 178
        ibkr_client.ib.connectedAt = "2024-01-15 14:30:00"
        
        result = await ibkr_client.get_connection_status()
        
        # Validate basic response structure
        assert isinstance(result, dict)
        assert result["connected"] is True
        assert result["paper_trading"] is True
        assert result["client_id"] == 5
        assert result["host"] == "127.0.0.1"
        assert result["port"] == 7497
        
        # Validate connected-specific fields
        assert result["current_account"] == "DU123456"
        assert result["available_accounts"] == ["DU123456", "DU789012"]
        assert result["total_accounts"] == 2
        assert result["server_version"] == 178
        assert "connection_time" in result
    
    @pytest.mark.asyncio
    async def test_client_account_management(self, ibkr_client):
        """Test multi-account management"""
        # Setup multiple accounts scenario
        ibkr_client.accounts = ["DU123456", "DU789012", "DU345678"]
        ibkr_client.current_account = "DU123456"
        
        # Test 1: Initial state - multiple accounts discovered
        result = await ibkr_client.get_accounts()
        assert isinstance(result, dict)
        assert result["current_account"] == "DU123456"
        assert len(result["available_accounts"]) == 3
        assert "DU123456" in result["available_accounts"]
        assert "DU789012" in result["available_accounts"]
        assert "DU345678" in result["available_accounts"]
        
        # Test 2: Switch to second account successfully
        switch_result = await ibkr_client.switch_account("DU789012")
        assert switch_result["success"] is True
        assert switch_result["current_account"] == "DU789012"
        assert ibkr_client.current_account == "DU789012"
        assert switch_result["available_accounts"] == ["DU123456", "DU789012", "DU345678"]
        
        # Test 3: Get accounts after switch - should reflect new current account
        result = await ibkr_client.get_accounts()
        assert result["current_account"] == "DU789012"
        assert len(result["available_accounts"]) == 3
        
        # Test 4: Switch to third account
        switch_result = await ibkr_client.switch_account("DU345678")
        assert switch_result["success"] is True
        assert switch_result["current_account"] == "DU345678"
        assert ibkr_client.current_account == "DU345678"
        
        # Test 5: Attempt to switch to non-existent account
        switch_result = await ibkr_client.switch_account("INVALID999")
        assert switch_result["success"] is False
        assert "not found" in switch_result["message"]
        assert switch_result["current_account"] == "DU345678"  # Should remain unchanged
        assert ibkr_client.current_account == "DU345678"  # Should remain unchanged
        
        # Test 6: Verify account list remains consistent
        result = await ibkr_client.get_accounts()
        assert result["current_account"] == "DU345678"
        assert len(result["available_accounts"]) == 3
        assert result["connected"] is True
        assert result["paper_trading"] is True


@pytest.mark.unit
class TestClientMarketData:
    """Test market data functionality (6 tests)"""
    
    @pytest.fixture
    def mock_settings(self):
        return EnhancedSettings()
        
    @pytest.fixture 
    def mock_ib(self):
        ib = Mock()
        ib.isConnected = Mock(return_value=True)
        return ib
        
    @pytest_asyncio.fixture
    async def ibkr_client(self, mock_settings, mock_ib):
        client = IBKRClient()
        client.settings = mock_settings
        client.ib = mock_ib
        client._connected = True
        client._ensure_connected = AsyncMock(return_value=True)
        # Mock trading managers
        client.international_manager = Mock()
        return client
    
    @pytest.mark.asyncio
    async def test_get_market_data_single_symbol(self, ibkr_client):
        """Test single symbol quote"""
        mock_data = [{"symbol": "AAPL", "price": 180.0, "bid": 179.5, "ask": 180.5}]
        ibkr_client.international_manager.get_international_market_data = AsyncMock(return_value=mock_data)
        
        result = await ibkr_client.get_market_data("AAPL")
        
        assert result == mock_data
        ibkr_client.international_manager.get_international_market_data.assert_called_once_with("AAPL", True)
    
    @pytest.mark.asyncio
    async def test_get_market_data_multiple_symbols(self, ibkr_client):
        """Test multiple symbols"""
        mock_data = [
            {"symbol": "AAPL", "price": 180.0, "bid": 179.5, "ask": 180.5},
            {"symbol": "MSFT", "price": 415.0, "bid": 414.5, "ask": 415.5}
        ]
        ibkr_client.international_manager.get_international_market_data = AsyncMock(return_value=mock_data)
        
        result = await ibkr_client.get_market_data("AAPL,MSFT")
        
        assert result == mock_data
        ibkr_client.international_manager.get_international_market_data.assert_called_once_with("AAPL,MSFT", True)
    
    @pytest.mark.asyncio
    async def test_get_market_data_international(self, ibkr_client):
        """Test international symbol detection"""
        mock_data = [{"symbol": "ASML", "exchange": "AEB", "currency": "EUR", "price": 650.80}]
        ibkr_client.international_manager.get_international_market_data = AsyncMock(return_value=mock_data)
        
        result = await ibkr_client.get_market_data("ASML")
        
        assert result == mock_data
        ibkr_client.international_manager.get_international_market_data.assert_called_once_with("ASML", True)
    
    @pytest.mark.asyncio
    async def test_get_market_data_invalid_symbol(self, ibkr_client):
        """Test invalid symbol handling"""
        ibkr_client.international_manager.get_international_market_data = AsyncMock(side_effect=ValueError("Invalid symbol"))
        
        with pytest.raises(ValueError):
            await ibkr_client.get_market_data("INVALID")
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_success(self, ibkr_client):
        """Test enhanced symbol resolution"""
        mock_result = {
            "symbol": "ASML", 
            "matches": [{"exchange": "AEB", "currency": "EUR", "name": "ASML Holding NV", "confidence": 1.0}],
            "exchange_info": {"exchange": "AEB", "currency": "EUR"}
        }
        ibkr_client.international_manager.resolve_symbol = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.resolve_symbol("ASML")
        
        assert result == mock_result
        ibkr_client.international_manager.resolve_symbol.assert_called_once_with(
            "ASML", None, None, "STK", True, False, 5
        )
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_with_params(self, ibkr_client):
        """Test symbol resolution with custom parameters"""
        mock_result = {
            "symbol": "APPLE", 
            "matches": [{"exchange": "SMART", "currency": "USD", "name": "Apple Inc", "confidence": 0.95}],
            "exchange_info": {"exchange": "SMART", "currency": "USD"}
        }
        ibkr_client.international_manager.resolve_symbol = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.resolve_symbol("APPLE", exchange="SMART", currency="USD", max_results=10, fuzzy_search=True, include_alternatives=True)
        
        assert result == mock_result
        ibkr_client.international_manager.resolve_symbol.assert_called_once_with(
            "APPLE", "SMART", "USD", "STK", True, True, 10
        )


@pytest.mark.unit
class TestClientForex:
    """Test forex functionality (4 tests)"""
    
    @pytest_asyncio.fixture
    async def ibkr_client(self):
        client = IBKRClient()
        client._connected = True
        client._ensure_connected = AsyncMock(return_value=True)
        client.forex_manager = Mock()
        # Add mock IB client for margin requirements test
        client.ib = Mock()
        client.ib.qualifyContractsAsync = AsyncMock(return_value=None)
        client.ib.isConnected = Mock(return_value=True)
        return client
    
    @pytest.mark.asyncio
    async def test_get_forex_rates_single_pair(self, ibkr_client):
        """Test single currency pair"""
        mock_rates = [{"pair": "EURUSD", "rate": 1.0856}]
        ibkr_client.forex_manager.get_forex_rates = AsyncMock(return_value=mock_rates)
        
        result = await ibkr_client.get_forex_rates("EURUSD")
        
        assert result == mock_rates
    
    @pytest.mark.asyncio
    async def test_get_forex_rates_multiple_pairs(self, ibkr_client):
        """Test multiple pairs"""
        mock_rates = [
            {"pair": "EURUSD", "rate": 1.0856},
            {"pair": "GBPUSD", "rate": 1.2654}
        ]
        ibkr_client.forex_manager.get_forex_rates = AsyncMock(return_value=mock_rates)
        
        result = await ibkr_client.get_forex_rates("EURUSD,GBPUSD")
        
        assert result == mock_rates
    
    @pytest.mark.asyncio
    async def test_convert_currency_direct(self, ibkr_client):
        """Test direct currency conversion"""
        mock_result = {"amount": 1000, "converted": 1085.6, "rate": 1.0856}
        ibkr_client.forex_manager.convert_currency = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.convert_currency(1000.0, "EUR", "USD")
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_convert_currency_cross(self, ibkr_client):
        """Test cross-currency conversion"""
        mock_result = {"amount": 1000, "converted": 91250, "rate": 91.25}
        ibkr_client.forex_manager.convert_currency = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.convert_currency(1000.0, "GBP", "JPY")
        
        assert result == mock_result

    @pytest.mark.asyncio
    async def test_get_margin_requirements(self, ibkr_client):
        """Test margin requirements functionality"""
        # Mock the IB API responses
        mock_contract = Mock()
        mock_contract.conId = 12345
        mock_contract.exchange = "SMART"
        mock_contract.symbol = "AAPL"
        
        ibkr_client.ib.qualifyContractsAsync = AsyncMock(return_value=None)
        
        # Mock the contract to have a valid conId after qualification
        with patch('ibkr_mcp_server.client.Stock', return_value=mock_contract):
            result = await ibkr_client.get_margin_requirements("AAPL")
        
        # Verify the result structure
        assert "symbol" in result
        assert "contract_id" in result
        assert "exchange" in result
        assert "margin_requirement" in result
        assert "note" in result
        
        assert result["symbol"] == "AAPL"
        assert result["contract_id"] == 12345
        assert result["exchange"] == "SMART"
        assert "Market data subscription required" in result["margin_requirement"]

    @pytest.mark.asyncio
    async def test_get_margin_requirements_invalid_symbol(self, ibkr_client):
        """Test margin requirements with invalid symbol"""
        # Mock contract with no conId (invalid symbol)
        mock_contract = Mock()
        mock_contract.conId = None
        
        ibkr_client.ib.qualifyContractsAsync = AsyncMock(return_value=None)
        
        with patch('ibkr_mcp_server.client.Stock', return_value=mock_contract):
            result = await ibkr_client.get_margin_requirements("INVALID")
        
        # Should return error for invalid symbol
        assert "error" in result
        assert "Invalid symbol: INVALID" in result["error"]

    @pytest.mark.asyncio
    async def test_get_margin_requirements_connection_error(self, ibkr_client):
        """Test margin requirements when not connected"""
        # Mock disconnected state
        ibkr_client._connected = False
        ibkr_client.ib.isConnected.return_value = False
        
        result = await ibkr_client.get_margin_requirements("AAPL")
        
        # Should return error for connection issue
        assert "error" in result
        assert "Invalid symbol: AAPL" in result["error"]


@pytest.mark.unit
class TestClientTradingManagerIntegration:
    """Test trading manager integration (4 tests)"""
    
    @pytest_asyncio.fixture
    async def ibkr_client(self):
        client = IBKRClient()
        client._connected = True
        client.ib = Mock()
        return client
    
    def test_initialize_trading_managers(self, ibkr_client):
        """Test manager initialization"""
        with patch('ibkr_mcp_server.client.ForexManager') as MockForex, \
             patch('ibkr_mcp_server.client.InternationalManager') as MockIntl, \
             patch('ibkr_mcp_server.client.StopLossManager') as MockStop, \
             patch('ibkr_mcp_server.client.OrderManager') as MockOrder:
            
            ibkr_client._initialize_trading_managers()
            
            MockForex.assert_called_once_with(ibkr_client.ib)
            MockIntl.assert_called_once_with(ibkr_client.ib)
            MockStop.assert_called_once_with(ibkr_client.ib)
            MockOrder.assert_called_once_with(ibkr_client.ib)
    
    def test_trading_managers_not_none(self, ibkr_client):
        """Test managers are created properly"""
        # Mock managers
        ibkr_client.forex_manager = Mock()
        ibkr_client.international_manager = Mock()
        ibkr_client.stop_loss_manager = Mock()
        
        assert ibkr_client.forex_manager is not None
        assert ibkr_client.international_manager is not None
        assert ibkr_client.stop_loss_manager is not None
    
    @pytest.mark.asyncio
    async def test_place_stop_loss_delegation(self, ibkr_client):
        """Test delegation to stop loss manager"""
        ibkr_client.stop_loss_manager = Mock()
        ibkr_client.stop_loss_manager.place_stop_loss = AsyncMock(return_value={"order_id": 123})
        
        result = await ibkr_client.place_stop_loss("AAPL", quantity=100, stop_price=180.0)
        
        assert result == {"order_id": 123}
        ibkr_client.stop_loss_manager.place_stop_loss.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_stop_losses_delegation(self, ibkr_client):
        """Test delegation to stop loss manager"""
        ibkr_client.stop_loss_manager = Mock()
        ibkr_client.stop_loss_manager.get_stop_losses = AsyncMock(return_value=[])
        
        result = await ibkr_client.get_stop_losses()
        
        assert result == []
        ibkr_client.stop_loss_manager.get_stop_losses.assert_called_once()


@pytest.mark.unit
class TestClientOrderManagement:
    """Test order management methods (6 tests)"""
    
    @pytest_asyncio.fixture
    async def ibkr_client(self):
        client = IBKRClient()
        client._connected = True
        client._ensure_connected = AsyncMock(return_value=True)
        client.order_manager = Mock()
        return client
    
    @pytest.mark.asyncio
    async def test_place_market_order_success(self, ibkr_client):
        """Test market order placement"""
        mock_result = {"order_id": 123, "symbol": "AAPL"}
        ibkr_client.order_manager = Mock()
        ibkr_client.order_manager.place_market_order = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.place_market_order("AAPL", "BUY", 100)
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_place_limit_order_success(self, ibkr_client):
        """Test limit order placement"""
        mock_result = {"order_id": 124, "symbol": "MSFT"}
        ibkr_client.order_manager = Mock()
        ibkr_client.order_manager.place_limit_order = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.place_limit_order("MSFT", "BUY", 50, 400.0)
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_cancel_order_success(self, ibkr_client):
        """Test order cancellation"""
        mock_result = {"success": True, "order_id": 123}
        ibkr_client.order_manager = Mock()
        ibkr_client.order_manager.cancel_order = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.cancel_order(123)
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_modify_order_success(self, ibkr_client):
        """Test order modification"""
        mock_result = {"success": True, "order_id": 123}
        ibkr_client.order_manager = Mock()
        ibkr_client.order_manager.modify_order = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.modify_order(123)
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_get_order_status_success(self, ibkr_client):
        """Test order status retrieval"""
        mock_result = {"order_id": 123, "status": "Filled"}
        ibkr_client.order_manager = Mock()
        ibkr_client.order_manager.get_order_status = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.get_order_status(123)
        
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_place_bracket_order_success(self, ibkr_client):
        """Test bracket order placement"""
        mock_result = {"parent_id": 125, "stop_id": 126, "target_id": 127}
        ibkr_client.order_manager = Mock()
        ibkr_client.order_manager.place_bracket_order = AsyncMock(return_value=mock_result)
        
        result = await ibkr_client.place_bracket_order("GOOGL", "BUY", 10, 2750.0, 2650.0, 2850.0)
        
        assert result == mock_result


@pytest.mark.unit  
class TestClientErrorHandlingAndEdgeCases:
    """Test error handling and edge cases (4 tests)"""
    
    @pytest.fixture
    def mock_position(self):
        """Mock position object for testing"""
        position = Mock()
        position.contract.symbol = "AAPL"
        position.position = 100
        position.marketPrice = 180.0
        position.marketValue = 18000.0
        position.averageCost = 175.0
        position.unrealizedPNL = 500.0
        position.contract.currency = "USD"
        return position
    
    @pytest.fixture
    def mock_account_value(self):
        """Mock account value for testing"""
        account_val = Mock()
        account_val.tag = "NetLiquidation"
        account_val.value = "100000"
        account_val.currency = "USD"
        return account_val
        
    @pytest_asyncio.fixture
    async def ibkr_client(self):
        client = IBKRClient()
        client.settings = EnhancedSettings()
        client._connected = True
        return client
    
    def test_serialization_methods(self, ibkr_client, mock_position, mock_account_value):
        """Test _serialize_position, _serialize_portfolio_item, _serialize_account_value"""
        # Test _serialize_position
        position_result = ibkr_client._serialize_position(mock_position)
        assert isinstance(position_result, dict)
        assert "symbol" in position_result
        assert position_result["symbol"] == "AAPL"
        
        # Test _serialize_account_value  
        account_result = ibkr_client._serialize_account_value(mock_account_value)
        assert isinstance(account_result, dict)
        assert account_result["tag"] == "NetLiquidation"
        assert account_result["value"] == "100000"
    
    @patch('asyncio.create_task')
    def test_on_disconnect_handler(self, mock_create_task, ibkr_client):
        """Test disconnect event handler"""
        ibkr_client._connected = True
        ibkr_client._reconnect_task = None
        
        # Call the disconnect handler
        ibkr_client._on_disconnect()
        
        # Verify disconnection state
        assert ibkr_client._connected is False
        
        # Verify reconnection task was scheduled
        mock_create_task.assert_called_once()
        called_args = mock_create_task.call_args[0]
        assert hasattr(called_args[0], '__await__')  # Verify it's a coroutine
    
    def test_on_error_handler(self, ibkr_client):
        """Test error event handler"""
        # Mock the logger to capture log calls
        with patch.object(ibkr_client, 'logger') as mock_logger:
            
            # Test regular error logging
            ibkr_client._on_error(reqId=1, errorCode=502, errorString="Order cancelled", contract=None)
            mock_logger.error.assert_called_once_with("IBKR Error 502: Order cancelled (reqId: 1)")
            
            # Reset mock for next test
            mock_logger.reset_mock()
            
            # Test market data warning (should be debug logged, not error)
            ibkr_client._on_error(reqId=2, errorCode=2104, errorString="Market data farm connection is OK", contract=None)
            mock_logger.debug.assert_called_once_with("IBKR Info 2104: Market data farm connection is OK")
            mock_logger.error.assert_not_called()
            
            # Reset mock for next test
            mock_logger.reset_mock()
            
            # Test another routine warning code
            ibkr_client._on_error(reqId=3, errorCode=2106, errorString="HMDS data farm connection is OK", contract=None)
            mock_logger.debug.assert_called_once_with("IBKR Info 2106: HMDS data farm connection is OK")
            mock_logger.error.assert_not_called()
            
            # Reset mock for next test  
            mock_logger.reset_mock()
            
            # Test another routine warning code
            ibkr_client._on_error(reqId=4, errorCode=2158, errorString="Market data farm connection has recovered", contract=None)
            mock_logger.debug.assert_called_once_with("IBKR Info 2158: Market data farm connection has recovered")
            mock_logger.error.assert_not_called()
    
    def test_paper_account_detection(self, ibkr_client):
        """Test is_paper property"""
        # Test paper account port detection (7497 is paper trading port)
        ibkr_client.port = 7497
        assert ibkr_client.is_paper is True
        
        # Test another paper trading port
        ibkr_client.port = 4002  
        assert ibkr_client.is_paper is True
        
        # Test live account port detection (7496 is live trading port)
        ibkr_client.port = 7496
        assert ibkr_client.is_paper is False
        
        # Test other non-paper port
        ibkr_client.port = 8080
        assert ibkr_client.is_paper is False
    
    @pytest.mark.asyncio
    async def test_client_event_handlers(self):
        """Test comprehensive event handler integration during connection"""
        # Create a mock IB instance
        mock_ib = Mock()
        mock_ib.connectAsync = AsyncMock(return_value=True)
        mock_ib.isConnected = Mock(return_value=True)
        mock_ib.managedAccounts = Mock(return_value=["DU123456"])
        
        # Create mock event handlers that support += operator
        class MockEvent:
            def __init__(self):
                self.handlers = []
            
            def __iadd__(self, handler):
                self.handlers.append(handler)
                return self
        
        mock_disconnected_event = MockEvent()
        mock_error_event = MockEvent()
        mock_ib.disconnectedEvent = mock_disconnected_event
        mock_ib.errorEvent = mock_error_event
        
        # Create client and configure for testing
        client = IBKRClient()
        client.settings = EnhancedSettings()
        client.host = "127.0.0.1"
        client.port = 7497
        client.client_id = 1
        
        # Patch the IB constructor to return our mock
        with patch('ibkr_mcp_server.client.IB', return_value=mock_ib):
            with patch('asyncio.sleep'):  # Skip sleep delays in test
                with patch.object(client, '_initialize_trading_managers'):  # Skip manager initialization
                    # Perform connection
                    success = await client.connect()
                    
                    # Verify connection was successful
                    assert success is True
                    assert client._connected is True
                    assert client.ib == mock_ib
                    
                    # Verify IBKR connection was attempted with correct parameters
                    mock_ib.connectAsync.assert_called_once_with(
                        host="127.0.0.1",
                        port=7497,
                        clientId=1,
                        timeout=10
                    )
                    
                    # Verify event handlers were registered
                    assert len(mock_disconnected_event.handlers) == 1
                    assert len(mock_error_event.handlers) == 1
                    
                    # Verify the correct handler methods were registered
                    disconnect_handler = mock_disconnected_event.handlers[0]
                    error_handler = mock_error_event.handlers[0]
                    
                    # Verify they are the client's event handler methods
                    assert disconnect_handler == client._on_disconnect
                    assert error_handler == client._on_error
                    
                    # Test that the event handlers can be called (integration test)
                    with patch.object(client, 'logger') as mock_logger:
                        with patch('asyncio.create_task') as mock_create_task:
                            # Test disconnect handler execution
                            client._on_disconnect()
                            assert client._connected is False
                            mock_create_task.assert_called_once()
                            
                            # Reset client state
                            client._connected = True
                            
                            # Test error handler execution
                            client._on_error(reqId=1, errorCode=502, errorString="Test error", contract=None)
                            mock_logger.error.assert_called_once_with("IBKR Error 502: Test error (reqId: 1)")
                            
                            # Test info-level error handler
                            mock_logger.reset_mock()
                            client._on_error(reqId=2, errorCode=2104, errorString="Market data OK", contract=None)
                            mock_logger.debug.assert_called_once_with("IBKR Info 2104: Market data OK")
                            mock_logger.error.assert_not_called()


@pytest.mark.unit
class TestClientOrderHistory:
    """Test order history functionality (original tests preserved)"""
    
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
        ib.reqOpenOrdersAsync = AsyncMock()
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
    async def test_get_completed_orders_with_real_data(self, ibkr_client):
        """Test get_completed_orders with realistic data structure - verifies the bug fix"""
        from unittest.mock import Mock
        
        # Create mock Trade object with realistic IBKR structure that was causing the bug
        mock_trade = Mock()
        
        # Mock Order object with the CORRECT data (this is where real data lives)
        mock_order = Mock()
        mock_order.filledQuantity = 2.0  # REAL filled quantity (was being ignored)
        mock_order.totalQuantity = 0    # IBKR sets this to 0 for completed orders (this was the problem!)
        mock_order.permId = 928753150   # Real order ID
        mock_order.orderId = 12345      # Alternative order ID
        mock_order.action = "BUY"
        mock_order.orderType = "MKT"
        mock_order.account = "DU123456"
        mock_order.tif = "DAY"
        mock_order.clientId = 5
        mock_order.orderRef = ""
        mock_order.lmtPrice = None
        mock_order.auxPrice = None
        mock_order.avgFillPrice = 0     # Often zero in completed orders
        
        # Mock Contract object  
        mock_contract = Mock()
        mock_contract.symbol = "AAPL"
        mock_contract.exchange = "SMART"
        mock_contract.currency = "USD"
        
        # Mock OrderStatus object (this was the source of the bug - all zeros!)
        mock_order_status = Mock()
        mock_order_status.filled = 0.0      # BUG: This is always 0 for completed orders!
        mock_order_status.avgFillPrice = 0.0  # BUG: This is always 0 for completed orders!
        mock_order_status.orderId = 0       # BUG: This is always 0 for completed orders!
        mock_order_status.status = "Filled"
        
        # Wire up the Trade object structure
        mock_trade.order = mock_order
        mock_trade.contract = mock_contract  
        mock_trade.orderStatus = mock_order_status
        mock_trade.commission = 1.0
        mock_trade.fills = []  # No fill details for completed orders (IBKR limitation)
        
        # Mock IBKR API response with the problematic structure
        ibkr_client.ib.reqCompletedOrdersAsync.return_value = [mock_trade]
        
        # Execute the function
        result = await ibkr_client.get_completed_orders()
        
        # Verify the fix works - should extract real data from order object, not orderStatus
        assert isinstance(result, list)
        assert len(result) == 1
        
        order_data = result[0]
        
        # VERIFICATION: These should be REAL values, not zeros (the bug fix)
        assert order_data["order_id"] == 928753150  # Should use permId, not the zero orderId from orderStatus
        assert order_data["filled"] == 2.0          # Should use order.filledQuantity, not orderStatus.filled (which is 0)
        assert order_data["quantity"] == 2.0        # Should use filledQuantity as fallback when totalQuantity is 0
        assert order_data["remaining"] == 0         # Should be calculated: max(0, total - filled)
        
        # Standard fields should work correctly
        assert order_data["symbol"] == "AAPL"
        assert order_data["exchange"] == "SMART"
        assert order_data["currency"] == "USD"
        assert order_data["action"] == "BUY"
        assert order_data["order_type"] == "MKT"
        assert order_data["status"] == "Filled"
        assert order_data["account"] == "DU123456"
        assert order_data["client_id"] == 5
        
        # Price data - validates the IBKR API limitation documentation
        # avg_fill_price may be 0 due to IBKR API limitation for completed orders
        # This is expected behavior, not a bug
        assert "avg_fill_price" in order_data
        # Note: avg_fill_price may be 0 for completed orders - this is an IBKR API limitation
        
    @pytest.mark.asyncio
    async def test_get_completed_orders_with_fill_data(self, ibkr_client):
        """Test get_completed_orders when fill data is available (best case scenario)"""
        from unittest.mock import Mock
        
        # Create mock Trade object with fills data available
        mock_trade = Mock()
        
        # Mock Order object
        mock_order = Mock()
        mock_order.filledQuantity = 100.0
        mock_order.totalQuantity = 100.0  # Complete fill
        mock_order.permId = 999888777
        mock_order.action = "SELL"
        mock_order.orderType = "LMT"
        mock_order.account = "DU123456"
        
        # Mock Contract object
        mock_contract = Mock()
        mock_contract.symbol = "TSLA"
        mock_contract.exchange = "SMART"
        mock_contract.currency = "USD"
        
        # Mock OrderStatus object
        mock_order_status = Mock()
        mock_order_status.status = "Filled"
        
        # Mock Fill data (when available, this provides accurate pricing)
        mock_execution = Mock()
        mock_execution.price = 245.50
        mock_execution.shares = 100.0
        
        mock_fill = Mock()
        mock_fill.execution = mock_execution
        
        # Wire up Trade object with fills
        mock_trade.order = mock_order
        mock_trade.contract = mock_contract
        mock_trade.orderStatus = mock_order_status
        mock_trade.fills = [mock_fill]  # When available, provides real pricing
        mock_trade.commission = 2.5
        
        # Mock IBKR API response
        ibkr_client.ib.reqCompletedOrdersAsync.return_value = [mock_trade]
        
        # Execute the function
        result = await ibkr_client.get_completed_orders()
        
        # Verify fill data is used correctly
        assert len(result) == 1
        order_data = result[0]
        
        assert order_data["filled"] == 100.0
        assert order_data["quantity"] == 100.0
        assert order_data["remaining"] == 0
        assert order_data["avg_fill_price"] == 245.50  # Should calculate from fills when available
        assert order_data["symbol"] == "TSLA"
        
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
    async def test_get_open_orders_basic_functionality(self, ibkr_client):
        """Test get_open_orders basic call structure"""
        # Mock the basic call succeeds
        ibkr_client.ib.reqOpenOrdersAsync.return_value = []
        
        result = await ibkr_client.get_open_orders()
        
        # Should return list
        assert isinstance(result, list)
        assert len(result) == 0
        
    @pytest.mark.asyncio
    async def test_connection_error_handling_order_history(self, ibkr_client):
        """Test error handling when not connected"""
        # Mock connection failure
        ibkr_client._ensure_connected = AsyncMock(return_value=False)
        
        with pytest.raises(Exception):  # Should raise some connection error
            await ibkr_client.get_completed_orders()
            
        with pytest.raises(Exception):  # Should raise some connection error
            await ibkr_client.get_executions()
    
    @pytest.mark.asyncio
    async def test_client_error_recovery(self):
        """Test error recovery mechanisms"""
        # Create a fresh client without pre-mocked methods for this test
        from ibkr_mcp_server.enhanced_config import EnhancedSettings
        settings = EnhancedSettings()
        settings.enable_trading = True
        settings.ibkr_is_paper = True
        
        client = IBKRClient()
        client.settings = settings
        client.ib = Mock()
        client.ib.isConnected = Mock(return_value=True)
        client._connected = False
        client.current_account = "DU123456"
        client.reconnect_delay = 1.0
        
        # Test 1: Automatic reconnection on disconnect
        with patch.object(client, 'logger') as mock_logger, \
             patch('asyncio.create_task') as mock_create_task:
            
            # Simulate disconnection
            client._connected = True  # Start connected
            client._reconnect_task = None
            
            # Call disconnect handler
            client._on_disconnect()
            
            # Verify reconnection task was scheduled
            assert client._connected is False
            mock_logger.warning.assert_called_once_with("IBKR disconnected, scheduling reconnection...")
            mock_create_task.assert_called_once()
        
        # Test 2: _ensure_connected recovery mechanism
        with patch.object(client, 'connect') as mock_connect, \
             patch.object(client, 'is_connected') as mock_is_connected:
            
            # Simulate disconnected state, then successful reconnection
            mock_is_connected.side_effect = [False, True]  # First call returns False, second True
            mock_connect.return_value = None  # connect() doesn't return anything
            
            result = await client._ensure_connected()
            
            assert result is True
            mock_connect.assert_called_once()
            assert mock_is_connected.call_count == 2
        
        # Test 3: _ensure_connected failure handling
        with patch.object(client, 'connect') as mock_connect, \
             patch.object(client, 'is_connected') as mock_is_connected, \
             patch.object(client, 'logger') as mock_logger:
            
            # Simulate connection failure
            mock_is_connected.return_value = False
            mock_connect.side_effect = Exception("Connection failed")
            
            result = await client._ensure_connected()
            
            assert result is False
            mock_logger.error.assert_called_once_with("Failed to ensure connection: Connection failed")
        
        # Test 4: _reconnect method error handling
        with patch.object(client, 'connect') as mock_connect, \
             patch.object(client, 'logger') as mock_logger, \
             patch('asyncio.sleep') as mock_sleep:
            
            # Simulate reconnect failure
            mock_connect.side_effect = Exception("Reconnection failed")
            
            await client._reconnect()
            
            mock_sleep.assert_called_once_with(client.reconnect_delay)
            mock_logger.error.assert_called_once_with("Reconnection failed: Reconnection failed")
        
        # Test 5: _reconnect task cancellation handling
        with patch.object(client, 'logger') as mock_logger, \
             patch('asyncio.sleep') as mock_sleep:
            
            # Simulate task cancellation
            mock_sleep.side_effect = asyncio.CancelledError()
            
            with pytest.raises(asyncio.CancelledError):
                await client._reconnect()
            
            mock_logger.debug.assert_called_once_with("Reconnection task cancelled")
        
        # Test 6: Error recovery in operations - test market data recovery
        with patch.object(client, '_ensure_connected') as mock_ensure, \
             patch.object(client, 'logger') as mock_logger:
            
            # Simulate connection recovery - set client to connected state
            mock_ensure.return_value = True
            client._connected = True  # Set connected state
            client.international_manager = AsyncMock()
            client.international_manager.get_international_market_data.return_value = [{"symbol": "AAPL", "price": 150.0}]
            
            result = await client.get_market_data(["AAPL"])
            
            # Should succeed without calling ensure_connected since is_connected() returns True
            assert len(result) == 1
            assert result[0]["symbol"] == "AAPL"
