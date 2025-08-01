# get_stop_losses

## Overview
View your active stop loss orders and their current status. Shows comprehensive order details 
including trigger prices, quantities, order types, and execution status. Essential for monitoring 
your risk management strategy and ensuring your protective orders are working correctly.

Provides real-time status updates and helps you track which positions are protected, 
which orders need adjustment, and what risk exposure remains unprotected.

## Parameters

**account**: Filter by specific account ID (optional - uses current account if not specified)

**symbol**: Filter by specific stock symbol (optional - shows all symbols if not specified)

**status**: Filter by order status (optional - defaults to "active"):
- "active" - Only currently active/working orders
- "all" - All orders including filled and cancelled
- "filled" - Only executed orders
- "cancelled" - Only cancelled orders

## Examples

### View all active stop losses
```python
get_stop_losses()
```
Shows all currently active stop loss orders across all positions

### Check stop losses for specific stock
```python
get_stop_losses(symbol="AAPL")
```
Shows only AAPL stop loss orders and their status

### Review all stop loss history
```python
get_stop_losses(status="all")
```
Shows complete history including filled and cancelled orders

### Monitor specific account
```python
get_stop_losses(account="DUH905195")
```
Shows stop losses for specific IBKR account

## Workflow

**Daily Risk Management Review:**

1. **Morning check**: Run get_stop_losses() to see overnight changes
2. **Identify gaps**: Look for positions without stop protection
3. **Review trigger levels**: Ensure stops are still appropriate for current prices
4. **Check for fills**: See if any stops executed overnight
5. **Plan adjustments**: Note which stops need modification

**Position Management Workflow:**
1. **After placing stops**: Verify orders appear in get_stop_losses output
2. **Regular monitoring**: Check status weekly or after significant market moves
3. **Profit adjustments**: When positions gain, update stops to protect profits
4. **Pre-close cleanup**: Cancel stops before manually closing positions

**Risk Assessment Process:**
1. **Calculate protection coverage**: What percentage of portfolio has stops?
2. **Review stop distances**: Are stops too tight or too loose?
3. **Check order types**: Mix of basic stops vs. stop-limits vs. trailing stops
4. **Monitor near-triggers**: Which stops are close to current prices?

## Troubleshooting

### "No stop losses found"
• You may not have any active stop loss orders placed
• Check if trading is enabled - orders require trading permissions
• Use get_portfolio to see your positions that could have stops
• Recent orders may take a moment to appear in the system

### "Order status shows 'Unknown'"
• Order may be in transition between states
• Refresh after a few moments for updated status
• Check get_connection_status to ensure stable IBKR connection
• Some order states may not be fully reflected in paper trading

### "Missing recent order"
• Newly placed orders may take 30-60 seconds to appear
• IBKR system may have delays during high-volume periods
• Check if order was actually placed successfully
• Use get_open_orders for broader order view if needed

### "Order details incomplete"
• Some fields may be empty for older or exotic order types
• Paper trading accounts may have limited order detail access
• Focus on key fields: symbol, quantity, stop_price, status
• Contact IBKR support for critical missing information

### "Stop price seems wrong"
• Trailing stops show dynamic prices that update with market
• Stop-limit orders show both stop price and limit price
• Market volatility can cause apparent price discrepancies
• Check order modification history if price seems changed

## Related Tools
• place_stop_loss - Set new stop loss orders for protection
• modify_stop_loss - Adjust existing stop orders as needed
• cancel_stop_loss - Remove stop orders before closing positions
• get_portfolio - See which positions need stop loss protection
• get_market_data - Check current prices vs. stop trigger levels
• get_open_orders - See all pending orders including stops
