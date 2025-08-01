# modify_stop_loss

## Overview
Change the trigger price or quantity of an existing stop loss order. Allows dynamic adjustment
of risk management parameters as market conditions change or positions become profitable.
Essential for active risk management and profit protection strategies.

Enables you to tighten stops as positions gain value, adjust for changing volatility,
or modify order parameters without canceling and replacing the entire order.

## Parameters

**order_id**: The order ID of the stop loss to modify (required)
- Get order IDs from get_stop_losses tool
- Order ID is returned when placing stop loss orders
- Must be an active, unfilled stop loss order

**new_stop_price**: Updated trigger price for the stop loss (optional)
- New price level that will trigger the order
- Must be appropriate for order direction (below market for sell stops)
- Use current market price as reference for reasonable levels

**new_quantity**: Updated quantity for the stop loss (optional)
- Number of shares for the modified order
- Cannot exceed your current position size
- Useful for partial position management

**new_limit_price**: Updated limit price for stop-limit orders (optional)
- Only applicable to "STP LMT" order types
- Price at which limit order will be placed when stop triggers
- Should be reasonable relative to new stop price

**new_time_in_force**: Updated order duration (optional)
- "GTC" (Good Till Cancelled) or "DAY"
- Most risk management strategies use GTC for persistence
- DAY orders expire at market close

**new_trail_amount**: Updated trailing amount for trailing stops (optional)
- Dollar amount to trail behind market price
- Only applicable to "TRAIL" order types
- Adjusts dynamically with market movements

**new_trail_percent**: Updated trailing percentage (optional)
- Percentage to trail behind market price
- Only applicable to "TRAIL" order types
- Expressed as decimal (5.0 = 5%)

## Examples

### Tighten stop loss as position profits
```python
# Original stop at $180, stock now at $200, tighten to $190
modify_stop_loss(
    order_id=12345,
    new_stop_price=190.00
)
```

### Reduce position size via stop
```python
# Reduce stop from 100 shares to 50 shares
modify_stop_loss(
    order_id=12345,
    new_quantity=50
)
```

### Adjust trailing stop percentage
```python
# Change trailing stop from 5% to 8% for more room
modify_stop_loss(
    order_id=12345,
    new_trail_percent=8.0
)
```

### Update stop-limit order prices
```python
# Adjust both stop and limit prices
modify_stop_loss(
    order_id=12345,
    new_stop_price=185.00,
    new_limit_price=183.00
)
```

### Change order duration
```python
# Change from GTC to DAY order
modify_stop_loss(
    order_id=12345,
    new_time_in_force="DAY"
)
```

## Workflow

**Profit Protection Process:**

1. **Monitor positions**: Check current prices vs original stop levels
2. **Identify profit opportunities**: Note positions with significant gains
3. **Calculate new stops**: Determine appropriate tighter stop levels
4. **Modify orders**: Use modify_stop_loss to update trigger prices
5. **Verify changes**: Check get_stop_losses to confirm modifications

**Dynamic Risk Management:**
1. **Market volatility changes**: Adjust stop distances for changing conditions
2. **Position sizing adjustments**: Modify quantities based on portfolio changes
3. **Time decay management**: Convert GTC orders to DAY when appropriate
4. **Strategy evolution**: Adapt stops as market conditions change

**Active Trading Workflow:**
1. **Intraday monitoring**: Watch for opportunities to tighten stops
2. **Technical level updates**: Adjust stops to new support/resistance levels
3. **News-based adjustments**: Modify stops around earnings or events
4. **End-of-day review**: Update stops based on daily price action

## Troubleshooting

### "Order not found" or "Invalid order ID"
• Order may have already been filled or cancelled
• Check get_stop_losses to see current active orders
• Order IDs are unique - ensure you're using correct ID
• Recently placed orders may need time to appear in system

### "Order cannot be modified"
• Some order types have modification restrictions
• Orders in process of execution cannot be modified
• Filled orders cannot be modified - they're complete
• Try canceling and placing new order if modification fails

### "New stop price rejected"
• Stop price may be too close to current market price
• Check that stop price direction is correct (sell stops below market)
• Some stocks have minimum stop distance requirements
• During volatile periods, exchanges may reject certain prices

### "Quantity exceeds position size"
• New quantity cannot exceed your current stock position
• Other orders may have reduced available shares
• Check get_portfolio to verify current position size
• Consider modifying other orders if needed

### "Modification timeout"
• IBKR systems may be slow during high-volume periods
• Modification request may be queued - wait before retrying
• Check get_stop_losses after a few minutes to see if change applied
• Network issues can cause modification delays

### "Order type doesn't support parameter"
• Trailing parameters only work with TRAIL order types
• Limit prices only apply to STP LMT orders
• Check original order type with get_stop_losses
• Some modifications may require canceling and replacing order

## Related Tools
• get_stop_losses - View current orders and their IDs for modification
• place_stop_loss - Create new stop loss orders
• cancel_stop_loss - Remove orders that can't be modified
• get_market_data - Check current prices for stop level decisions
• get_portfolio - Verify position sizes before quantity modifications
