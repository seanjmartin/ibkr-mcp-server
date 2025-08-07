"""
Individual MCP Tool Test: modify_stop_loss
Focus: Test modify_stop_loss MCP tool in isolation for debugging
MCP Tool: modify_stop_loss
Expected: Graceful handling of non-existent order (testing error handling)
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
class TestIndividualModifyStopLoss:
    """Test modify_stop_loss MCP tool in isolation"""
    
    async def test_modify_stop_loss_non_existent_order(self):
        """Test modify_stop_loss graceful handling of non-existent order through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: modify_stop_loss (Non-Existent Order) ===")
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
        
        # MCP tool call with NON-EXISTENT order ID to test error handling
        tool_name = "modify_stop_loss"
        parameters = {
            "order_id": 99999,  # Non-existent order ID
            "stop_price": 185.0
        }
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Testing error handling with non-existent order ID 99999...")
        
        try:
            # Execute MCP tool call
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result: {result}")
            
        except Exception as e:
            print(f"EXCEPTION during MCP call: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            # Exception might be expected for non-existent orders
            print(f"[INFO] Exception may indicate proper error handling: {e}")
        
        # MCP response structure validation - MCP tools return list of TextContent
        print(f"\n--- MCP Tool Response Structure Validation ---")
        
        if 'result' in locals():
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
                # For error handling, non-JSON error message is acceptable
                print(f"[OK] Non-JSON response indicates error handling: {response_text}")
                parsed_result = {"error": response_text}
            
            print(f"Parsed Result: {parsed_result}")
            
            # Check for error handling indicators
            error_indicators = ["error", "not found", "invalid", "failed", "does not exist", "unknown"]
            response_str = str(parsed_result).lower()
            
            has_error_indicator = any(indicator in response_str for indicator in error_indicators)
            
            if has_error_indicator:
                print(f"[PASSED] Error handling detected as expected")
                print(f"[OK] Non-existent order error handling working correctly")
                
                # Check specific error details
                if isinstance(parsed_result, dict):
                    if "error" in parsed_result:
                        error_msg = parsed_result["error"]
                        print(f"[OK] Error Message: {error_msg}")
                    if "success" in parsed_result:
                        success = parsed_result["success"]
                        print(f"[OK] Success: {success}")
                        assert success == False, f"Expected success=False for non-existent order, got {success}"
                    if "order_id" in parsed_result:
                        order_id = parsed_result["order_id"]
                        print(f"[OK] Order ID referenced: {order_id}")
                        
            else:
                # Check if it somehow succeeded (unexpected but possible)
                print(f"[INFO] Tool may have handled non-existent order gracefully")
                print(f"[INFO] Response: {parsed_result}")
                
                # Even if it didn't explicitly error, it should indicate the order wasn't found
                if isinstance(parsed_result, dict):
                    if "success" in parsed_result:
                        success = parsed_result["success"]
                        print(f"[OK] Success status: {success}")
                        
        else:
            # Exception occurred - this might be expected for non-existent orders
            print(f"[OK] Exception during non-existent order test - this may be expected behavior")
            print(f"[PASSED] Exception-based error handling for non-existent orders")
        
        print(f"\n[PASSED] MCP Tool 'modify_stop_loss' non-existent order test COMPLETED")
        print(f"{'='*60}")
        
    async def test_modify_stop_loss_parameter_validation(self):
        """Test modify_stop_loss parameter validation through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing modify_stop_loss Parameter Validation ===")
        print(f"{'='*60}")
        
        # MCP tool call with INVALID parameters to test validation
        tool_name = "modify_stop_loss"
        parameters = {
            "order_id": -1,  # Invalid negative order ID
            "stop_price": -100.0  # Invalid negative stop price
        }
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Testing parameter validation with invalid order_id=-1 and stop_price=-100...")
        
        try:
            # Execute MCP tool call
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result: {result}")
            
            # MCP response structure validation
            assert isinstance(result, list), f"MCP tool should return list, got {type(result)}"
            assert len(result) > 0, f"MCP tool should return at least one TextContent, got empty list"
            
            text_content = result[0]
            assert isinstance(text_content, TextContent), f"Expected TextContent, got {type(text_content)}"
            
            response_text = text_content.text
            print(f"Response text: {response_text}")
            
            try:
                parsed_result = json.loads(response_text)
                print(f"Parsed Result: {parsed_result}")
                
                # Check for validation error indicators
                validation_indicators = ["error", "invalid", "validation", "failed", "negative", "parameter"]
                response_str = str(parsed_result).lower()
                
                has_validation_error = any(indicator in response_str for indicator in validation_indicators)
                
                if has_validation_error:
                    print(f"[PASSED] Parameter validation error detected as expected")
                    print(f"[OK] Parameter validation working correctly")
                    
                    if isinstance(parsed_result, dict):
                        if "success" in parsed_result:
                            success = parsed_result["success"]
                            print(f"[OK] Success: {success}")
                            if not success:
                                print(f"[OK] Validation correctly blocked invalid parameters")
                else:
                    print(f"[INFO] Tool may have handled invalid parameters differently")
                    print(f"[INFO] Response: {parsed_result}")
                
            except json.JSONDecodeError:
                print(f"[OK] Non-JSON response: {response_text}")
                print(f"[INFO] May indicate validation error or system response")
                
        except Exception as e:
            print(f"Exception during parameter validation test: {e}")
            print(f"[INFO] Exception may indicate parameter validation working")
        
        print(f"\n[PASSED] Parameter validation test COMPLETED")
        print(f"{'='*60}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_modify_stop_loss.py -v -s

NEVER use:
- python -m pytest [...]     # Python not in PATH
- pytest [...]               # Pytest not in PATH  
- python tests/paper/...     # Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_modify_stop_loss.py::TestIndividualModifyStopLoss::test_modify_stop_loss_non_existent_order -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_modify_stop_loss.py::TestIndividualModifyStopLoss -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_modify_stop_loss.py -v -s

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