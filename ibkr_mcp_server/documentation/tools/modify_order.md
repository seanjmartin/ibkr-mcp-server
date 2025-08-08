# modify_order

## Overview
Modify existing pending orders by changing quantity, price, or time-in-force without cancelling and re-placing. 
Order modification is faster and maintains queue priority better than cancelling and creating new orders.

Ideal for adjusting to changing market conditions while keeping your place in the order book. Works with limit orders, stop orders, and other order types that support modification.

## Parameters

**order_id**: Unique order identifier to modify
• Integer value from original order placement
• Get from place_limit_order, place_market_order responses
• Also available via get_open_orders for pending orders
• Must be exact order ID for existing unfilled order

**quantity**: New order quantity (optional)
• Whole number of shares for stocks (e.g., 100, 250, 500)
• Minimum 25,000 units for forex pairs
• Can increase or decrease from original quantity
• Must be positive integer within MAX_ORDER_SIZE limits

**price**: New limit price (optional)  
• For limit orders: new limit price for execution
• For stop orders: new stop trigger price
• Use local currency (USD for US stocks, EUR for ASML, etc.)
• Price must be reasonable relative to current market

**time_in_force**: New order duration (optional)
• "DAY" - Order expires at end of trading session
• "GTC" - Good Till Cancelled, remains until filled/cancelled
• "IOC" - Immediate Or Cancel
• "FOK" - Fill Or Kill
• Can change from DAY to GTC or vice versa

## Examples

### Adjust limit price closer to market
```python
modify_order(12345, price=178.25)
```
Changes limit price to $178.25 for order 12345

### Increase order quantity
```python
modify_order(12345, quantity=200)
```
Changes order size to 200 shares

### Change to GTC order
```python
modify_order(12345, time_in_force="GTC")
```
Makes order Good Till Cancelled instead of Day order

### Multiple modifications
```python
modify_order(12345, quantity=150, price=179.50, time_in_force="GTC")
```
Changes quantity, price, and duration in single modification

### International stock modification
```python
modify_order(54321, price=645.00)  # ASML order price change to €645.00
```

## Workflow

**Dynamic Price Management:**
1. **Market monitoring**: Watch price movement relative to your orders
2. **Opportunity assessment**: Decide if price adjustment needed
3. **Quick modification**: Adjust limit price to stay competitive
4. **Fill monitoring**: Use get_order_status to track execution
5. **Further adjustments**: Modify again if market continues moving

**Order Size Optimization:**
1. **Position review**: Check current holdings and available cash
2. **Risk assessment**: Determine optimal position size
3. **Quantity modification**: Adjust order size without losing queue priority
4. **Balance verification**: Ensure sufficient buying power for increased size
5. **Execution tracking**: Monitor fill progress with new quantity

**Time Extension Strategy:**
1. **End of day approach**: Evaluate unfilled DAY orders
2. **Strategy persistence**: Decide if order should continue overnight
3. **GTC conversion**: Change DAY orders to Good Till Cancelled
4. **Extended monitoring**: Track GTC orders over multiple sessions
5. **Eventual cancellation**: Remove stale GTC orders when strategy changes

## Safety Features

### Automatic Protection
• **Kill Switch**: Order modification disabled if emergency mode active
• **Rate Limiting**: Modification requests subject to API rate limits (5/minute)
• **Size Limits**: Modified quantity must be within MAX_ORDER_SIZE
• **Daily Limits**: Modifications count toward daily order activity limits
• **Account Verification**: Confirms order belongs to current account

### Modification Validation
• **Order Existence**: Verifies order ID exists and is modifiable
• **Parameter Validation**: Ensures new values are reasonable and valid
• **Market Rules**: Checks exchange-specific modification rules
• **Buying Power**: Verifies sufficient funds for increased order size
• **Price Reasonableness**: Ensures modified price isn't too far from market

### Risk Management Integration
• **Audit Logging**: All modifications logged with before/after values
• **Safety Framework**: Uses same validation as other trading operations
• **Position Limits**: Modified orders must stay within position size limits
• **Emergency Integration**: Modification can be halted via kill switch

## Troubleshooting

### "Order not found" or "Order not modifiable"
• Verify order ID is correct and order still exists
• Order may have been filled, cancelled, or already executed
• Some order types cannot be modified (check with get_order_status)
• Use get_open_orders to see currently modifiable orders

### "New quantity exceeds maximum order size"
• Modified quantity exceeds MAX_ORDER_SIZE configuration limit
• Reduce quantity to fit within limits
• Consider placing additional separate order instead
• Check current size limits with account configuration

### "Insufficient buying power for increased quantity"
• Increasing order size requires additional buying power
• Check available cash with get_account_summary
• Cancel other pending orders to free up buying power
• Reduce quantity increase to fit available funds

### "Price modification rejected - too far from market"
• New limit price is too far from current market price
• Check current market price with get_market_data
• Adjust price closer to current market levels
• Some exchanges have rules about maximum price deviation

### "Time in force change not allowed"
• Not all order types support time-in-force changes
• Some exchanges don't allow changing from DAY to GTC or vice versa
• Cancel and re-place order if TIF change is critical
• Check order type capabilities with get_order_status

### "Modification request rejected by exchange"
• Exchange may not allow modification at current time
• Order may be in process of being filled
• Try again in a few seconds if order is still pending
• Some complex orders have modification restrictions

## Related Tools
• get_open_orders - See all orders available for modification
• get_order_status - Check current order parameters before modifying
• get_market_data - Check current prices to set appropriate new limits
• get_account_summary - Verify buying power before increasing order size
• cancel_order - Alternative to modification if major changes needed
• place_limit_order - Replace order entirely if modification not sufficient
• get_executions - Check if order partially filled before modification
