#!/usr/bin/env python3

# Test new forex functionality directly via client
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ibkr_mcp_server.client import ibkr_client

async def test_new_features():
    """Test the new forex, international, and stop loss features"""
    print("Testing enhanced IBKR MCP Server features...")
    
    try:
        # Test connection
        connected = await ibkr_client.connect()
        if not connected:
            print("ERROR: Could not connect to IBKR")
            return
            
        print("SUCCESS: Connected to IBKR")
        
        # Test forex rates
        print("\n=== Testing Forex Rates ===")
        try:
            rates = await ibkr_client.get_forex_rates("EURUSD,GBPUSD")
            print(f"SUCCESS: Retrieved {len(rates)} forex rates")
            for rate in rates:
                print(f"  {rate.get('pair', 'Unknown')}: {rate.get('last', 'N/A')}")
        except Exception as e:
            print(f"Forex rates error: {e}")
        
        # Test currency conversion
        print("\n=== Testing Currency Conversion ===")
        try:
            result = await ibkr_client.convert_currency(1000.0, "USD", "EUR")
            print(f"SUCCESS: $1000 USD = {result.get('converted_amount', 'N/A')} EUR")
            print(f"  Rate: {result.get('exchange_rate', 'N/A')}")
        except Exception as e:
            print(f"Currency conversion error: {e}")
        
        # Test international market data
        print("\n=== Testing International Market Data ===")
        try:
            data = await ibkr_client.get_international_market_data("ASML,AAPL")
            print(f"SUCCESS: Retrieved {len(data)} international quotes")
            for item in data:
                print(f"  {item.get('symbol', 'Unknown')} ({item.get('exchange', 'N/A')}/{item.get('currency', 'N/A')}): {item.get('last', 'N/A')}")
        except Exception as e:
            print(f"International market data error: {e}")
        
        # Test symbol resolution
        print("\n=== Testing Symbol Resolution ===")
        try:
            result = await ibkr_client.resolve_international_symbol("SAP")
            print(f"SUCCESS: Resolved SAP - {result}")
        except Exception as e:
            print(f"Symbol resolution error: {e}")
        
        # Test stop loss (should be protected by safety)
        print("\n=== Testing Stop Loss (Safety Protected) ===")
        try:
            result = await ibkr_client.place_stop_loss(
                symbol="AAPL", quantity=100, stop_price=150.0
            )
            print(f"Stop loss result: {result}")
        except Exception as e:
            print(f"EXPECTED: Stop loss protected by safety - {e}")
        
        print("\n=== All Tests Complete ===")
        
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        try:
            await ibkr_client.disconnect()
            print("Disconnected from IBKR")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_new_features())
