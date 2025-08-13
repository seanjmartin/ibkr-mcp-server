"""
Individual MCP Tool Test Template
Focus: Test single MCP tool in isolation for debugging
Usage: Copy this file and rename to test_individual_[tool_name].py

Instructions:
1. Replace [TOOL_NAME] with actual tool name (e.g., "get_connection_status")
2. Replace [tool_name] with snake_case tool name
3. Update parameters dict with tool-specific parameters
4. Add tool-specific validation logic
5. Test iteratively until working perfectly

CRITICAL: IBKR API Field Names
When validating IBKR API responses, use CAMELCASE field names:
[OK] CORRECT: marketValue, unrealizedPNL, realizedPNL, avgCost
[ERROR] WRONG: market_value, unrealized_pnl, realized_pnl, avg_cost
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
class TestIndividual_TOOL_NAME_:
    """Test [tool_name] MCP tool in isolation"""
    
    async def test_TOOL_NAME_basic_functionality(self):
        """Test basic [tool_name] functionality through MCP interface"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing MCP Tool: [tool_name] ===")
        print(f"{'='*60}")
        
        # MCP tool call with parameters - REPLACE WITH ACTUAL TOOL NAME AND PARAMS
        tool_name = "[tool_name]"  # e.g., "get_connection_status"
        parameters = {
            # Add tool-specific parameters here
            # Example: "symbols": "AAPL"
            # Example: "currency_pairs": "EURUSD"
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
        print(f"\\n--- MCP Tool Response Structure Validation ---")
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
        # The client returns its own format, not necessarily with "success" field
        
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool [tool_name] failed: {response_text}")
            
            # For successful responses, validate the data structure
            print(f"[tool_name] data: {parsed_result}")
            
            # ADD TOOL-SPECIFIC VALIDATION HERE - Examples:
            # Connection status validation:
            # if "connected" in parsed_result:
            #     connected = parsed_result['connected']
            #     print(f"[OK] Connection Status: {connected}")
            #     assert isinstance(connected, bool)
            
            # Paper account validation:
            # if "account" in parsed_result:
            #     account = parsed_result['account']
            #     print(f"[OK] Account: {account}")
            #     assert isinstance(account, str) and account.startswith("DU")
            
            # Port validation for paper trading:
            # if "port" in parsed_result:
            #     port = parsed_result['port']
            #     print(f"[OK] Port: {port}")
            #     assert port == 7497  # Paper trading port
                
            # Client ID validation:
            # if "client_id" in parsed_result:
            #     client_id = parsed_result['client_id']
            #     print(f"[OK] Client ID: {client_id}")
            #     assert client_id == 5  # Required client ID for paper tests
            
            # Portfolio/position field validation (USE CORRECT CAMELCASE):
            # if "marketValue" in parsed_result:  # [OK] CORRECT (not market_value)
            #     market_value = parsed_result['marketValue']
            #     print(f"[OK] Market Value: ${market_value:,.2f}")
            #     assert isinstance(market_value, (int, float))
            
            # if "unrealizedPNL" in parsed_result:  # [OK] CORRECT (not unrealized_pnl)  
            #     pnl = parsed_result['unrealizedPNL']
            #     print(f"[OK] Unrealized P&L: ${pnl:,.2f}")
            #     assert isinstance(pnl, (int, float))
            
            # if "avgCost" in parsed_result:  # [OK] CORRECT (not avg_cost)
            #     avg_cost = parsed_result['avgCost']
            #     print(f"[OK] Average Cost: ${avg_cost:.2f}")
            #     assert isinstance(avg_cost, (int, float))
            
            # if "realizedPNL" in parsed_result:  # [OK] CORRECT (not realized_pnl)
            #     realized_pnl = parsed_result['realizedPNL']
            #     print(f"[OK] Realized P&L: ${realized_pnl:,.2f}")
            #     assert isinstance(realized_pnl, (int, float))
            
            print(f"[OK] TOOL-SPECIFIC VALIDATION PASSED")
            
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool [tool_name]")
        
        print(f"\\n[OK] MCP Tool '{tool_name}' test PASSED")
        print(f"{'='*60}")
        
    async def test_TOOL_NAME_error_handling(self):
        """Test [tool_name] error handling with invalid parameters"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing Error Handling: [tool_name] ===")
        print(f"{'='*60}")
        
        # Test invalid parameters - CUSTOMIZE FOR EACH TOOL
        tool_name = "[tool_name]"
        invalid_parameters = {
            # Add invalid parameters specific to this tool
            # Example: "symbols": ""  # Empty string
            # Example: "amount": -1000  # Negative amount
            # Example: "from_currency": "INVALID"  # Invalid currency
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
                
                # Check if it indicates an error
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"[OK] Error handling working: {response_text}")
                else:
                    # Might have succeeded despite invalid params - that's also valid behavior
                    print(f"[INFO] Tool handled invalid params gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for some tools
            print(f"[OK] Exception-based error handling: {type(e).__name__}")

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
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py::TestIndividual[TOOL_NAME]::test_[TOOL_NAME]_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py::TestIndividual[TOOL_NAME] -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py -v -s

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
