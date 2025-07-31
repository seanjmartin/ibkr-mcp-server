#!/usr/bin/env python3
"""
Test forex and trading capabilities in ib-async
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from ib_async import IB, Forex, MarketOrder, Order
    
    print("Available contract types:")
    print("- Forex imported successfully")
    
    print("\nForex contract creation test:")
    eurusd = Forex('EURUSD')
    print(f"EURUSD contract: {eurusd}")
    
    print(f"Currency pair: {eurusd.pair}")
    print(f"Exchange: {eurusd.exchange}")
    
    print("\nAvailable IB methods for trading:")
    ib = IB()
    
    # Look for trading-related methods
    trading_methods = []
    for method in dir(ib):
        if any(keyword in method.lower() for keyword in ['order', 'trade', 'place']):
            trading_methods.append(method)
    
    print("Trading methods found:")
    for method in sorted(trading_methods):
        print(f"  - {method}")
        
    print("\nOrder types available:")
    print("- MarketOrder imported successfully")
    market_order = MarketOrder('BUY', 1000)  # 1000 units
    print(f"Sample market order: {market_order}")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
