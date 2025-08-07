# Proven Pattern for Creating IBKR MCP Tool Tests

## Quick Reference Template

### Step 1: Copy and Customize Template
```powershell
# Copy template to new test file
Copy-Item "test_individual_template.py" "test_individual_[tool_name].py"
```

### Step 2: Core Replacements
```python
# 1. Update file header
"""
Individual MCP Tool Test: [tool_name]
Focus: Test [tool_name] MCP tool in isolation for debugging
MCP Tool: [tool_name]
Expected: [Brief description of expected behavior]
"""

# 2. Update class name and methods
class TestIndividual[ToolName]:
    async def test_[tool_name]_basic_functionality(self):

# 3. Set tool name and parameters
tool_name = "[tool_name]"  # e.g., "get_accounts"
parameters = {}            # Tool-specific parameters or {} for none
```

### Step 3: Add Tool-Specific Validation
```python
# Replace the generic validation with tool-specific checks
if "expected_field" in parsed_result:
    field_value = parsed_result['expected_field']
    print(f"[OK] Expected Field: {field_value}")
    assert isinstance(field_value, expected_type)
    # Add specific assertions for this tool
```

### Step 4: Update Documentation Strings
```python
# Fix execution commands in docstring
r"""
EXAMPLE EXECUTION COMMANDS:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py::TestIndividual[ToolName]::test_[tool_name]_basic_functionality -v -s
"""
```

## Proven Structure (Based on Tests 1.1 & 1.2)

### Universal MCP Response Pattern
```python
# ALL MCP tools follow this response structure
result = await call_tool(tool_name, parameters)

# Validate MCP response structure
assert isinstance(result, list)
assert len(result) > 0
text_content = result[0]
assert isinstance(text_content, TextContent)

# Parse JSON response from IBKR client
response_text = text_content.text
parsed_result = json.loads(response_text)
```

### Connection Setup Pattern
```python
# Force IBKR connection first (consistent across all tests)
from ibkr_mcp_server.client import ibkr_client
try:
    connection_success = await ibkr_client.connect()
    if connection_success:
        print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
        print(f"[OK] Paper account: {ibkr_client.current_account}")
except Exception as e:
    print(f"[ERROR] Connection error: {e}")
```

### Required Validations
```python
# Every test must validate these common fields
if "paper_trading" in parsed_result:
    assert parsed_result['paper_trading'] == True
    
if "connected" in parsed_result:
    assert parsed_result['connected'] == True
    
if "client_id" in parsed_result:
    assert parsed_result['client_id'] == 5  # Required client ID
```

## Tool-Specific Examples

### No-Parameter Tools (get_connection_status, get_accounts, get_portfolio)
```python
tool_name = "get_connection_status"
parameters = {}  # Empty dict for no parameters
```

### Parameter-Based Tools (get_market_data, get_forex_rates)
```python
tool_name = "get_market_data"
parameters = {"symbols": "AAPL"}  # Tool-specific parameters
```

### Validation Examples by Tool Type

#### Connection/Account Tools
```python
if "current_account" in parsed_result:
    current_account = parsed_result['current_account']
    assert isinstance(current_account, str)
    assert current_account.startswith("DU")  # Paper account validation
```

#### Market Data Tools
```python
if "symbol" in parsed_result:
    symbol = parsed_result['symbol']
    assert isinstance(symbol, str)
    assert symbol == "AAPL"  # Requested symbol validation
```

#### Forex Tools
```python
if "rate" in parsed_result:
    rate = parsed_result['rate']
    assert isinstance(rate, (int, float))
    assert rate > 0  # Positive rate validation
```

## Critical Requirements

### Execution Format (MANDATORY)
```powershell
# ALWAYS use this exact format - no variations
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py::TestIndividual[ToolName]::test_[tool_name]_basic_functionality -v -s
```

