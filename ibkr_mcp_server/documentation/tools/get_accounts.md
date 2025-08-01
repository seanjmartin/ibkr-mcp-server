# get_accounts

## Overview
List all available IBKR accounts and see which one is currently active. Essential for 
multi-account management and understanding which account your operations will affect.
Shows account IDs, types (paper vs live), and current active status.

Helps prevent confusion about which account you're working with and ensures 
operations are performed on the intended account.

## Parameters

This tool takes no parameters - it returns information about all accounts 
you have access to through your IBKR connection.

## Examples

### List all available accounts
```python
get_accounts()
```
Shows all accounts with IDs, types, and which is currently active

### Multi-account workflow
```python
# 1. See what accounts are available
accounts = get_accounts()
# 2. Switch to desired account
switch_account("DUH905195")
# 3. Verify the switch
updated_accounts = get_accounts()  # Should show new active account
```

## Workflow

**Account Discovery Process:**

1. **Initial setup**: Run get_accounts to see what's available
2. **Account identification**: Note paper vs live accounts
3. **Access verification**: Confirm you can see expected accounts
4. **Active account check**: See which account is currently selected
5. **Planning operations**: Choose appropriate account for your needs

**Multi-Account Strategy:**
1. **Development accounts**: Identify paper trading accounts for testing
2. **Production accounts**: Identify live accounts for actual trading
3. **Account segregation**: Keep different strategies in different accounts
4. **Risk management**: Use separate accounts for different risk levels

**Troubleshooting Workflow:**
1. **Connection issues**: Use get_accounts to verify IBKR connectivity
2. **Permission problems**: Check if expected accounts appear
3. **Active account confusion**: See which account operations will use
4. **Account switching validation**: Confirm switches worked correctly

## Troubleshooting

### "No accounts found" or empty list
• Check IBKR Gateway/TWS connection with get_connection_status
• Verify you're logged into IBKR with correct credentials
• Some connection issues may prevent account discovery
• Try reconnecting to IBKR and running get_accounts again

### "Expected account missing from list"
• Account may be temporarily restricted or suspended
• Live accounts require different permissions than paper accounts
• Some accounts may not be enabled for API access
• Check IBKR platform directly to verify account status

### "Cannot determine active account"
• Active account information may not be available during connection issues
• Default account is usually selected automatically
• Use switch_account to explicitly set desired account
• Check get_account_summary to see current account details

### "Account types unclear"
• Paper accounts typically start with 'DU' prefix
• Live accounts typically start with 'U' prefix  
• Account type information may vary by IBKR configuration
• When in doubt, check small operations in suspected paper account first

### "Account list seems stale"
• Account information is cached during IBKR connection
• New accounts may not appear until reconnection
• Recently closed accounts may still appear temporarily
• Restart MCP server if account list seems outdated

## Related Tools
• switch_account - Change which account is active for operations
• get_account_summary - Get detailed information about current account
• get_connection_status - Check IBKR connectivity if account issues
• get_portfolio - See positions in currently active account
