# Paper Testing Strategy for IBKR MCP Server

## Overview

This document outlines the strategy for validating the IBKR MCP Server **MCP tool layer** with actual paper trading connections. Paper testing represents the critical bridge between unit tests and Claude Desktop integration, ensuring all **17 MCP tools work correctly** through the complete MCP protocol stack.

## CRITICAL TESTING LAYER CORRECTION

### What We MUST Test (MCP Tool Layer)
```
Claude Desktop → MCP Protocol → call_tool() → Our MCP Tools → IBKR Client → IBKR API
```

**Correct Test Pattern:**
```python
# Testing the MCP tool interface that Claude Desktop actually uses
result = await call_tool("get_connection_status", {})
result = await call_tool("get_accounts", {})  
result = await call_tool("get_portfolio", {})
```

### What We Were INCORRECTLY Testing (Client Layer)
```
Test → IBKR Client → IBKR API
```

**Incorrect Pattern (What We Were Doing):**
```python
# This bypasses the MCP layer entirely - NOT what Claude Desktop uses!
client = IBKRClient()
result = await client.get_accounts()  # WRONG LAYER
result = await client.get_portfolio()  # WRONG LAYER
```

## Core Testing Philosophy

### MCP Tool Integration Focus
Our paper tests must validate the **complete MCP tool stack**:
- **MCP Protocol Layer**: Tool request/response handling
- **Tool Validation**: Parameter validation and safety checks
- **IBKR Integration**: Real API calls through client layer
- **Error Handling**: MCP-level error responses
- **Safety Framework**: Integration with trading safety systems

## CRITICAL EXECUTION REQUIREMENTS

### Windows Execution Commands (MANDATORY)
**ALL paper tests MUST use full Python path:**
```powershell
C:\Python313\python.exe -m pytest [test_file] -v -s
```

### Client ID Requirements (MANDATORY)
**ALL paper tests MUST use client ID 5** for shared IBKR Gateway connection:
- Prevents connection conflicts between tests
- Allows sequential test execution
- Matches IBKR Gateway configuration
- Enables efficient test suite execution

### Correct Test Execution Examples
```powershell
# Individual test execution
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py::TestIndividualGetConnectionStatus::test_get_connection_status_basic_functionality -v -s

# Full test class
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py::TestIndividualGetConnectionStatus -v -s

# Entire test file
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py -v -s

# With timeout protection
timeout 10 C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_connection_status.py -v -s --tb=short
```

### 17 MCP Tools to Test
**Portfolio & Account (5 tools):**
1. `get_portfolio` - Portfolio positions and P&L
2. `get_account_summary` - Account balances and metrics  
3. `get_accounts` - Available IBKR accounts
4. `switch_account` - Change active account
5. `get_connection_status` - IBKR connection health

**Market Data (2 tools):**
6. `get_market_data` - Live stock quotes (global)
7. `resolve_international_symbol` - Exchange/currency resolution

**Forex & Currency (2 tools):**
8. `get_forex_rates` - Live forex rates (21 pairs)
9. `convert_currency` - Multi-currency conversion

**Risk Management (4 tools):**
10. `place_stop_loss` - Create stop orders (READ-ONLY testing)
11. `get_stop_losses` - View active stops
12. `modify_stop_loss` - Change stop order (READ-ONLY testing)
13. `cancel_stop_loss` - Remove stop order (READ-ONLY testing)

**Order Management (3 tools):**
14. `get_open_orders` - View pending orders
15. `get_completed_orders` - View recent trades
16. `get_executions` - Detailed execution info

**Documentation (1 tool):**
17. `get_tool_documentation` - Help system

### Test Structure Requirements
Each test must use the **call_tool()** interface:
```python
@pytest.mark.paper
class TestPaperTradingMCPTools:
    """Test all 17 MCP tools with live paper trading connection"""
    
    async def test_get_connection_status_tool(self):
        """Test get_connection_status MCP tool"""
        result = await call_tool("get_connection_status", {})
        
        # Validate MCP response structure
        assert "success" in result
        assert result["success"] is True
        assert "data" in result
        
        # Validate IBKR connection data
        connection_data = result["data"]
        assert "status" in connection_data
        assert "account" in connection_data
        assert connection_data["account"].startswith("DU")  # Paper account
```

## MCP Response Structure Validation

### Required Response Format
Every MCP tool must return standardized response structure:
```python
# Success Response
{
    "success": True,
    "data": { /* Tool-specific data */ },
    "metadata": { /* Optional metadata */ }
}

# Error Response  
{
    "success": False,
    "error": "Description of error",
    "details": { /* Optional error details */ }
}
```

