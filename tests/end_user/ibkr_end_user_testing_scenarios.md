# IBKR MCP Server End-User Testing Scenarios

## Overview

This document provides 10 comprehensive testing scenarios designed to exercise all 23 MCP tools through realistic end-user workflows. Each scenario tests multiple tools in logical sequences that mirror actual trading activities.

## Prerequisites

- IBKR MCP Server configured and running
- Paper trading account active (DU* prefix)
- IB Gateway connected on port 7497
- Claude Desktop with IBKR MCP tools enabled
- All safety settings configured appropriately

## Testing Approach

- Run scenarios **one at a time** in sequence
- **Document any errors or unexpected behavior**
- **Note response times** for performance issues
- **Verify data accuracy** against IBKR Client Portal
- **Test both success and error cases**

---

## Scenario 1: System Health Check and Basic Connection

**Objective:** Verify core system functionality and connection stability  
**Tools Tested:** 5 tools  

### Test Steps:

1. **Connection Status Check**
   ```
   "Check my IBKR connection status"
   ```
   **Expected:** Connected to paper trading, client ID shown, account DU* format
   **Tools:** `get_connection_status`

2. **Account Information**
   ```
   "Show me all my IBKR accounts"
   ```
   **Expected:** List of accounts with current account marked  
   **Tools:** `get_accounts`

3. **Account Balance Overview**
   ```
   "What's my account balance?"
   ```
   **Expected:** Multi-currency balances, buying power, portfolio value  
   **Tools:** `get_account_summary`

4. **Portfolio Review**
   ```
   "Show me my current portfolio"
   ```
   **Expected:** Position list (may be empty), P&L data, market values  
   **Tools:** `get_portfolio`

5. **Documentation System Test**
   ```
   "Help with portfolio management"
   ```
   **Expected:** Comprehensive help documentation returned  
   **Tools:** `get_tool_documentation`

### Success Criteria:
- All tools respond within 10 seconds
- Connection shows "paper trading" mode
- Account data matches IBKR Client Portal
- No connection errors or timeouts

---

## Scenario 2: US Market Data and Research

**Objective:** Test US market data capabilities and quote accuracy  
**Tools Tested:** 2 tools  

### Test Steps:

1. **Single US Stock Quote**
   ```
   "What's Apple trading at right now?"
   ```
   **Expected:** AAPL quote with bid/ask, volume, exchange=SMART, currency=USD  
   **Tools:** `get_market_data`

2. **Multiple US Stocks**
   ```
   "Get quotes for Apple, Microsoft, and Google"
   ```
   **Expected:** AAPL, MSFT, GOOGL quotes with current prices  
   **Tools:** `get_market_data`

3. **Large-Cap Technology Stocks**
   ```
   "Get quotes for AAPL, MSFT, GOOGL, AMZN, TSLA, META"
   ```
   **Expected:** All 6 tech stocks with live market data  
   **Tools:** `get_market_data`

4. **Stock Symbol Resolution**
   ```
   "Where does Apple trade and in what currency?"
   ```
   **Expected:** SMART exchange, USD currency, company details  
   **Tools:** `resolve_international_symbol`

### Success Criteria:
- All quotes return current market data
- Bid/ask spreads are reasonable
- Volume data is present
- Response times under 5 seconds
- Price data matches external sources

---

## Scenario 3: International Markets and Global Trading

**Objective:** Test international market data and symbol resolution  
**Tools Tested:** 2 tools  

### Test Steps:

1. **European Stock Quotes**
   ```
   "Get quotes for ASML and SAP"
   ```
   **Expected:** ASML (AEB/EUR), SAP (XETRA/EUR) with auto-detection  
   **Tools:** `get_market_data`

2. **Asian Market Quotes**
   ```
   "Get quotes for Toyota and Samsung"
   ```
   **Expected:** 7203 (TSE/JPY), 005930 (KSE/KRW) with proper symbols  
   **Tools:** `get_market_data`

3. **Mixed Global Markets**
   ```
   "Get quotes for Apple, ASML, Toyota, and Vodafone"
   ```
   **Expected:** US, Dutch, Japanese, UK stocks with correct exchanges  
   **Tools:** `get_market_data`

4. **International Symbol Resolution**
   ```
   "Where does ASML trade?"
   ```
   **Expected:** AEB (Amsterdam), EUR currency, company details  
   **Tools:** `resolve_international_symbol`

