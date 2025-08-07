#!/usr/bin/env python3
"""
Quick IBKR connection test to verify Gateway accessibility
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from ib_async import IB

async def test_quick_connection():
    """Test basic IBKR connection with 10-second timeout"""
    ib = IB()
    
    try:
        print("Attempting IBKR Gateway connection...")
        print("Host: 127.0.0.1, Port: 7497, Client ID: 100")
        
        # Connect with aggressive timeout
        await asyncio.wait_for(
            ib.connectAsync('127.0.0.1', 7497, clientId=100),
            timeout=10.0
        )
        
        print("SUCCESS: Connected to IBKR Gateway!")
        
        # Get basic account info
        accounts = ib.managedAccounts()
        print(f"Accounts: {accounts}")
        
        # Disconnect
        await ib.disconnectAsync()
        print("SUCCESS: Disconnected cleanly")
        return True
        
    except asyncio.TimeoutError:
        print("ERROR: Connection timed out (Gateway not responding)")
        return False
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False
    finally:
        if ib.isConnected():
            await ib.disconnectAsync()

if __name__ == "__main__":
    result = asyncio.run(test_quick_connection())
    sys.exit(0 if result else 1)
