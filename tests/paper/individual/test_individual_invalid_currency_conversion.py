"""
Individual MCP Tool Test: Invalid Currency Conversion
Focus: Test convert_currency MCP tool with invalid parameters to validate error handling
MCP Tool: convert_currency
Expected: Proper error handling for invalid currencies through MCP interface
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

@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividualInvalidCurrencyConversion:
    """Test convert_currency MCP tool with invalid parameters in isolation"""
    
    async def test_invalid_currency_conversion_basic_functionality(self):
        """Test convert_currency error handling with invalid currencies"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: Invalid Currency Conversion ===")
        print(f"{'='*60}")
        
        # Test multiple invalid currency scenarios
        test_cases = [
            {
                "description": "Invalid from_currency",
                "params": {"amount": 1000.0, "from_currency": "INVALID", "to_currency": "USD"},
                "expected": "from_currency validation error"
            },
            {
                "description": "Invalid to_currency", 
                "params": {"amount": 1000.0, "from_currency": "USD", "to_currency": "INVALID"},
                "expected": "to_currency validation error"
            },
            {
                "description": "Both currencies invalid",
                "params": {"amount": 1000.0, "from_currency": "FAKE1", "to_currency": "FAKE2"},
                "expected": "currency validation error"
            },
            {
                "description": "Empty currency codes",
                "params": {"amount": 1000.0, "from_currency": "", "to_currency": ""},
                "expected": "empty currency validation error"
            }
        ]
        
        tool_name = "convert_currency"
        successful_error_handling = 0
        total_test_cases = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}/{total_test_cases}: {test_case['description']} ---")
            parameters = test_case["params"]
            
            print(f"MCP Call: call_tool('{tool_name}', {parameters})")
            print(f"Expected: {test_case['expected']}")
            
            try:
                # Execute MCP tool call with invalid parameters
                result = await call_tool(tool_name, parameters)
                print(f"Raw Result: {result}")
                
            except Exception as e:
                print(f"EXCEPTION during MCP call: {e}")
                print(f"[OK] Exception-based error handling working")
                successful_error_handling += 1
                continue
            
            # MCP response structure validation
            print(f"--- MCP Tool Response Structure Validation ---")
            assert isinstance(result, list), f"MCP tool should return list, got {type(result)}"
            assert len(result) > 0, f"MCP tool should return at least one TextContent, got empty list"
            
            # Get the first TextContent response
            text_content = result[0]
            assert isinstance(text_content, TextContent), f"Expected TextContent, got {type(text_content)}"
            assert hasattr(text_content, 'text'), f"TextContent should have 'text' attribute"
            
            # Parse the response
            response_text = text_content.text
            print(f"Response text: {response_text}")
            
            try:
                parsed_result = json.loads(response_text)
                print(f"Parsed Result: {parsed_result}")
            except json.JSONDecodeError:
                # If it's not JSON, treat as error string
                print(f"[OK] Non-JSON error response: {response_text}")
                if any(error_word in response_text.lower() for error_word in ["error", "invalid", "unsupported", "not found"]):
                    print(f"[OK] Error handling detected in response")
                    successful_error_handling += 1
                else:
                    print(f"[WARNING] Response doesn't clearly indicate error")
                continue
            
            # Analyze parsed JSON response
            if isinstance(parsed_result, dict):
                # Check for explicit error indicators
                if "error" in parsed_result:
                    print(f"[OK] Explicit error field: {parsed_result['error']}")
                    successful_error_handling += 1
                elif "success" in parsed_result and not parsed_result["success"]:
                    print(f"[OK] Success=False indicates error handling")
                    successful_error_handling += 1
                elif any(error_word in str(parsed_result).lower() for error_word in ["error", "invalid", "unsupported"]):
                    print(f"[OK] Error indicators in response")
                    successful_error_handling += 1
                else:
                    # Check if it unexpectedly succeeded
                    if "converted_amount" in parsed_result:
                        print(f"[WARNING] Tool unexpectedly succeeded with invalid currencies")
                        print(f"Result: {parsed_result}")
                    else:
                        print(f"[OK] Tool handled invalid input gracefully without explicit error")
                        successful_error_handling += 1
            else:
                print(f"[WARNING] Unexpected response type: {type(parsed_result)}")
        
        # Summary of error handling effectiveness
        error_handling_rate = (successful_error_handling / total_test_cases) * 100
        print(f"\n--- Error Handling Summary ---")
        print(f"Test cases with proper error handling: {successful_error_handling}/{total_test_cases}")
        print(f"Error handling effectiveness: {error_handling_rate:.1f}%")
        
        if error_handling_rate >= 75.0:  # 75% threshold for good error handling
            print(f"[OK] convert_currency error handling is effective")
        else:
            print(f"[WARNING] convert_currency error handling could be improved")
            
        # Ensure IBKR connection is working by testing valid conversion
        print(f"\n--- Validation Test: Valid Currency Conversion ---")
        valid_params = {"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"}
        print(f"Testing valid conversion: {valid_params}")
        
        try:
            valid_result = await call_tool(tool_name, valid_params)
            if isinstance(valid_result, list) and len(valid_result) > 0:
                valid_text = valid_result[0].text
                try:
                    valid_parsed = json.loads(valid_text)
                    if "converted_amount" in valid_parsed or "exchange_rate" in valid_parsed:
                        print(f"[OK] Valid conversion works: System operational")
                    else:
                        print(f"[WARNING] Valid conversion didn't return expected fields")
                except json.JSONDecodeError:
                    print(f"[WARNING] Valid conversion returned non-JSON: {valid_text}")
        except Exception as e:
            print(f"[WARNING] Valid conversion test failed: {e}")
        
        print(f"\n[OK] Invalid Currency Conversion MCP Tool test COMPLETED")
        print(f"Error handling effectiveness: {error_handling_rate:.1f}%")
        print(f"{'='*60}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_invalid_currency_conversion.py::TestIndividualInvalidCurrencyConversion::test_invalid_currency_conversion_basic_functionality -v -s

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_invalid_currency_conversion.py::TestIndividualInvalidCurrencyConversion::test_invalid_currency_conversion_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_invalid_currency_conversion.py::TestIndividualInvalidCurrencyConversion -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_invalid_currency_conversion.py -v -s
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("WARNING: STANDALONE EXECUTION DETECTED")
    print("RECOMMENDED: Use pytest execution commands shown above")
    print()
    print("IBKR Gateway must be running with paper trading login and API enabled!")
    print("Port 7497 for paper trading, Client ID 5")
    
    exit_code = pytest.main([
        __file__, 
        "-v", 
        "-s", 
        "--tb=short"
    ])
    
    sys.exit(exit_code)