5. **Complex International Resolution**
   ```
   "Where does Toyota trade?"
   ```
   **Expected:** TSE (Tokyo), JPY currency, symbol 7203  
   **Tools:** `resolve_international_symbol`

### Success Criteria:
- Auto-detection works for all international symbols
- Correct exchanges and currencies identified
- Price data in native currencies
- USD equivalents provided where applicable

---

## Scenario 4: Forex Trading and Currency Operations

**Objective:** Test forex rates and currency conversion functionality  
**Tools Tested:** 2 tools  

### Test Steps:

1. **Major Forex Pair**
   ```
   "What's the current EUR/USD rate?"
   ```
   **Expected:** Live EURUSD rate with bid/ask spread  
   **Tools:** `get_forex_rates`

2. **Multiple Major Pairs**
   ```
   "Show me rates for EUR/USD, GBP/USD, and USD/JPY"
   ```
   **Expected:** 3 major pairs with live rates and spreads  
   **Tools:** `get_forex_rates`

3. **Cross Currency Pairs**
   ```
   "Get rates for EUR/GBP, EUR/JPY, and GBP/JPY"
   ```
   **Expected:** Cross pairs with calculated rates  
   **Tools:** `get_forex_rates`

4. **Simple Currency Conversion**
   ```
   "Convert $5000 to Euros"
   ```
   **Expected:** USD to EUR conversion with live rate and amount  
   **Tools:** `convert_currency`

5. **Complex Cross-Currency Conversion**
   ```
   "How much is £2000 in Japanese Yen?"
   ```
   **Expected:** GBP to JPY conversion via USD cross-rate  
   **Tools:** `convert_currency`

6. **Large Amount Conversion**
   ```
   "Convert €50,000 to US Dollars"
   ```
   **Expected:** EUR to USD conversion with proper decimal precision  
   **Tools:** `convert_currency`

### Success Criteria:
- All forex rates show tight spreads (< 5 pips for majors)
- Currency conversions use live rates
- Cross-currency calculations are accurate
- Proper handling of decimal precision

---

## Scenario 5: Order Management and Order History

**Objective:** Test order information retrieval and order management  
**Tools Tested:** 3 tools  

### Test Steps:

1. **Open Orders Review**
   ```
   "Show me my pending orders"
   ```
   **Expected:** List of open orders (likely empty for fresh paper account)  
   **Tools:** `get_open_orders`

2. **Completed Orders History**
   ```
   "Show me my recent trades"
   ```
   **Expected:** List of completed orders (may be empty)  
   **Tools:** `get_completed_orders`

3. **Execution Details**
   ```
   "Get my execution details for the last 7 days"
   ```
   **Expected:** Detailed execution information (may be empty)  
   **Tools:** `get_executions`

4. **Filtered Execution History**
   ```
   "Show me Apple executions from the last 30 days"
   ```
   **Expected:** AAPL-specific executions or appropriate empty response  
   **Tools:** `get_executions`

5. **Account-Specific Orders**
   ```
   "Show me all pending orders for my current account"
   ```
   **Expected:** Orders filtered by current account  
   **Tools:** `get_open_orders`

### Success Criteria:
- Tools handle empty states gracefully
- Proper data structure returned even when no orders exist
- Account filtering works correctly
- No errors on empty result sets

---

## Scenario 6: Risk Management and Stop Loss Testing

**Objective:** Test stop loss capabilities and risk management tools  
**Tools Tested:** 4 tools  

### Test Steps:

1. **Current Stop Loss Review**
   ```
   "Show me all my stop loss orders"
   ```
   **Expected:** List of active stops (likely empty)  
   **Tools:** `get_stop_losses`

2. **Stop Loss Parameter Validation**
   ```
   "Set a stop loss on Apple: 0 shares at $180"
   ```
   **Expected:** Parameter validation error for invalid quantity  
   **Tools:** `place_stop_loss`

3. **Stop Loss with Invalid Symbol**
   ```
   "Set a stop loss on INVALID123: 100 shares at $50"
   ```
   **Expected:** Symbol validation error  
   **Tools:** `place_stop_loss`

4. **Stop Loss Modification Test**
   ```
   "Modify stop loss order #99999 to $185"
   ```
   **Expected:** Graceful error for non-existent order ID  
   **Tools:** `modify_stop_loss`

5. **Stop Loss Cancellation Test**
   ```
   "Cancel stop loss order #99999"
   ```
   **Expected:** Graceful error for non-existent order ID  
   **Tools:** `cancel_stop_loss`

