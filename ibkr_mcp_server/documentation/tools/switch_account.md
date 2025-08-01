# switch_account

## Overview
Switch between different IBKR accounts if you have multiple accounts. Changes the active account
for all subsequent operations including portfolio viewing, trading, and account management.
Essential for users managing multiple IBKR accounts from a single interface.

All tools (get_portfolio, get_account_summary, trading operations) will use the newly
selected account until you switch again or restart the system.

## Parameters

**account_id**: The account ID to switch to (required)
- Must be a valid IBKR account ID that you have access to
- Account IDs typically start with 'U' for live accounts or 'DU' for paper accounts
- Get available account IDs from get_accounts tool

## Examples

### Switch to paper trading account
```python
switch_account("DUH905195")
```
Switches to paper trading account for testing

### Switch to live trading account
```python
switch_account("U1234567")
```
Switches to live trading account (use with caution)

### Verify account switching workflow
```python
# 1. See available accounts
accounts = get_accounts()
# 2. Switch to desired account
switch_account("DUH905195")
# 3. Verify switch worked
summary = get_account_summary()  # Should show new account data
```

## Workflow

**Multi-Account Management:**

1. **List accounts**: Use get_accounts to see all available accounts
2. **Identify target**: Choose the account you want to work with
3. **Switch account**: Use switch_account with the target account ID
4. **Verify switch**: Check account_summary or portfolio to confirm
5. **Perform operations**: All subsequent tools use the new account

**Paper vs Live Trading Workflow:**
1. **Development phase**: Switch to paper account for testing
2. **Strategy validation**: Test all operations in paper trading
3. **Go-live preparation**: Verify live account access and settings
4. **Production switch**: Switch to live account only when ready
5. **Safety check**: Always verify which account is active

**Account-Specific Operations:**
1. **Portfolio review**: Switch to account, then get_portfolio
2. **Trading operations**: Ensure correct account before placing orders
3. **Performance analysis**: Switch between accounts to compare performance
4. **Risk management**: Set appropriate stop losses per account

## Troubleshooting

### "Account not found" or "Access denied"
• Verify account ID is correct - check get_accounts for valid IDs
• Ensure you have permissions to access the specified account
• Some accounts may be temporarily restricted or suspended
• Live accounts require additional permissions vs paper accounts

### "Switch appears successful but operations fail"
• Account switching may take a few seconds to fully propagate
• Wait 5-10 seconds after switching before running other operations
• Some operations may cache previous account - retry if needed
• Check get_connection_status to ensure stable IBKR connection

### "Cannot switch to live account"
• Live accounts require explicit trading permissions
• Paper accounts are enabled by default for safety
• Live account access may require additional IBKR approvals
• Check your IBKR platform settings for account permissions

### "Operations still using old account"
• Account switching affects the MCP server state, not IBKR platform
• Some cached data may still reflect previous account temporarily
• Refresh operations like get_portfolio to see new account data
• Restart MCP server if switching issues persist

### "Forgot which account is active"
• Use get_account_summary to see current account information
• Use get_accounts to see which account is marked as active
• Account ID is typically shown in most tool responses
• When in doubt, explicitly switch to desired account

## Related Tools
• get_accounts - List all available accounts and see which is active
• get_account_summary - Verify current account details after switching
• get_portfolio - Check positions in newly selected account
• get_connection_status - Ensure stable connection during account operations
