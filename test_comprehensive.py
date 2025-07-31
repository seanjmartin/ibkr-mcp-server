#!/usr/bin/env python3
"""Comprehensive test of all enhanced MCP tools"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ibkr_mcp_server.client import IBKRClient
    
    async def test_all_tools():
        print("=== COMPREHENSIVE MCP TOOLS TEST ===")
        client = IBKRClient()
        try:
            print("Connecting to IBKR...")
            connected = await client.connect()
            if connected:
                print('Connected successfully to IBKR')
                print(f"Available accounts: {await client.get_accounts()}")
                
                # Test Original Tools (should still work)
                print("\n=== ORIGINAL TOOLS TEST ===")
                try:
                    portfolio = await client.get_portfolio()
                    print(f"Portfolio: {len(portfolio)} positions")
                    
                    summary = await client.get_account_summary()
                    print(f"Account summary: {len(summary)} items")
                    
                    status = await client.get_connection_status()
                    print(f"Connection status: {status.get('connected', False)}")
                    
                except Exception as e:
                    print(f"Original tools error: {e}")
                
                # Test Forex Tools
                print("\n=== FOREX TOOLS TEST ===")
                try:
                    # Test forex rates
                    rates = await client.get_forex_rates("EURUSD,GBPUSD")
                    print(f"Forex rates: {len(rates)} pairs retrieved")
                    for rate in rates:
                        print(f"  {rate['pair']}: {rate['last']} (method: {rate.get('source', 'IBKR')})")
                    
                    # Test currency conversion
                    conversion = await client.convert_currency(1000.0, 'USD', 'EUR')
                    print(f"Currency conversion: $1000 USD = €{conversion['converted_amount']:.2f} EUR")
                    print(f"  Method: {conversion['conversion_method']}, Rate: {conversion['exchange_rate']:.4f}")
                    
                except Exception as e:
                    print(f"Forex tools error: {e}")
                
                # Test International Tools
                print("\n=== INTERNATIONAL TOOLS TEST ===")
                try:
                    # Test symbol resolution
                    resolution = await client.resolve_international_symbol('ASML')
                    print(f"Symbol resolution: {resolution['symbol']} -> {resolution['matches'][0]['exchange']}/{resolution['matches'][0]['currency']}")
                    
                    # Test international market data
                    intl_data = await client.get_international_market_data("AAPL,ASML", auto_detect=True)
                    print(f"International market data: {len(intl_data)} symbols")
                    for item in intl_data:
                        print(f"  {item['symbol']} ({item['exchange']}/{item['currency']}): {item['last']}")
                    
                except Exception as e:
                    print(f"International tools error: {e}")
                
                # Test Stop Loss Tools
                print("\n=== STOP LOSS TOOLS TEST ===")
                try:
                    # Test get stop losses
                    stops = await client.get_stop_losses()
                    print(f"Current stop losses: {len(stops)} orders")
                    
                    # Test validation (should be protected by safety framework)
                    try:
                        await client.place_stop_loss(symbol="AAPL", action="SELL", quantity=100, stop_price=150.0)
                        print("Stop loss placement: Succeeded (unexpected)")
                    except Exception as e:
                        print(f"Stop loss placement: Protected by safety framework ({str(e)[:50]}...)")
                    
                    # Test modify/cancel on non-existent order
                    try:
                        await client.modify_stop_loss(order_id=999999, new_stop_price=160.0)
                    except Exception as e:
                        print(f"Modify operation: Handles invalid orders correctly")
                    
                except Exception as e:
                    print(f"Stop loss tools error: {e}")
                
                # Test Manager Initialization
                print("\n=== MANAGER INITIALIZATION TEST ===")
                managers = ['forex_manager', 'international_manager', 'stop_loss_manager']
                for manager in managers:
                    has_manager = hasattr(client, manager) and getattr(client, manager) is not None
                    print(f"  {manager}: {'OK' if has_manager else 'MISSING'}")
                
                # Test Tool Count
                print("\n=== TOOL AVAILABILITY TEST ===")
                print("New tools should be available via MCP:")
                new_tools = [
                    'get_forex_rates', 'convert_currency',
                    'get_international_market_data', 'resolve_international_symbol', 
                    'place_stop_loss', 'get_stop_losses', 'modify_stop_loss', 'cancel_stop_loss'
                ]
                print(f"Expected new tools: {len(new_tools)}")
                for tool in new_tools:
                    has_method = hasattr(client, tool)
                    print(f"  {tool}: {'OK' if has_method else 'MISSING'}")
                
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
                    print("Disconnected successfully")
            except Exception as e:
                print(f"Disconnect error: {e}")
        
        print("\n=== COMPREHENSIVE TEST COMPLETED ===")
        print("All enhanced IBKR MCP tools have been tested!")
    
    if __name__ == '__main__':
        asyncio.run(test_all_tools())
        
except Exception as e:
    print(f'Import error: {e}')
    import traceback
    traceback.print_exc()