### Success Criteria:
- Parameter validation catches invalid inputs
- Graceful error handling for non-existent orders
- Proper safety framework integration
- Clear error messages for invalid operations

---

## Scenario 7: Order Placement Validation Testing

**Objective:** Test order placement capabilities and validation  
**Tools Tested:** 6 tools  

### Test Steps:

1. **Market Order Validation**
   ```
   "Buy 0 shares of Apple at market price"
   ```
   **Expected:** Parameter validation error for invalid quantity  
   **Tools:** `place_market_order`

2. **Limit Order Validation**
   ```
   "Place a limit order: buy Tesla at $0 limit"
   ```
   **Expected:** Parameter validation error for invalid price  
   **Tools:** `place_limit_order`

3. **Bracket Order Validation**
   ```
   "Place bracket order: buy AAPL at $180, stop $190, target $170"
   ```
   **Expected:** Logic validation error (stop > entry > target)  
   **Tools:** `place_bracket_order`

4. **Order Status Check**
   ```
   "Check the status of order #99999"
   ```
   **Expected:** Graceful error for non-existent order  
   **Tools:** `get_order_status`

5. **Order Modification Test**
   ```
   "Modify order #99999 to 200 shares"
   ```
   **Expected:** Graceful error for non-existent order  
   **Tools:** `modify_order`

6. **Order Cancellation Test**
   ```
   "Cancel order #99999"
   ```
   **Expected:** Graceful error for non-existent order  
   **Tools:** `cancel_order`

### Success Criteria:
- All validation rules properly enforced
- Safety framework prevents invalid orders
- Clear error messages for validation failures
- Graceful handling of non-existent order IDs

---

## Scenario 8: Account Management and Multi-Account Testing

**Objective:** Test account switching and management capabilities  
**Tools Tested:** 2 tools  

### Test Steps:

1. **Current Account Information**
   ```
   "What account am I currently using?"
   ```
   **Expected:** Current account details with DU prefix  
   **Tools:** `get_accounts`

2. **Account Switch Test (Same Account)**
   ```
   "Switch to account DU123456" (use actual account ID from step 1)
   ```
   **Expected:** Successful switch confirmation to same account  
   **Tools:** `switch_account`

3. **Account Switch Validation**
   ```
   "Switch to account INVALID123"
   ```
   **Expected:** Validation error for invalid account ID  
   **Tools:** `switch_account`

4. **Post-Switch Verification**
   ```
   "Show me my current account details"
   ```
   **Expected:** Account details showing correct active account  
   **Tools:** `get_accounts`

5. **Account Balance After Switch**
   ```
   "What's my account balance after switching?"
   ```
   **Expected:** Balance information for the active account  
   **Tools:** `get_account_summary`

### Success Criteria:
- Account switching works correctly
- Validation prevents invalid account switches
- Account information remains consistent
- Balance data updates correctly after switch

---

## Scenario 9: Error Handling and Edge Cases

**Objective:** Test system behavior with invalid inputs and edge cases  
**Tools Tested:** Multiple tools with error conditions  

### Test Steps:

1. **Invalid Symbol Testing**
   ```
   "Get quotes for INVALID123, FAKE456, NOTREAL789"
   ```
   **Expected:** Graceful error handling for all invalid symbols  
   **Tools:** `get_market_data`

2. **Invalid Currency Conversion**
   ```
   "Convert $1000 from INVALID to USD"
   ```
   **Expected:** Currency validation error  
   **Tools:** `convert_currency`

3. **Invalid Forex Pairs**
   ```
   "Get rates for INVALID/USD, FAKE/EUR"
   ```
   **Expected:** Forex pair validation errors  
   **Tools:** `get_forex_rates`

4. **Large Number Testing**
   ```
   "Convert $999999999 to Euros"
   ```
   **Expected:** Proper handling of large amounts  
   **Tools:** `convert_currency`

5. **Empty Parameter Testing**
   ```
   "Get quotes for"
   ```
   **Expected:** Parameter validation error for missing symbol  
   **Tools:** `get_market_data`

6. **Documentation Edge Cases**
   ```
   "Help with NONEXISTENT_CATEGORY"
   ```
   **Expected:** Graceful error or default help content  
   **Tools:** `get_tool_documentation`

### Success Criteria:
- All invalid inputs handled gracefully
- No system crashes or timeouts
- Clear, helpful error messages
- Proper validation at MCP tool level

---

