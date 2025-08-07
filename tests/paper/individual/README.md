# Individual MCP Tool Testing - Iterative Development

## Purpose

This directory contains **individual MCP tool tests** for iterative development and debugging. Each test file focuses on **one specific MCP tool** and can be run in isolation to debug and perfect the test before integrating into the main test suite.

## Testing Strategy

### **Isolated Development Pattern**
1. **One Tool Per File** - Each MCP tool gets its own test file
2. **Independent Execution** - Each test runs completely standalone
3. **Iterative Debugging** - Modify and rerun individual tests quickly
4. **MCP Layer Focus** - All tests use proper `call_tool()` interface
5. **Graduate to Main Suite** - Move working tests to consolidated suite

### **File Naming Convention**
```
test_individual_[tool_name].py
```

Examples:
- `test_individual_get_connection_status.py`
- `test_individual_get_accounts.py`  
- `test_individual_get_portfolio.py`
- `test_individual_get_market_data.py`

## Development Workflow

### **Step 1: Create Individual Test**
```bash
# Copy template to new tool test
cp test_individual_template.py test_individual_get_connection_status.py

# Edit to focus on specific MCP tool
# Implement proper call_tool() usage
# Add tool-specific validation
```

### **Step 2: Iterative Development**
```bash
# Run single test in isolation
pytest tests/paper/individual/test_individual_get_connection_status.py -v -s

# Debug and modify test
# Rerun immediately to test changes
# Continue until test passes reliably
```

### **Step 3: Graduate to Main Suite** 
```bash
# Once working, add to main consolidated test suite
# Keep individual test as reference/debugging backup
```

## Test Execution Commands

### **CRITICAL: Windows Execution Requirements**

**ALL individual tests MUST be run using pytest with full Python path:**
```powershell
C:\Python313\python.exe -m pytest [test_file] -v -s
```

**CRITICAL: Client ID 5 Requirement**  
All paper tests use **client ID 5** for shared IBKR Gateway connection strategy.

### **Run Single Individual Test (CORRECT FORMAT)**
```powershell
# Basic execution (REQUIRED FORMAT)
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py -v -s

# Specific test method
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py::TestIndividualGetConnectionStatus::test_get_connection_status_basic_functionality -v -s

# With timeout protection (10 seconds) - Windows timeout command
timeout 10 C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py -v -s --tb=short

# Maximum debug output
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py -v -s --tb=long --capture=no --log-cli-level=DEBUG
```

### **Run All Individual Tests (CORRECT FORMAT)**
```powershell
# Run all individual tests
C:\Python313\python.exe -m pytest tests/paper/individual/ -v -s

# With timeout protection for each test
timeout 300 C:\Python313\python.exe -m pytest tests/paper/individual/ -v -s --tb=short
```

### **WRONG - Commands That Do NOT Work:**
```bash
python -m pytest [...]     # ❌ Python not in PATH
pytest [...]               # ❌ Pytest not in PATH  
python tests/paper/...     # ❌ Direct execution bypasses pytest framework
timeout 10s [...]          # ❌ Linux timeout syntax on Windows
```

## Template Structure

Each individual test file follows this pattern:

```python
"""
Individual MCP Tool Test: [TOOL_NAME]
Focus: Test single MCP tool in isolation for debugging
MCP Tool: [tool_name]
Expected: [brief description of expected behavior]
"""

import pytest
import asyncio
from ibkr_mcp_server.main import call_tool  # Proper MCP interface

@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividual[ToolName]:
    """Test [tool_name] MCP tool in isolation"""
    
    async def test_[tool_name]_basic_functionality(self):
        """Test basic [tool_name] functionality"""
        # Clear test description
        print(f"\\n=== Testing MCP Tool: [tool_name] ===")
        
        # MCP tool call with parameters
        result = await call_tool("[tool_name]", {
            # Tool-specific parameters
        })
        
        # MCP response structure validation
        assert "success" in result
        assert isinstance(result["success"], bool)
        
        if result["success"]:
            assert "data" in result
            # Tool-specific data validation
            print(f"SUCCESS: [tool_name] returned data: {result['data']}")
        else:
            assert "error" in result
            print(f"ERROR: [tool_name] failed: {result['error']}")
            
        # Tool-specific assertions
        
    async def test_[tool_name]_error_handling(self):
        """Test [tool_name] error handling"""
        # Test invalid parameters if applicable
        pass
        
    async def test_[tool_name]_edge_cases(self):
        """Test [tool_name] edge cases"""
        # Tool-specific edge case testing
        pass

# Standalone execution for debugging
if __name__ == "__main__":
    # Run this specific test file directly
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
```

