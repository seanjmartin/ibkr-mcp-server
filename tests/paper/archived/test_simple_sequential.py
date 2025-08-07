#!/usr/bin/env python3

import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ibkr_mcp_server.client import IBKRClient

async def test_connection():
    print("Testing IBKR connection...")
    client = IBKRClient()
    client.client_id = 5
    
    try:
        connected = await client.connect()
        print(f"Connected: {connected}")
        if connected:
            await client.disconnect()
            print("Disconnected successfully")
        return connected
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    print("=== Testing 3 sequential connections ===")
    for i in range(3):
        print(f"\n--- Test {i+1} ---")
        success = await test_connection()
        if not success:
            print("Test failed, stopping")
            break
        print("Waiting 5 seconds...")
        await asyncio.sleep(5)
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