## Scenario 10: Comprehensive Integration Workflow

**Objective:** Test multiple tools in realistic trading workflow  
**Tools Tested:** Multiple tools in sequence  

### Test Steps:

1. **Morning System Check**
   ```
   "Check my connection and show me my portfolio"
   ```
   **Expected:** Connection status and portfolio overview  
   **Tools:** `get_connection_status`, `get_portfolio`

2. **Market Research Phase**
   ```
   "Get quotes for Apple, Microsoft, ASML, and show me EUR/USD rate"
   ```
   **Expected:** Mixed US/international quotes plus forex rate  
   **Tools:** `get_market_data`, `get_forex_rates`

3. **Currency Analysis**
   ```
   "Convert €10,000 to USD and show me GBP/USD rate"
   ```
   **Expected:** Currency conversion and additional forex rate  
   **Tools:** `convert_currency`, `get_forex_rates`

4. **Risk Assessment**
   ```
   "Show me my current stop losses and pending orders"
   ```
   **Expected:** Risk management overview  
   **Tools:** `get_stop_losses`, `get_open_orders`

5. **Account Analysis**
   ```
   "What's my buying power and account balance?"
   ```
   **Expected:** Complete account financial overview  
   **Tools:** `get_account_summary`

6. **Documentation Lookup**
   ```
   "Help with international trading"
   ```
   **Expected:** Comprehensive international trading help  
   **Tools:** `get_tool_documentation`

7. **Final System Status**
   ```
   "Show me my execution history and verify my connection"
   ```
   **Expected:** Execution details and connection confirmation  
   **Tools:** `get_executions`, `get_connection_status`

### Success Criteria:
- All tools work seamlessly together
- No performance degradation over extended use
- Data consistency across all tools
- Smooth workflow with realistic usage patterns

---

## Complex Interpretation Scenarios (11-15)

These scenarios test Claude's ability to interpret complex user requests and intelligently combine multiple MCP tools to provide comprehensive responses.

---

## Scenario 11: Portfolio Risk Assessment and Rebalancing Analysis

**Objective:** Test intelligent portfolio analysis requiring multiple data sources and calculations  
**User Request:** *"I'm worried about my portfolio risk. Can you analyze my current positions, check how they're performing today, assess my currency exposure, and recommend if I should set up better protection?"*

**Required Tool Combinations:**
- Portfolio analysis + market data + forex rates + risk management
- Multi-step interpretation and data synthesis

### Expected Tool Sequence:

1. **Portfolio Assessment**
   ```
   Tools: get_portfolio, get_account_summary
   Purpose: Understand current holdings and account status
   ```

2. **Current Market Performance**
   ```
   Tools: get_market_data (for each position)
   Purpose: Get live quotes for all holdings
   ```

3. **Currency Risk Analysis**
   ```
   Tools: get_forex_rates, convert_currency
   Purpose: Assess foreign exchange exposure
   ```

4. **Risk Management Review**
   ```
   Tools: get_stop_losses, get_open_orders
   Purpose: Evaluate current protection levels
   ```

5. **Integration Analysis**
   ```
   Expected: Claude synthesizes all data to provide:
   - Position-level performance summary
   - Currency exposure percentage breakdown
   - Risk assessment with specific recommendations
   - Stop loss coverage analysis
   - Actionable next steps for portfolio protection
   ```

### Success Criteria:
- Automatically identifies all portfolio positions
- Calculates real-time performance for each position
- Quantifies currency exposure risk
- Provides specific, actionable recommendations
- Demonstrates understanding of portfolio risk concepts

---

## Scenario 12: Global Market Opportunity Analysis

**Objective:** Test international market research requiring symbol resolution and cross-market comparison  
**User Request:** *"I'm interested in semiconductor companies. Can you show me how ASML compares to US chip stocks, what the currency implications are for European investments, and help me understand the trading logistics?"*

**Required Tool Combinations:**
- Market data + symbol resolution + forex analysis + documentation
- Cross-market comparison and educational synthesis

### Expected Tool Sequence:

1. **Semiconductor Stock Research**
   ```
   Tools: get_market_data (ASML, NVDA, AMD, INTC, etc.)
   Purpose: Compare global semiconductor stocks
   ```

2. **International Symbol Analysis**
   ```
   Tools: resolve_international_symbol (ASML)
   Purpose: Understand European trading mechanics
   ```

