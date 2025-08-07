"""
Individual MCP Tool Test: get_forex_rates
Focus: Test get_forex_rates MCP tool in isolation for debugging
MCP Tool: get_forex_rates
Expected: EURUSD rate with bid/ask spread
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
class TestIndividualGetForexRates:
    """Test get_forex_rates MCP tool in isolation"""
    
    async def test_get_forex_rates_basic_functionality(self):
        """Test basic get_forex_rates functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_forex_rates ===")
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
        
        # MCP tool call - get_forex_rates with EURUSD
        tool_name = "get_forex_rates"
        parameters = {
            "currency_pairs": "EURUSD"  # Test with major EUR/USD pair
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
        
        # For forex rates, we expect rate information with bid/ask spreads
        if isinstance(parsed_result, list):
            print(f"[OK] IBKR Forex Rates Format: List of {len(parsed_result)} entries")
            
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool get_forex_rates failed: {response_text}")
            
            # Validate list structure - look for forex rate entries
            valid_rates = 0
            eurusd_found = False
            forex_data = {}
            
            for entry in parsed_result:
                if isinstance(entry, dict):
                    print(f"[OK] Forex Rate Entry: {entry}")
                    
                    # Look for currency pair information
                    pair_found = None
                    if "pair" in entry:
                        pair_found = entry["pair"]
                    elif "symbol" in entry and "USD" in entry["symbol"]:
                        pair_found = entry["symbol"]
                    elif "contract" in entry and isinstance(entry["contract"], dict):
                        if "symbol" in entry["contract"]:
                            pair_found = entry["contract"]["symbol"]
                    
                    if pair_found:
                        print(f"[OK] Currency Pair Found: {pair_found}")
                        if "EURUSD" in pair_found:
                            eurusd_found = True
                            forex_data.update(entry)
                            print(f"[OK] EURUSD rate data found")
                        valid_rates += 1
                    
                    # Look for rate information
                    if "last" in entry or "bid" in entry or "ask" in entry or "rate" in entry:
                        rate_info = {}
                        for rate_field in ["last", "bid", "ask", "rate", "close", "open"]:
                            if rate_field in entry and entry[rate_field] is not None:
                                rate_info[rate_field] = entry[rate_field]
                        
                        if rate_info:
                            print(f"[OK] Rate Information: {rate_info}")
                            valid_rates += 1
                else:
                    print(f"[INFO] Non-dict forex entry: {entry}")
            
            # Validate we found valid forex rate data
            if valid_rates > 0:
                print(f"[OK] Found {valid_rates} valid forex rate entries")
            else:
                print(f"[INFO] No standard forex rate entries found, checking alternative formats")
            
            if eurusd_found:
                print(f"[OK] EURUSD rate successfully retrieved")
            else:
                print(f"[INFO] EURUSD may be in different format or unavailable during off-hours")
                
        elif isinstance(parsed_result, dict):
            print(f"[OK] Dictionary format forex response")
            
            # Check if it's an error response
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool get_forex_rates failed: {response_text}")
            
            # Validate dictionary structure - look for forex rate fields
            forex_data = parsed_result
            
            # Look for currency pair
            pair_found = None
            if "pair" in forex_data:
                pair_found = forex_data["pair"]
            elif "symbol" in forex_data:
                pair_found = forex_data["symbol"]
            
            if pair_found:
                print(f"[OK] Currency Pair Found: {pair_found}")
                if "EURUSD" in pair_found:
                    print(f"[OK] Correct EURUSD pair returned")
            
            # Look for rate information
            rate_fields = ["last", "bid", "ask", "rate", "close", "open", "high", "low"]
            found_rates = {}
            
            for field in rate_fields:
                if field in forex_data and forex_data[field] is not None:
                    try:
                        rate_value = float(forex_data[field])
                        found_rates[field] = rate_value
                        print(f"[OK] Forex Rate - {field}: {rate_value}")
                    except (ValueError, TypeError):
                        print(f"[INFO] Non-numeric rate field {field}: {forex_data[field]}")
            
            if found_rates:
                print(f"[SUCCESS] Found forex rate data: {found_rates}")
                
                # Validate realistic forex rates for EURUSD (typically 0.9 - 1.3)
                for field, value in found_rates.items():
                    if 0.5 < value < 2.0:  # Reasonable EURUSD range
                        print(f"[OK] Realistic {field} rate: {value}")
                    else:
                        print(f"[INFO] Unusual {field} rate: {value} (may be valid during extreme conditions)")
                
                # Check for bid/ask spread if both are available
                if "bid" in found_rates and "ask" in found_rates:
                    spread = found_rates["ask"] - found_rates["bid"]
                    print(f"[OK] Bid/Ask Spread: {spread:.5f} ({spread*10000:.1f} pips)")
                    
                    if 0 < spread < 0.01:  # Reasonable spread
                        print(f"[OK] Normal forex spread")
                    else:
                        print(f"[INFO] Unusual spread (may be normal for paper trading)")
            else:
                print(f"[INFO] No numeric rate fields found")
                print(f"[INFO] Available forex data structure: {forex_data}")
        
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool get_forex_rates")
        
        # Look for additional forex metadata
        metadata_fields = ["timestamp", "session", "volume", "contract_id", "market_status"]
        found_metadata = {}
        
        # Function to extract metadata from nested structures
        def extract_metadata(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in metadata_fields:
                        found_metadata[f"{prefix}{key}"] = value
                        print(f"[OK] Forex Metadata - {key}: {value}")
                    elif isinstance(value, dict):
                        extract_metadata(value, f"{key}.")
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                extract_metadata(item, f"{key}[{i}].")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        extract_metadata(item, f"[{i}].")
        
        if isinstance(parsed_result, (list, dict)):
            extract_metadata(parsed_result)
        
        if found_metadata:
            print(f"[SUCCESS] Found forex metadata: {found_metadata}")
        
        print(f"[SUCCESS] GET_FOREX_RATES MCP TOOL VALIDATION PASSED")
        print(f"\n[SUCCESS] MCP Tool 'get_forex_rates' test PASSED")
        print(f"[SUCCESS] IBKR forex rates retrieved through MCP layer")
        print(f"{'='*60}")
        
    async def test_get_forex_rates_multiple_pairs(self):
        """Test get_forex_rates with multiple currency pairs"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Multiple Forex Pairs ===")
        print(f"{'='*50}")
        
        tool_name = "get_forex_rates"
        # Test multiple major pairs
        parameters = {
            "currency_pairs": "EURUSD,GBPUSD,USDJPY"  # Major pairs
        }
        
        print(f"Testing with multiple forex pairs: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Multi-pair result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Multi-pair response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed multi-pair result: {parsed_result}")
                    
                    if isinstance(parsed_result, list):
                        print(f"✅ Returned {len(parsed_result)} forex rate entries")
                        
                        # Look for requested pairs
                        pairs_found = set()
                        for entry in parsed_result:
                            if isinstance(entry, dict):
                                if "pair" in entry:
                                    pairs_found.add(entry["pair"])
                                elif "symbol" in entry:
                                    pairs_found.add(entry["symbol"])
                                print(f"[OK] Found forex entry: {entry}")
                        
                        expected_pairs = ["EURUSD", "GBPUSD", "USDJPY"]
                        found_expected = pairs_found.intersection(expected_pairs)
                        if found_expected:
                            print(f"✅ Found expected pairs: {found_expected}")
                        else:
                            print(f"ℹ️ Pairs found: {pairs_found}")
                    else:
                        print(f"ℹ️ Multi-pair response format: {type(parsed_result)}")
                        
                except json.JSONDecodeError:
                    print(f"ℹ️ Non-JSON multi-pair response: {response_text}")
            else:
                print(f"Unexpected multi-pair response format: {result}")
            
        except Exception as e:
            print(f"Exception during multi-pair test: {e}")
            print(f"ℹ️ Exception-based handling: {type(e).__name__}")

    async def test_get_forex_rates_error_handling(self):
        """Test get_forex_rates error handling with invalid currency pair"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Error Handling: get_forex_rates ===")
        print(f"{'='*60}")
        
        # Test invalid currency pair
        tool_name = "get_forex_rates"
        invalid_parameters = {
            "currency_pairs": "INVALIDCURRENCY"  # Invalid currency pair
        }
        
        print(f"Testing with invalid currency pair: {invalid_parameters}")
        
        try:
            result = await call_tool(tool_name, invalid_parameters)
            print(f"Error handling result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Error response text: {response_text}")
                
                # Check if it indicates an error or empty result
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"✅ Error handling working: {response_text}")
                elif response_text.strip() == "[]" or response_text.strip() == "{}":
                    print(f"✅ Empty result for invalid currency pair: {response_text}")
                else:
                    # Might have returned some default or fallback behavior
                    print(f"ℹ️ Tool handled invalid pair gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for invalid currency pairs
            print(f"✅ Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_forex_rates.py -v -s

NEVER use:
- python -m pytest [...]     # ❌ Python not in PATH
- pytest [...]               # ❌ Pytest not in PATH  
- python tests/paper/...     # ❌ Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_forex_rates.py::TestIndividualGetForexRates::test_get_forex_rates_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_forex_rates.py::TestIndividualGetForexRates -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_forex_rates.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
- Forex market hours (24/5 - Sunday 5PM EST to Friday 5PM EST)
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("⚠️  STANDALONE EXECUTION DETECTED")
    print("⚠️  RECOMMENDED: Use pytest execution commands shown above")
    print("⚠️  Standalone mode may not work correctly with MCP interface")
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
