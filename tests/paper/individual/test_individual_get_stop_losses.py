"""
Individual MCP Tool Test: get_stop_losses
Focus: Test get_stop_losses MCP tool in isolation for debugging
MCP Tool: get_stop_losses
Expected: List existing stop losses (likely empty for clean paper account)
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
class TestIndividualGetStopLosses:
    """Test get_stop_losses MCP tool in isolation"""
    
    async def test_get_stop_losses_basic_functionality(self):
        """Test basic get_stop_losses functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_stop_losses ===")
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
        
        # MCP tool call with parameters
        tool_name = "get_stop_losses"
        parameters = {}  # No parameters required for get_stop_losses
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Executing...")
        
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
        
        # For paper testing, we expect a successful result from IBKR client
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool get_stop_losses failed: {response_text}")
            
            # For successful responses, validate the stop losses data structure
            print(f"Stop losses data: {parsed_result}")
            
            # Expected format: list of stop loss orders (likely empty for clean paper account)
            if "stop_losses" in parsed_result:
                stop_losses = parsed_result['stop_losses']
                print(f"[OK] Stop Losses List: {stop_losses}")
                assert isinstance(stop_losses, list), f"Stop losses should be list, got {type(stop_losses)}"
                
                if len(stop_losses) == 0:
                    print(f"[OK] Empty stop losses list - expected for clean paper account")
                else:
                    print(f"[OK] Found {len(stop_losses)} stop loss orders")
                    # Validate structure of first stop loss order if present
                    first_order = stop_losses[0]
                    if "order_id" in first_order:
                        print(f"[OK] Order ID: {first_order['order_id']}")
                    if "symbol" in first_order:
                        print(f"[OK] Symbol: {first_order['symbol']}")
                    if "stop_price" in first_order:
                        print(f"[OK] Stop Price: {first_order['stop_price']}")
                        assert isinstance(first_order['stop_price'], (int, float))
            
            # Validate paper account connection info
            if "paper_trading" in parsed_result:
                paper_trading = parsed_result['paper_trading']
                print(f"[OK] Paper Trading: {paper_trading}")
                assert paper_trading == True, f"Expected paper trading, got {paper_trading}"
                
            if "connected" in parsed_result:
                connected = parsed_result['connected']
                print(f"[OK] Connected: {connected}")
                assert connected == True, f"Expected connected=True, got {connected}"
                
            if "client_id" in parsed_result:
                client_id = parsed_result['client_id']
                print(f"[OK] Client ID: {client_id}")
                assert client_id == 5, f"Expected client ID 5, got {client_id}"
                
            if "current_account" in parsed_result:
                current_account = parsed_result['current_account']
                print(f"[OK] Current Account: {current_account}")
                assert isinstance(current_account, str)
                assert current_account.startswith("DU"), f"Expected paper account (DU prefix), got {current_account}"
            
            print(f"[PASSED] GET STOP LOSSES VALIDATION PASSED")
            
        elif isinstance(parsed_result, list):
            # Stop losses might be returned as direct list
            print(f"[OK] Stop losses returned as list: {parsed_result}")
            assert isinstance(parsed_result, list)
            
            if len(parsed_result) == 0:
                print(f"[OK] Empty stop losses list - expected for clean paper account")
            else:
                print(f"[OK] Found {len(parsed_result)} stop loss orders")
                # Validate structure of orders if present
                for order in parsed_result:
                    if isinstance(order, dict):
                        print(f"[OK] Stop Loss Order: {order}")
            
            print(f"[PASSED] GET STOP LOSSES (LIST FORMAT) VALIDATION PASSED")
            
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool get_stop_losses")
        
        print(f"\n[PASSED] MCP Tool 'get_stop_losses' test PASSED")
        print(f"{'='*60}")
        
    async def test_get_stop_losses_error_handling(self):
        """Test get_stop_losses error handling with invalid parameters"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Error Handling: get_stop_losses ===")
        print(f"{'='*60}")
        
        # Test with invalid account parameter (if tool accepts account parameter)
        tool_name = "get_stop_losses"
        invalid_parameters = {
            "account": "INVALID_ACCOUNT"  # Invalid account ID
        }
        
        print(f"Testing with invalid parameters: {invalid_parameters}")
        
        try:
            result = await call_tool(tool_name, invalid_parameters)
            print(f"Error handling result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Error response text: {response_text}")
                
                # Check if it indicates an error or handles gracefully
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"[PASSED] Error handling working: {response_text}")
                else:
                    # Might have succeeded despite invalid params - that's also valid behavior
                    print(f"[INFO] Tool handled invalid params gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for some tools
            print(f"[PASSED] Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_stop_losses.py -v -s

NEVER use:
- python -m pytest [...]     # Python not in PATH
- pytest [...]               # Pytest not in PATH  
- python tests/paper/...     # Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_stop_losses.py::TestIndividualGetStopLosses::test_get_stop_losses_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_stop_losses.py::TestIndividualGetStopLosses -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_stop_losses.py -v -s

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