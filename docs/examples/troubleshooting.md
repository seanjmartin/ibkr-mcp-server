# Troubleshooting Examples

Common issues and solutions when using the IBKR MCP Server with practical examples.

## Overview

This guide provides step-by-step solutions to common problems, error messages, and unexpected behaviors. Each section includes symptoms, causes, and detailed resolution steps.

## Connection Issues

### Problem: Cannot Connect to IBKR

**Symptoms:**
```
"Check my IBKR connection status"
→ ❌ IBKR Connection Issues Detected
→ Status: Disconnected
→ Error: Connection refused (port 7497)
```

**Causes:**
- IB Gateway not running
- Wrong port configuration
- API not enabled
- Firewall blocking connection

**Solutions:**

**Step 1: Verify IB Gateway is Running**
```
1. Open IB Gateway application
2. Log in with your IBKR credentials
3. Ensure you see "Connected" status
4. Keep IB Gateway running while using the system
```

**Step 2: Check Port Configuration**
```
Paper Trading: Port 7497
Live Trading: Port 7496

In your .env file:
IBKR_PORT=7497  # For paper trading
IBKR_PORT=7496  # For live trading
```

**Step 3: Enable API in IB Gateway**
```
1. In IB Gateway, go to Configure → Settings
2. Check "Enable ActiveX and Socket Clients"
3. Add 127.0.0.1 to trusted IP addresses
4. Set socket port to match your configuration
5. Click OK and restart IB Gateway
```

**Step 4: Test Connection**
```
"Check my IBKR connection status"
→ Should now show: ✅ Connected to IBKR Paper Trading
```

### Problem: Connection Drops Frequently

**Symptoms:**
- Connection works initially but drops after a few minutes
- Intermittent "connection lost" errors
- Orders fail with connection errors

**Causes:**
- Network instability
- IB Gateway timeout settings
- Too many simultaneous connections

**Solutions:**

**Step 1: Adjust IB Gateway Settings**
```
1. In IB Gateway: Configure → Settings
2. Set "Auto-restart" to 24:00 (never)
3. Enable "Read-Only API"
4. Increase timeout settings if available
```

**Step 2: Network Stability**
```
1. Use wired internet connection if possible
2. Close other bandwidth-heavy applications
3. Check firewall and antivirus settings
4. Consider using a dedicated machine for trading
```

**Step 3: Reconnection Testing**
```
"Check my IBKR connection status"
Wait 30 seconds
"Check my IBKR connection status"
→ Should maintain stable connection
```

## Market Data Issues

### Problem: Stock Quotes Not Updating

**Symptoms:**
```
"Get quote for Apple"
→ Returns stale data or "No data available"
→ Timestamps are old
→ International stocks show no prices
```

**Causes:**
- Markets are closed
- Data subscription issues
- Symbol format problems
- Exchange connectivity issues

**Solutions:**

**Step 1: Check Market Hours**
```
US Markets: 9:30 AM - 4:00 PM EST (Monday-Friday)
European: 3:30 AM - 11:30 AM EST (Monday-Friday)
Asian: 8:00 PM - 2:00 AM EST (Sunday-Thursday)

Outside these hours, expect delayed or no updates
```

**Step 2: Verify Symbol Format**
```
Correct: "Get quote for AAPL"
Correct: "Get quote for ASML"  # System auto-detects exchange
Avoid: Complex symbol formats unless necessary
```

**Step 3: Test with Different Stocks**
```
"Get quotes for AAPL, MSFT, GOOGL"  # US stocks
"Get quotes for ASML, SAP"          # European stocks
"Get quotes for Toyota (7203)"      # Asian stocks
```

**Step 4: Check Data Permissions**
```
1. In IBKR Client Portal, verify market data subscriptions
2. Paper accounts may have delayed data (15-20 minutes)
3. Some international markets require separate subscriptions
```

### Problem: International Stocks Not Found

**Symptoms:**
```
"Get quote for Toyota"
→ Error: Symbol not found
→ International companies return no data
```

**Causes:**
- Wrong symbol format
- Exchange not supported
- Company not in reference database

**Solutions:**

**Step 1: Use Correct International Symbols**
```
Toyota: Use "7203" (Japanese symbol)
Samsung: Use "005930" (Korean symbol)
ASML: Use "ASML" (automatically detected)
```

**Step 2: Check Symbol Resolution**
```
"Where does Toyota trade?"
→ Should return TSE (Tokyo Stock Exchange) information
```

**Step 3: Try Alternative Formats**
```
"Get quote for Toyota Motor"
"Get quote for 7203"
"Get quote for TM"  # If ADR available
```

## Order Management Issues

### Problem: Stop Loss Orders Not Working

**Symptoms:**
```
"Set a stop loss on Apple at $175"
→ Error: Stop loss orders not enabled
→ Or: Order placed but doesn't trigger when price hit
```

**Causes:**
- Stop loss feature disabled in configuration
- Wrong order parameters
- Insufficient position size
- Market closed when stop should trigger

**Solutions:**