### Validation Requirements
Each test must verify:
1. **Response Structure**: Correct success/error format
2. **Data Integrity**: Expected data fields and types  
3. **Error Handling**: Proper error responses for invalid inputs
4. **Safety Integration**: Safety framework responses when applicable
5. **Performance**: Response times within acceptable limits (<10 seconds)

## Target Test Suite Structure

### Primary Test File: `test_paper_mcp_tools.py`
```python
@pytest.mark.paper
class TestPaperTradingMCPTools:
    """Test all 17 MCP tools with live paper trading"""
    
    # Portfolio & Account Tools (5 tests)
    async def test_get_connection_status_tool(self):
        """Test connection status MCP tool"""
        result = await call_tool("get_connection_status", {})
        # Validate MCP response + IBKR connection data
    
    async def test_get_accounts_tool(self):  
        """Test accounts listing MCP tool"""
        result = await call_tool("get_accounts", {})
        # Validate account list with paper account detection
    
    async def test_get_account_summary_tool(self):
        """Test account summary MCP tool"""  
        result = await call_tool("get_account_summary", {})
        # Validate account balances and currency breakdown
    
    async def test_get_portfolio_tool(self):
        """Test portfolio MCP tool"""
        result = await call_tool("get_portfolio", {})
        # Validate portfolio positions (may be empty)
    
    async def test_switch_account_tool(self):
        """Test account switching MCP tool"""
        # Get current account first
        accounts = await call_tool("get_accounts", {})
        current_account = accounts["data"]["current_account"]
        
        # Test switching to same account (safe operation)
        result = await call_tool("switch_account", {"account_id": current_account})
        # Validate successful switch confirmation
    
    # Market Data Tools (2 tests)
    async def test_get_market_data_tool(self):
        """Test market data MCP tool"""
        result = await call_tool("get_market_data", {"symbols": "AAPL"})
        # Validate US stock quote with price/bid/ask
    
    async def test_get_international_market_data_tool(self):
        """Test international market data MCP tool"""  
        result = await call_tool("get_market_data", {"symbols": "ASML"})
        # Validate auto-detection to AEB/EUR with pricing
    
    async def test_resolve_international_symbol_tool(self):
        """Test symbol resolution MCP tool"""
        result = await call_tool("resolve_international_symbol", {"symbol": "ASML"})
        # Validate exchange/currency resolution to AEB/EUR
    
    # Forex & Currency Tools (2 tests)
    async def test_get_forex_rates_tool(self):
        """Test forex rates MCP tool"""
        result = await call_tool("get_forex_rates", {"currency_pairs": "EURUSD"})
        # Validate forex rate with bid/ask spread
    
    async def test_convert_currency_tool(self):
        """Test currency conversion MCP tool"""
        result = await call_tool("convert_currency", {
            "amount": 1000.0,
            "from_currency": "USD", 
            "to_currency": "EUR"
        })
        # Validate conversion with live rates
    
    # Risk Management Tools (4 tests - READ-ONLY)
    async def test_get_stop_losses_tool(self):
        """Test get stop losses MCP tool (read-only)"""
        result = await call_tool("get_stop_losses", {})
        # Validate stop loss list (likely empty for new paper account)
    
    async def test_place_stop_loss_tool_validation(self):
        """Test stop loss placement parameter validation"""
        # Test parameter validation without actual order placement
        result = await call_tool("place_stop_loss", {
            "symbol": "AAPL",
            "action": "SELL", 
            "quantity": 0,  # Invalid quantity should be caught
            "stop_price": 180.0
        })
        # Should return validation error through MCP layer
        assert result["success"] is False
        assert "quantity" in result.get("error", "").lower()
    
    async def test_modify_stop_loss_tool_validation(self):
        """Test stop loss modification parameter validation"""
        result = await call_tool("modify_stop_loss", {
            "order_id": 99999,  # Non-existent order ID
            "stop_price": 185.0
        })
        # Should handle non-existent order gracefully
    
    async def test_cancel_stop_loss_tool_validation(self):
        """Test stop loss cancellation parameter validation"""  
        result = await call_tool("cancel_stop_loss", {"order_id": 99999})
        # Should handle non-existent order gracefully
    
    # Order Management Tools (3 tests - READ-ONLY)
    async def test_get_open_orders_tool(self):
        """Test get open orders MCP tool"""
        result = await call_tool("get_open_orders", {})
        # Validate open orders list (likely empty)
    
    async def test_get_completed_orders_tool(self):
        """Test get completed orders MCP tool"""
        result = await call_tool("get_completed_orders", {})
        # Validate completed orders list (may be empty)
    
    async def test_get_executions_tool(self):
        """Test get executions MCP tool"""
        result = await call_tool("get_executions", {})
        # Validate execution details (may be empty)
    
    # Documentation Tool (1 test)
    async def test_get_tool_documentation_tool(self):
        """Test documentation MCP tool"""
        result = await call_tool("get_tool_documentation", {
            "tool_or_category": "forex"
        })
        # Validate documentation content returned
        assert result["success"] is True
        assert "forex" in result["data"].lower()
    
    # Error Handling Tests (3 tests)
    async def test_invalid_tool_parameters(self):
        """Test MCP tool parameter validation"""
        # Test various invalid parameters through MCP layer
        result = await call_tool("get_market_data", {"symbols": ""})  # Empty symbol
        assert result["success"] is False
        
        result = await call_tool("convert_currency", {
            "amount": -1000,  # Negative amount
            "from_currency": "USD",
            "to_currency": "EUR" 
        })
        assert result["success"] is False
    
    async def test_invalid_currency_conversion(self):
        """Test invalid currency conversion through MCP"""
        result = await call_tool("convert_currency", {
            "amount": 1000.0,
            "from_currency": "INVALID",  # Invalid currency
            "to_currency": "USD"
        })
        assert result["success"] is False
        assert "currency" in result.get("error", "").lower()
    
    async def test_invalid_symbol_handling(self):
        """Test invalid symbol handling through MCP"""
        result = await call_tool("get_market_data", {"symbols": "INVALID123"})
        # Should handle invalid symbols gracefully with proper MCP error response
        assert result["success"] is False
        assert "symbol" in result.get("error", "").lower()
```

