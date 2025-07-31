#!/usr/bin/env python3
"""Test international trading functionality"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ibkr_mcp_server.client import IBKRClient
    
    async def test_international():
        print("Starting international trading test...")
        client = IBKRClient()
        try:
            print("Connecting to IBKR...")
            connected = await client.connect()
            if connected:
                print('Connected successfully')
                
                # Test 1: Symbol resolution
                print("\n=== Testing Symbol Resolution ===")
                try:
                    result = await client.resolve_international_symbol('ASML')
                    print('ASML resolution:', result)
                    
                    result2 = await client.resolve_international_symbol('SAP', exchange='XETRA', currency='EUR')
                    print('SAP resolution:', result2)
                except Exception as e:
                    print(f'Symbol resolution error: {e}')
                
                # Test 2: International market data with auto-detection
                print("\n=== Testing Auto-Detection Market Data ===")
                try:
                    symbols = "ASML,SAP,7203"  # Netherlands, Germany, Japan
                    result = await client.get_international_market_data(symbols, auto_detect=True)
                    print(f'Auto-detect market data for {symbols}:')
                    for item in result:
                        print(f"  {item.get('symbol', 'N/A')} ({item.get('exchange', 'N/A')}/{item.get('currency', 'N/A')}): {item.get('last', 'N/A')}")
                except Exception as e:
                    print(f'Auto-detect market data error: {e}')
                
                # Test 3: Explicit format market data
                print("\n=== Testing Explicit Format Market Data ===")
                try:
                    symbols = "ASML.AEB.EUR,SAP.XETRA.EUR"  # Explicit format
                    result = await client.get_international_market_data(symbols, auto_detect=False)
                    print(f'Explicit format market data for {symbols}:')
                    for item in result:
                        print(f"  {item.get('symbol', 'N/A')} ({item.get('exchange', 'N/A')}/{item.get('currency', 'N/A')}): {item.get('last', 'N/A')}")
                except Exception as e:
                    print(f'Explicit format market data error: {e}')
                
                # Test 4: Mixed symbols (US + International)
                print("\n=== Testing Mixed Symbols ===")
                try:
                    symbols = "AAPL,ASML,GOOGL"  # US, Dutch, US
                    result = await client.get_international_market_data(symbols, auto_detect=True)
                    print(f'Mixed symbols market data for {symbols}:')
                    for item in result:
                        print(f"  {item.get('symbol', 'N/A')} ({item.get('exchange', 'N/A')}/{item.get('currency', 'N/A')}): {item.get('last', 'N/A')}")
                except Exception as e:
                    print(f'Mixed symbols error: {e}')
                
            else:
                print('Failed to connect - check if IB Gateway is running')
        except Exception as e:
            print(f'Test error: {e}')
            import traceback
            traceback.print_exc()
        finally:
            try:
                if hasattr(client, 'ib') and client.ib and client.ib.isConnected():
                    print("\nDisconnecting...")
                    await client.disconnect()
                    print("Disconnected")
            except Exception as e:
                print(f"Disconnect error: {e}")
        
        print("International trading test completed.")
    
    if __name__ == '__main__':
        asyncio.run(test_international())
        
except Exception as e:
    print(f'Import error: {e}')
    import traceback
    traceback.print_exc()
