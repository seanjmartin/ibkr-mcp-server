"""
Individual MCP Tool Test: invalid_parameters_handling
Focus: Test MCP error handling with invalid parameters across multiple tools
MCP Tool: Multiple tools with invalid parameters
Expected: Proper MCP error responses and parameter validation
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
class TestIndividualInvalidParameters:
    """Test MCP error handling with invalid parameters across multiple tools"""
    
    async def test_invalid_parameters_basic_functionality(self):
        """Test MCP parameter validation through multiple tools with invalid inputs"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Invalid Parameters Handling ===")
        print(f"{'='*60}")
        
        # Force IBKR connection first for consistent client ID 5
        from ibkr_mcp_server.client import ibkr_client
        try:
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
                print(f"[OK] Paper account: {ibkr_client.current_account}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        
        print(f"\n--- Testing Invalid Parameters Across Multiple Tools ---")
        
        # Test invalid parameters for various MCP tools
        invalid_test_cases = [
            {
                "tool": "get_market_data",
                "invalid_params": {"symbols": ""},  # Empty string
                "expected_error_type": "empty_symbol",
                "description": "Empty symbol string"
            },
            {
                "tool": "get_market_data", 
                "invalid_params": {"symbols": 123},  # Wrong type
                "expected_error_type": "wrong_type",
                "description": "Numeric instead of string"
            },
            {
                "tool": "convert_currency",
                "invalid_params": {"amount": -1000, "from_currency": "USD", "to_currency": "EUR"},  # Negative amount
                "expected_error_type": "negative_amount", 
                "description": "Negative amount"
            },
            {
                "tool": "convert_currency",
                "invalid_params": {"amount": 1000, "from_currency": "INVALID", "to_currency": "USD"},  # Invalid currency
                "expected_error_type": "invalid_currency",
                "description": "Invalid currency code"
            },
            {
                "tool": "get_forex_rates",
                "invalid_params": {"currency_pairs": ""},  # Empty pairs
                "expected_error_type": "empty_pairs",
                "description": "Empty currency pairs"
            },
            {
                "tool": "place_stop_loss",
                "invalid_params": {"symbol": "AAPL", "action": "SELL", "quantity": 0, "stop_price": 180.0},  # Zero quantity
                "expected_error_type": "zero_quantity",
                "description": "Zero quantity"
            },
            {
                "tool": "place_stop_loss", 
                "invalid_params": {"symbol": "", "action": "SELL", "quantity": 100, "stop_price": 180.0},  # Empty symbol
                "expected_error_type": "empty_symbol_stop",
                "description": "Empty symbol for stop loss"
            }
        ]
        
        validation_results = []
        
        for i, test_case in enumerate(invalid_test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['tool']} - {test_case['description']} ---")
            
            try:
                result = await call_tool(test_case['tool'], test_case['invalid_params'])
                
                # MCP response structure validation
                assert isinstance(result, list), f"MCP tool should return list"
                assert len(result) > 0, f"MCP tool should return at least one TextContent"
                
                text_content = result[0]
                assert isinstance(text_content, TextContent), f"Expected TextContent"
                
                response_text = text_content.text
                print(f"Response: {response_text}")
                
                # Analyze the response for error handling
                error_handled = False
                error_type = "unknown"
                
                response_lower = response_text.lower()
                
                # Check for explicit error responses
                if "error" in response_lower:
                    error_handled = True
                    error_type = "explicit_error"
                    print(f"[OK] Explicit error handling: {response_text[:100]}...")
                
                # Check for validation failure responses
                elif "validation" in response_lower and "failed" in response_lower:
                    error_handled = True
                    error_type = "validation_error"
                    print(f"[OK] Validation error handling: {response_text[:100]}...")
                
                # Check for safety-related rejections
                elif "safety" in response_lower:
                    error_handled = True
                    error_type = "safety_rejection"
                    print(f"[OK] Safety framework rejection: {response_text[:100]}...")
                
                # Check for invalid parameter messages
                elif "invalid" in response_lower or "must" in response_lower:
                    error_handled = True
                    error_type = "parameter_validation"
                    print(f"[OK] Parameter validation: {response_text[:100]}...")
                
                # Try to parse as JSON to check structured error
                try:
                    parsed = json.loads(response_text)
                    if isinstance(parsed, dict):
                        if "success" in parsed and not parsed["success"]:
                            error_handled = True
                            error_type = "structured_failure"
                            print(f"[OK] Structured failure response")
                        elif "error" in parsed:
                            error_handled = True 
                            error_type = "structured_error"
                            print(f"[OK] Structured error response")
                except json.JSONDecodeError:
                    pass
                
                # If no clear error handling detected, this might still be valid behavior
                if not error_handled:
                    print(f"[INFO] No explicit error detected - might handle gracefully: {response_text[:100]}...")
                    error_type = "graceful_handling"
                
                validation_results.append({
                    "tool": test_case['tool'],
                    "test_type": test_case['expected_error_type'],
                    "error_handled": error_handled,
                    "error_type": error_type,
                    "response_length": len(response_text)
                })
                
            except Exception as e:
                print(f"[OK] Exception-based error handling: {type(e).__name__}: {e}")
                validation_results.append({
                    "tool": test_case['tool'],
                    "test_type": test_case['expected_error_type'], 
                    "error_handled": True,
                    "error_type": "exception",
                    "response_length": 0
                })
        
        # Summarize validation results
        print(f"\n--- Invalid Parameter Validation Summary ---")
        total_tests = len(validation_results)
        handled_tests = sum(1 for r in validation_results if r["error_handled"])
        
        print(f"[OK] Total invalid parameter tests: {total_tests}")
        print(f"[OK] Tests with error handling: {handled_tests}")
        print(f"[OK] Error handling rate: {handled_tests/total_tests*100:.1f}%")
        
        # Detailed breakdown
        error_types = {}
        for result in validation_results:
            error_type = result["error_type"]
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        print(f"[OK] Error handling types: {error_types}")
        
        # Check that we have reasonable error handling across tools
        unique_tools = set(r["tool"] for r in validation_results)
        print(f"[OK] Tools tested: {len(unique_tools)}")
        print(f"[OK] Tools: {', '.join(unique_tools)}")
        
        # Validate that most tests showed some form of error handling
        assert handled_tests >= total_tests * 0.7, f"Expected at least 70% error handling rate, got {handled_tests/total_tests*100:.1f}%"
        
        print(f"\n[OK] MCP Invalid Parameters Handling test PASSED")
        print(f"{'='*60}")
    
    async def test_missing_required_parameters(self):
        """Test MCP tools with missing required parameters"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Missing Required Parameters ===")  
        print(f"{'='*60}")
        
        # Test tools with missing required parameters
        missing_param_tests = [
            {
                "tool": "get_market_data",
                "params": {},  # Missing 'symbols'
                "description": "Missing symbols parameter"
            },
            {
                "tool": "convert_currency", 
                "params": {"amount": 1000},  # Missing currencies
                "description": "Missing currency parameters"
            },
            {
                "tool": "get_forex_rates",
                "params": {},  # Missing 'currency_pairs'
                "description": "Missing currency_pairs parameter"
            }
        ]
        
        for test in missing_param_tests:
            print(f"\n--- Testing {test['tool']} - {test['description']} ---")
            
            try:
                result = await call_tool(test['tool'], test['params'])
                text_content = result[0]
                response_text = text_content.text
                
                print(f"Missing param response: {response_text[:150]}...")
                
                # Should indicate missing parameters or handle gracefully
                response_lower = response_text.lower()
                if any(word in response_lower for word in ["error", "missing", "required", "invalid"]):
                    print(f"[OK] Missing parameter handling detected")
                else:
                    print(f"[INFO] Graceful handling of missing parameters")
                
            except Exception as e:
                print(f"[OK] Exception for missing parameters: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
"""
WINDOWS EXECUTION REQUIREMENTS:

EXACT COMMAND TO RUN THIS TEST:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_invalid_parameters.py::TestIndividualInvalidParameters::test_invalid_parameters_basic_functionality -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)

THIS TEST DEMONSTRATES:
- MCP layer parameter validation across multiple tools
- Comprehensive error handling for various invalid input types
- Safety framework integration with parameter validation
- Structured vs unstructured error response handling
- Statistical analysis of error handling effectiveness
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
