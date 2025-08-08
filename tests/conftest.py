"""
Pytest configuration and shared fixtures for IBKR MCP Server testing.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime, timezone

# Import core components
from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings
from ibkr_mcp_server.safety_framework import TradingSafetyManager

# Mock ib_async components
try:
    from ib_async import IB, Stock, Forex, Order, Trade, Ticker, Contract
except ImportError:
    # Create minimal mocks if ib_async not available
    class IB:
        pass
    class Stock:
        pass
    class Forex:
        pass
    class Order:
        pass
    class Trade:
        pass
    class Ticker:
        pass
    class Contract:
        pass


@pytest.fixture
def mock_settings():
    """Mock enhanced settings for testing"""
    settings = EnhancedSettings()
    settings.enable_trading = True
    settings.enable_forex_trading = True
    settings.enable_international_trading = True
    settings.enable_stop_loss_orders = True
    settings.ibkr_is_paper = True
    settings.ibkr_host = "127.0.0.1"
    settings.ibkr_port = 7497
    return settings


@pytest.fixture
def mock_ib():
    """Mock IB client with common methods"""
    ib = Mock(spec=IB)
    ib.connectAsync = AsyncMock(return_value=True)
    ib.isConnected = Mock(return_value=True)
    ib.disconnectAsync = AsyncMock()
    
    # Create a proper mock contract for testing
    mock_contract = Mock()
    mock_contract.minSize = None  # No minimum size constraint
    mock_contract.secType = 'STK'  # Stock type
    mock_contract.symbol = 'AAPL'
    mock_contract.exchange = 'SMART'
    mock_contract.currency = 'USD'
    
    ib.qualifyContractsAsync = AsyncMock(return_value=[mock_contract])
    ib.reqTickersAsync = AsyncMock()
    ib.placeOrder = Mock()
    ib.reqOpenOrdersAsync = AsyncMock(return_value=[])
    ib.reqCompletedOrdersAsync = AsyncMock(return_value=[])
    ib.reqExecutionsAsync = AsyncMock(return_value=[])
    ib.whatIfOrderAsync = AsyncMock()
    ib.accountSummaryAsync = AsyncMock()
    ib.portfolioAsync = AsyncMock()
    ib.accountValuesAsync = AsyncMock()
    return ib


@pytest.fixture
async def ibkr_client(mock_settings, mock_ib):
    """Create IBKR client with mocked dependencies"""
    client = IBKRClient()
    client.settings = mock_settings
    client.ib = mock_ib
    client._connected = True
    
    # Mock trading managers
    client.forex_manager = Mock()
    client.international_manager = Mock()
    client.stop_loss_manager = Mock()
    client.safety_manager = TradingSafetyManager()
    
    return client


@pytest.fixture
def safety_manager():
    """Create safety manager for testing"""
    return TradingSafetyManager()


@pytest.fixture
def sample_forex_ticker():
    """Sample forex ticker data for testing"""
    ticker = Mock(spec=Ticker)
    ticker.contract = Mock()
    ticker.contract.symbol = 'EURUSD'
    ticker.contract.conId = 12087792
    ticker.last = 1.0856
    ticker.bid = 1.0855
    ticker.ask = 1.0857
    ticker.close = 1.0850
    ticker.high = 1.0865
    ticker.low = 1.0840
    ticker.volume = 125000
    return ticker


@pytest.fixture
def sample_stock_ticker():
    """Sample stock ticker data for testing"""
    ticker = Mock(spec=Ticker)
    ticker.contract = Mock()
    ticker.contract.symbol = 'AAPL'
    ticker.contract.exchange = 'SMART'
    ticker.contract.currency = 'USD'
    ticker.last = 185.50
    ticker.bid = 185.48
    ticker.ask = 185.52
    ticker.close = 184.30
    ticker.high = 186.20
    ticker.low = 183.90
    ticker.volume = 45678900
    return ticker


@pytest.fixture
def sample_international_ticker():
    """Sample international stock ticker data for testing"""
    ticker = Mock(spec=Ticker)
    ticker.contract = Mock()
    ticker.contract.symbol = 'ASML'
    ticker.contract.exchange = 'AEB'
    ticker.contract.currency = 'EUR'
    ticker.last = 650.80
    ticker.bid = 650.60
    ticker.ask = 651.00
    ticker.close = 648.50
    ticker.high = 655.20
    ticker.low = 645.30
    ticker.volume = 145230
    return ticker


@pytest.fixture
def sample_portfolio_item():
    """Sample portfolio item for testing"""
    from ib_async import PortfolioItem
    
    item = Mock(spec=PortfolioItem)
    item.contract = Mock()
    item.contract.symbol = 'AAPL'
    item.contract.exchange = 'SMART'
    item.contract.currency = 'USD'
    item.position = 100
    item.marketPrice = 185.50
    item.marketValue = 18550.0
    item.averageCost = 180.00
    item.unrealizedPNL = 550.0
    item.realizedPNL = 0.0
    item.account = 'DU123456'
    return item


@pytest.fixture
def sample_account_values():
    """Sample account values for testing"""
    from ib_async import AccountValue
    
    values = []
    
    # Cash balances
    usd_cash = Mock(spec=AccountValue)
    usd_cash.account = 'DU123456'
    usd_cash.tag = 'CashBalance'
    usd_cash.value = '50000.00'
    usd_cash.currency = 'USD'
    values.append(usd_cash)
    
    # Total portfolio value
    nav = Mock(spec=AccountValue)
    nav.account = 'DU123456'
    nav.tag = 'NetLiquidation'
    nav.value = '75000.00'
    nav.currency = 'USD'
    values.append(nav)
    
    # Buying power
    buying_power = Mock(spec=AccountValue)
    buying_power.account = 'DU123456'
    buying_power.tag = 'BuyingPower'
    buying_power.value = '150000.00'
    buying_power.currency = 'USD'
    values.append(buying_power)
    
    return values


@pytest.fixture
def mock_forex_rates():
    """Mock forex rates data"""
    return [
        {
            'pair': 'EURUSD',
            'last': 1.0856,
            'bid': 1.0855,
            'ask': 1.0857,
            'close': 1.0850,
            'high': 1.0865,
            'low': 1.0840,
            'volume': 125000,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'change': 0.0006,
            'change_percent': 0.055
        },
        {
            'pair': 'GBPUSD',
            'last': 1.2654,
            'bid': 1.2653,
            'ask': 1.2655,
            'close': 1.2648,
            'high': 1.2670,
            'low': 1.2640,
            'volume': 98000,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'change': 0.0006,
            'change_percent': 0.047
        }
    ]


@pytest.fixture
def mock_international_symbols():
    """Mock international symbol data"""
    return {
        'ASML': {
            'symbol': 'ASML',
            'exchange': 'AEB',
            'currency': 'EUR',
            'name': 'ASML Holding NV',
            'sector': 'Technology',
            'country': 'Netherlands'
        },
        'SAP': {
            'symbol': 'SAP',
            'exchange': 'XETRA',
            'currency': 'EUR',
            'name': 'SAP SE',
            'sector': 'Technology',
            'country': 'Germany'
        },
        '7203': {
            'symbol': '7203',
            'exchange': 'TSE',
            'currency': 'JPY',
            'name': 'Toyota Motor Corporation',
            'sector': 'Consumer Cyclical',
            'country': 'Japan'
        }
    }


@pytest.fixture
async def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Helper functions for test data generation
def generate_mock_order(order_id: int = 12345, symbol: str = "AAPL") -> Dict[str, Any]:
    """Generate mock order data"""
    return {
        'order_id': order_id,
        'symbol': symbol,
        'action': 'SELL',
        'quantity': 100,
        'order_type': 'STP',
        'stop_price': 180.00,
        'status': 'Submitted',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'account': 'DU123456'
    }


def generate_mock_execution(symbol: str = "AAPL") -> Dict[str, Any]:
    """Generate mock execution data"""
    return {
        'symbol': symbol,
        'side': 'BOT',
        'shares': 100,
        'price': 185.50,
        'time': datetime.now(timezone.utc).isoformat(),
        'exchange': 'SMART',
        'commission': 1.00,
        'pnl': 550.0
    }


# pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "unit: Unit tests with mocks only"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring IBKR connection"
    )
    config.addinivalue_line(
        "markers", "paper: Tests requiring paper trading account"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "safety: Safety framework validation tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 30 seconds"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on location"""
    for item in items:
        # Mark tests based on directory structure
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "paper" in str(item.fspath):
            item.add_marker(pytest.mark.paper)
            item.add_marker(pytest.mark.slow)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Mark safety tests
        if "safety" in str(item.fspath) or "safety" in item.name:
            item.add_marker(pytest.mark.safety)
