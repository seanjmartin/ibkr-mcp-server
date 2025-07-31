#!/usr/bin/env python3
"""
Check available order types in current ib-async version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def check_available_order_types():
    """Check what order types are available in current ib-async"""
    
    print("Available Order Types in ib-async")
    print("=" * 40)
    
    try:
        import ib_async
        print(f"ib-async version: {ib_async.__version__}")
        
        # Try importing various order types
        order_types = []
        
        try:
            from ib_async import MarketOrder
            order_types.append(("MarketOrder", MarketOrder))
        except ImportError:
            pass
            
        try:
            from ib_async import LimitOrder
            order_types.append(("LimitOrder", LimitOrder))
        except ImportError:
            pass
            
        try:
            from ib_async import StopOrder
            order_types.append(("StopOrder", StopOrder))
        except ImportError:
            pass
            
        try:
            from ib_async import StopLimitOrder  
            order_types.append(("StopLimitOrder", StopLimitOrder))
        except ImportError:
            pass
            
        try:
            from ib_async import Order
            order_types.append(("Order", Order))
        except ImportError:
            pass
            
        try:
            from ib_async import BracketOrder
            order_types.append(("BracketOrder", BracketOrder))
        except ImportError:
            pass
        
        print(f"\nAvailable order types ({len(order_types)}):")
        for name, cls in order_types:
            print(f"  - {name}: {cls}")
        
        # Test creating basic stop orders
        print("\nTesting Stop Order Creation:")
        
        if any(name == "StopOrder" for name, _ in order_types):
            stop = StopOrder('SELL', 100, 95.0)
            print(f"  Stop Order: {stop}")
            print(f"  Attributes: action={stop.action}, qty={stop.totalQuantity}, stop=${stop.auxPrice}")
        
        if any(name == "StopLimitOrder" for name, _ in order_types):  
            stop_limit = StopLimitOrder('SELL', 100, 95.0, 94.5)
            print(f"  Stop Limit: {stop_limit}")
            print(f"  Stop=${stop_limit.auxPrice}, Limit=${stop_limit.lmtPrice}")
        
        if any(name == "Order" for name, _ in order_types):
            # Create manual stop order
            manual_stop = Order()
            manual_stop.action = 'SELL'
            manual_stop.totalQuantity = 100
            manual_stop.orderType = 'STP'
            manual_stop.auxPrice = 95.0
            manual_stop.tif = 'GTC'
            print(f"  Manual Stop: {manual_stop.orderType} order, stop=${manual_stop.auxPrice}")
        
        # Check what methods IB class has for order management
        print("\nIB Class Order Management Methods:")
        from ib_async import IB
        ib = IB()
        
        order_methods = [method for method in dir(ib) if 'order' in method.lower()]
        for method in sorted(order_methods):
            print(f"  - {method}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_available_order_types()
