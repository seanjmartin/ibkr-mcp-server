# cancel_order

## Overview
Cancel pending orders that have not yet been executed. Essential for order management when market conditions change, strategies need adjustment, or orders are no longer needed.

Works with all order types (market, limit, stop, bracket) and provides immediate cancellation for better position control. Cancellation is typically instantaneous for unfilled orders.

## Parameters

**order_id**: Unique order identifier to cancel
• Integer value returned when order was originally placed
• Get from place_market_order, place_limit_order, or place_bracket_order responses
• Also available via get_open_orders for pending orders
• Must be exact order ID - partial matches not supported

## Examples

### Cancel single order
```python
cancel_order(12345)
```
Cancels order with ID 12345 if still pending

### Cancel after order placement
```python
# Place order and get ID
result = place_limit_order("AAPL", "BUY", 100, 175.50)
order_id = result["order_id"]

# Cancel if conditions change
cancel_order(order_id)
```

### Cancel from open orders list
```python
# Review pending orders
open_orders = get_open_orders()
for order in open_orders:
    if order["symbol"] == "TSLA":
        cancel_order(order["order_id"])
```

## Workflow

**Order Management Strategy:**
1. **Order review**: Use get_open_orders to see pending orders
2. **Strategy reassessment**: Determine which orders to keep/cancel
3. **Selective cancellation**: Cancel orders that no longer fit strategy
4. **Confirmation check**: Verify cancellation with get_order_status
5. **Portfolio rebalancing**: Place new orders if needed

**Market Condition Response:**
1. **Market monitoring**: Watch for significant price movements
2. **Order relevance check**: Assess if pending orders still make sense
3. **Immediate cancellation**: Cancel outdated orders quickly
4. **Strategy adjustment**: Replace with orders at better prices
5. **Risk management**: Ensure cancellations don't leave positions unprotected

**Position Size Management:**
1. **Portfolio review**: Check current position sizes
2. **Order impact assessment**: Evaluate how pending orders affect allocation
3. **Excess order cancellation**: Cancel orders that would over-allocate
4. **Rebalancing**: Adjust remaining orders for proper position sizing
5. **Risk limits**: Ensure total exposure stays within limits

## Safety Features

### Automatic Protection
• **Kill Switch**: Order cancellation continues to work even in emergency mode
• **Rate Limiting**: Cancellation requests subject to API rate limits
• **Audit Logging**: All cancellation attempts logged for compliance
• **Safety Wrapper**: Cancellation uses same safety framework as other tools

### Cancellation Validation
• **Order ID Verification**: Confirms order exists and belongs to account
• **Order Status Check**: Ensures order is still cancellable (not already filled)
• **Account Verification**: Confirms order belongs to current account
• **Timing Validation**: Checks if order is still in cancellable state

### Risk Management Integration
• **Emergency Cancellation**: Can be used as part of risk management
• **Position Protection**: Cancelling protective orders requires confirmation
• **Audit Trail**: Complete record of cancellation reasons and timing
• **Safety Framework**: Integrated with overall trading safety system

## Troubleshooting

### "Order not found" or "Invalid order ID"
• Verify order ID is correct (check for typos)
• Order may have already been filled or cancelled
• Use get_open_orders to see current pending orders
• Order ID must belong to your account

### "Order cannot be cancelled - already filled"
• Order executed before cancellation request reached exchange
• Check get_executions or get_completed_orders for fill details
• This is normal behavior for fast-moving markets
• Consider using shorter time-in-force for future orders

### "Order cannot be cancelled - already cancelled"
• Order was previously cancelled (possibly by another system)
• Check order history to see cancellation timestamp
• No action needed - order is already cancelled
• Use get_order_status to confirm final order state

### "Cancellation request rejected"
• Order may be in process of being filled
• Exchange may not allow cancellation at this moment
• Try again in a few seconds if order is still pending
• Contact support if persistent issues with cancellation

### "Rate limit exceeded for cancellations"
• Too many cancellation requests in short time period
• Wait 1 minute before attempting more cancellations
• Consider batching cancellation decisions
• Review cancellation frequency patterns

### "Cannot cancel bracket order component"
• Some bracket order components cannot be cancelled individually
• Cancel the parent order to cancel entire bracket
• Check order relationships with get_order_status
• Use modify_order instead if you want to adjust prices

## Related Tools
• get_open_orders - See all pending orders available for cancellation
• get_order_status - Check current status of specific order before cancelling
• get_completed_orders - Verify if order was filled before cancellation attempt
• modify_order - Alternative to cancelling - adjust order parameters instead
• place_market_order - Replace cancelled order with immediate execution
• place_limit_order - Replace cancelled order with new limit price
• get_executions - Check if order was partially filled before cancellation
