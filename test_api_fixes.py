#!/usr/bin/env python3
"""
Test script for IBKR MCP server API fixes
"""
import asyncio
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from ibkr_mcp_server.client import ibkr_client

async def test_connection():
    """Test basic connection"""
    try:
        print("Testing connection...")
        connected = await ibkr_client._ensure_connected()
        print(f"Connection status: {connected}")
        
        if connected:
            print(f"Account: {ibkr_client.current_account}")
            print(f"Connected to: {ibkr_client.host}:{ibkr_client.port}")
        
        return connected
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

async def test_account_summary():
    """Test fixed account summary API"""
    try:
        print("\nTesting account summary...")
        summary = await ibkr_client.get_account_summary()
        print(f"Got {len(summary)} account values")
        for item in summary[:3]:  # Show first 3
            print(f"  - {item}")
        return True
    except Exception as e:
        print(f"Account summary failed: {e}")
        return False

async def test_portfolio():
    """Test portfolio retrieval"""
    try:
        print("\nTesting portfolio...")
        positions = await ibkr_client.get_portfolio()
        print(f"Got {len(positions)} positions")
        if positions:
            print(f"  - Sample: {positions[0]}")
        return True
    except Exception as e:
        print(f"Portfolio failed: {e}")
        return False

async def test_market_data():
    """Test new market data method"""
    try:
        print("\nTesting market data...")
        quotes = await ibkr_client.get_market_data("AAPL,TSLA")
        print(f"Got {len(quotes)} quotes")
        for quote in quotes:
            print(f"  - {quote}")
        return True
    except Exception as e:
        print(f"Market data failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("IBKR MCP Server API Fix Test")
    print("=" * 40)
    
    success_count = 0
    total_tests = 4
    
    # Test connection first
    if await test_connection():
        success_count += 1
        
        # Only run other tests if connected
        if await test_account_summary():
            success_count += 1
            
        if await test_portfolio():
            success_count += 1
            
        if await test_market_data():
            success_count += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("All tests passed! API fixes successful.")
    else:
        print("Some tests failed. Check IB Gateway connection.")

if __name__ == "__main__":
    asyncio.run(main())
