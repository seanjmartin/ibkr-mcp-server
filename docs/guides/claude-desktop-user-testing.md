# Claude Desktop User Testing Guide

Complete guide for testing the IBKR MCP Server as an actual Claude Desktop user trading against a paper account.

## Overview

This guide sets up **real Claude Desktop integration** for hands-on testing with your IBKR paper account. This is different from automated tests - you'll interact with Claude Desktop exactly like an end user would, placing real orders in your paper account.

## Prerequisites

- ✅ IBKR MCP Server installed and configured
- ✅ IBKR paper account with IB Gateway running
- ✅ Claude Desktop installed on your machine
- ✅ Paper trading account with DU* prefix

## Current Project Status

Your configuration is already set up for user testing:

**Connection Settings:**
- Paper Trading: ✅ Enabled (port 7497)
- Client ID: 5 (tested and working)
- Trading Features: ✅ All enabled for paper account

**Safety Limits:**
- Max Order Size: 10 shares (conservative for testing)
- Max Order Value: $500 USD
- Max Daily Orders: 20
- Paper Account Verification: ✅ Required

## Step 1: Configure Claude Desktop

### Find Claude Desktop Configuration File

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

### Add IBKR MCP Server Configuration

```json
{
  "mcpServers": {
    "ibkr": {
      "command": "C:\\Python313\\python.exe",
      "args": ["-m", "ibkr_mcp_server.main"],
      "cwd": "C:\\YourMCP-ServerLocation\\Projects\\ibkr-mcp-server",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note:** Update the paths to match your actual installation:
- `command`: Path to your Python 3.13 executable
- `cwd`: Path to your ibkr-mcp-server directory

## Step 2: Start IBKR Gateway

1. **Launch IB Gateway**
2. **Login to your paper account** (should start with DU)
3. **Verify API settings:**
   - ✅ "Enable ActiveX and Socket Clients" checked
   - ✅ Socket port: 7497 (paper trading)
   - ✅ Trusted IPs: 127.0.0.1 added
   - ✅ Client ID: Available (system will use ID 5)

## Step 3: Test Claude Desktop Integration

### Restart Claude Desktop
Close and reopen Claude Desktop to load the MCP server configuration.

### Basic Connection Tests

Open a new conversation in Claude Desktop and try these commands:

#### Test 1: Connection Status
```
Check my IBKR connection status
```

**Expected Response:**
- Connected to IBKR Paper Trading
- Account starting with DU (e.g., DUH905195)
- Client ID 5
- All systems operational

#### Test 2: Account Information
```
Show me all my IBKR accounts
```

**Expected Response:**
- List of your paper accounts
- Current account highlighted
- Paper trading confirmation

#### Test 3: Portfolio Overview
```
Show me my current portfolio
```

**Expected Response:**
- Current positions (may be empty for new account)
- Portfolio value summary
- Currency breakdowns

## Step 4: Market Data Testing

### US Market Data
```
What's Apple trading at right now?
```

**Expected Response:**
- Real-time AAPL quote
- Bid/ask prices
- Volume and session data

### International Market Data
```
Get quotes for Apple, ASML, and Toyota
```

**Expected Response:**
- AAPL: US market (SMART/USD)
- ASML: Dutch market (AEB/EUR) with auto-detection
- 7203: Japanese market (TSE/JPY) for Toyota

### Forex Data
```
What's the current EUR/USD rate?
```

**Expected Response:**
- Live forex rate
- Bid/ask spread
- Market session information

## Step 5: Order Placement Testing

### Market Order Test
```
Buy 5 shares of Apple at current market price
```

**Expected Response:**
- Order confirmation with order ID
- Execution details
- Updated portfolio/account balance

### Limit Order Test
```
Place a limit order to buy 3 shares of Microsoft at $400
```

**Expected Response:**
- Limit order placed
- Order ID provided
- Status: Working/Pending

### Order Management
```
Show me my pending orders
```

**Expected Response:**
- List of open orders
- Order details and status
- Time in force information

```
Cancel my Microsoft limit order
```

**Expected Response:**
- Order cancellation confirmation
- Updated order status

## Step 6: Risk Management Testing

### Stop Loss Orders
```
Set a stop loss on my Apple position at $170
```

**Expected Response:**
- Stop loss order placed
- Risk protection confirmation
- Order ID for tracking

### Portfolio Protection
```
Show me all my stop loss orders
```

**Expected Response:**
- Active stop loss orders
- Protection levels
- Distance from current market

## Step 7: Advanced Features Testing

### Currency Conversion
```
Convert $1000 to Euros using live rates
```

### International Trading
```
Get quote for ASML and place a small test order
```

### Bracket Orders
```
Place a bracket order: buy 2 shares of Tesla at $240, stop loss $220, profit target $260
```

## User Experience Testing Scenarios

### Scenario 1: New User First Experience
```
1. "I'm new to this system, can you help me get started?"
2. "Check my connection to IBKR"
3. "What's in my portfolio?"
4. "Show me how to get a stock quote"
5. "How do I place a small test order?"
```

### Scenario 2: Active Trading Session
```
1. "Check my account balance"
2. "Get quotes for AAPL, MSFT, GOOGL"
3. "Buy 5 shares of Apple at market price"
4. "Set a stop loss at 8% below my purchase price"
5. "Show me my portfolio now"
```

### Scenario 3: International Investing
```
1. "I want to invest in European stocks"
2. "Get quote for ASML"
3. "Where does ASML trade and in what currency?"
4. "Convert €1000 to USD for comparison"
5. "Place a small limit order for ASML"
```

### Scenario 4: Risk Management Focus
```
1. "Show me my current positions"
2. "Set stop losses on all my positions"
3. "Show me my risk protection status"
4. "What's my maximum potential loss?"
```

## Testing Checklist

### Basic Functionality
- [ ] Connection status check
- [ ] Account information retrieval
- [ ] Portfolio display
- [ ] Real-time market data
- [ ] Currency conversion

### Order Placement
- [ ] Market order execution
- [ ] Limit order placement
- [ ] Order modification
- [ ] Order cancellation
- [ ] Order status checking

### Risk Management
- [ ] Stop loss placement
- [ ] Stop loss modification
- [ ] Portfolio protection review
- [ ] Emergency controls

### International Features
- [ ] International stock quotes
- [ ] Currency conversions
- [ ] Exchange detection
- [ ] Multi-currency account handling

### Error Handling
- [ ] Invalid symbol handling
- [ ] Order limit enforcement
- [ ] Safety feature activation
- [ ] Network error recovery

## Common Issues and Solutions

### Connection Problems
**Issue:** "Connection refused" errors

**Solutions:**
1. Verify IB Gateway is running and logged in
2. Check port 7497 is configured correctly
3. Ensure API is enabled in IB Gateway
4. Restart Claude Desktop

### Order Issues
**Issue:** Orders being rejected

**Solutions:**
1. Check order size limits (max 10 shares in current config)
2. Verify order value under $500 limit
3. Ensure sufficient paper trading balance
4. Check daily order limits (max 20/day)

### Tool Access Issues
**Issue:** IBKR tools not available in Claude Desktop

**Solutions:**
1. Verify Claude Desktop configuration file syntax
2. Check Python path in configuration
3. Restart Claude Desktop after config changes
4. Check error logs in server output

## Performance Expectations

### Response Times
- **Connection Status:** < 2 seconds
- **Market Data:** < 3 seconds
- **Order Placement:** < 5 seconds
- **Portfolio Retrieval:** < 4 seconds

### Order Execution
- **Market Orders:** Usually fill immediately
- **Limit Orders:** Fill when price reached
- **Stop Losses:** Activate when triggered

## Safety Features in Action

### Automatic Protections
- Order size limited to 10 shares max
- Order value limited to $500 USD max
- Paper account verification enforced
- All operations logged for audit

### Manual Controls
```
"Activate emergency kill switch"
"Show me my daily trading limits"
"What safety features are active?"
```

## Advanced User Testing

### Extended Session Testing
1. Keep Claude Desktop open for 30+ minutes
2. Place multiple orders throughout session
3. Monitor connection stability
4. Test various order types and modifications

### Error Recovery Testing
1. Disconnect IB Gateway during operation
2. Test reconnection behavior
3. Verify order status after reconnection
4. Test safety feature activation

### Load Testing
1. Place multiple rapid orders (within limits)
2. Request multiple market data updates
3. Test system responsiveness under load
4. Monitor for rate limiting

## Documentation and Support

### Built-in Help
```
"Help with forex trading"
"Show me stop loss examples"
"How do I place a bracket order?"
```

### Log File Locations
Check logs for troubleshooting:
- **Windows:** `%TEMP%\ibkr-mcp-server.log`
- **Audit Logs:** `%TEMP%\ibkr-trading-audit.log`

### Support Resources
- [API Quick Reference](../api/API_QUICK_REFERENCE.md)
- [Trading Guide](trading.md)
- [Troubleshooting](../examples/troubleshooting.md)

## Success Criteria

### Technical Success
- ✅ Claude Desktop connects to IBKR successfully
- ✅ All 23 MCP tools accessible and functional
- ✅ Orders execute in paper account
- ✅ Real-time data feeds working
- ✅ Safety features prevent dangerous operations

### User Experience Success
- ✅ Natural language trading works intuitively
- ✅ Error messages are clear and helpful
- ✅ Response times are acceptable
- ✅ System feels reliable and professional
- ✅ Trading workflows feel natural

## Next Steps

After successful user testing:

1. **Document Issues:** Note any problems or confusing experiences
2. **Performance Tuning:** Optimize based on real usage patterns
3. **Feature Requests:** Identify missing functionality users need
4. **Safety Validation:** Confirm all safety features work as expected
5. **Scaling Preparation:** Prepare for live trading deployment

---

**Remember:** This is real paper trading - orders will actually execute in your IBKR paper account. All trades are with virtual money, but the experience is identical to live trading.

**Safety First:** Start with small test orders to verify everything works correctly before attempting larger or more complex trades.
