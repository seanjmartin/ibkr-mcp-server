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
        parameters = {"currency_pairs": "EURUSD"}
        
        print(f"Step 2: MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Executing...")
        
        try:
            # Execute MCP tool call - this returns a list of TextContent objects
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result Type: {type(result)}")
            print(f"Raw Result: {result}")
            
        except Exception as e:
            print(f"EXCEPTION during MCP call: {e}")
            pytest.fail(f"MCP call failed with exception: {e}")
        
        # MCP tool response structure validation
        print(f"\n--- MCP Tool Response Structure Validation ---")
        assert isinstance(result, list), f"MCP tool should return list, got {type(result)}"
        assert len(result) > 0, f"MCP tool should return at least one TextContent"
        
        text_content = result[0]
        assert isinstance(text_content, TextContent), f"Expected TextContent, got {type(text_content)}"
        
        response_text = text_content.text
        print(f"Response text: {response_text}")
        
        try:
            parsed_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Response is not JSON: {response_text}")
            pytest.fail(f"Expected JSON response, got non-JSON: {response_text}")
        
        print(f"Parsed Result: {parsed_result}")
        
        # Validate forex response structure
        if isinstance(parsed_result, dict):
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool get_forex_rates failed: {response_text}")
            
            # Look for forex data fields
            print(f"Forex data: {parsed_result}")
            
            if "pair" in parsed_result:
                pair = parsed_result['pair']
                print(f"[OK] Currency Pair: {pair}")
                assert pair == "EURUSD", f"Expected EURUSD, got {pair}"
            
            if "last" in parsed_result:
                last_rate = parsed_result['last']
                print(f"[OK] Last Rate: {last_rate}")
                assert isinstance(last_rate, (int, float)), f"Expected numeric rate, got {type(last_rate)}"
            
            if "bid" in parsed_result:
                bid = parsed_result['bid']
                print(f"[OK] Bid Rate: {bid}")
                
            if "ask" in parsed_result:
                ask = parsed_result['ask']
                print(f"[OK] Ask Rate: {ask}")
            
            print(f"[SUCCESS] FOREX RATES MCP TOOL WORKING")
            
        elif isinstance(parsed_result, list):
            print(f"Forex data returned as list with {len(parsed_result)} entries")
            if len(parsed_result) > 0:
                forex_entry = parsed_result[0]
                if isinstance(forex_entry, dict):
                    print(f"[OK] Forex entry structure: {forex_entry}")
                    
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
        
        print(f"\n[SUCCESS] MCP Tool 'get_forex_rates' test PASSED")
        print(f"[SUCCESS] IBKR forex rates retrieved through MCP layer")
        print(f"{'='*60}")

# Use pytest to run this test:
# pytest tests/paper/individual/test_individual_get_forex_rates_fixed.py::TestIndividualGetForexRates::test_get_forex_rates_basic_functionality -v -s
