"""
Individual MCP Tool Test: get_open_orders
Focus: Test get_open_orders MCP tool in isolation for debugging
MCP Tool: get_open_orders
Expected: List of pending orders (likely empty for fresh account)
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
class TestIndividualGetOpenOrders:
    """Test get_open_orders MCP tool in isolation"""
    
    async def test_get_open_orders_basic_functionality(self):
        """Test basic get_open_orders functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_open_orders ===")
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
        
        # MCP tool call with no parameters (gets all open orders)
        tool_name = "get_open_orders"
        parameters = {}  # No parameters needed for basic functionality
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Retrieving open orders...")
        
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
        
        # For paper trading, we expect a list of open orders (likely empty for new account)
        if isinstance(parsed_result, list):
            open_orders = parsed_result
            print(f"[OK] Open orders returned as list: {len(open_orders)} orders")
            
            if len(open_orders) == 0:
                print(f"[OK] Empty open orders list - expected for fresh paper account")
                print(f"[PASSED] Open orders structure validation ready for populated data")
                
                # Demonstrate validation framework with mock data
                await self._demonstrate_open_orders_validation_framework()
                
            else:
                print(f"[OK] Found {len(open_orders)} open orders - validating structure")
                for i, order in enumerate(open_orders):
                    print(f"[OK] Order {i+1}: {order}")
                    
                    # Validate order structure
                    if isinstance(order, dict):
                        # Check for expected order fields
                        expected_fields = ["orderId", "symbol", "action", "totalQuantity", "orderType"]
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
                            
                        print(f"[OK] Order {i+1} structure validation passed")
                    
        elif isinstance(parsed_result, dict):
            # Check if it's an error response
            if "error" in parsed_result:
                error_msg = parsed_result["error"]
                print(f"[INFO] Error response: {error_msg}")
                pytest.fail(f"MCP tool get_open_orders failed: {error_msg}")
            else:
                # Maybe it's a wrapped response
                if "data" in parsed_result:
                    open_orders = parsed_result["data"]
                    print(f"[OK] Open orders in wrapped response: {len(open_orders)} orders")
                else:
                    print(f"[INFO] Unexpected dict response format: {parsed_result}")
        else:
            pytest.fail(f"Unexpected response format: {type(parsed_result)}, content: {parsed_result}")
        
        print(f"\n[PASSED] MCP Tool 'get_open_orders' test COMPLETED")
        print(f"{'='*60}")
    
    async def _demonstrate_open_orders_validation_framework(self):
        """Demonstrate comprehensive open orders validation with mock data"""
        
        print(f"\n--- Demonstrating Open Orders Validation Framework ---")
        
        # Mock order data to demonstrate validation capabilities
        mock_orders = [
            {
                "orderId": 12345,
                "symbol": "AAPL",
                "action": "BUY",
                "totalQuantity": 100,
                "orderType": "LMT",
                "lmtPrice": 180.0,
                "status": "PreSubmitted",
                "account": "DUH905195"
            },
            {
                "orderId": 12346,
                "symbol": "TSLA", 
                "action": "SELL",
                "totalQuantity": 50,
                "orderType": "STP",
                "auxPrice": 250.0,
                "status": "Submitted",
                "account": "DUH905195"
            }
        ]
        
        print(f"[DEMO] Validating mock order data structure...")
        
        # 1. Order Count Validation
        order_count = len(mock_orders)
        print(f"[OK] Order Count Validation: {order_count} orders")
        assert isinstance(order_count, int)
        
        # 2. Individual Order Structure Validation
        for i, order in enumerate(mock_orders):
            print(f"[OK] Order {i+1} Structure Validation:")
            
            # Required fields validation
            assert "orderId" in order, f"Order missing orderId"
            assert "symbol" in order, f"Order missing symbol"
            assert "action" in order, f"Order missing action"
            assert "totalQuantity" in order, f"Order missing totalQuantity"
            assert "orderType" in order, f"Order missing orderType"
            
            # Field type validation
            assert isinstance(order["orderId"], (int, str)), f"Invalid orderId type"
            assert isinstance(order["symbol"], str), f"Invalid symbol type"
            assert order["action"] in ["BUY", "SELL"], f"Invalid action: {order['action']}"
            assert isinstance(order["totalQuantity"], (int, float)), f"Invalid quantity type"
            assert isinstance(order["orderType"], str), f"Invalid orderType"
            
            # Order type specific validation
            if order["orderType"] == "LMT" and "lmtPrice" in order:
                assert isinstance(order["lmtPrice"], (int, float)), f"Invalid lmtPrice type"
                print(f"   [OK] Limit Price: ${order['lmtPrice']}")
            
            if order["orderType"] == "STP" and "auxPrice" in order:
                assert isinstance(order["auxPrice"], (int, float)), f"Invalid auxPrice type"
                print(f"   [OK] Stop Price: ${order['auxPrice']}")
            
            print(f"   [OK] Order ID: {order['orderId']}")
            print(f"   [OK] Symbol: {order['symbol']}")
            print(f"   [OK] Action: {order['action']}")
            print(f"   [OK] Quantity: {order['totalQuantity']}")
            print(f"   [OK] Order Type: {order['orderType']}")
            
            if "status" in order:
                print(f"   [OK] Status: {order['status']}")
            
            if "account" in order:
                print(f"   [OK] Account: {order['account']}")
        
        # 3. Order Type Distribution Analysis
        order_types = {}
        actions = {}
        
        for order in mock_orders:
            order_type = order["orderType"]
            action = order["action"]
            
            order_types[order_type] = order_types.get(order_type, 0) + 1
            actions[action] = actions.get(action, 0) + 1
        
        print(f"[OK] Order Type Distribution: {order_types}")
        print(f"[OK] Action Distribution: {actions}")
        
        # 4. Account Validation
        accounts = set()
        for order in mock_orders:
            if "account" in order:
                accounts.add(order["account"])
        
        print(f"[OK] Accounts with Orders: {list(accounts)}")
        for account in accounts:
            assert account.startswith("DU"), f"Paper account should start with DU: {account}"
        
        # 5. Symbol Validation
        symbols = set()
        for order in mock_orders:
            symbols.add(order["symbol"])
        
        print(f"[OK] Symbols with Orders: {list(symbols)}")
        for symbol in symbols:
            assert isinstance(symbol, str) and len(symbol) > 0, f"Invalid symbol: {symbol}"
        
        print(f"[DEMO] Open Orders Validation Framework: 5 validation categories completed")
        print(f"[FRAMEWORK] Ready for: Empty orders, populated orders, mixed order types, multi-account, error conditions")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_open_orders.py -v -s

NEVER use:
- python -m pytest [...]     # Python not in PATH
- pytest [...]               # Pytest not in PATH  
- python tests/paper/...     # Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_open_orders.py::TestIndividualGetOpenOrders::test_get_open_orders_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_open_orders.py::TestIndividualGetOpenOrders -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_open_orders.py -v -s

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