3. **Currency Impact Assessment**
   ```
   Tools: get_forex_rates (EUR/USD), convert_currency
   Purpose: Calculate currency implications
   ```

4. **Trading Education**
   ```
   Tools: get_tool_documentation (international trading)
   Purpose: Explain international trading concepts
   ```

5. **Synthesis Response**
   ```
   Expected: Claude provides:
   - Comparative analysis of semiconductor stocks by region
   - ASML vs US competitors performance comparison
   - Currency risk explanation with EUR/USD impact
   - Step-by-step guide for international trading
   - Risk considerations for European investments
   ```

### Success Criteria:
- Identifies relevant comparison stocks automatically
- Performs meaningful cross-market analysis
- Explains currency implications clearly
- Provides educational context about international trading
- Offers practical next steps for investment consideration

---

## Scenario 13: Trading Strategy Validation and Setup

**Objective:** Test trading strategy analysis requiring order validation and risk calculation  
**User Request:** *"I want to buy $10,000 worth of Apple with a 15% stop loss and 25% profit target. Can you help me calculate the right position size, set up the orders properly, and make sure I'm not exceeding my risk limits?"*

**Required Tool Combinations:**
- Account analysis + market data + order calculation + risk validation
- Mathematical calculations and safety verification

### Expected Tool Sequence:

1. **Account Capacity Check**
   ```
   Tools: get_account_summary
   Purpose: Verify available buying power
   ```

2. **Current Market Data**
   ```
   Tools: get_market_data (AAPL)
   Purpose: Get current price for calculations
   ```

3. **Position Size Calculation**
   ```
   Expected: Claude calculates:
   - Shares = $10,000 ÷ current AAPL price
   - Stop loss price = current price × 0.85
   - Profit target = current price × 1.25
   ```

4. **Order Structure Validation**
   ```
   Tools: place_bracket_order (validation mode)
   Purpose: Test order parameters for validity
   ```

5. **Risk Assessment**
   ```
   Tools: get_portfolio (for position sizing context)
   Purpose: Ensure trade fits portfolio risk profile
   ```

6. **Comprehensive Response**
   ```
   Expected: Claude provides:
   - Exact position size calculation
   - Stop loss and profit target prices
   - Risk-reward ratio analysis
   - Percentage of portfolio at risk
   - Step-by-step order placement instructions
   - Alternative position sizes if $10k exceeds limits
   ```

### Success Criteria:
- Performs accurate mathematical calculations
- Validates order parameters before suggesting placement
- Assesses risk relative to total portfolio
- Provides clear, actionable trading instructions
- Includes appropriate risk warnings and alternatives

---

## Scenario 14: Multi-Currency Investment Planning

**Objective:** Test complex currency analysis requiring multiple conversions and market data  
**User Request:** *"I have $50,000 to invest internationally. Can you show me what that would buy in European and Asian markets, compare some good international stocks, and help me understand the currency risks I'd be taking on?"*

**Required Tool Combinations:**
- Currency conversion + international market data + risk analysis + education
- Multi-step planning with risk assessment

### Expected Tool Sequence:

1. **Currency Conversion Analysis**
   ```
   Tools: convert_currency (USD→EUR, USD→JPY, USD→GBP)
   get_forex_rates (major pairs)
   Purpose: Calculate purchasing power in different currencies
   ```

2. **International Stock Research**
   ```
   Tools: get_market_data (ASML, SAP, 7203, 005930, VOD)
   resolve_international_symbol (for each)
   Purpose: Analyze quality international stocks
   ```

3. **Currency Risk Assessment**
   ```
   Tools: get_forex_rates (historical context via documentation)
   Purpose: Explain currency volatility concepts
   ```

4. **Educational Context**
   ```
   Tools: get_tool_documentation (international trading, forex)
   Purpose: Provide currency risk education
   ```

5. **Investment Planning Synthesis**
   ```
   Expected: Claude provides:
   - Purchasing power in EUR (€X), JPY (¥X), GBP (£X)
   - Share quantities possible for each international stock
   - Currency risk explanation with specific examples
   - Diversification recommendations across regions
   - Hedging strategy suggestions
   - Timeline considerations for currency moves
   ```

### Success Criteria:
- Accurate multi-currency calculations
- Meaningful international stock comparisons
- Clear currency risk explanation with examples
- Practical diversification recommendations
- Educational value about international investing

---

## Scenario 15: Comprehensive Portfolio Audit and Optimization

