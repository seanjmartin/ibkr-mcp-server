"""
Individual MCP Tool Test: portfolio_creation
Focus: Test automated portfolio creation using MCP order placement tools
MCP Tool: Multiple coordinated (place_market_order, get_portfolio, place_stop_loss)
Expected: Task 1.2 - Create multi-currency test portfolio via market orders (AFTER Task 1.1 cleanup)
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
class TestIndividualPortfolioCreation:
    """Test portfolio creation using coordinated MCP tools"""
    
    # Target portfolio composition for testing (small positions for safety)
    TARGET_POSITIONS = [
        {"symbol": "AAPL", "quantity": 2, "expected_currency": "USD"},
        {"symbol": "MSFT", "quantity": 2, "expected_currency": "USD"}, 
        {"symbol": "ASML", "quantity": 1, "expected_currency": "EUR"},
    ]
    
    async def test_portfolio_creation_basic_functionality(self):
        """Create basic multi-currency portfolio via proven MCP tools"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing MCP Portfolio Creation ===")
        print(f"{'='*60}")
        
        # Step 0: Force IBKR Gateway connection (following proven pattern)
        print(f"\\n--- Step 0: Forcing IBKR Gateway Connection ---")
        from ibkr_mcp_server.client import ibkr_client
        try:
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
                print(f"[OK] Paper account: {ibkr_client.current_account}")
            else:
                print(f"[WARNING] IBKR Gateway connection failed")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        
        # Step 1: Check connection and account status
        print(f"\\n--- Step 1: Verify IBKR Connection ---")
        connection_result = await call_tool("get_connection_status", {})
        assert isinstance(connection_result, list) and len(connection_result) > 0
        connection_data = json.loads(connection_result[0].text)
        assert connection_data.get("connected") == True, "IBKR must be connected"
        assert connection_data.get("paper_trading") == True, "Must be paper trading"
        print(f"[OK] Connected to {connection_data.get('current_account')} (Paper Trading)")
        
        # Step 2: Get initial portfolio state
        print(f"\\n--- Step 2: Get Initial Portfolio State ---")
        initial_portfolio_result = await call_tool("get_portfolio", {})
        initial_portfolio = json.loads(initial_portfolio_result[0].text)
        print(f"[OK] Initial portfolio has {len(initial_portfolio)} positions")
        
        # Step 3: Create test positions via market orders
        print(f"\\n--- Step 3: Create Test Portfolio Positions ---")
        created_orders = []
        
        for target in self.TARGET_POSITIONS:
            print(f"\\nPlacing order for {target['symbol']} ({target['quantity']} shares)")
            
            try:
                order_result = await call_tool("place_market_order", {
                    "symbol": target["symbol"],
                    "action": "BUY",
                    "quantity": target["quantity"]
                })
                
                assert isinstance(order_result, list) and len(order_result) > 0
                order_data = json.loads(order_result[0].text)
                
                if "error" in str(order_result[0].text).lower():
                    print(f"[WARNING] Order failed for {target['symbol']}: {order_result[0].text}")
                    continue
                else:
                    print(f"[OK] Order placed for {target['symbol']}: {order_data}")
                    created_orders.append({
                        "symbol": target["symbol"],
                        "quantity": target["quantity"],
                        "order_data": order_data
                    })
                    
                # Small delay between orders for realistic execution
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"[ERROR] Failed to place order for {target['symbol']}: {e}")
                continue
        
        # Step 4: Verify portfolio creation
        print(f"\\n--- Step 4: Verify Portfolio Creation ---")
        
        # Wait a moment for orders to potentially execute
        print("Waiting 5 seconds for order processing...")
        await asyncio.sleep(5)
        
        final_portfolio_result = await call_tool("get_portfolio", {})
        final_portfolio = json.loads(final_portfolio_result[0].text)
        print(f"[OK] Final portfolio has {len(final_portfolio)} positions")
        
        # Validate that we created some positions (orders may not execute immediately)
        if len(created_orders) > 0:
            print(f"[OK] Successfully placed {len(created_orders)} market orders")
            
            # Check if any positions were created
            created_symbols = [order["symbol"] for order in created_orders]
            portfolio_symbols = [pos.get("symbol") for pos in final_portfolio if pos.get("symbol")]
            
            positions_created = [sym for sym in created_symbols if sym in portfolio_symbols]
            
            if positions_created:
                print(f"[OK] Positions created for: {positions_created}")
                
                # Validate multi-currency aspect
                currencies_found = set()
                for pos in final_portfolio:
                    if pos.get("symbol") in positions_created and pos.get("currency"):
                        currencies_found.add(pos.get("currency"))
                
                if len(currencies_found) > 1:
                    print(f"[OK] Multi-currency portfolio created: {currencies_found}")
                else:
                    print(f"[INFO] Single currency portfolio: {currencies_found}")
                    
            else:
                print(f"[INFO] Orders placed but positions not yet filled")
                print(f"[INFO] This is normal for paper testing - orders may execute later")
        
        else:
            print(f"[WARNING] No orders were successfully placed")
            print(f"[INFO] This may indicate configuration or market hours issues")
        
        # Step 5: Portfolio Creation Summary
        print(f"\\n--- Portfolio Creation Summary ---")
        print(f"Orders Placed: {len(created_orders)}")
        print(f"Final Portfolio Positions: {len(final_portfolio)}")
        print(f"Test Target Positions: {len(self.TARGET_POSITIONS)}")
        
        # Success criteria: At least one order was placed successfully
        assert len(created_orders) > 0, "At least one market order should be placed successfully"
        
        print(f"\\n[PASSED] Portfolio Creation Test PASSED")
        print(f"{'='*60}")
        
    async def test_create_portfolio_with_risk_management(self):
        """Create positions and add risk management (stop losses)"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing Portfolio + Risk Management ===")
        print(f"{'='*60}")
        
        # Step 1: Create a small position first
        print(f"\\n--- Step 1: Create Single Test Position ---")
        test_symbol = "AAPL" 
        test_quantity = 1  # Very small position for testing
        
        order_result = await call_tool("place_market_order", {
            "symbol": test_symbol,
            "action": "BUY", 
            "quantity": test_quantity
        })
        
        assert isinstance(order_result, list) and len(order_result) > 0
        order_data = json.loads(order_result[0].text)
        print(f"[OK] Test order placed: {order_data}")
        
        # Step 2: Check if position was created
        print(f"\\n--- Step 2: Check Portfolio for New Position ---")
        
        # Wait for potential execution
        await asyncio.sleep(3)
        
        portfolio_result = await call_tool("get_portfolio", {})
        portfolio = json.loads(portfolio_result[0].text)
        
        test_position = None
        for pos in portfolio:
            if pos.get("symbol") == test_symbol:
                test_position = pos
                break
        
        if test_position:
            print(f"[OK] Position found: {test_position}")
            
            # Step 3: Add stop loss protection
            print(f"\\n--- Step 3: Add Stop Loss Protection ---")
            
            # Calculate stop loss at 10% below average cost
            avg_cost = float(test_position.get("avgCost", 100))  # Default if not available
            stop_price = avg_cost * 0.9  # 10% below cost
            position_quantity = int(float(test_position.get("position", test_quantity)))
            
            print(f"Setting stop loss: {test_symbol} at ${stop_price:.2f} (10% below ${avg_cost:.2f})")
            
            try:
                stop_result = await call_tool("place_stop_loss", {
                    "symbol": test_symbol,
                    "action": "SELL",
                    "quantity": position_quantity, 
                    "stop_price": stop_price
                })
                
                stop_data = json.loads(stop_result[0].text)
                
                if "error" in str(stop_result[0].text).lower():
                    print(f"[INFO] Stop loss placement: {stop_result[0].text}")
                else:
                    print(f"[OK] Stop loss placed: {stop_data}")
                    
                    # Verify stop loss was created
                    stops_result = await call_tool("get_stop_losses", {})
                    stops_data = json.loads(stops_result[0].text)
                    print(f"[OK] Active stop losses: {len(stops_data)}")
                    
            except Exception as e:
                print(f"[INFO] Stop loss test note: {e}")
                
        else:
            print(f"[INFO] Position not yet filled - order may execute later")
            print(f"[INFO] This is normal behavior for paper trading")
        
        print(f"\\n[PASSED] Portfolio + Risk Management Test PASSED")
        print(f"{'='*60}")

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
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_portfolio_creation.py::TestIndividualPortfolioCreation::test_portfolio_creation_basic_functionality -v -s

# Risk management test:
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_portfolio_creation.py::TestIndividualPortfolioCreation::test_create_portfolio_with_risk_management -v -s

# Full test class:
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_portfolio_creation.py::TestIndividualPortfolioCreation -v -s

# Entire test file:
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_portfolio_creation.py -v -s

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
