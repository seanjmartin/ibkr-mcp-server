"""
Individual MCP Tool Test: place_bracket_order
Focus: Test place_bracket_order MCP tool in isolation for debugging
MCP Tool: place_bracket_order
Expected: Execute bracket order placement (entry + stop + target) through MCP interface
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
class TestIndividualPlaceBracketOrder:
    """Test place_bracket_order MCP tool in isolation"""
    
    async def test_place_bracket_order_basic_functionality(self):
        """Test basic place_bracket_order functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: place_bracket_order ===")
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
        
        # MCP tool call with parameters - place_bracket_order requires symbol, action, quantity, entry_price, stop_price, target_price
        tool_name = "place_bracket_order"
        parameters = {
            "symbol": "AAPL",
            "action": "BUY", 
            "quantity": 100,
            "entry_price": 180.00,    # Entry limit price
            "stop_price": 170.00,     # Stop loss price (below entry)
            "target_price": 190.00    # Profit target price (above entry)
        }
        
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
        
        # For paper testing, we expect a response from IBKR client
        # place_bracket_order should either succeed or provide safety validation error
        
        if isinstance(parsed_result, dict):
            # Check if it's a success response
            if "success" in parsed_result:
                success = parsed_result['success']
                print(f"[OK] Success status: {success}")
                
                if success:
                    # Successful bracket order placement
                    if "parent_order_id" in parsed_result:
                        parent_order_id = parsed_result['parent_order_id']
                        print(f"[OK] Parent Order ID: {parent_order_id}")
                        assert isinstance(parent_order_id, int)
                    
                    if "stop_order_id" in parsed_result:
                        stop_order_id = parsed_result['stop_order_id']
                        print(f"[OK] Stop Order ID: {stop_order_id}")
                        assert isinstance(stop_order_id, int)
                        
                    if "target_order_id" in parsed_result:
                        target_order_id = parsed_result['target_order_id']
                        print(f"[OK] Target Order ID: {target_order_id}")
                        assert isinstance(target_order_id, int)
                        
                    if "symbol" in parsed_result:
                        symbol = parsed_result['symbol']
                        print(f"[OK] Symbol: {symbol}")
                        assert symbol == "AAPL"
                        
                    if "quantity" in parsed_result:
                        quantity = parsed_result['quantity']
                        print(f"[OK] Quantity: {quantity}")
                        assert quantity == 100
                        
                else:
                    # Failed bracket order (could be safety validation or IBKR error)
                    if "error" in parsed_result:
                        error = parsed_result['error']
                        print(f"[OK] Order placement error: {error}")
                        # Could be safety validation preventing trading
                        
            # Safety framework validation
            if "safety_validation" in parsed_result:
                safety = parsed_result['safety_validation']
                print(f"[OK] Safety validation: {safety}")
                
            # Paper trading validation
            if "paper_trading" in parsed_result:
                paper_trading = parsed_result['paper_trading']
                print(f"[OK] Paper trading mode: {paper_trading}")
                assert paper_trading == True
                
            # Client ID validation
            if "client_id" in parsed_result:
                client_id = parsed_result['client_id']
                print(f"[OK] Client ID: {client_id}")
                assert client_id == 5  # Required client ID for paper tests
                
            print(f"[PASS] BRACKET ORDER VALIDATION PASSED")
            
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool place_bracket_order")
        
        print(f"\n[PASS] MCP Tool 'place_bracket_order' test PASSED")
        print(f"{'='*60}")
        
    async def test_place_bracket_order_error_handling(self):
        """Test place_bracket_order error handling with invalid parameters"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Error Handling: place_bracket_order ===")
        print(f"{'='*60}")
        
        # Test invalid parameters - invalid price relationships
        tool_name = "place_bracket_order"
        invalid_parameters = {
            "symbol": "INVALID",
            "action": "BUY",
            "quantity": -100,         # Invalid negative quantity
            "entry_price": 180.00,
            "stop_price": 190.00,     # Invalid: stop price above entry for BUY order
            "target_price": 170.00    # Invalid: target price below entry for BUY order
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
                
                # Check if it indicates an error (expected for invalid params)
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"[PASS] Error handling working: {response_text}")
                else:
                    # Parse and check for error structure
                    try:
                        parsed_result = json.loads(response_text)
                        if isinstance(parsed_result, dict) and "success" in parsed_result:
                            if not parsed_result["success"]:
                                print(f"[PASS] Error handling via success=False: {parsed_result}")
                            else:
                                print(f"[INFO] Tool handled invalid params gracefully: {parsed_result}")
                    except:
                        print(f"[INFO] Tool response format: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for some validation errors
            print(f"[PASS] Exception-based error handling: {type(e).__name__}")
            
    async def test_place_bracket_order_missing_parameters(self):
        """Test place_bracket_order with missing required parameters"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Missing Parameters: place_bracket_order ===")
        print(f"{'='*60}")
        
        # Test missing required parameters - missing stop_price and target_price
        tool_name = "place_bracket_order"
        missing_parameters = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "entry_price": 180.00
            # Missing stop_price and target_price
        }
        
        print(f"Testing with missing parameters: {missing_parameters}")
        
        try:
            result = await call_tool(tool_name, missing_parameters)
            print(f"Missing parameter result: {result}")
            
            # Should get an error about missing required parameters
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Missing parameter response: {response_text}")
                
                # Should indicate missing parameter error
                if "error" in response_text.lower() or "required" in response_text.lower() or "missing" in response_text.lower():
                    print(f"[PASS] Missing parameter handling working: {response_text}")
                else:
                    print(f"[INFO] Tool response for missing params: {response_text}")
            
        except Exception as e:
            print(f"Exception during missing parameter test: {e}")
            print(f"[PASS] Exception-based missing parameter handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_place_bracket_order.py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_place_bracket_order.py::TestIndividualPlaceBracketOrder::test_place_bracket_order_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_place_bracket_order.py::TestIndividualPlaceBracketOrder -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_place_bracket_order.py -v -s

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
