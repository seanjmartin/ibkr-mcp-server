#!/usr/bin/env python3
"""
Test current market data tool behavior with forex symbols
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from ibkr_mcp_server.client import ibkr_client

async def test_forex_symbols():
    """Test what happens when we try forex symbols"""
    
    print("Testing current market data tool with forex symbols...")
    
    # Test 1: Regular stock (should work)
    try:
        print("\n1. Testing stock symbol AAPL:")
        result = await ibkr_client.get_market_data("AAPL")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Forex symbol (should fail)
    try:
        print("\n2. Testing forex symbol EURUSD:")
        result = await ibkr_client.get_market_data("EURUSD")
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Try to create forex contract manually
    try:
        print("\n3. Testing manual Forex contract creation:")
        from ib_async import Forex
        
        await ibkr_client._ensure_connected()
        
        # Create forex contract
        eurusd = Forex('EURUSD')
        print(f"   Forex contract created: {eurusd}")
        
        # Try to qualify it
        qualified = await ibkr_client.ib.qualifyContractsAsync(eurusd)
        print(f"   Qualified contracts: {qualified}")
        
        if qualified:
            # Try to get ticker
            tickers = await ibkr_client.ib.reqTickersAsync(*qualified)
            print(f"   Tickers: {tickers}")
            
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_forex_symbols())