## Implementation Plan

### Phase 1: IMMEDIATE - Rewrite All Tests for MCP Layer
**Priority: CRITICAL** - All current tests are testing wrong layer!

1. **Audit Current Tests** - Identify which tests bypass MCP layer
2. **Convert Client Calls** - Replace client.method() with call_tool()
3. **Add MCP Validation** - Verify proper MCP response structure
4. **Test All 17 Tools** - Ensure complete MCP tool coverage

### Phase 2: Integration with Safety Framework
Test safety framework integration through MCP layer:
- **Trading controls** - Verify trading disabled by default
- **Order limits** - Test size and value limits through MCP
- **Kill switch** - Test emergency halt through MCP interface
- **Rate limiting** - Verify API rate limiting via MCP

### Phase 3: Production Validation
- **Extended Testing** - Multiple consecutive test runs
- **Error Injection** - Network interruption simulation
- **Load Testing** - API rate limit verification

## Individual Test Development Strategy

### Iterative, Isolated Testing Approach
To address the complexity of debugging each MCP tool individually, we implement an **individual test development system**:

#### **Core Concept: One Tool Per File**
```
tests/paper/individual/
├── test_individual_template.py           # Template for new tests
├── test_individual_get_connection_status.py  # Working example
├── test_individual_get_accounts.py       # Individual tool tests
├── test_individual_get_portfolio.py      # One tool per file
├── run_individual_test.bat/.sh          # Easy execution scripts
└── README.md                           # Complete documentation
```

#### **Development Workflow**
1. **Copy Template** - Start with `test_individual_template.py`
2. **Customize Tool** - Replace placeholders with specific MCP tool details
3. **Iterate Debug** - Run single test repeatedly until working perfectly
4. **Graduate to Suite** - Move working test logic to consolidated suite

#### **Template Usage Pattern**
```python
# Template structure for any MCP tool
@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividual[ToolName]:
    async def test_[tool_name]_basic_functionality(self):
        # MCP tool call with proper call_tool() interface
        result = await call_tool("[tool_name]", {parameters})
        
        # MCP response structure validation
        assert "success" in result
        if result["success"]:
            assert "data" in result
            # Tool-specific validation
        else:
            assert "error" in result
```

#### **Execution Options**
```bash
# Method 1: Dedicated runner script
run_individual_test.bat get_connection_status

# Method 2: Direct Python execution  
python test_individual_get_connection_status.py

# Method 3: Pytest with debug options
pytest test_individual_get_connection_status.py -v -s --tb=long
```

#### **Benefits of Individual Testing**
- ✅ **Fast Iteration** - Modify and rerun single test quickly
- ✅ **Isolated Debugging** - Focus on one tool without distractions
- ✅ **Independent Development** - Work on multiple tools in parallel
- ✅ **Precise Error Identification** - Know exactly which tool has issues
- ✅ **Gradual Progress** - Build confidence one tool at a time
- ✅ **Template Reuse** - Consistent structure across all MCP tools

## Implementation Plan

### Phase 1: Individual Test Development (NEW PRIORITY)
1. **Create Individual Tests** - Use template system for each MCP tool
2. **Iterative Debugging** - Perfect each tool test in isolation  
3. **Validate MCP Interface** - Ensure proper call_tool() usage
4. **Build Working Examples** - Create 3-4 proven individual tests

