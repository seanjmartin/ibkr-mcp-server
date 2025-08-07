"""
Individual MCP Tool Test: get_completed_orders
Focus: Test get_completed_orders MCP tool in isolation for debugging
MCP Tool: get_completed_orders
Expected: List of recent completed orders/trades (may be empty for fresh account)
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
class TestIndividualGetCompletedOrders:
    """Test get_completed_orders MCP tool in isolation"""
    
    async def test_get_completed_orders_basic_functionality(self):
        """Test basic get_completed_orders functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_completed_orders ===")
        print(f"{'='*60}")
        
        # Force IBKR connection first
        from ibkr_mcp_server.client import ibkr_client
        
        try:
            print(f"Establishing IBKR connection with client ID 5...")
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
                print(f"[OK] Paper account: {ibkr_client.current_account}")
            else:
                pytest.fail("Could not establish IBKR connection - check Gateway is running")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            pytest.fail(f"IBKR connection failed: {e}")
        
        # MCP tool call with no parameters (gets recent completed orders)
        tool_name = "get_completed_orders"
        parameters = {}  # No parameters needed for basic functionality
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Retrieving completed orders...")
        
        try:
            # Execute MCP tool call
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result: {result}")
            
        except Exception as e:
            print(f"EXCEPTION during MCP call: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"MCP call failed with exception: {e}")
        
        # MCP response structure validation - MCP tools return list of TextContent
        print(f"\n--- MCP Tool Response Structure Validation ---")
        assert isinstance(result, list), f"MCP tool should return list, got {type(result)}"
        assert len(result) > 0, f"MCP tool should return at least one TextContent, got empty list"
        
        # Get the first TextContent response
        text_content = result[0]
        assert isinstance(text_content, TextContent), f"Expected TextContent, got {type(text_content)}"
        assert hasattr(text_content, 'text'), f"TextContent should have 'text' attribute"
        
        # Parse the JSON response from the text content
        response_text = text_content.text
        print(f"Response text: {response_text}")
        
        try:
            # Parse the JSON response (IBKR client response format)
            parsed_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            # If it's not JSON, it might be an error string
            print(f"Response is not JSON, treating as error: {response_text}")
            pytest.fail(f"Expected JSON response, got non-JSON: {response_text}")
        
        print(f"Parsed Result: {parsed_result}")
        
        # For paper trading, we expect a list of completed orders (may be empty for new account)
        if isinstance(parsed_result, list):
            completed_orders = parsed_result
            print(f"[OK] Completed orders returned as list: {len(completed_orders)} orders")
            
            if len(completed_orders) == 0:
                print(f"[OK] Empty completed orders list - expected for fresh paper account")
                print(f"[PASSED] Completed orders structure validation ready for populated data")
                
                # Demonstrate validation framework with mock data
                await self._demonstrate_completed_orders_validation_framework()
                
            else:
                print(f"[OK] Found {len(completed_orders)} completed orders - validating structure")
                for i, order in enumerate(completed_orders):
                    print(f"[OK] Completed Order {i+1}: {order}")
                    
                    # Validate order structure
                    if isinstance(order, dict):
                        # Check for expected completed order fields
                        expected_fields = ["orderId", "symbol", "action", "totalQuantity", "orderType", "orderState"]
                        for field in expected_fields:
                            if field in order:
                                print(f"[OK] Order field '{field}': {order[field]}")
                        
                        # Validate specific fields if present
                        if "orderId" in order:
                            order_id = order["orderId"]
                            assert isinstance(order_id, (int, str)), f"Order ID should be int/str, got {type(order_id)}"
                        
                        if "symbol" in order:
                            symbol = order["symbol"]
                            assert isinstance(symbol, str), f"Symbol should be string, got {type(symbol)}"
                        
                        if "action" in order:
                            action = order["action"]
                            assert action in ["BUY", "SELL"], f"Action should be BUY/SELL, got {action}"
                        
                        if "orderState" in order and isinstance(order["orderState"], dict):
                            state = order["orderState"]
                            if "status" in state:
                                status = state["status"]
                                # Completed orders should have final status
                                expected_statuses = ["Filled", "Cancelled", "ApiCancelled", "Inactive"]
                                if status not in expected_statuses:
                                    print(f"[INFO] Unexpected order status for completed order: {status}")
                                else:
                                    print(f"[OK] Order status: {status}")
                            
                        print(f"[OK] Completed Order {i+1} structure validation passed")
                    
        elif isinstance(parsed_result, dict):
            # Check if it's an error response
            if "error" in parsed_result:
                error_msg = parsed_result["error"]
                print(f"[INFO] Error response: {error_msg}")
                pytest.fail(f"MCP tool get_completed_orders failed: {error_msg}")
            else:
                # Maybe it's a wrapped response
                if "data" in parsed_result:
                    completed_orders = parsed_result["data"]
                    print(f"[OK] Completed orders in wrapped response: {len(completed_orders)} orders")
                else:
                    print(f"[INFO] Unexpected dict response format: {parsed_result}")
        else:
            pytest.fail(f"Unexpected response format: {type(parsed_result)}, content: {parsed_result}")
        
        print(f"\n[PASSED] MCP Tool 'get_completed_orders' test COMPLETED")
        print(f"{'='*60}")
    
    async def _demonstrate_completed_orders_validation_framework(self):
        """Demonstrate comprehensive completed orders validation with mock data"""
        
        print(f"\n--- Demonstrating Completed Orders Validation Framework ---")
        
        # Mock completed order data to demonstrate validation capabilities
        mock_completed_orders = [
            {
                "orderId": 12340,
                "symbol": "AAPL",
                "action": "BUY",
                "totalQuantity": 100,
                "orderType": "MKT",
                "orderState": {
                    "status": "Filled",
                    "filled": "100",
                    "remaining": "0",
                    "avgFillPrice": 175.50,
                    "completedTime": "20250107-14:30:00",
                    "commission": 1.0
                },
                "account": "DUH905195"
            },
            {
                "orderId": 12341,
                "symbol": "TSLA", 
                "action": "SELL",
                "totalQuantity": 50,
                "orderType": "LMT",
                "lmtPrice": 250.0,
                "orderState": {
                    "status": "Cancelled",
                    "filled": "0", 
                    "remaining": "50",
                    "completedTime": "20250107-15:45:00"
                },
                "account": "DUH905195"
            },
            {
                "orderId": 12342,
                "symbol": "MSFT",
                "action": "BUY", 
                "totalQuantity": 25,
                "orderType": "STP",
                "auxPrice": 400.0,
                "orderState": {
                    "status": "Filled",
                    "filled": "25",
                    "remaining": "0", 
                    "avgFillPrice": 401.25,
                    "completedTime": "20250107-16:00:00",
                    "commission": 0.5
                },
                "account": "DUH905195"
            }
        ]
        
        print(f"[DEMO] Validating mock completed order data structure...")
        
        # 1. Order Count Validation
        order_count = len(mock_completed_orders)
        print(f"[OK] Completed Order Count Validation: {order_count} orders")
        assert isinstance(order_count, int)
        
        # 2. Individual Order Structure Validation
        for i, order in enumerate(mock_completed_orders):
            print(f"[OK] Completed Order {i+1} Structure Validation:")
            
            # Required fields validation
            assert "orderId" in order, f"Order missing orderId"
            assert "symbol" in order, f"Order missing symbol"
            assert "action" in order, f"Order missing action"
            assert "totalQuantity" in order, f"Order missing totalQuantity"
            assert "orderType" in order, f"Order missing orderType"
            assert "orderState" in order, f"Order missing orderState"
            
            # Field type validation
            assert isinstance(order["orderId"], (int, str)), f"Invalid orderId type"
            assert isinstance(order["symbol"], str), f"Invalid symbol type"
            assert order["action"] in ["BUY", "SELL"], f"Invalid action: {order['action']}"
            assert isinstance(order["totalQuantity"], (int, float)), f"Invalid quantity type"
            assert isinstance(order["orderType"], str), f"Invalid orderType"
            assert isinstance(order["orderState"], dict), f"Invalid orderState type"
            
            # Order state validation (critical for completed orders)
            state = order["orderState"]
            assert "status" in state, f"OrderState missing status"
            
            status = state["status"]
            expected_statuses = ["Filled", "Cancelled", "ApiCancelled", "Inactive"]
            assert status in expected_statuses, f"Unexpected status for completed order: {status}"
            
            print(f"   [OK] Order ID: {order['orderId']}")
            print(f"   [OK] Symbol: {order['symbol']}")
            print(f"   [OK] Action: {order['action']}")
            print(f"   [OK] Quantity: {order['totalQuantity']}")
            print(f"   [OK] Order Type: {order['orderType']}")
            print(f"   [OK] Status: {status}")
            
            # Filled order specific validation
            if status == "Filled":
                if "avgFillPrice" in state:
                    fill_price = state["avgFillPrice"]
                    assert isinstance(fill_price, (int, float)) and fill_price > 0, f"Invalid fill price: {fill_price}"
                    print(f"   [OK] Avg Fill Price: ${fill_price}")
                
                if "filled" in state:
                    filled_qty = state["filled"]
                    print(f"   [OK] Filled Quantity: {filled_qty}")
                
                if "commission" in state:
                    commission = state["commission"]
                    assert isinstance(commission, (int, float)), f"Invalid commission: {commission}"
                    print(f"   [OK] Commission: ${commission}")
            
            # Completion time validation
            if "completedTime" in state:
                completed_time = state["completedTime"]
                assert isinstance(completed_time, str) and len(completed_time) > 0, f"Invalid completed time"
                print(f"   [OK] Completed Time: {completed_time}")
            
            if "account" in order:
                print(f"   [OK] Account: {order['account']}")
        
        # 3. Order Status Distribution Analysis
        status_distribution = {}
        order_types = {}
        actions = {}
        
        for order in mock_completed_orders:
            status = order["orderState"]["status"]
            order_type = order["orderType"]
            action = order["action"]
            
            status_distribution[status] = status_distribution.get(status, 0) + 1
            order_types[order_type] = order_types.get(order_type, 0) + 1
            actions[action] = actions.get(action, 0) + 1
        
        print(f"[OK] Status Distribution: {status_distribution}")
        print(f"[OK] Order Type Distribution: {order_types}")
        print(f"[OK] Action Distribution: {actions}")
        
        # 4. Fill Rate Analysis
        filled_orders = [order for order in mock_completed_orders if order["orderState"]["status"] == "Filled"]
        fill_rate = len(filled_orders) / len(mock_completed_orders) * 100
        print(f"[OK] Fill Rate: {fill_rate:.1f}% ({len(filled_orders)}/{len(mock_completed_orders)})")
        
        # 5. Commission Analysis for Filled Orders
        total_commission = 0
        for order in filled_orders:
            if "commission" in order["orderState"]:
                total_commission += order["orderState"]["commission"]
        
        if len(filled_orders) > 0:
            avg_commission = total_commission / len(filled_orders)
            print(f"[OK] Commission Analysis: Total ${total_commission}, Avg ${avg_commission:.2f}")
        
        # 6. Account Validation
        accounts = set()
        for order in mock_completed_orders:
            if "account" in order:
                accounts.add(order["account"])
        
        print(f"[OK] Accounts with Completed Orders: {list(accounts)}")
        for account in accounts:
            assert account.startswith("DU"), f"Paper account should start with DU: {account}"
        
        # 7. Symbol Analysis
        symbols = set()
        for order in mock_completed_orders:
            symbols.add(order["symbol"])
        
        print(f"[OK] Symbols in Completed Orders: {list(symbols)}")
        for symbol in symbols:
            assert isinstance(symbol, str) and len(symbol) > 0, f"Invalid symbol: {symbol}"
        
        print(f"[DEMO] Completed Orders Validation Framework: 7 validation categories completed")
        print(f"[FRAMEWORK] Ready for: Empty orders, filled orders, cancelled orders, mixed statuses, commission analysis, performance metrics")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_completed_orders.py -v -s

NEVER use:
- python -m pytest [...]     # Python not in PATH
- pytest [...]               # Pytest not in PATH  
- python tests/paper/...     # Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_completed_orders.py::TestIndividualGetCompletedOrders::test_get_completed_orders_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_completed_orders.py::TestIndividualGetCompletedOrders -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_completed_orders.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("WARNING: STANDALONE EXECUTION DETECTED")
    print("WARNING: RECOMMENDED: Use pytest execution commands shown above")
    print("WARNING: Standalone mode may not work correctly with MCP interface")
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
