#!/usr/bin/env python3
"""
Test international exchange capabilities in IBKR
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from ibkr_mcp_server.client import ibkr_client

async def test_international_exchanges():
    """Test international stock contracts and exchanges"""
    
    print("Testing International Exchange Capabilities...")
    
    try:
        from ib_async import Stock
        
        await ibkr_client._ensure_connected()
        
        # Test European stocks
        print("\n1. European Exchanges:")
        european_stocks = [
            ("ASML", "AEB", "EUR"),      # Netherlands - Euronext Amsterdam
            ("SAP", "XETRA", "EUR"),     # Germany - XETRA
            ("NESN", "SWX", "CHF"),      # Switzerland - SIX Swiss Exchange
            ("VOD", "LSE", "GBP"),       # UK - London Stock Exchange
            ("MC", "SBF", "EUR"),        # France - Euronext Paris
        ]
        
        european_contracts = []
        for symbol, exchange, currency in european_stocks:
            stock = Stock(symbol, exchange, currency)
            european_contracts.append(stock)
            print(f"   Created: {stock}")
        
        # Try to qualify European contracts
        print("\n   Qualifying European contracts...")
        qualified_eu = await ibkr_client.ib.qualifyContractsAsync(*european_contracts)
        print(f"   Qualified {len(qualified_eu)} out of {len(european_contracts)} European contracts")
        
        for contract in qualified_eu:
            print(f"   ✅ {contract.symbol} on {contract.exchange} ({contract.currency})")
        
        # Test Asian stocks
        print("\n2. Asian Exchanges:")
        asian_stocks = [
            ("7203", "TSE", "JPY"),      # Toyota - Tokyo Stock Exchange
            ("2330", "SEHK", "HKD"),     # TSMC - Hong Kong Exchange
            ("005930", "KSE", "KRW"),    # Samsung - Korea Exchange
            ("CBA", "ASX", "AUD"),       # Commonwealth Bank - Australian Securities Exchange
        ]
        
        asian_contracts = []
        for symbol, exchange, currency in asian_stocks:
            stock = Stock(symbol, exchange, currency)
            asian_contracts.append(stock)
            print(f"   Created: {stock}")
        
        # Try to qualify Asian contracts
        print("\n   Qualifying Asian contracts...")
        qualified_asia = await ibkr_client.ib.qualifyContractsAsync(*asian_contracts)
        print(f"   Qualified {len(qualified_asia)} out of {len(asian_contracts)} Asian contracts")
        
        for contract in qualified_asia:
            print(f"   ✅ {contract.symbol} on {contract.exchange} ({contract.currency})")
        
        # Test if we can get market data for international stocks
        print("\n3. Market Data Test:")
        all_qualified = qualified_eu + qualified_asia
        if all_qualified:
            print(f"   Testing market data for {len(all_qualified)} international contracts...")
            tickers = await ibkr_client.ib.reqTickersAsync(*all_qualified[:3])  # Test first 3
            
            for ticker in tickers:
                print(f"   📊 {ticker.contract.symbol} ({ticker.contract.exchange}): "
                      f"Last={ticker.last}, Bid={ticker.bid}, Ask={ticker.ask}")
        
        # Test trading capabilities
        print("\n4. Trading Methods Available:")
        trading_methods = [method for method in dir(ibkr_client.ib) 
                          if 'order' in method.lower() and not method.startswith('_')]
        
        print("   Available trading methods:")
        for method in sorted(trading_methods)[:10]:  # Show first 10
            print(f"   - {method}")
        
    except Exception as e:
        print(f"   Error during international exchange test: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_international_exchanges())