### Phase 2: Tool-by-Tool Validation
1. **Connection Tools** - get_connection_status, get_accounts (foundation)
2. **Market Data Tools** - get_market_data, resolve_international_symbol
3. **Forex Tools** - get_forex_rates, convert_currency
4. **Portfolio Tools** - get_portfolio, get_account_summary
5. **Order Tools** - get_open_orders, get_completed_orders (read-only)

### Phase 3: Consolidated Suite Creation
1. **Graduate Working Tests** - Move proven individual tests to main suite
2. **Shared Connection Pattern** - Implement single long-lived connection
3. **Complete Integration** - All 17 MCP tools in consolidated test suite

### Phase 4: Safety Framework Integration
Test safety framework integration through MCP layer:
- **Trading controls** - Verify trading disabled by default
- **Order limits** - Test size and value limits through MCP
- **Kill switch** - Test emergency halt through MCP interface
- **Rate limiting** - Verify API rate limiting via MCP

### Phase 5: Production Validation
- **Extended Testing** - Multiple consecutive test runs
- **Error Injection** - Network interruption simulation
- **Load Testing** - API rate limit verification

## Success Criteria for Completion

### Technical Requirements - MCP Layer
- ✅ All 17 MCP tools tested through call_tool() interface
- ✅ Proper MCP response structure validation
- ✅ Parameter validation testing for each tool
- ✅ Safety framework integration verified
- ✅ Error handling through MCP layer validated

### Individual Test Success Criteria
- ✅ Each tool test works perfectly in isolation
- ✅ Template system enables rapid test creation
- ✅ Iterative debugging process proven effective
- ✅ All 17 tools have individual test coverage
- ✅ Working tests ready for graduation to main suite

### Operational Requirements
- ✅ Tests represent actual Claude Desktop usage patterns
- ✅ Complete end-to-end MCP protocol validation
- ✅ Real IBKR API integration through MCP layer
- ✅ Proper timeout and error handling

## Next Steps - INDIVIDUAL TESTING PRIORITY

### 1. Start with Individual Test Development (RECOMMENDED)
Use the new individual testing system for iterative development:
```bash
# Test the first working example
cd C:\Users\sean\Documents\Projects\ibkr-mcp-server
tests\paper\individual\run_individual_test.bat get_connection_status

# Create next priority tests using template
cp tests\paper\individual\test_individual_template.py tests\paper\individual\test_individual_get_accounts.py
# Customize for get_accounts tool and test iteratively
```

### 2. Build Core Foundation Tests (Phase 1)
Create and perfect these critical individual tests:
1. **get_connection_status** ✅ (Already created)
2. **get_accounts** (Copy from template, customize)
3. **get_account_summary** (Copy from template, customize)
4. **get_portfolio** (Copy from template, customize)

### 3. Validate Individual Test Approach
Confirm the individual testing methodology works:
- Test each tool in complete isolation
- Validate proper MCP call_tool() interface usage
- Ensure MCP response structure validation
- Debug any import or infrastructure issues

### 4. Scale to All 17 MCP Tools
Once individual testing approach proven:
- Create individual tests for all remaining tools
- Use template system for consistent structure
- Perfect each tool test through iteration
- Build library of working individual test examples

### 5. Graduate to Consolidated Suite
After individual tests work:
- Move proven test logic to consolidated suite
- Implement shared connection pattern
- Create single comprehensive test file
- Maintain individual tests for future debugging

## Legacy Conversion (If Needed)

If maintaining existing tests, convert them properly:

### Audit Current Tests (CRITICAL)
```bash
# Find direct client calls (WRONG LAYER)
grep -r "client\." tests/paper/  
grep -r "await.*\\.get_" tests/paper/

# Find correct MCP calls
grep -r "call_tool" tests/paper/  
```

### Convert Incorrect Tests
```python
# BEFORE (Wrong Layer - Delete This)
result = await client.get_accounts()

# AFTER (Correct MCP Layer - Use This)  
result = await call_tool("get_accounts", {})
```

### Add MCP Response Structure Validation
```python
# Every MCP tool test must include:
assert "success" in result
assert isinstance(result["success"], bool)
if result["success"]:
    assert "data" in result
else:
    assert "error" in result
```

---

**CRITICAL STATUS**: Current tests bypass MCP layer entirely!  
**IMMEDIATE ACTION**: Rewrite all paper tests to use call_tool() interface  
**TARGET**: Test the complete MCP stack that Claude Desktop actually uses  
**DEADLINE**: Fix before any production deployment - we're testing wrong layer!
