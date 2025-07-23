"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import MagicMock

from ibkr_mcp_server.client import IBKRClient


@pytest.fixture
def mock_ib():
    """Mock IB object for testing."""
    ib = MagicMock()
    ib.isConnected.return_value = True
    ib.managedAccounts.return_value = ['DU1234567', 'DU7654321']
    return ib


@pytest.fixture
def ibkr_client_mock(mock_ib):
    """Mock IBKR client for testing."""
    client = IBKRClient()
    client.ib = mock_ib
    client._connected = True
    client.accounts = ['DU1234567', 'DU7654321']
    client.current_account = 'DU1234567'
    return client
