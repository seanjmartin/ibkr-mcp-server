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
        
        # FORCE CONNECTION FIRST - ensure IBKR client is connected with client ID 5
        print(f"Step 1: Forcing IBKR Gateway connection with client ID 5...")
        from ibkr_mcp_server.client import ibkr_client
        
        # Set client ID to 5 BEFORE any connection attempt (required for paper tests)
        ibkr_client.client_id = 5
        
        try:
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
        
        print(f"Step 2: MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Executing...")
        
        try:
            # Execute MCP tool call
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result Type: {type(result)}")
            print(f"Raw Result Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
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
        
        # Tool-specific validation for get_completed_orders
        print(f"\n--- get_completed_orders Tool-Specific Validation ---")
        
        # Every test must validate these common fields (from proven pattern)
        if "paper_trading" in parsed_result:
            assert parsed_result['paper_trading'] == True
            print(f"[OK] Paper trading confirmed: {parsed_result['paper_trading']}")
            
        if "connected" in parsed_result:
            assert parsed_result['connected'] == True
            print(f"[OK] Connection confirmed: {parsed_result['connected']}")
            
        if "client_id" in parsed_result:
            assert parsed_result['client_id'] == 5  # Required client ID
            print(f"[OK] Client ID verified: {parsed_result['client_id']}")
        
        # get_completed_orders specific validation
        if isinstance(parsed_result, list):
            completed_orders = parsed_result
            print(f"[OK] Completed orders list: {len(completed_orders)} orders")
            assert isinstance(completed_orders, list), f"Orders should be list, got {type(completed_orders)}"
            
            if len(completed_orders) == 0:
                print(f"[OK] Empty completed orders list - expected for fresh paper account")
            else:
                print(f"[OK] Found {len(completed_orders)} completed orders")
                for i, order in enumerate(completed_orders):
                    print(f"[OK] Completed Order {i+1}: {order}")
                    # Validate basic order structure
                    if isinstance(order, dict):
                        if "orderId" in order:
                            print(f"[OK] Order ID: {order['orderId']}")
                        if "symbol" in order:
                            print(f"[OK] Symbol: {order['symbol']}")
                        if "action" in order:
                            print(f"[OK] Action: {order['action']}")
        
        print(f"\n[SUCCESS] GET_COMPLETED_ORDERS MCP TOOL WORKING")
        print(f"\n[SUCCESS] MCP Tool 'get_completed_orders' test PASSED")
        print(f"[SUCCESS] IBKR completed orders data retrieved through MCP layer")
        print(f"{'='*60}")

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