**Step 1: Enable Stop Loss Orders**
```
In .env file:
ENABLE_STOP_LOSS_ORDERS=true

Restart the IBKR MCP Server after changing configuration
```

**Step 2: Verify Order Parameters**
```
Correct: "Set a stop loss on my Apple position at $175"
Include: Symbol, trigger price, position specification
Check: Do you actually own Apple stock?
```

**Step 3: Check Position Size**
```
"Show me my current Apple position"
→ Verify you have shares to protect with stop loss
→ Stop loss quantity should not exceed position size
```

**Step 4: Test Stop Loss Functionality**
```
"Set a stop loss on Apple at $175"
"Show me my stop loss orders"
→ Should show active stop loss order
```

### Problem: Orders Rejected or Fail

**Symptoms:**
- Orders fail with "insufficient buying power"
- Orders rejected with parameter errors
- Stop losses cancelled unexpectedly

**Causes:**
- Account limitations
- Order size too large
- Wrong order parameters
- Safety limits exceeded

**Solutions:**

**Step 1: Check Account Status**
```
"What's my account balance?"
"Show me my buying power"
→ Verify sufficient funds for orders
```

**Step 2: Verify Order Size**
```
Check configuration limits:
MAX_ORDER_SIZE=1000        # Maximum shares per order
MAX_ORDER_VALUE_USD=10000  # Maximum dollar value
```

**Step 3: Review Safety Settings**
```
"Check if I've hit daily trading limits"
"Show me my recent order activity"
→ May have exceeded daily order limits
```

## Currency and Forex Issues

### Problem: Currency Conversion Errors

**Symptoms:**
```
"Convert $1000 to Euros"
→ Error: Currency conversion failed
→ Or: Wrong conversion rates returned
```

**Causes:**
- Forex markets closed (weekends)
- Unsupported currency pair
- Network issues with rate provider

**Solutions:**

**Step 1: Check Forex Market Hours**
```
Forex markets closed: Friday 5 PM EST - Sunday 5 PM EST
During weekends, rates may be stale or unavailable
```

**Step 2: Verify Currency Support**
```
Supported: USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD, HKD, KRW, DKK, SEK, NOK
Unsupported: Exotic currencies, cryptocurrencies
```

**Step 3: Test with Major Pairs**
```
"What's the EUR/USD rate?"
"Convert $100 to GBP"  # Test with major currencies first
```

**Step 4: Check Network Connectivity**
```
"Check my IBKR connection status"
→ Ensure stable connection for forex data
```

### Problem: Forex Rates Seem Wrong

**Symptoms:**
- Forex rates very different from expected
- Bid/ask spreads unusually wide
- Rates not updating during market hours

**Causes:**
- Using paper trading (may have artificial rates)
- Market volatility
- Low liquidity periods
- Data provider issues

**Solutions:**

**Step 1: Verify Trading Mode**
```
"Check my connection status"
→ Paper trading may show simulated rates
→ Live accounts get real market rates
```

**Step 2: Compare with External Sources**
```
Cross-check rates with financial websites
Account for bid/ask spreads in comparisons
Paper trading spreads may be wider than reality
```

**Step 3: Check Market Conditions**
```
During major news events or off-hours:
- Spreads naturally widen
- Volatility increases
- Liquidity decreases
```

## Portfolio and Account Issues

### Problem: Portfolio Shows Wrong Values

**Symptoms:**
```
"Show me my portfolio"
→ Position values seem incorrect
→ P&L calculations don't match expectations
→ Currency conversions look wrong
```

**Causes:**
- Stale market data
- Currency conversion issues
- Position quantity discrepancies
- Time zone differences

**Solutions:**

**Step 1: Refresh Market Data**
```
"Get fresh quotes for all my positions"
"Check my connection and reconnect if needed"
```

**Step 2: Verify Position Quantities**
```
"Show me detailed position information"
→ Compare with IBKR Client Portal
→ Check for pending orders that might affect positions
```

**Step 3: Check Currency Conversions**
```
"Convert my EUR positions to USD equivalent"
"What are current forex rates for my currencies?"
```

**Step 4: Time Zone Considerations**
```
Portfolio values update based on most recent market data
International positions may show different values during off-hours
```

### Problem: Account Balance Discrepancies

**Symptoms:**
- Available balance doesn't match expectations
- Buying power seems wrong
- Currency allocations incorrect

**Causes:**
- Pending orders reducing buying power
- Currency conversion timing
- Margin requirements
- Account restrictions

**Solutions:**

**Step 1: Check Pending Orders**
```
"Show me my pending orders"
→ Pending orders reserve buying power
→ Cancel unnecessary pending orders
```

**Step 2: Review Account Summary**
```
"Give me detailed account summary"
→ Shows all currency balances
→ Explains buying power calculations
```

**Step 3: Compare with IBKR Portal**
```
Log into IBKR Client Portal directly
Compare values with system output
Check for account notifications or restrictions
```

## Safety and Security Issues

### Problem: Kill Switch Activated Unexpectedly

**Symptoms:**
```
All trading commands fail with:
"Emergency kill switch is active"
"Trading halted for safety reasons"
```