### File Structure Requirements
```
tests/paper/individual/
├── test_individual_template.py        # Master template
├── test_individual_get_connection_status.py  # ✅ WORKING example
├── test_individual_get_accounts.py           # ✅ WORKING example
└── test_individual_[new_tool].py             # New test following pattern
```

### Success Criteria Checklist
- [ ] Test runs successfully under pytest
- [ ] Uses client ID 5 consistently  
- [ ] Returns real IBKR API data
- [ ] Validates MCP response structure
- [ ] Includes tool-specific assertions
- [ ] No Unicode characters (Windows compatibility)
- [ ] Proper docstring with execution commands

## Proven Timeline
- **Template Setup:** 2-3 minutes (copy & rename)
- **Customization:** 5-7 minutes (replacements & validation)
- **Testing & Debug:** 3-5 minutes (run & fix issues)
- **Total per Test:** ~10-15 minutes from template to passing

## Copy-Paste Quick Start
```python
# 1. Copy template
# 2. Find/Replace: [tool_name] → actual_tool_name
# 3. Find/Replace: [ToolName] → ActualToolName  
# 4. Update parameters = {} with tool-specific params
# 5. Add tool-specific validation logic
# 6. Update docstring execution commands
# 7. Run: C:\Python313\python.exe -m pytest [test_file] -v -s
```

This pattern has been proven with **Tests 1.1 and 1.2** - both pass consistently and demonstrate end-to-end MCP functionality with real IBKR API data.

## ❌ **CRITICAL: "Empty State Only" Test Problem**

### **Problem Identified in Test 1.4:**
Test validated empty portfolio but had no framework for populated portfolios.

### **Root Cause:** 
Basic "does it return data?" validation instead of comprehensive structure validation.

### **Fix Pattern:** 
Build validation framework that handles BOTH empty and populated scenarios in the same test.

### **Detection:** 
Look for tests that only check empty responses without demonstrating they can handle complex data structures.

### **Avoid:** 
Write tests that only work for current state instead of building frameworks ready for production data.

### **Enhanced Test Approach:**
```python
# BAD: Only handles empty state
if len(positions) == 0:
    print("[OK] Empty portfolio")
    # Test ends here - no framework for populated data

# GOOD: Handles both empty and populated states  
if len(positions) == 0:
    print("[OK] Empty portfolio - expected for new accounts")
    # Demonstrate framework with mock data
    await self._demonstrate_validation_framework()
else:
    print(f"[OK] Populated portfolio with {len(positions)} positions")
    # Use same validation framework for real data
    await self._validate_populated_data(positions)
```

## ⚠️ **MANDATORY: Windows Terminal Compatibility**

### **STRICT PROHIBITION: No Unicode Emojis in Tests**

**❌ FORBIDDEN CHARACTERS:**
- ✓ ✅ ❌ ❗ ⚠️ 🎉 🔧 📊 💰 and ANY Unicode emoji/symbol
- These cause `UnicodeEncodeError: 'charmap' codec can't encode character` on Windows

**✅ REQUIRED ALTERNATIVES:**
```python
# BAD - Will fail on Windows
print("✓ Currency USD: Supported")
print("🎉 Test passed!")
print("❌ Validation failed")

# GOOD - Windows compatible
print("[OK] Currency USD: Supported") 
print("[PASSED] Test passed!")
print("[ERROR] Validation failed")
```

### **Immediate Action Required:**
- **Remove ALL Unicode characters** from test output immediately upon detection
- **Use ASCII alternatives:** [OK], [ERROR], [WARNING], [PASSED], [FAILED]
- **Test on Windows terminals** before considering tests complete
- **Search existing tests** for Unicode characters and replace them

### **Detection Pattern:**
```bash
# Search for Unicode characters in test files
grep -P "[^\x00-\x7F]" tests/**/*.py
```

### **Enforcement:**
Any test containing Unicode emoji/symbols is considered **BROKEN** and must be fixed immediately for Windows compatibility.

**This is a HARD REQUIREMENT for production deployment.**