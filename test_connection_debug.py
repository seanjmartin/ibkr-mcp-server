#!/usr/bin/env python3
"""
Debug IBKR connection with multiple client IDs
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from ib_async import IB

async def test_multiple_client_ids():
    """Test connection with different client IDs"""
    
    for client_id in [1, 5, 10, 50, 100, 200]:
        ib = IB()
        
        try:
            print(f"\nTrying Client ID {client_id}...")
            
            # Very short timeout to quickly test each ID
            await asyncio.wait_for(
                ib.connectAsync('127.0.0.1', 7497, clientId=client_id),
                timeout=3.0
            )
            
            print(f"SUCCESS: Client ID {client_id} connected!")
            
            # Get accounts quickly
            accounts = ib.managedAccounts()
            print(f"Accounts: {accounts}")
            
            # Disconnect immediately
            await ib.disconnectAsync()
            print(f"SUCCESS: Client ID {client_id} disconnected cleanly")
            
            # Wait before trying next ID
            await asyncio.sleep(1)
            
        except asyncio.TimeoutError:
            print(f"TIMEOUT: Client ID {client_id} - Gateway not responding")
        except Exception as e:
            print(f"ERROR: Client ID {client_id} failed: {e}")
        finally:
            if ib.isConnected():
                try:
                    await ib.disconnectAsync()
                except:
                    pass

if __name__ == "__main__":
    asyncio.run(test_multiple_client_ids())
