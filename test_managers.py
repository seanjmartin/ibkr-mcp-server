#!/usr/bin/env python3
"""Test script to validate trading managers initialization"""

import sys
import asyncio
from pathlib import Path

# Add the package path
sys.path.insert(0, str(Path(__file__).parent))

from ibkr_mcp_server.client import IBKRClient

async def test_managers():
    """Test basic manager initialization and connection"""
    client = IBKRClient()
    
    print("Testing manager initialization...")
    
    try:
        # Test manager attributes without connection first
        has_forex = hasattr(client, 'forex_manager')
        has_intl = hasattr(client, 'international_manager')  
        has_stop = hasattr(client, 'stop_loss_manager')
        
        print("MANAGER_TEST_RESULTS:")
        print(f"Forex manager: {has_forex}")
        print(f"International manager: {has_intl}")
        print(f"Stop loss manager: {has_stop}")
        
        # Now test connection
        print("Testing connection...")
        connected = await client.connect()
        
        if connected:
            print("Connection: SUCCESS")
            
            # Test connection status using is_connected method
            is_conn = client.is_connected()
            print(f"Is connected: {is_conn}")
            
            # Test a basic operation
            accounts = await client.get_accounts()
            print(f"Accounts retrieved: {len(accounts)} accounts")
            
        else:
            print("Connection: FAILED")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if client._connected:
            print("Disconnecting...")
            await client.disconnect()
            
    print("Manager test complete.")

if __name__ == "__main__":
    asyncio.run(test_managers())