## Priority Order for Individual Test Development

### **Phase 1: Core Foundation (3 tests)**
1. `test_individual_get_connection_status.py` - Validate MCP server connectivity
2. `test_individual_get_accounts.py` - Test account listing
3. `test_individual_get_account_summary.py` - Test account balance data

### **Phase 2: Market Data (3 tests)**  
4. `test_individual_get_market_data.py` - US stock quotes (AAPL)
5. `test_individual_get_market_data_international.py` - International stocks (ASML)
6. `test_individual_resolve_international_symbol.py` - Symbol resolution

### **Phase 3: Forex & Currency (2 tests)**
7. `test_individual_get_forex_rates.py` - Forex rates (EURUSD)
8. `test_individual_convert_currency.py` - Currency conversion

### **Phase 4: Portfolio & Orders (4 tests)**
9. `test_individual_get_portfolio.py` - Portfolio positions
10. `test_individual_get_open_orders.py` - Pending orders
11. `test_individual_get_completed_orders.py` - Trade history  
12. `test_individual_get_executions.py` - Execution details

### **Phase 5: Risk Management (4 tests - Read-Only)**
13. `test_individual_get_stop_losses.py` - Stop loss listing
14. `test_individual_place_stop_loss_validation.py` - Parameter validation
15. `test_individual_modify_stop_loss_validation.py` - Modification validation
16. `test_individual_cancel_stop_loss_validation.py` - Cancellation validation

### **Phase 6: Advanced Features (1 test)**
17. `test_individual_get_tool_documentation.py` - Help system

## Debugging Utilities

### **Common Issues and Solutions**
- **MCP Import Issues**: Use proper `from ibkr_mcp_server.main import call_tool`
- **Async/Await Problems**: Ensure all tests marked with `@pytest.mark.asyncio`
- **Connection Issues**: Verify IBKR Gateway running with API enabled
- **Timeout Issues**: Use 10-second timeout protection for hanging detection

### **Debug Output Template**
```python
# Add detailed debug output to each test
print(f"\\n=== Testing MCP Tool: {tool_name} ===")
print(f"Parameters: {parameters}")
print(f"Result: {result}")
print(f"Success: {result.get('success', 'N/A')}")
if result.get('success'):
    print(f"Data Preview: {str(result['data'])[:200]}...")
else:
    print(f"Error: {result.get('error', 'N/A')}")
```

## Benefits of Individual Testing

### **Development Benefits**
- ✅ **Fast Iteration** - Modify and rerun single test quickly
- ✅ **Isolated Debugging** - Focus on one tool without distractions  
- ✅ **Independent Development** - Work on multiple tools in parallel
- ✅ **Clear Success Criteria** - Each tool has specific validation requirements

### **Testing Benefits**
- ✅ **Precise Error Identification** - Know exactly which tool has issues
- ✅ **Targeted Debugging** - Focus debugging effort on specific functionality
- ✅ **Gradual Progress** - Build confidence one tool at a time
- ✅ **Reference Implementation** - Working individual tests as examples

### **Integration Benefits**
- ✅ **Proven Components** - Only integrate tests that work individually
- ✅ **Clear Test Structure** - Consistent pattern across all MCP tools
- ✅ **Easy Maintenance** - Individual tests remain for future debugging
- ✅ **Documentation** - Each test documents expected MCP tool behavior

---

**Next Step**: Create template file and first individual test for debugging.
