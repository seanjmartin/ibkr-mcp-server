# cancel_stop_loss

## Overview
Remove a stop loss order you no longer want. Completely cancels the order and frees up
the position for other strategies or manual management. Essential for order management
when you want to close positions manually or replace stops with different parameters.

Use this tool when you want to remove risk protection temporarily, replace stops with
different order types, or prepare to manually close positions.

## Parameters

**order_id**: The order ID of the stop loss to cancel (required)
- Get order IDs from get_stop_losses tool
- Order ID is returned when placing stop loss orders
- Must be an active, unfilled stop loss order

## Examples

### Cancel single stop loss order
```python
cancel_stop_loss(order_id=12345)
```
Removes the stop loss order completely

### Pre-manual close workflow
```python
# 1. Check current stops
stops = get_stop_losses(symbol="AAPL")
# 2. Cancel stop before manual close
cancel_stop_loss(order_id=stops[0]['order_id'])
# 3. Manually close position at desired price
```

### Replace stop with different type
```python
# 1. Cancel existing basic stop
cancel_stop_loss(order_id=12345)
# 2. Place new trailing stop
place_stop_loss(
    symbol="AAPL",
    action="SELL",
    quantity=100,
    order_type="TRAIL",
    trail_percent=5.0
)
```

## Workflow

**Manual Position Management:**

1. **Identify target positions**: Choose positions for manual management
2. **Locate stop orders**: Use get_stop_losses to find relevant orders
3. **Cancel protection**: Remove stop loss orders with cancel_stop_loss
4. **Manual execution**: Place manual orders at desired timing/price
5. **Monitor closely**: Without stops, positions have no automatic protection

**Stop Loss Replacement Process:**
1. **Evaluate current stops**: Assess if current stops are optimal
2. **Plan new strategy**: Decide on better stop loss approach
3. **Cancel existing**: Remove current stop loss orders
4. **Implement new**: Place improved stop loss orders
5. **Verify new protection**: Confirm new stops are active

**Position Closure Preparation:**
1. **Decision to close**: Determine positions to close manually
2. **Remove automation**: Cancel stop losses to prevent interference
3. **Market timing**: Wait for optimal manual exit opportunity
4. **Execute closure**: Manually close positions at desired prices
5. **Confirm completion**: Verify positions are closed and stops cancelled

## Troubleshooting

### "Order not found" or "Invalid order ID"
• Order may have already been filled or cancelled
• Check get_stop_losses to see current active orders
• Order IDs change when orders are modified or replaced
• Recently cancelled orders may still appear briefly

### "Order cannot be cancelled"
• Order may be in process of execution (partially filled)
• Some order types have cancellation restrictions during market hours
• Orders very close to execution may be protected from cancellation
• Try again in a few moments if order is in transition

### "Cancellation timeout or delay"
• High-volume periods may cause delayed cancellation processing
• IBKR systems may queue cancellation requests
• Check get_stop_losses after 30-60 seconds to verify cancellation
• Network issues can cause cancellation delays

### "Order shows as cancelled but still appears"
• System updates may be delayed during busy periods
• Cancelled orders may remain visible briefly before removal
• Refresh get_stop_losses view to see updated status
• Some display systems cache order information

### "Accidental cancellation"
• Once cancelled, stop loss orders cannot be "uncancelled"
• Position is now unprotected until new stop is placed
• Place new stop loss immediately if cancellation was accidental
• Consider using modify_stop_loss instead of cancel/replace workflow

### "Position now unprotected"
• Cancelling stop loss removes all automatic risk protection
• Monitor position closely until new protection is in place
• Consider immediate manual exit if market moves against position
• Set alerts or notifications for position without stop protection

## Related Tools
• get_stop_losses - View current orders and their IDs for cancellation
• place_stop_loss - Create new stop loss orders after cancellation
• modify_stop_loss - Adjust existing orders instead of cancel/replace
• get_portfolio - Check positions that may need new protection
• get_market_data - Monitor unprotected positions after cancellation

## Safety Considerations

**Risk Management:**
• Cancelling stops removes automatic loss protection
• Monitor positions closely until new protection is established
• Have a manual exit plan before cancelling protective orders
• Consider market conditions before removing stop protection

**Best Practices:**
• Cancel stops only when you have immediate alternative plan
• Don't leave large positions unprotected for extended periods
• Use modify_stop_loss when possible instead of cancel/replace
• Set position alerts if you must temporarily remove stops
• Have predetermined manual exit levels ready
