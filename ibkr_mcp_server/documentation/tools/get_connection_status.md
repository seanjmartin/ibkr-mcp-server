# get_connection_status

## Overview
Check if you're connected to IBKR and view connection details. Shows connection health,
account information, system status, and diagnostic information. Essential for troubleshooting
when other tools aren't working properly or when you need to verify system status.

Provides comprehensive connection diagnostics including server status, account access,
API permissions, and connection stability metrics.

## Parameters

This tool takes no parameters - it returns comprehensive status information
about your current IBKR connection and system state.

## Examples

### Basic connection check
```python
get_connection_status()
```
Shows complete connection status and diagnostics

### Troubleshooting workflow
```python
# If other tools are failing, start here
status = get_connection_status()
# Check if connected before proceeding
if status['connected']:
    # Proceed with other operations
    portfolio = get_portfolio()
```

### System health monitoring
```python
# Regular health check
status = get_connection_status()
# Monitor for connection issues
if not status['connected']:
    # Handle disconnection
```

## Workflow

**Connection Troubleshooting Process:**

1. **First step diagnosis**: Always check connection status when tools fail
2. **Connection verification**: Confirm you're connected to IBKR
3. **Account validation**: Verify correct account access
4. **Permission check**: Ensure API permissions are enabled
5. **Stability assessment**: Check for connection quality issues

**System Monitoring Workflow:**
1. **Regular health checks**: Periodically verify connection stability
2. **Pre-operation validation**: Check status before important operations
3. **Error diagnosis**: Use when other tools return unexpected errors
4. **Performance monitoring**: Track connection quality over time

**Setup Validation Process:**
1. **Initial setup**: Verify IBKR Gateway/TWS configuration
2. **Account access**: Confirm correct account connectivity
3. **API permissions**: Validate API settings and permissions
4. **Network stability**: Check for connectivity issues

## Troubleshooting

### "Not connected to IBKR"
• Check if IBKR Gateway or TWS is running
• Verify IBKR software is logged in with correct credentials
• Check port settings (typically 7497 for paper, 7496 for live)
• Ensure "Enable ActiveX and Socket Clients" is checked in IBKR API settings

### "Connection unstable" or frequent disconnections
• Network connectivity issues between your system and IBKR
• IBKR servers may be experiencing high load or maintenance
• Check your internet connection stability
• Consider increasing connection timeout settings

### "API permissions denied"
• "Enable ActiveX and Socket Clients" must be enabled in IBKR
• Check that API socket port matches configuration (7497/7496)
• Verify IP address is allowed (127.0.0.1 for local connections)
• Some accounts may have API access restrictions

### "Account access issues"
• Verify you're logged into correct IBKR account
• Paper trading vs live account mismatch with port settings
• Account may be temporarily restricted or require additional permissions
• Check IBKR platform directly to verify account status

### "System status shows errors"
• IBKR system maintenance or outages affecting service
• Market data feed issues or subscription problems
• API rate limiting due to excessive requests
• Check IBKR status page for known system issues

### "Connection works but data seems stale"
• Market data subscriptions may be limited in paper trading
• Some international markets may have delayed data
• Check if markets are open for the symbols you're monitoring
• Data feed issues may cause temporary staleness

## Related Tools
• get_accounts - Verify account access if connection issues
• get_market_data - Test data connectivity after connection verification
• get_portfolio - Validate account data access
• switch_account - Try different account if current account has issues

## Technical Information

**Connection Parameters:**
• Host: Typically 127.0.0.1 (localhost)
• Paper Trading Port: 7497
• Live Trading Port: 7496
• Client ID: Unique identifier for this connection

**Required IBKR Settings:**
• Enable ActiveX and Socket Clients: MUST be checked
• Socket Port: Must match your configuration
• Trusted IPs: Must include 127.0.0.1
• API Logging: Recommended for troubleshooting

**Common Status Indicators:**
• Connected: Basic connection established
• Authenticated: Account access verified
• Market Data: Data feeds operational
• Trading Enabled: Order placement permissions active