**Causes:**
- Automatic safety trigger
- Manual activation (forgotten)
- System error detection
- Rate limit violations

**Solutions:**

**Step 1: Check Kill Switch Status**
```
"Show me safety system status"
→ Will show if kill switch is active and why
```

**Step 2: Review Recent Activity**
```
"Show me recent trading activity"
"Check if I hit any safety limits"
→ Look for patterns that triggered safety systems
```

**Step 3: Deactivate Kill Switch**
```
Only if you're certain it's safe to do so:
"Deactivate emergency kill switch with override code"
→ Requires manual confirmation for safety
```

**Step 4: Prevent Future Triggers**
```
Review and adjust safety settings if needed
Understand what caused the trigger
Modify trading patterns to avoid future activations
```

### Problem: Daily Limits Exceeded

**Symptoms:**
```
Orders fail with:
"Daily order limit exceeded"
"Trading volume limit reached"
```

**Causes:**
- Exceeded maximum daily orders
- Hit daily trading volume limits
- Too many rapid-fire orders

**Solutions:**

**Step 1: Check Daily Statistics**
```
"Show me my daily trading statistics"
→ See how close you are to limits
```

**Step 2: Review Limit Settings**
```
Current default limits:
MAX_DAILY_ORDERS=50
MAX_ORDERS_PER_MINUTE=5

These can be adjusted in configuration if needed
```

**Step 3: Wait for Reset**
```
Daily limits reset at midnight UTC
Plan trading activity within limits
Consider batching orders to stay within limits
```

## System Performance Issues

### Problem: Slow Response Times

**Symptoms:**
- Commands take a long time to respond
- Timeouts on market data requests
- System seems sluggish overall

**Causes:**
- Network connectivity issues
- High system load
- IBKR server issues
- Too many simultaneous requests

**Solutions:**

**Step 1: Check Network**
```
Test internet connection speed
Close other bandwidth-heavy applications
Use wired connection if possible
```

**Step 2: Reduce Request Frequency**
```
Avoid rapid-fire requests
Space out market data requests
Use batch requests when possible
```

**Step 3: Restart System**
```
1. Close Claude Desktop
2. Stop IB Gateway
3. Wait 30 seconds
4. Restart IB Gateway
5. Restart Claude Desktop
6. Test: "Check my connection status"
```

### Problem: Memory or Resource Issues

**Symptoms:**
- System becomes unresponsive
- Error messages about resources
- Performance degrades over time

**Causes:**
- Memory leaks
- Too many concurrent operations
- Large data sets
- System resource constraints

**Solutions:**

**Step 1: Restart Applications**
```
Close and restart Claude Desktop
Close and restart IB Gateway
This clears memory and resets connections
```

**Step 2: Reduce Complexity**
```
Avoid very large portfolio queries
Limit simultaneous market data requests
Close other applications if needed
```

**Step 3: System Resources**
```
Check available RAM and CPU
Close unnecessary programs
Consider dedicated trading machine
```

## Advanced Troubleshooting

### Debug Mode and Logging

**Enable Detailed Logging:**
```
In .env file:
LOG_LEVEL=DEBUG
ENABLE_AUDIT_LOGGING=true

This provides more detailed error information
```

**Check Log Files:**
```
Logs are typically in temp directory:
- Windows: %TEMP%\ibkr-mcp-server.log
- Contains detailed error information
- Audit trail of all operations
```

### Testing Connectivity

**Basic Connectivity Test:**
```
1. "Check my IBKR connection status"
2. "Get quote for AAPL"
3. "Show me my account balance"
4. "What's the EUR/USD rate?"

All should work if system is properly connected
```

**International Connectivity Test:**
```
1. "Get quotes for ASML, SAP, Toyota"
2. "Convert $1000 to Euros"
3. "Where does ASML trade?"

Tests international market data and forex
```

### Common Error Patterns

**"Symbol not found" Errors:**
- Check symbol spelling and format
- Verify market is supported
- Try alternative symbol formats

**"Insufficient data" Errors:**
- Check market hours
- Verify data subscriptions
- Test with different symbols

**"Safety violation" Errors:**
- Review safety settings
- Check daily limits
- Verify order parameters

**"Connection timeout" Errors:**
- Check network connectivity
- Restart IB Gateway
- Verify port configuration

## Getting Additional Help

### Information to Gather

**Before Seeking Help:**
1. Exact error message or unexpected behavior
2. Steps to reproduce the problem
3. Your system configuration (paper vs live, etc.)
4. Recent changes to setup
5. Log file entries if available

### Self-Help Resources

**System Status Check:**
```
"Show me comprehensive system status"
→ Provides overview of all system components
```

**Built-in Documentation:**
```
"Help with forex trading"
"Show me stop loss documentation"
→ Access built-in help system
```

**Configuration Review:**
```
Review your .env file settings
Check Claude Desktop configuration
Verify IB Gateway settings
```

---

**Remember:** Most issues are configuration-related and can be resolved by carefully checking settings, restarting components, and following the systematic troubleshooting steps above. When in doubt, start with the basics: connection, configuration, and market hours.
