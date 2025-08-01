# get_open_orders

View all pending orders that haven't been filled yet.

## Overview

The `get_open_orders` tool shows you all orders that are currently active in the market, waiting to be executed. This includes limit orders waiting for your target price, stop losses monitoring your positions, and any other orders that are "working" in the system.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | No | Specific account ID to query. If not provided, uses your current active account |

## Usage Examples

### View All Open Orders
```
get_open_orders()
```
Shows all pending orders for your current account.

### Account-Specific Query
```
get_open_orders(account="DUH905195")
```
Shows open orders for a specific account.

## Response Format

Each open order contains:

- **Order ID**: Unique identifier for tracking
- **Symbol**: Stock, forex pair, or instrument
- **Action**: BUY or SELL
- **Quantity**: Number of shares/units
- **Order Type**: LMT, STP, STP LMT, TRAIL
- **Limit Price**: Target price (for limit orders)
- **Stop Price**: Trigger price (for stop orders)  
- **Time in Force**: GTC, DAY, etc.
- **Status**: PreSubmitted, Submitted, etc.
- **Remaining**: Unfilled quantity
- **Created Time**: When order was placed

## Example Response

```json
[
  {
    "orderId": 67890,
    "symbol": "TSLA",
    "action": "BUY",
    "totalQuantity": 100,
    "orderType": "LMT",
    "limitPrice": 200.00,
    "timeInForce": "GTC",
    "status": "Submitted",
    "remaining": 100,
    "createdTime": "2024-01-15T09:30:00Z"
  },
  {
    "orderId": 67891,
    "symbol": "AAPL", 
    "action": "SELL",
    "totalQuantity": 50,
    "orderType": "STP",
    "stopPrice": 145.00,
    "timeInForce": "GTC",
    "status": "Submitted", 
    "remaining": 50,
    "createdTime": "2024-01-15T10:15:00Z"
  }
]
```

## Order Status Meanings

- **PreSubmitted**: Order created but not yet sent to exchange
- **Submitted**: Order sent to exchange and active
- **PendingSubmit**: Order being processed for submission
- **PendingCancel**: Cancel request in progress
- **Inactive**: Order exists but not currently active

## Order Types Explained

### Limit Orders (LMT)
- **Purpose**: Buy/sell at specific price or better
- **Status**: Waiting for market price to reach your limit
- **Example**: "BUY 100 AAPL at $150 or less"

### Stop Orders (STP)
- **Purpose**: Trigger market order when price reached
- **Status**: Monitoring market price for trigger
- **Example**: "SELL 100 AAPL if price drops to $140"

### Stop Limit Orders (STP LMT) 
- **Purpose**: Trigger limit order when stop price reached
- **Status**: Waiting for stop trigger, then becomes limit order
- **Example**: "SELL 100 AAPL if price drops to $140, but no less than $139"

### Trailing Stop Orders (TRAIL)
- **Purpose**: Dynamic stop that follows favorable price movement
- **Status**: Continuously adjusting stop price
- **Example**: "SELL 100 AAPL if price drops 5% from highest point"

## Time in Force Options

- **GTC (Good Till Cancelled)**: Order stays active until filled or cancelled
- **DAY**: Order expires at end of trading day
- **IOC (Immediate or Cancel)**: Fill immediately or cancel
- **FOK (Fill or Kill)**: Fill entire order immediately or cancel

## Common Use Cases

- **Order Management**: Monitor all active trading instructions
- **Position Protection**: Check stop losses are in place
- **Price Targeting**: Track limit orders waiting for entry/exit prices
- **Risk Assessment**: Review total market exposure from pending orders
- **Daily Review**: End-of-day check of what orders are still working

## Managing Open Orders

After viewing open orders, you can:
- **Modify**: Use `modify_stop_loss` for stop orders
- **Cancel**: Use `cancel_stop_loss` for stop orders
- **Monitor**: Check status and remaining quantity
- **Adjust**: Change prices or quantities as market conditions change

## Notes

- Orders may execute between when you check and when they're displayed
- Paper trading accounts may have simulated order behavior
- Market hours affect order processing and status
- Some orders may not appear immediately after placement

## Related Tools

- `get_completed_orders` - Recently filled orders
- `get_executions` - Detailed execution information
- `place_stop_loss` - Create new stop loss orders
- `modify_stop_loss` - Adjust existing stop orders
- `cancel_stop_loss` - Remove stop loss orders

## Troubleshooting

**No orders shown**: This is normal if you don't have any pending orders. All your orders may have been filled or cancelled.

**Order not appearing**: New orders may take a few seconds to show up. Check the order status or try again.

**Unexpected status**: Order status can change rapidly during market hours. Refresh to see current status.

**Order partially filled**: Check the "remaining" field to see how much quantity is still pending.
