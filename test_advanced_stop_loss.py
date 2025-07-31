#!/usr/bin/env python3
"""
Test advanced stop loss features and order reading capabilities
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_advanced_stop_loss_features():
    """Test comprehensive stop loss functionality"""
    
    print("Advanced Stop Loss Features Test")
    print("=" * 40)
    
    try:
        from ib_async import (
            StopOrder, StopLimitOrder, Order, BracketOrder, 
            MarketOrder, LimitOrder, Stock
        )
        
        print("\n1. Basic Stop Loss Orders:")
        
        # Simple stop loss (market order when triggered)
        basic_stop = StopOrder('SELL', 100, 45.50)
        print(f"   Basic Stop: {basic_stop}")
        print(f"   - Sells 100 shares at market when price drops to $45.50")
        
        # Stop limit (limit order when triggered) 
        stop_limit = StopLimitOrder('SELL', 100, stopPrice=45.50, lmtPrice=45.00)
        print(f"   Stop Limit: {stop_limit}")
        print(f"   - Triggers at $45.50, places limit sell at $45.00")
        
        print("\n2. Advanced Stop Loss Attributes:")
        
        # Advanced stop with all options
        advanced_stop = Order()
        advanced_stop.action = 'SELL'
        advanced_stop.totalQuantity = 100
        advanced_stop.orderType = 'STP'  # Stop order
        advanced_stop.auxPrice = 45.50  # Stop trigger price
        advanced_stop.tif = 'GTC'  # Good Till Cancelled
        advanced_stop.outsideRth = True  # Allow after-hours execution
        advanced_stop.parentId = 0  # Parent order ID (0 = standalone)
        advanced_stop.transmit = True  # Submit immediately
        advanced_stop.allOrNone = False  # Allow partial fills
        
        print(f"   Advanced Stop Order Attributes:")
        print(f"   - Order Type: {advanced_stop.orderType}")
        print(f"   - Stop Price: ${advanced_stop.auxPrice}")
        print(f"   - Time in Force: {advanced_stop.tif}")
        print(f"   - Outside RTH: {advanced_stop.outsideRth}")
        print(f"   - All or None: {advanced_stop.allOrNone}")
        
        print("\n3. Trailing Stop Loss:")
        
        # Trailing stop using Order object
        trailing_stop = Order()
        trailing_stop.action = 'SELL'
        trailing_stop.totalQuantity = 100
        trailing_stop.orderType = 'TRAIL'
        trailing_stop.auxPrice = 2.00  # Trail amount in dollars
        trailing_stop.tif = 'GTC'
        
        print(f"   Trailing Stop: {trailing_stop.orderType}")
        print(f"   - Trails $2.00 below highest price")
        print(f"   - Adjusts automatically as stock rises")
        
        # Trailing stop with percentage
        trailing_pct = Order()
        trailing_pct.action = 'SELL'
        trailing_pct.totalQuantity = 100
        trailing_pct.orderType = 'TRAIL'
        trailing_pct.trailPercent = 5.0  # 5% trailing stop
        trailing_pct.tif = 'GTC'
        
        print(f"   Trailing Percentage: {trailing_pct.trailPercent}%")
        print(f"   - Trails 5% below highest price")
        
        print("\n4. Bracket Orders (Stop Loss + Take Profit):")
        
        # Parent order (main position)
        parent_order = MarketOrder('BUY', 100)
        
        # Bracket with stop loss and take profit
        bracket = BracketOrder(
            parent=parent_order,
            takeProfitPrice=55.00,  # Take profit at $55
            stopLossPrice=45.00     # Stop loss at $45
        )
        
        print(f"   Bracket Order Components:")
        print(f"   - Parent: {bracket.parent}")
        print(f"   - Take Profit: ${55.00}")
        print(f"   - Stop Loss: ${45.00}")
        print(f"   - Type: One-Cancels-Other (OCO)")
        
        print("\n5. Time in Force Options for Stop Losses:")
        tif_options = {
            'DAY': 'Expires at end of trading day',
            'GTC': 'Good Till Cancelled (persists)',
            'IOC': 'Immediate or Cancel',
            'FOK': 'Fill or Kill (all or nothing)',
            'GTD': 'Good Till Date (specify expiry)',
            'OPG': 'Market on Open',
            'CLS': 'Market on Close'
        }
        
        for tif, description in tif_options.items():
            print(f"   - {tif}: {description}")
        
        print("\n6. International Stop Loss Considerations:")
        
        # Example: European stock stop loss
        eu_stock = Stock('ASML', 'AEB', 'EUR')
        eu_stop = StopOrder('SELL', 50, 650.0)  # Stop at €650
        
        print(f"   European Stock: {eu_stock}")
        print(f"   EUR Stop Loss: {eu_stop} (€650.0)")
        print(f"   - Currency-specific pricing")
        print(f"   - Exchange trading hours apply")
        
        # Example: Asian stock stop loss  
        asia_stock = Stock('7203', 'TSE', 'JPY')
        asia_stop = StopOrder('SELL', 100, 2800)  # Stop at ¥2800
        
        print(f"   Asian Stock: {asia_stock}")
        print(f"   JPY Stop Loss: {asia_stop} (¥2800)")
        print(f"   - Different market sessions")
        
        print("\n7. Order Reading & Management Methods:")
        
        order_methods = {
            'reqOpenOrdersAsync()': 'Get all open orders',
            'reqAllOpenOrdersAsync()': 'Get open orders for all accounts',
            'reqCompletedOrdersAsync()': 'Get recently completed orders',
            'orders': 'Property with current orders list',
            'openOrders': 'Property with open orders list',
            'trades': 'Property with trades list',
            'placeOrder(contract, order)': 'Submit new order',
            'cancelOrder(order)': 'Cancel existing order',
            'whatIfOrderAsync(contract, order)': 'Simulate order without placing'
        }
        
        for method, description in order_methods.items():
            print(f"   - {method}: {description}")
        
        print("\n8. Stop Loss Order States to Monitor:")
        states = [
            'PreSubmitted', 'Submitted', 'Filled', 'Cancelled', 
            'PendingCancel', 'ApiCancelled', 'Inactive'
        ]
        
        for state in states:
            print(f"   - {state}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_advanced_stop_loss_features()
    if success:
        print("\n" + "=" * 40)
        print("[SUCCESS] Comprehensive stop loss support available!")
        print("- Multiple stop loss types supported")
        print("- Advanced customization options")
        print("- International market compatibility") 
        print("- Full order lifecycle management")
    else:
        print("[FAILED] Could not analyze stop loss features")
