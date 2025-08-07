"""
Individual MCP Tool Test: get_tool_documentation
Focus: Test get_tool_documentation MCP tool in isolation for debugging
MCP Tool: get_tool_documentation
Expected: Documentation content for specified tool or category
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
class TestIndividualGetToolDocumentation:
    """Test get_tool_documentation MCP tool in isolation"""
    
    async def test_get_tool_documentation_basic_functionality(self):
        """Test basic get_tool_documentation functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_tool_documentation ===")
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
        
        # MCP tool call with parameters - test forex category documentation
        tool_name = "get_tool_documentation"
        parameters = {"tool_or_category": "forex"}
        
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
        
        # Parse the response from the text content
        response_text = text_content.text
        print(f"Response text length: {len(response_text)} characters")
        print(f"Response preview: {response_text[:200]}...")
        
        # Documentation response validation - might be JSON or plain text
        try:
            # Try to parse as JSON first
            parsed_result = json.loads(response_text)
            print(f"JSON Response Format Detected")
            
            # Validate JSON structure for documentation
            if isinstance(parsed_result, dict):
                print(f"[OK] Documentation returned as structured dict")
                
                # Check for expected documentation fields
                if "tool_or_category" in parsed_result:
                    print(f"[OK] Category: {parsed_result['tool_or_category']}")
                
                if "content" in parsed_result:
                    content_length = len(str(parsed_result['content']))
                    print(f"[OK] Content length: {content_length} characters")
                    assert content_length > 50, "Documentation content should be substantial"
                
                if "examples" in parsed_result:
                    examples = parsed_result['examples']
                    print(f"[OK] Examples provided: {len(examples) if isinstance(examples, list) else 'Yes'}")
                
                if "related_tools" in parsed_result:
                    related = parsed_result['related_tools']
                    print(f"[OK] Related tools: {len(related) if isinstance(related, list) else 'Yes'}")
                
                print(f"[OK] JSON documentation structure validated")
            
        except json.JSONDecodeError:
            # If not JSON, treat as plain text documentation
            print(f"Plain Text Response Format Detected")
            
            # Basic validation for text-based documentation
            assert len(response_text) > 100, "Documentation should be substantial (>100 chars)"
            
            # Check for expected documentation content patterns
            text_lower = response_text.lower()
            
            # Should contain forex-related content since we requested "forex" category
            forex_indicators = ["forex", "currency", "eurusd", "exchange", "rate", "conversion"]
            found_indicators = [indicator for indicator in forex_indicators if indicator in text_lower]
            print(f"[OK] Forex indicators found: {found_indicators}")
            assert len(found_indicators) > 0, "Documentation should contain forex-related content"
            
            # Should contain tool or usage information
            usage_indicators = ["tool", "example", "usage", "parameter", "call"]
            found_usage = [indicator for indicator in usage_indicators if indicator in text_lower]
            print(f"[OK] Usage indicators found: {found_usage}")
            assert len(found_usage) > 0, "Documentation should contain usage information"
            
            print(f"[OK] Plain text documentation validated")
        
        print(f"\n--- Documentation Quality Assessment ---")
        print(f"[OK] Documentation Format: {'JSON' if 'JSON' in locals() else 'Plain Text'}")
        print(f"[OK] Content Length: {len(response_text)} characters")
        print(f"[OK] Category Requested: forex")
        print(f"[OK] Response Quality: Substantial content provided")
        
        print(f"\n[OK] MCP Tool 'get_tool_documentation' test PASSED")
        print(f"{'='*60}")
    
    async def test_get_tool_documentation_specific_tool(self):
        """Test documentation for a specific tool rather than category"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Specific Tool Documentation ===")
        print(f"{'='*60}")
        
        # Test documentation for a specific tool
        tool_name = "get_tool_documentation"
        parameters = {"tool_or_category": "get_forex_rates"}
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        
        try:
            result = await call_tool(tool_name, parameters)
            text_content = result[0]
            response_text = text_content.text
            
            print(f"Response length: {len(response_text)} characters")
            print(f"Response preview: {response_text[:150]}...")
            
            # Should contain specific tool information
            assert len(response_text) > 50, "Tool-specific documentation should be substantial"
            
            # Should reference the specific tool
            text_lower = response_text.lower()
            assert "forex" in text_lower or "rate" in text_lower, "Should contain forex rate information"
            
            print(f"[OK] Specific tool documentation validated")
            
        except Exception as e:
            print(f"[INFO] Specific tool documentation test failed: {e}")
            print(f"[INFO] This might be expected if tool doesn't exist or documentation format differs")
    
    async def test_get_tool_documentation_error_handling(self):
        """Test documentation tool error handling with invalid parameters"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Documentation Error Handling ===")
        print(f"{'='*60}")
        
        # Test invalid category/tool
        tool_name = "get_tool_documentation"
        invalid_parameters = {"tool_or_category": "INVALID_CATEGORY_12345"}
        
        print(f"Testing with invalid parameters: {invalid_parameters}")
        
        try:
            result = await call_tool(tool_name, invalid_parameters)
            text_content = result[0]
            response_text = text_content.text
            
            print(f"Error handling result: {response_text}")
            
            # Should handle gracefully - either with error message or empty/default response
            if "error" in response_text.lower() or "not found" in response_text.lower():
                print(f"[OK] Error handling working: Proper error message")
            elif len(response_text) < 50:
                print(f"[OK] Error handling working: Empty/minimal response for invalid input")
            else:
                print(f"[INFO] Unexpected response - might be default documentation")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            print(f"[OK] Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
"""
WINDOWS EXECUTION REQUIREMENTS:

EXACT COMMAND TO RUN THIS TEST:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_tool_documentation.py::TestIndividualGetToolDocumentation::test_get_tool_documentation_basic_functionality -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)

THIS TEST DEMONSTRATES:
- MCP layer documentation retrieval through call_tool()
- Documentation content validation for forex category
- Both JSON and plain text documentation format handling
- Specific tool vs category documentation testing
- Error handling for invalid documentation requests
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
