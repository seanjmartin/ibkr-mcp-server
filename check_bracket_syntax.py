#!/usr/bin/env python3
"""
Check BracketOrder syntax and create comprehensive stop loss analysis
"""
from ib_async import BracketOrder, MarketOrder, LimitOrder, StopOrder

def check_bracket_order():
    print("BracketOrder Syntax Check")
    print("=" * 30)
    
    try:
        # Check BracketOrder help
        print("BracketOrder signature:")
        print(BracketOrder.__doc__)
        
        # Try different approaches
        parent = MarketOrder('BUY', 100)
        take_profit = LimitOrder('SELL', 100, 55.0)
        stop_loss = StopOrder('SELL', 100, 45.0)
        
        # Method 1: Using separate orders
        print(f"\nParent: {parent}")
        print(f"Take Profit: {take_profit}")
        print(f"Stop Loss: {stop_loss}")
        
        # Try to create bracket
        try:
            bracket = BracketOrder(parent, take_profit, stop_loss)
            print(f"Bracket created: {bracket}")
        except Exception as e:
            print(f"Method 1 failed: {e}")
            
        # Check what parameters BracketOrder actually accepts
        import inspect
        sig = inspect.signature(BracketOrder.__init__)
        print(f"\nBracketOrder parameters: {sig}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_bracket_order()
