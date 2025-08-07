#!/usr/bin/env python3

import asyncio
from ib_async import IB

async def test_simple_connection():
    """Test basic IBKR Gateway connection"""
    print("Testing basic IBKR Gateway connection...")
    
    ib = IB()
    try:
        print("Attempting to connect to Gateway on port 7497 with client ID 5...")
        await ib.connectAsync('127.0.0.1', 7497, clientId=5, timeout=10)
        print("SUCCESS: Connected successfully!")
        
        # Brief test
        print(f"Connection status: {ib.isConnected()}")
        
        print("Disconnecting...")
        ib.disconnect()  # This is the correct sync method
        print("SUCCESS: Disconnected successfully!")
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_connection())