**Objective:** Test full portfolio analysis requiring all data sources and strategic thinking  
**User Request:** *"I want a complete review of my trading setup. Can you audit my current positions, check my protection levels, analyze my recent trading performance, assess my risk management, and give me a comprehensive improvement plan?"*

**Required Tool Combinations:**
- All portfolio tools + market data + order history + risk management + documentation
- Comprehensive analysis and strategic recommendations

### Expected Tool Sequence:

1. **Complete Portfolio Snapshot**
   ```
   Tools: get_portfolio, get_account_summary, get_connection_status
   Purpose: Full account overview and system status
   ```

2. **Current Market Valuation**
   ```
   Tools: get_market_data (for all positions)
   Purpose: Real-time valuation of all holdings
   ```

3. **Trading History Analysis**
   ```
   Tools: get_completed_orders, get_executions
   Purpose: Performance and execution quality review
   ```

4. **Risk Management Assessment**
   ```
   Tools: get_stop_losses, get_open_orders
   Purpose: Evaluate current protection and pending activity
   ```

5. **Currency and International Exposure**
   ```
   Tools: get_forex_rates, convert_currency (for international positions)
   Purpose: Multi-currency risk assessment
   ```

6. **Educational Enhancement**
   ```
   Tools: get_tool_documentation (relevant categories)
   Purpose: Provide improvement strategies
   ```

7. **Comprehensive Audit Report**
   ```
   Expected: Claude synthesizes all data into:
   - Portfolio composition and diversification analysis
   - Real-time P&L with performance metrics
   - Risk management scorecard and gaps
   - Currency exposure breakdown
   - Trading execution quality assessment
   - Specific improvement recommendations with priorities
   - Action plan with step-by-step implementation
   - Risk mitigation strategies
   - Performance benchmarking suggestions
   ```

### Success Criteria:
- Integrates data from all relevant tools seamlessly
- Provides quantitative analysis with specific metrics
- Identifies concrete improvement opportunities
- Prioritizes recommendations by impact and urgency
- Demonstrates sophisticated understanding of portfolio management
- Offers actionable next steps with clear rationale

---

## Complex Scenario Success Metrics

### Interpretation Quality:
- **Context Understanding**: 95% accurate interpretation of user intent
- **Tool Selection**: Optimal tool combinations for each request
- **Data Integration**: Seamless synthesis of multiple data sources
- **Response Completeness**: Addresses all aspects of complex requests

### Technical Performance:
- **Multi-Tool Coordination**: All tool sequences execute without errors
- **Data Consistency**: Information from different tools aligns properly
- **Calculation Accuracy**: Mathematical operations are precise
- **Performance**: Complex scenarios complete within 60 seconds

### Educational Value:
- **Concept Explanation**: Clear explanation of complex financial concepts
- **Risk Communication**: Appropriate risk warnings and considerations
- **Action Guidance**: Specific, actionable recommendations
- **Strategic Thinking**: Demonstrates understanding of broader implications

### User Experience:
- **Response Structure**: Logical flow and organization
- **Clarity**: Complex information presented in understandable format
- **Completeness**: Comprehensive answers that anticipate follow-up questions
- **Professionalism**: Investment-grade analysis and recommendations

---

## Testing Results Documentation

### For Each Scenario, Record:

1. **Tool Performance**
   - Response times for each tool
   - Any timeouts or delays
   - Error rates and types

2. **Data Accuracy**
   - Quote accuracy vs external sources
   - Currency conversion precision
   - Account balance consistency

3. **Error Handling**
   - How invalid inputs are handled
   - Error message clarity and helpfulness
   - Recovery from error states

4. **Integration Issues**
   - Tool interaction problems
   - State consistency issues
   - Workflow interruptions

### Success Metrics:

- **Response Time**: 95% of tools respond within 10 seconds
- **Accuracy**: All market data within 1% of external sources
- **Error Handling**: 100% of invalid inputs handled gracefully
- **Reliability**: No crashes or system failures during testing
- **Usability**: Clear, helpful responses for all scenarios

## Next Steps After Testing

1. **Document Issues**: Record all problems found during testing
2. **Prioritize Fixes**: Rank issues by severity and frequency
3. **Performance Analysis**: Identify slow tools for optimization
4. **User Experience**: Note areas for improvement in responses
5. **Production Readiness**: Assess overall system stability

---

**Note**: This testing plan exercises all 23 MCP tools through realistic end-user scenarios. Run each scenario completely before moving to the next, and document any issues immediately for efficient debugging.