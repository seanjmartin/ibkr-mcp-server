#!/usr/bin/env python3
"""
Explore IBKR stop loss and order management capabilities
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def explore_stop_loss_capabilities():
    """Explore available stop loss order types and functionality"""
    
    print("IBKR Stop Loss Capabilities Analysis")
    print("=" * 50)
    
    try:
        # Import order types
        from ib_async import (
            MarketOrder, LimitOrder, StopOrder, StopLimitOrder,
            TrailStopOrder, TrailStopLimitOrder, BracketOrder,
            Order, OrderState, Trade, Fill
        )
        
        print("\n1. Available Stop Loss Order Types:")
        
        # Basic Stop Order
        print("\n   A. Stop Order (Market Stop):")
        stop_order = StopOrder('SELL', 100, 95.0)
        print(f"      {stop_order}")
        print(f"      - Triggers market sell when price hits $95.0")
        print(f"      - Action: {stop_order.action}, Quantity: {stop_order.totalQuantity}")
        print(f"      - Stop Price: {stop_order.auxPrice}")
        
        # Stop Limit Order  
        print("\n   B. Stop Limit Order:")
        stop_limit = StopLimitOrder('SELL', 100, 95.0, 94.5)
        print(f"      {stop_limit}")
        print(f"      - Triggers limit sell at $94.5 when price hits $95.0")
        print(f"      - Stop Price: {stop_limit.auxPrice}, Limit Price: {stop_limit.lmtPrice}")
        
        # Trailing Stop Order
        print("\n   C. Trailing Stop Order:")
        trail_stop = TrailStopOrder('SELL', 100, trailAmount=2.0)
        print(f"      {trail_stop}")
        print(f"      - Trails $2.0 below highest price")
        print(f"      - Trail Amount: {trail_stop.trailStopPrice}")
        
        # Trailing Stop Limit Order
        print("\n   D. Trailing Stop Limit Order:")
        trail_limit = TrailStopLimitOrder('SELL', 100, trailAmount=2.0, lmtPriceOffset=0.5)
        print(f"      {trail_limit}")
        print(f"      - Trails $2.0, then limit order $0.5 below trigger")
        
        # Bracket Order (includes stop loss)
        print("\n   E. Bracket Order (with Stop Loss & Take Profit):")
        parent = MarketOrder('BUY', 100)
        bracket = BracketOrder(parent, takeProfitPrice=105.0, stopLossPrice=95.0)
        print(f"      Parent: {bracket.parent}")
        print(f"      Take Profit: {bracket.takeProfit}")  
        print(f"      Stop Loss: {bracket.stopLoss}")
        print(f"      - One-Cancels-Other (OCO) structure")
        
        print("\n2. Order Attributes for Stop Losses:")
        
        # Create comprehensive stop order with all attributes
        advanced_stop = Order()
        advanced_stop.action = 'SELL'
        advanced_stop.totalQuantity = 100
        advanced_stop.orderType = 'STP'
        advanced_stop.auxPrice = 95.0  # Stop price
        advanced_stop.tif = 'GTC'  # Good Till Cancelled
        advanced_stop.outsideRth = True  # Allow outside regular trading hours
        advanced_stop.transmit = True
        
        print(f"   Advanced Stop Order Attributes:")
        print(f"   - Order Type: {advanced_stop.orderType}")
        print(f"   - Time in Force: {advanced_stop.tif}")
        print(f"   - Outside RTH: {advanced_stop.outsideRth}")
        print(f"   - Transmit: {advanced_stop.transmit}")
        
        print("\n3. Time in Force Options:")
        tif_options = ['DAY', 'GTC', 'IOC', 'FOK', 'GTD', 'OPG', 'CLS']
        for tif in tif_options:
            descriptions = {
                'DAY': 'Day order (expires at market close)',
                'GTC': 'Good Till Cancelled',
                'IOC': 'Immediate or Cancel',
                'FOK': 'Fill or Kill',
                'GTD': 'Good Till Date',
                'OPG': 'Market on Open',
                'CLS': 'Market on Close'
            }
            print(f"   - {tif}: {descriptions.get(tif, 'Standard option')}")
        
        print("\n4. Stop Loss Attributes Available:")
        attributes = [
            'auxPrice',      # Stop trigger price
            'lmtPrice',      # Limit price (for stop-limit)
            'trailStopPrice', # Trailing amount
            'trailPercent',   # Trailing percentage
            'parentId',       # For bracket orders
            'ocaGroup',       # One-Cancels-All group
            'triggerMethod',  # How stop is triggered
            'adjustedStopPrice', # Adjusted trailing stop
            'outsideRth',     # Outside regular trading hours
            'allOrNone',      # All-or-none execution
        ]
        
        for attr in attributes:
            print(f"   - {attr}: Available for customization")
        
        print("\n5. Order States and Monitoring:")
        states = ['PreSubmitted', 'Submitted', 'Filled', 'Cancelled', 'PendingCancel', 'ApiCancelled']
        print("   Order states for tracking:")
        for state in states:
            print(f"   - {state}")
        
        print("\n6. International Market Considerations:")
        print("   - Stop orders work on international exchanges")
        print("   - Currency-specific pricing (EUR, GBP, JPY, etc.)")
        print("   - Exchange-specific trading hours affect execution")
        print("   - Some exchanges may have different stop order rules")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error exploring stop loss capabilities: {e}")
        return False

if __name__ == "__main__":
    success = explore_stop_loss_capabilities()
    if success:
        print("\n" + "=" * 50)
        print("✅ IBKR has comprehensive stop loss support!")
        print("✅ Multiple order types available")
        print("✅ Advanced customization options")
        print("✅ International market compatible")
    else:
        print("\n❌ Could not analyze stop loss capabilities")
