#!/usr/bin/env python3
"""
Standalone API test - bypasses the singleton client
"""
import asyncio
from ib_async import IB

async def test_api_direct():
    """Test the ib-async API methods directly"""
    print("Direct ib-async API Test")
    print("=" * 30)
    
    ib = IB()
    
    try:
        print("Connecting with client ID 3...")
        await ib.connectAsync('127.0.0.1', 7497, clientId=3)
        print("Connected successfully!")
        
        # Test account summary - our fix
        print("\nTesting reqAccountSummaryAsync()...")
        summary = await ib.reqAccountSummaryAsync()
        print(f"Got {len(summary)} account summary items")
        for item in summary[:3]:
            print(f"  {item.tag}: {item.value}")
        
        # Test positions
        print("\nTesting reqPositionsAsync()...")
        positions = await ib.reqPositionsAsync()
        print(f"Got {len(positions)} positions")
        
        # Test market data - new method
        print("\nTesting qualifyContractsAsync()...")
        from ib_async import Stock
        stock = Stock('AAPL', 'SMART', 'USD')
        qualified = await ib.qualifyContractsAsync(stock)
        print(f"Qualified {len(qualified)} contracts")
        
        if qualified:
            print("\nTesting reqTickersAsync()...")
            tickers = await ib.reqTickersAsync(*qualified)
            print(f"Got {len(tickers)} tickers")
            for ticker in tickers:
                print(f"  {ticker.contract.symbol}: ${ticker.close}")
        
        print("\nAll API methods working correctly!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if ib.isConnected():
            await ib.disconnectAsync()

if __name__ == "__main__":
    success = asyncio.run(test_api_direct())
    if success:
        print("\n✓ API fixes validated - all methods work!")
    else:
        print("\n✗ Some API issues remain")
