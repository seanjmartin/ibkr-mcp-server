#!/usr/bin/env python3
"""
Test individual paper tests with proper event loop handling
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ibkr_mcp_server.client import IBKRClient


async def test_sequential_connections():
    """Test sequential connections to see if event loop handling can be fixed"""
    print("=== Testing Sequential IBKR Connections ===")
    
    for i in range(3):
        print(f"\n--- Test {i+1} ---")
        client = IBKRClient()
        client.client_id = 5
        
        try:
            print("Connecting...")
            connected = await client.connect()
            if connected:
                print("SUCCESS: Connected successfully")
                
                # Test a simple operation
                status = await client.get_connection_status()
                print(f"Account: {status.get('current_account', 'Unknown')}")
                
                print("Disconnecting...")
                await client.disconnect()
                print("SUCCESS: Disconnected successfully")
                
                # Wait between tests to allow cleanup
                print("Waiting 3 seconds for cleanup...")
                await asyncio.sleep(3)
            else:
                print("ERROR: Connection failed")
                break
                
        except Exception as e:
            print(f"ERROR: Test {i+1} failed: {e}")
            try:
                await client.disconnect()
            except:
                pass
            break
    
    print("\n=== Sequential connection test completed ===")


if __name__ == "__main__":
    # Try with a single event loop for all tests
    asyncio.run(test_sequential_connections())
