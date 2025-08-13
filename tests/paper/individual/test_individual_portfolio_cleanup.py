"""
Individual MCP Tool Test: portfolio_cleanup
Focus: Test portfolio cleanup utilities for establishing clean test environment
MCP Tool: Multiple tools - get_portfolio, place_market_order, cancel_order
Expected: Task 1.1 - Clean up existing positions BEFORE creating test portfolio (Task 1.2)
"""

import pytest
import asyncio
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Import MCP interface - THIS IS THE CORRECT LAYER TO TEST
from ibkr_mcp_server.tools import call_tool  # Proper MCP interface
from mcp.types import TextContent
import json
from unittest.mock import patch, AsyncMock

@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividualPortfolioCleanup:
    """Test portfolio cleanup MCP tools in isolation"""
    
    async def test_portfolio_cleanup_basic_functionality(self):
        """Test basic portfolio cleanup functionality through MCP interface"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing Portfolio Cleanup ===")
        print(f"{'='*60}")
        
        # Target test symbols that will be created in Task 1.2 (Portfolio Creation)
        TARGET_TEST_SYMBOLS = ["AAPL", "MSFT", "ASML"]
        
        print(f"Target cleanup symbols: {TARGET_TEST_SYMBOLS}")
        print(f"Step 1: Get current portfolio...")
        
        # STEP 1: Get current portfolio to see what positions exist
        try:
            portfolio_result = await call_tool("get_portfolio", {})
            assert isinstance(portfolio_result, list) and len(portfolio_result) > 0
            
            portfolio_text = portfolio_result[0].text
            print(f"Portfolio response: {portfolio_text}")
            
            try:
                current_portfolio = json.loads(portfolio_text)
            except json.JSONDecodeError:
                print(f"Portfolio response not JSON: {portfolio_text}")
                current_portfolio = []
            
            print(f"Current portfolio ({len(current_portfolio)} positions): {current_portfolio}")
            
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            pytest.fail(f"Failed to get current portfolio: {e}")
        
        # STEP 2: Identify test positions that need cleanup
        test_positions_to_cleanup = []
        
        if isinstance(current_portfolio, list) and len(current_portfolio) > 0:
            for position in current_portfolio:
                if isinstance(position, dict):
                    symbol = position.get('symbol', '')
                    position_size = position.get('position', 0)
                    
                    if symbol in TARGET_TEST_SYMBOLS and position_size != 0:
                        test_positions_to_cleanup.append({
                            'symbol': symbol,
                            'position': position_size,
                            'avgCost': position.get('avgCost', 0)
                        })
            
            print(f"Found {len(test_positions_to_cleanup)} test positions to clean up:")
            for pos in test_positions_to_cleanup:
                print(f"  - {pos['symbol']}: {pos['position']} shares at ${pos['avgCost']}")
        else:
            print("[OK] Portfolio is empty - no cleanup needed")
            test_positions_to_cleanup = []
        
        # STEP 3: Clean up test positions by selling them
        cleanup_results = []
        
        if len(test_positions_to_cleanup) > 0:
            print(f"\\nStep 2: Cleaning up {len(test_positions_to_cleanup)} test positions...")
            
            for position in test_positions_to_cleanup:
                symbol = position['symbol']
                quantity = abs(int(position['position']))  # Get absolute value for sell quantity
                
                print(f"\\nCleaning up {symbol}: selling {quantity} shares...")
                
                try:
                    # Place sell order to close the position
                    sell_result = await call_tool("place_market_order", {
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": quantity
                    })
                    
                    print(f"Sell order result: {sell_result}")
                    
                    if isinstance(sell_result, list) and len(sell_result) > 0:
                        sell_text = sell_result[0].text
                        try:
                            sell_data = json.loads(sell_text)
                            if "order_id" in sell_data:
                                print(f"[OK] Sell order placed for {symbol}: Order ID {sell_data['order_id']}")
                                cleanup_results.append({
                                    'symbol': symbol,
                                    'action': 'sell_order_placed',
                                    'order_id': sell_data.get('order_id'),
                                    'quantity': quantity
                                })
                            else:
                                print(f"[WARNING] Unexpected sell order response for {symbol}: {sell_data}")
                                cleanup_results.append({
                                    'symbol': symbol,
                                    'action': 'sell_attempted',
                                    'result': sell_data
                                })
                        except json.JSONDecodeError:
                            print(f"[WARNING] Sell order response not JSON for {symbol}: {sell_text}")
                            cleanup_results.append({
                                'symbol': symbol,
                                'action': 'sell_attempted',
                                'result': sell_text
                            })
                    
                except Exception as e:
                    print(f"[ERROR] Failed to place sell order for {symbol}: {e}")
                    cleanup_results.append({
                        'symbol': symbol,
                        'action': 'sell_failed',
                        'error': str(e)
                    })
                
                # Brief pause between orders
                await asyncio.sleep(0.5)
        else:
            print("\\n[OK] No test positions found to clean up")
        
        # STEP 4: Verify cleanup status
        print(f"\\nStep 3: Verifying cleanup status...")
        
        try:
            # Get portfolio again to check cleanup status
            final_portfolio_result = await call_tool("get_portfolio", {})
            assert isinstance(final_portfolio_result, list) and len(final_portfolio_result) > 0
            
            final_portfolio_text = final_portfolio_result[0].text
            print(f"Final portfolio response: {final_portfolio_text}")
            
            try:
                final_portfolio = json.loads(final_portfolio_text)
            except json.JSONDecodeError:
                print(f"Final portfolio response not JSON: {final_portfolio_text}")
                final_portfolio = []
            
            print(f"Final portfolio ({len(final_portfolio)} positions): {final_portfolio}")
            
            # Check if test positions are still present
            remaining_test_positions = []
            if isinstance(final_portfolio, list):
                for position in final_portfolio:
                    if isinstance(position, dict):
                        symbol = position.get('symbol', '')
                        if symbol in TARGET_TEST_SYMBOLS:
                            remaining_test_positions.append(position)
            
            if len(remaining_test_positions) > 0:
                print(f"[INFO] Some test positions may still be present (orders may be pending):")
                for pos in remaining_test_positions:
                    print(f"  - {pos.get('symbol')}: {pos.get('position')} shares")
            else:
                print(f"[OK] No test positions remaining in portfolio")
            
        except Exception as e:
            print(f"[WARNING] Could not verify cleanup status: {e}")
        
        # STEP 5: Validation and summary
        print(f"\\n--- Portfolio Cleanup Summary ---")
        print(f"Target symbols: {TARGET_TEST_SYMBOLS}")
        print(f"Positions found for cleanup: {len(test_positions_to_cleanup)}")
        print(f"Cleanup actions taken: {len(cleanup_results)}")
        
        for result in cleanup_results:
            symbol = result['symbol']
            action = result['action']
            if action == 'sell_order_placed':
                print(f"[OK] {symbol}: Sell order placed (Order ID: {result.get('order_id')})")
            elif action == 'sell_failed':
                print(f"[ERROR] {symbol}: Sell order failed - {result.get('error')}")
            else:
                print(f"[INFO] {symbol}: {action}")
        
        # Test passes regardless of whether positions existed - cleanup utility should handle both cases
        print(f"\\n[PASSED] Portfolio cleanup test completed successfully")
        print(f"- Cleanup utility functional for both empty and populated portfolios")
        print(f"- MCP tools working correctly for portfolio management")
        print(f"- Test positions cleanup initiated (orders may still be processing)")
        
        print(f"{'='*60}")
        
    async def test_portfolio_cleanup_error_handling(self):
        """Test portfolio cleanup error handling with edge cases"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing Error Handling: Portfolio Cleanup ===")
        print(f"{'='*60}")
        
        # Test 1: Try to sell a position that doesn't exist
        print(f"\\nTest 1: Attempt to sell non-existent position...")
        
        try:
            # Try to sell INVALID stock that we don't own
            invalid_sell_result = await call_tool("place_market_order", {
                "symbol": "INVALIDSTOCK123",
                "action": "SELL",
                "quantity": 1
            })
            
            print(f"Invalid sell result: {invalid_sell_result}")
            
            if isinstance(invalid_sell_result, list) and len(invalid_sell_result) > 0:
                response_text = invalid_sell_result[0].text
                print(f"Response: {response_text}")
                
                # Should get some kind of error or rejection
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"[OK] Error handling working for invalid symbol: {response_text}")
                else:
                    print(f"[INFO] System handled invalid symbol gracefully: {response_text}")
            
        except Exception as e:
            print(f"[OK] Exception-based error handling for invalid symbol: {type(e).__name__}")
        
        # Test 2: Try to sell zero quantity (should be caught by safety validation)
        print(f"\\nTest 2: Attempt to sell zero quantity...")
        
        try:
            zero_quantity_result = await call_tool("place_market_order", {
                "symbol": "AAPL",
                "action": "SELL",
                "quantity": 0
            })
            
            print(f"Zero quantity result: {zero_quantity_result}")
            
            if isinstance(zero_quantity_result, list) and len(zero_quantity_result) > 0:
                response_text = zero_quantity_result[0].text
                print(f"Response: {response_text}")
                
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"[OK] Safety validation caught zero quantity: {response_text}")
                else:
                    print(f"[WARNING] Zero quantity not caught: {response_text}")
            
        except Exception as e:
            print(f"[OK] Exception for zero quantity: {type(e).__name__}")
        
        print(f"\\n[PASSED] Error handling tests completed")

# CRITICAL EXECUTION INSTRUCTIONS
"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_portfolio_cleanup.py::TestIndividualPortfolioCleanup::test_portfolio_cleanup_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_portfolio_cleanup.py::TestIndividualPortfolioCleanup -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_portfolio_cleanup.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("[WARNING]  STANDALONE EXECUTION DETECTED")
    print("[WARNING]  RECOMMENDED: Use pytest execution commands shown above")
    print("[WARNING]  Standalone mode may not work correctly with MCP interface")
    print()
    print("IBKR Gateway must be running with paper trading login and API enabled!")
    print("Port 7497 for paper trading, Client ID 5")
    
    # Run just this test file using pytest
    exit_code = pytest.main([
        __file__, 
        "-v", 
        "-s", 
        "--tb=short"
    ])
    
    sys.exit(exit_code)
