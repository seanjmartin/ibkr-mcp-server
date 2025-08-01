# get_account_summary

## Overview
Check your account balance, buying power, and key financial metrics from your Interactive Brokers account.
Provides comprehensive account information including cash balances, margin requirements, buying power,
and portfolio value. Essential for understanding your financial position before making trading decisions.

Supports multi-currency accounts and provides detailed breakdowns of cash balances in different currencies,
margin usage, and available funds for trading across various asset classes.

## Parameters

**account**: Account ID to retrieve summary for (optional)
- If not specified, uses your currently active account
- Useful if you have multiple IBKR accounts
- Get account IDs from get_accounts tool

## Examples

### Basic account summary
```python
get_account_summary()
```
Shows complete financial summary for your active account

### Specific account summary
```python
get_account_summary(account="DUH905195")
```
Shows summary for specific IBKR account ID

### Pre-trading check
```python
# Check available funds before placing large order
summary = get_account_summary()
buying_power = summary['BuyingPower']
if buying_power > 10000:
    # Proceed with trade
```

## Workflow

**Daily Account Review:**

1. **Morning check**: Review overnight changes in account value
2. **Cash position**: Check available cash in each currency
3. **Margin usage**: Monitor margin requirements and utilization
4. **Buying power**: Assess available funds for new positions
5. **Performance tracking**: Compare account value to previous periods

**Pre-Trading Workflow:**
1. **Verify buying power**: Ensure sufficient funds for planned trades
2. **Check margin requirements**: Understand margin impact of new positions
3. **Currency allocation**: See cash distribution across currencies
4. **Risk assessment**: Review total account exposure

**Multi-Currency Management:**
1. **Currency balances**: Track cash in USD, EUR, GBP, JPY, etc.
2. **FX exposure**: Understand currency risk in account
3. **Conversion planning**: Identify currency conversion needs
4. **Hedging decisions**: Plan currency hedging strategies

## Troubleshooting

### "Account data seems stale"
• Account summaries update throughout trading day
• Some metrics may have slight delays during volatile periods
• Refresh after a few moments if data seems outdated
• Check get_connection_status if persistent issues

### "Missing currency balances"
• Multi-currency data may not show for accounts with single currency
• Some currencies only appear when you have positions in them
• Paper trading accounts may have simplified currency reporting
• Zero balances may not be displayed in summary

### "Buying power calculation unclear"
• Buying power includes cash plus available margin
• Different asset classes have different margin requirements
• Day trading buying power may differ from overnight
• Options and futures have separate buying power calculations

### "Margin requirements seem high"
• Margin requirements vary by stock volatility and market conditions
• International stocks may have higher margin requirements
• During volatile periods, IBKR may increase margin requirements
• Some stocks may be temporarily non-marginable

### "Portfolio value doesn't match positions"
• Portfolio value includes unrealized P&L from all positions
• Currency fluctuations affect international positions
• Corporate actions may temporarily affect valuations
• Options and derivatives contribute to total portfolio value

## Related Tools
• get_portfolio - See detailed position information
• get_accounts - List all available accounts
• switch_account - Change active account for operations
• convert_currency - Convert balances between currencies
• get_connection_status - Check IBKR connection if data issues
• get_market_data - Get current prices affecting portfolio value
