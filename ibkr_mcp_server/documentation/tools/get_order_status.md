# get_order_status

## Overview
Retrieve detailed status information for any order by its ID. Essential for tracking order execution progress, 
understanding fill details, and monitoring order lifecycle from placement to completion.

Provides comprehensive order information including execution status, fill quantities, average prices, 
remaining quantities, and timestamps for all order state changes.

## Parameters

**order_id**: Unique order identifier to query
• Integer value from original order placement response
• Get from place_market_order, place_limit_order, place_bracket_order results
• Also available from get_open_orders or get_completed_orders
• Must be exact order ID belonging to your account

## Examples

### Check order execution status
```python
get_order_status(12345)
```
Returns complete status information for order 12345

### Monitor new order after placement
```python
# Place order and immediately check status
result = place_limit_order("AAPL", "BUY", 100, 175.50)
order_id = result["order_id"]
status = get_order_status(order_id)
```

### Track bracket order components
```python
# Check parent order status
parent_status = get_order_status(12345)
# Check associated stop and target orders
stop_status = get_order_status(12346)
target_status = get_order_status(12347)
```

## Response Information

### Order Identification
• **Order ID**: Unique identifier for this order
• **Parent Order ID**: For bracket order components
• **Symbol**: Stock symbol or currency pair
• **Exchange**: Trading venue (SMART, AEB, TSE, etc.)
• **Currency**: Trading currency (USD, EUR, JPY, etc.)

### Order Parameters
• **Action**: BUY or SELL
• **Order Type**: MKT (market), LMT (limit), STP (stop), etc.
• **Total Quantity**: Original order size
• **Limit Price**: Limit price (for limit orders)
• **Stop Price**: Stop trigger price (for stop orders)
• **Time in Force**: DAY, GTC, IOC, FOK

### Execution Details
• **Status**: Submitted, PreSubmitted, Filled, Cancelled, etc.
• **Filled Quantity**: Number of shares actually executed
• **Remaining Quantity**: Shares still pending execution
• **Average Fill Price**: Weighted average price of all fills
• **Commission**: Trading fees charged
• **Last Fill Price**: Price of most recent partial fill
• **Last Fill Quantity**: Size of most recent partial fill

### Timing Information
• **Submit Time**: When order was submitted to exchange
• **Last Update Time**: Most recent status change
• **Fill Time**: When order was completed (if filled)
• **Expiry Time**: When DAY orders expire (if applicable)

## Order Status Values

### Active States
• **Submitted**: Order sent to exchange, awaiting acceptance
• **PreSubmitted**: Order accepted but not yet active (for future sessions)
• **Working**: Order is active and working in the market
• **PartiallyFilled**: Some shares filled, remainder still working

### Completed States
• **Filled**: Order completely executed
• **Cancelled**: Order cancelled before execution
• **Expired**: DAY order expired at end of session
• **Rejected**: Order rejected by exchange or risk management

### Special States
• **PendingSubmit**: Order being processed for submission
• **PendingCancel**: Cancellation request being processed
• **PendingModify**: Modification request being processed

## Workflow

**Real-Time Order Monitoring:**
1. **Immediate status check**: Get status right after order placement
2. **Periodic monitoring**: Check status every few minutes for active orders
3. **Fill detection**: Monitor for status changes to Filled or PartiallyFilled
4. **Execution analysis**: Review fill prices and quantities
5. **Next action planning**: Decide on follow-up orders based on fills

**Order Execution Analysis:**
1. **Fill price review**: Compare actual fills to expected prices
2. **Execution quality**: Assess if fills were favorable
3. **Partial fill management**: Decide whether to cancel remainder
4. **Commission tracking**: Monitor trading costs
5. **Performance evaluation**: Analyze execution vs expectations

**Problem Diagnosis:**
1. **Status investigation**: Check why order isn't filling
2. **Market condition analysis**: Compare order price to current market
3. **Order adjustment planning**: Determine if modification needed
4. **Cancellation assessment**: Decide if order should be cancelled
5. **Strategy revision**: Adjust approach based on order behavior

## Safety Features

### Information Security
• **Account Isolation**: Only shows orders belonging to your account
• **Order Validation**: Confirms order ID exists and is accessible
• **Status Accuracy**: Real-time status from IBKR systems
• **Complete Audit**: All status queries logged for compliance

### Error Handling
• **Invalid Order ID**: Clear error message for non-existent orders
• **Access Control**: Cannot view orders from other accounts
• **Connection Monitoring**: Handles IBKR connectivity issues gracefully
• **Status Consistency**: Ensures status information is current and accurate

## Troubleshooting

### "Order not found" 
• Verify order ID is correct (check for typos)
• Order may be very old and no longer in system
• Order must belong to your account
• Use get_open_orders or get_completed_orders to find valid order IDs

### "Order status shows 'Unknown'"
• Temporary IBKR system issue - try again in a few seconds
• Order may be in transition between states
• Check IBKR connection status with get_connection_status
• Contact support if status remains unknown for extended period

### "Filled quantity doesn't match expected"
• Partial fills are common for large orders
• Check remaining quantity to see if order is still working
• Market conditions may prevent complete fills
• Consider modifying price if remainder isn't filling

### "Commission shows zero"
• Some paper trading accounts don't calculate commissions
• Commission may be calculated at end of trading day
• Bonds and some international stocks have different commission structures
• Check with IBKR if commission calculation seems incorrect

### "Order shows expired but was GTC"
• GTC orders can still expire under certain conditions
• Some exchanges have maximum GTC duration (90 days typically)
• Corporate actions or stock splits may cause order cancellation
• Check order parameters to confirm time-in-force setting

### "Status not updating in real-time"
• IBKR status updates can have slight delays
• Try refreshing status after 10-15 seconds
• During high volatility, status updates may be slower
• Use get_executions for fastest fill notifications

## Related Tools
• get_open_orders - See all currently pending orders and their IDs
• get_completed_orders - View recently filled or cancelled orders
• get_executions - Get detailed execution information for filled orders
• modify_order - Change order parameters based on current status
• cancel_order - Cancel order if status shows it's still working
• place_market_order - Place new order based on current order analysis
• get_portfolio - See how executed orders affected your positions
