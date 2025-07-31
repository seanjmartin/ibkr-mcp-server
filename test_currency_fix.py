#!/usr/bin/env python3
"""Test currency conversion fix"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ibkr_mcp_server.client import IBKRClient
    
    async def test_conversion():
        print("Starting currency conversion test...")
        client = IBKRClient()
        try:
            print("Attempting to connect to IBKR...")
            connected = await client.connect()
            if connected:
                print('Connected successfully')
                
                # Test currency conversion
                print("Testing USD to EUR conversion...")
                result = await client.convert_currency(1000.0, 'USD', 'EUR')
                print('Conversion result:', result)
                
                # Test another conversion
                print("Testing EUR to GBP conversion...")
                result2 = await client.convert_currency(500.0, 'EUR', 'GBP')
                print('Conversion result 2:', result2)
                
            else:
                print('Failed to connect - check if IB Gateway is running on port 7497')
        except Exception as e:
            print(f'Error during test: {e}')
            import traceback
            traceback.print_exc()
        finally:
            try:
                if hasattr(client, 'ib') and client.ib and client.ib.isConnected():
                    print("Disconnecting...")
                    await client.disconnect()
                    print("Disconnected")
            except Exception as e:
                print(f"Error during disconnect: {e}")
        
        print("Test completed.")
    
    if __name__ == '__main__':
        asyncio.run(test_conversion())
        
except Exception as e:
    print(f'Import error: {e}')
    import traceback
    traceback.print_exc()
