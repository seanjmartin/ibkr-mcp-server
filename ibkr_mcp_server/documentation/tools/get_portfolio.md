# get_portfolio

## Overview
View your current stock positions, quantities, and profit/loss across all holdings.
Provides comprehensive position details including unrealized gains/losses, average costs, 
market values, and position sizes. Essential for portfolio management, risk assessment, 
and performance tracking across your IBKR account.

Supports multi-currency portfolios and provides detailed breakdowns for both 
US and international positions with proper currency attribution.

## Parameters

**account**: Account ID to retrieve portfolio for (optional)
- If not specified, uses your currently active account
- Useful if you have multiple IBKR accounts
- Get account IDs from get_accounts tool

## Examples

### View current portfolio
```python
get_portfolio()
```
Shows all positions in your active account with P&L details

### Check specific account portfolio
```python
get_portfolio(account="DUH905195")
```
Shows portfolio for specific IBKR account ID

### Combined with market data
```python
# First get portfolio
portfolio = get_portfolio()
# Then get current prices
symbols = [pos['symbol'] for pos in portfolio]
prices = get_market_data(','.join(symbols))
```
Combines position data with live market prices

## Workflow

**Daily Portfolio Review:**

1. **Morning check**: Review overnight P&L changes
2. **Position sizing**: Assess if any positions became too large/small
3. **Risk assessment**: Look for concentrated positions or sectors
4. **Performance tracking**: Compare individual stock performance
5. **Rebalancing needs**: Identify positions needing adjustment

**Risk Management Workflow:**
1. **Calculate portfolio exposure**: Sum total position values
2. **Identify large positions**: Look for positions >5% of portfolio
3. **Check stop loss coverage**: Use with get_stop_losses to see protection
4. **Currency exposure**: Note international positions and FX risk
5. **Sector/geographic diversification**: Assess concentration risks

**Tax Planning Process:**
1. **Gain/loss analysis**: Review unrealized gains and losses
2. **Harvest opportunities**: Identify losses for tax harvesting
3. **Long-term vs short-term**: Track holding periods
4. **Currency implications**: Consider FX gains/losses on international positions

## Troubleshooting

### "No positions found"
• Portfolio may be empty if no stocks currently held
• Check if you're looking at the correct account
• Recent trades may not appear immediately
• Some derivatives/options may not show in standard portfolio view

### "Position quantities seem wrong"
• Check for recent trades that may not be fully settled
• Corporate actions (splits, dividends) can affect quantities
• Some positions may be partially allocated across accounts
• Verify with IBKR platform if quantities seem significantly off

### "Unrealized P&L calculations incorrect"
• P&L based on average cost vs current market price
• Currency fluctuations affect international positions
• Market data delays can cause temporary calculation issues
• Corporate actions may temporarily distort cost basis

### "Missing recent trades"
• New positions may take several minutes to appear
• Settlement cycles (T+1, T+2) affect position reporting
• Check get_executions for recent trade confirmations
• Some exotic instruments may have delayed reporting

### "International positions show wrong currency"
• International stocks show P&L in local currency (EUR, GBP, JPY)
• Use convert_currency to convert to your base currency
• Some ADRs may show in USD even for foreign companies
• Check exchange field to understand currency denomination

### "Average cost seems incorrect"
• Average cost includes commissions and fees
• Corporate actions can affect cost basis calculations
• Currency conversions at trade time vs current may differ
• IBKR may adjust cost basis for tax optimization

## Related Tools
• get_market_data - Get current prices for your positions
• get_account_summary - See total account value and cash balances
• convert_currency - Convert international positions to base currency
• get_stop_losses - Check risk protection on your positions
• switch_account - Change active account if you have multiple accounts
• get_connection_status - Verify IBKR connection if data seems stale
