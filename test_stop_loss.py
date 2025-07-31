#!/usr/bin/env python3
"""Test stop loss management functionality"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ibkr_mcp_server.client import IBKRClient
    
    async def test_stop_loss():
        print("Starting stop loss management test...")
        client = IBKRClient()
        try:
            print("Connecting to IBKR...")
            connected = await client.connect()
            if connected:
                print('Connected successfully')
                
                # Test 1: Get existing stop losses
                print("\n=== Testing Get Stop Losses ===")
                try:
                    result = await client.get_stop_losses()
                    print(f'Current stop losses: {len(result)} found')
                    for stop in result:
                        print(f"  Order {stop.get('order_id', 'N/A')}: {stop.get('symbol', 'N/A')} {stop.get('action', 'N/A')} {stop.get('quantity', 'N/A')} @ {stop.get('stop_price', 'N/A')}")
                except Exception as e:
                    print(f'Get stop losses error: {e}')
                
                # Test 2: Test stop loss validation (should fail safely)
                print("\n=== Testing Stop Loss Validation ===")
                try:
                    # This should fail validation - testing safety framework
                    await client.place_stop_loss(
                        symbol="AAPL",
                        action="SELL", 
                        quantity=100,
                        stop_price=150.0,
                        order_type="STP"
                    )
                    print("Stop loss placement succeeded (unexpected in paper trading)")
                except Exception as e:
                    print(f'Stop loss validation working: {e}')
                
                # Test 3: Test stop loss manager capabilities (framework test)
                print("\n=== Testing Stop Loss Manager Framework ===")
                try:
                    if hasattr(client, 'stop_loss_manager') and client.stop_loss_manager:
                        print("Stop loss manager initialized successfully")
                        
                        # Test validation methods
                        from ibkr_mcp_server.utils import safe_float
                        print(f"Safe float test: {safe_float('150.0')} = {safe_float('150.0')}")
                        
                        # Test if manager has expected methods
                        methods = ['place_stop_loss', 'get_active_stops', 'modify_stop_loss', 'cancel_stop_loss']
                        for method in methods:
                            has_method = hasattr(client.stop_loss_manager, method)
                            print(f"  {method}: {'✅' if has_method else '❌'}")
                    else:
                        print("Stop loss manager not initialized")
                except Exception as e:
                    print(f'Manager framework error: {e}')
                
                # Test 4: Test modify/cancel operations (on non-existent orders)
                print("\n=== Testing Modify/Cancel Operations ===")
                try:
                    # Test modify (should handle non-existent order gracefully)
                    result = await client.modify_stop_loss(order_id=999999, new_stop_price=160.0)
                    print(f'Modify result: {result}')
                except Exception as e:
                    print(f'Modify operation error (expected): {e}')
                
                try:
                    # Test cancel (should handle non-existent order gracefully)
                    result = await client.cancel_stop_loss(order_id=999999)
                    print(f'Cancel result: {result}')
                except Exception as e:
                    print(f'Cancel operation error (expected): {e}')
                    
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
        
        print("Stop loss management test completed.")
    
    if __name__ == '__main__':
        asyncio.run(test_stop_loss())
        
except Exception as e:
    print(f'Import error: {e}')
    import traceback
    traceback.print_exc()
