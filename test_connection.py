#!/usr/bin/env python3
"""Test IBKR connection without problematic Unicode characters."""

import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ibkr_connection():
    """Test basic IBKR connection."""
    try:
        print("Testing IBKR MCP Server connection...")
        
        # Import and test connection
        from ibkr_mcp_server.client import IBKRClient
        from ibkr_mcp_server.config import settings
        
        print(f"Connecting to {settings.ibkr_host}:{settings.ibkr_port}")
        print(f"Client ID: {settings.ibkr_client_id}")
        print(f"Paper mode: {settings.ibkr_is_paper}")
        
        # Create client and test connection
        client = IBKRClient()
        await client.connect()
        
        print("SUCCESS: Connected to IB Gateway!")
        
        # Test basic functionality
        try:
            accounts = await client.get_accounts()
            print(f"Found {len(accounts)} account(s): {accounts}")
        except Exception as e:
            print(f"Account info: {e}")
        
        # Disconnect
        await client.disconnect()
        print("Connection test completed successfully!")
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure IB Gateway is running")
        print("2. Check that API is enabled in Gateway settings")
        print("3. Verify port 7497 is correct")
        print("4. Ensure 127.0.0.1 is in trusted IPs")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_ibkr_connection())
    if not success:
        sys.exit(1)
