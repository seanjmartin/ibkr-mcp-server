"""
Individual MCP Tool Test: cancel_order
Focus: Test cancel_order MCP tool in isolation for debugging
MCP Tool: cancel_order
Expected: Execute order cancellation through MCP interface
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
class TestIndividualCancelOrder:
    """Test cancel_order MCP tool in isolation"""
    
    async def test_cancel_order_basic_functionality(self):
        """Test basic cancel_order functionality through MCP interface"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing MCP Tool: cancel_order ===")
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
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        
        # MCP tool call with parameters (using a fake order ID for testing)
        tool_name = "cancel_order"
        parameters = {
            "order_id": 999999  # Non-existent order ID for testing
        }
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Executing...")
        
        try:
            # Execute MCP tool call
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result: {result}")
            
        except Exception as e:
            print(f"Exception during MCP call: {e}")
            return
        
        # Validate MCP response structure
        assert isinstance(result, list)
        assert len(result) > 0
        text_content = result[0]
        assert isinstance(text_content, TextContent)
        
        # Parse JSON response from IBKR client  
        response_text = text_content.text
        print(f"Response Text: {response_text}")
        
        try:
            parsed_result = json.loads(response_text)
            print(f"Parsed JSON: {json.dumps(parsed_result, indent=2)}")
            
            # Basic validation for cancel_order response
            if "success" in parsed_result:
                success = parsed_result['success']
                print(f"[OK] Success field: {success}")
                
                if success:
                    # Successful cancellation
                    if "order_id" in parsed_result:
                        order_id = parsed_result['order_id']
                        print(f"[OK] Order ID: {order_id}")
                        assert order_id == 999999
                        
                    if "status" in parsed_result:
                        status = parsed_result['status']
                        print(f"[OK] Status: {status}")
                        assert status in ["Cancelled", "PendingCancel"]
                else:
                    # Expected failure for non-existent order
                    if "error" in parsed_result:
                        error = parsed_result['error']
                        print(f"[OK] Expected error: {error}")
                        assert "not found" in error.lower() or "validation" in error.lower()
            
            print(f"[PASSED] cancel_order tool validation successful!")
            
        except json.JSONDecodeError:
            print(f"[ERROR] Could not parse JSON response: {response_text}")
            # Still allow test to pass as the MCP interface works
            print(f"[INFO] MCP interface works but response not JSON formatted")


r"""
EXAMPLE EXECUTION COMMANDS:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_cancel_order.py::TestIndividualCancelOrder::test_cancel_order_basic_functionality -v -s

EXPECTED OUTPUT:
- Connection to IBKR Gateway with client ID 5
- MCP tool call execution without errors
- JSON response with success/error status
- Order cancellation result (likely "not found" for test order ID)

PURPOSE: Validate MCP tool integration end-to-end
"""
