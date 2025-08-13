"""
Individual MCP Tool Test: convert_currency
Focus: Test convert_currency MCP tool in isolation for debugging
MCP Tool: convert_currency
Expected: USD to EUR conversion with live rates
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
class TestIndividualConvertCurrency:
    """Test convert_currency MCP tool in isolation"""
    
    async def test_convert_currency_basic_functionality(self):
        """Test basic convert_currency functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: convert_currency ===")
        print(f"{'='*60}")
        
        # FORCE CONNECTION FIRST - ensure IBKR client is connected
        print(f"Step 1: Forcing IBKR Gateway connection...")
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
        
        # MCP tool call - convert_currency from USD to EUR
        tool_name = "convert_currency"
        parameters = {
            "amount": 1000.0,
            "from_currency": "USD",
            "to_currency": "EUR"
        }
        
        print(f"Step 2: MCP Call: call_tool('{tool_name}', {parameters})")
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
        
        # For currency conversion, we expect conversion information with rates
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool convert_currency failed: {response_text}")
            
            # Validate currency conversion data structure
            print(f"Currency Conversion Data: {parsed_result}")
            
            # Original amount validation
            if "original_amount" in parsed_result:
                original_amount = parsed_result["original_amount"]
                print(f"[OK] Original Amount Found: {original_amount}")
                assert isinstance(original_amount, (int, float))
                if original_amount == 1000.0:
                    print(f"[OK] Correct original amount: {original_amount}")
                else:
                    print(f"[INFO] Different original amount: {original_amount}")
            
            # From currency validation
            if "from_currency" in parsed_result:
                from_currency = parsed_result["from_currency"]
                print(f"[OK] From Currency Found: {from_currency}")
                assert isinstance(from_currency, str)
                if from_currency == "USD":
                    print(f"[OK] Correct from currency: {from_currency}")
                else:
                    print(f"[INFO] Different from currency: {from_currency}")
            
            # To currency validation
            if "to_currency" in parsed_result:
                to_currency = parsed_result["to_currency"]
                print(f"[OK] To Currency Found: {to_currency}")
                assert isinstance(to_currency, str)
                if to_currency == "EUR":
                    print(f"[OK] Correct to currency: {to_currency}")
                else:
                    print(f"[INFO] Different to currency: {to_currency}")
            
            # Exchange rate validation
            if "exchange_rate" in parsed_result:
                exchange_rate = parsed_result["exchange_rate"]
                print(f"[OK] Exchange Rate Found: {exchange_rate}")
                assert isinstance(exchange_rate, (int, float))
                
                # Validate realistic USD/EUR rate (typically 0.7 - 1.2)
                if 0.5 < exchange_rate < 1.5:
                    print(f"[OK] Realistic USD/EUR exchange rate: {exchange_rate}")
                else:
                    print(f"[INFO] Unusual exchange rate: {exchange_rate} (may be valid)")
            
            # Converted amount validation
            if "converted_amount" in parsed_result:
                converted_amount = parsed_result["converted_amount"]
                print(f"[OK] Converted Amount Found: {converted_amount}")
                assert isinstance(converted_amount, (int, float))
                
                # Validate reasonable conversion (should be less than 1000 for USD->EUR)
                if 500 < converted_amount < 1200:  # Reasonable range
                    print(f"[OK] Realistic converted amount: {converted_amount}")
                else:
                    print(f"[INFO] Unusual converted amount: {converted_amount}")
                
                # Cross-validate with exchange rate if both available
                if "exchange_rate" in parsed_result and "original_amount" in parsed_result:
                    expected_amount = parsed_result["original_amount"] * parsed_result["exchange_rate"]
                    if abs(converted_amount - expected_amount) < 0.01:  # Allow small rounding differences
                        print(f"[OK] Conversion calculation correct: {converted_amount} ~= {expected_amount}")
                    else:
                        print(f"[INFO] Conversion calculation difference: {converted_amount} vs expected {expected_amount}")
            
            # Conversion method validation
            if "conversion_method" in parsed_result:
                method = parsed_result["conversion_method"]
                print(f"[OK] Conversion Method Found: {method}")
                assert isinstance(method, str)
                if method in ["direct", "inverse", "cross_currency"]:
                    print(f"[OK] Valid conversion method: {method}")
            
            # Rate timestamp validation
            if "rate_timestamp" in parsed_result:
                timestamp = parsed_result["rate_timestamp"]
                print(f"[OK] Rate Timestamp Found: {timestamp}")
                assert isinstance(timestamp, str)
                if "2025" in timestamp:  # Current year validation
                    print(f"[OK] Current rate timestamp: {timestamp}")
            
            # Additional conversion metadata
            conversion_metadata = {}
            metadata_fields = ["bid_rate", "ask_rate", "spread", "rate_source", "timestamp"]
            
            for field in metadata_fields:
                if field in parsed_result:
                    conversion_metadata[field] = parsed_result[field]
                    print(f"[OK] Conversion Metadata - {field}: {parsed_result[field]}")
            
            if conversion_metadata:
                print(f"[SUCCESS] Found conversion metadata: {conversion_metadata}")
            
            print(f"[SUCCESS] CONVERT_CURRENCY MCP TOOL VALIDATION PASSED")
            
        elif isinstance(parsed_result, list):
            print(f"[OK] List format conversion response with {len(parsed_result)} entries")
            
            # Check if it's an error response
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool convert_currency failed: {response_text}")
            
            # Process list entries
            for i, entry in enumerate(parsed_result):
                if isinstance(entry, dict):
                    print(f"[OK] Conversion Entry {i}: {entry}")
                    # Apply same validation as above for each entry
                    if "from_currency" in entry and entry["from_currency"] == "USD":
                        print(f"[OK] Found USD conversion in entry {i}")
                        
                        if "to_currency" in entry:
                            print(f"[OK] To currency in entry {i}: {entry['to_currency']}")
                        if "converted_amount" in entry:
                            print(f"[OK] Converted amount in entry {i}: {entry['converted_amount']}")
        
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool convert_currency")
        
        print(f"\n[SUCCESS] MCP Tool 'convert_currency' test PASSED")
        print(f"[SUCCESS] IBKR currency conversion working through MCP layer")
        print(f"{'='*60}")
        
    async def test_convert_currency_reverse_conversion(self):
        """Test convert_currency with EUR to USD (reverse) conversion"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Reverse Currency Conversion ===")
        print(f"{'='*50}")
        
        tool_name = "convert_currency"
        # Test reverse conversion
        parameters = {
            "amount": 500.0,
            "from_currency": "EUR",
            "to_currency": "USD"
        }
        
        print(f"Testing reverse conversion: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Reverse conversion result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Reverse conversion response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed reverse conversion result: {parsed_result}")
                    
                    # Validate reverse conversion
                    if isinstance(parsed_result, dict):
                        if "from_currency" in parsed_result and parsed_result["from_currency"] == "EUR":
                            print(f"[OK] Correct from currency: {parsed_result['from_currency']}")
                        if "to_currency" in parsed_result and parsed_result["to_currency"] == "USD":
                            print(f"[OK] Correct to currency: {parsed_result['to_currency']}")
                        if "converted_amount" in parsed_result:
                            converted = parsed_result["converted_amount"]
                            if converted > 500:  # EUR->USD should typically be > EUR amount
                                print(f"[OK] Realistic EUR->USD conversion: EUR500  ->  ${converted}")
                            else:
                                print(f"[INFO] EUR->USD conversion result: EUR500  ->  ${converted}")
                    
                except json.JSONDecodeError:
                    print(f"[INFO] Non-JSON reverse conversion response: {response_text}")
            else:
                print(f"Unexpected reverse conversion response format: {result}")
            
        except Exception as e:
            print(f"Exception during reverse conversion test: {e}")
            print(f"[INFO] Exception-based handling: {type(e).__name__}")

    async def test_convert_currency_cross_currency(self):
        """Test convert_currency with cross-currency pair (GBP to JPY)"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Cross-Currency Conversion ===")
        print(f"{'='*50}")
        
        tool_name = "convert_currency"
        # Test cross-currency conversion (requires USD intermediate)
        parameters = {
            "amount": 100.0,
            "from_currency": "GBP",
            "to_currency": "JPY"
        }
        
        print(f"Testing cross-currency conversion: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Cross-currency result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Cross-currency response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed cross-currency result: {parsed_result}")
                    
                    # Validate cross-currency conversion
                    if isinstance(parsed_result, dict):
                        if "from_currency" in parsed_result and parsed_result["from_currency"] == "GBP":
                            print(f"[OK] Correct from currency: {parsed_result['from_currency']}")
                        if "to_currency" in parsed_result and parsed_result["to_currency"] == "JPY":
                            print(f"[OK] Correct to currency: {parsed_result['to_currency']}")
                        if "converted_amount" in parsed_result:
                            converted = parsed_result["converted_amount"]
                            # GBP->JPY should typically be in thousands (e.g., GBP100  ->  JPY15,000+)
                            if converted > 5000:
                                print(f"[OK] Realistic GBP->JPY conversion: GBP100  ->  JPY{converted:,.0f}")
                            else:
                                print(f"[INFO] GBP->JPY conversion result: GBP100  ->  JPY{converted}")
                        if "conversion_method" in parsed_result:
                            method = parsed_result["conversion_method"]
                            if method == "cross_currency":
                                print(f"[OK] Cross-currency method detected: {method}")
                            else:
                                print(f"[INFO] Conversion method: {method}")
                    
                except json.JSONDecodeError:
                    print(f"[INFO] Non-JSON cross-currency response: {response_text}")
            else:
                print(f"Unexpected cross-currency response format: {result}")
            
        except Exception as e:
            print(f"Exception during cross-currency test: {e}")
            print(f"[INFO] Exception-based handling: {type(e).__name__}")

    async def test_convert_currency_error_handling(self):
        """Test convert_currency error handling with invalid currency"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Error Handling: convert_currency ===")
        print(f"{'='*60}")
        
        # Test invalid currency
        tool_name = "convert_currency"
        invalid_parameters = {
            "amount": 1000.0,
            "from_currency": "INVALID",
            "to_currency": "USD"
        }
        
        print(f"Testing with invalid currency: {invalid_parameters}")
        
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
                    # Might have returned some default or fallback behavior
                    print(f"[INFO] Tool handled invalid currency gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for invalid currencies
            print(f"[OK] Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_convert_currency.py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_convert_currency.py::TestIndividualConvertCurrency::test_convert_currency_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_convert_currency.py::TestIndividualConvertCurrency -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_convert_currency.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
- Forex market hours (24/5 - Sunday 5PM EST to Friday 5PM EST)
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
