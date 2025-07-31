#!/usr/bin/env python3
"""Test the correct way to call ib-async methods."""

import asyncio
from ib_async import IB, Stock

async def test_methods():
    ib = IB()
    
    try:
        # Connect to IB Gateway
        await ib.connectAsync('127.0.0.1', 7497, clientId=1)
        print("Connected to IB Gateway")
        
        # Test account summary - check the correct parameters
        print("\n=== Testing Account Summary ===")
        try:
            # The new way might be different
            summary = await ib.reqAccountSummaryAsync()
            print(f"Account summary: {summary}")
        except Exception as e:
            print(f"reqAccountSummaryAsync error: {e}")
        
        # Test positions
        print("\n=== Testing Positions ===")
        try:
            positions = await ib.reqPositionsAsync()
            print(f"Positions: {positions}")
        except Exception as e:
            print(f"reqPositionsAsync error: {e}")
        
        # Test tickers for market data
        print("\n=== Testing Market Data ===")
        try:
            apple_stock = Stock('AAPL', 'SMART', 'USD')
            tesla_stock = Stock('TSLA', 'SMART', 'USD')
            
            contracts = await ib.qualifyContractsAsync(apple_stock, tesla_stock)
            print(f"Qualified contracts: {len(contracts)}")
            
            if contracts:
                tickers = await ib.reqTickersAsync(*contracts[:1])  # Just test one
                print(f"Market data: {tickers}")
        except Exception as e:
            print(f"Market data error: {e}")
            
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()

if __name__ == "__main__":
    asyncio.run(test_methods())
