"""Tests for IBKR client functionality."""

import pytest
from ibkr_mcp_server.client import IBKRClient


def test_client_creation():
    """Test client can be created."""
    client = IBKRClient()
    assert client is not None


@pytest.mark.asyncio
async def test_client_connect():
    """Test client connect method."""
    client = IBKRClient()
    result = await client.connect()
    assert result is True


@pytest.mark.asyncio
async def test_client_disconnect():
    """Test client disconnect method."""
    client = IBKRClient()
    result = await client.disconnect()
    assert result is True
