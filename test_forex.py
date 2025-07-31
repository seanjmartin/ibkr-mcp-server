#!/usr/bin/env python3
"""Test forex functionality"""

import sys
import asyncio
from pathlib import Path

# Add the package path
sys.path.insert(0, str(Path(__file__).parent))

from ibkr_mcp_server.client import IBKRClient

async def test_forex():
    """Test forex functionality"""
    client = IBKRClient()
    
    print("Testing forex functionality...")
    
    try:
        # Connect first
        connected = await client.connect()
        if not connected:
            print("ERROR: Connection failed")
            return
        
        print("SUCCESS: Connection successful")
        
        # Test forex rates
        print("Testing forex rates...")
        rates = await client.get_forex_rates("EURUSD")
        print(f"SUCCESS: Forex rates retrieved: {len(rates)} pairs")
        if rates:
            rate = rates[0]
            print(f"  EURUSD: Last={rate.get('last')}, Bid={rate.get('bid')}, Ask={rate.get('ask')}")
        
        # Test currency conversion
        print("Testing currency conversion...")
        conversion = await client.convert_currency(1000.0, "USD", "EUR")
        print(f"SUCCESS: Conversion successful: $1000 = EUR {conversion.get('converted_amount', 'N/A')}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if client._connected:
            await client.disconnect()
            
    print("Forex test complete.")

if __name__ == "__main__":
    asyncio.run(test_forex())
