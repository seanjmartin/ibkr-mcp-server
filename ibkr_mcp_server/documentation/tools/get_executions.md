# get_executions

View detailed execution information for your trades including commission, settlement, and timing data.

## Overview

The `get_executions` tool provides comprehensive details about how your orders were executed by the exchange. Unlike `get_completed_orders` which shows order-level information, this tool shows execution-level details including partial fills, multiple executions per order, and detailed commission breakdowns.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | No | Specific account ID to query. If not provided, uses your current active account |
| `symbol` | string | No | Filter executions by specific symbol (e.g., "AAPL", "EURUSD") |

## Usage Examples

### All Executions
```
get_executions()
```
Shows all recent executions for your current account.

### Account-Specific
```
get_executions(account="DUH905195")
```
Shows executions for a specific account.

### Symbol-Specific
```
get_executions(symbol="AAPL")
```
Shows only executions for Apple stock.

### Combined Filters
```
get_executions(account="DUH905195", symbol="TSLA")
```
Shows Tesla executions for a specific account.

## Response Format

Each execution contains detailed information:

- **Execution ID**: Unique identifier for this execution
- **Order ID**: Parent order that generated this execution
- **Symbol**: Instrument traded
- **Side**: BUY or SELL
- **Shares**: Quantity executed in this fill
- **Price**: Exact execution price
- **Time**: Precise execution timestamp
- **Exchange**: Where the execution occurred
- **Commission**: Fees for this specific execution
- **Realized PnL**: Profit/loss realized from this execution
- **Client Order ID**: Your internal order reference

## Example Response

```json
[
  {
    "execId": "0001f4e5.65f0b2c1.01.01",
    "orderId": 12345,
    "symbol": "AAPL",
    "side": "BUY",
    "shares": 50,
    "price": 150.23,
    "time": "2024-01-15T14:30:25.123Z",
    "exchange": "NASDAQ",
    "commission": 0.75,
    "realizedPnL": 0.0,
    "clientOrderId": "MyOrder_001"
  },
  {
    "execId": "0001f4e5.65f0b2c2.01.01", 
    "orderId": 12345,
    "symbol": "AAPL",
    "side": "BUY",
    "shares": 50,
    "price": 150.27,
    "time": "2024-01-15T14:30:26.456Z",
    "exchange": "NASDAQ",
    "commission": 0.75,
    "realizedPnL": 0.0,
    "clientOrderId": "MyOrder_001"
  }
]
```

## Key Differences from get_completed_orders

| Feature | get_completed_orders | get_executions |
|---------|---------------------|----------------|
| **Level** | Order-level summary | Execution-level detail |
| **Granularity** | One record per order | Multiple records per order (if partially filled) |
| **Price Info** | Average fill price | Exact execution prices |
| **Commission** | Total commission | Commission per execution |
| **Timing** | Order completion time | Individual execution times |

## Common Use Cases

- **Execution Analysis**: Understand how large orders were filled
- **Price Improvement Tracking**: See if you got better prices than expected
- **Commission Calculation**: Detailed fee breakdown per execution
- **Market Impact Analysis**: Study how your orders affected the market
- **Algorithmic Trading**: Review execution quality for trading algorithms
- **Compliance Reporting**: Detailed audit trail for regulatory requirements

## Understanding Multiple Executions

Large orders are often filled in multiple pieces:

```
Order: BUY 1000 AAPL at Market
├── Execution 1: 300 shares at $150.23
├── Execution 2: 400 shares at $150.25  
└── Execution 3: 300 shares at $150.27
```

Each execution appears as a separate record with its own commission and timestamp.

## Settlement Information

Executions show when trades will settle:
- **US Stocks**: Typically T+1 (next business day)
- **International**: May be T+2 or T+3
- **Forex**: Usually T+2
- **Options**: T+1

## Notes

- Executions are the building blocks of completed orders
- Perfect for detailed trade analysis and cost accounting
- Shows actual market conditions when your trades executed
- Essential for understanding execution quality and market impact

## Related Tools

- `get_completed_orders` - Order-level trading history
- `get_open_orders` - Currently pending orders
- `get_portfolio` - Current positions
- `place_stop_loss` - Risk management orders

## Troubleshooting

**No executions found**: Check that you have recent trading activity. Paper accounts may have limited execution data.

**Missing details**: Some execution details may not be available immediately after trading. Real-time data may take a few minutes to populate fully.

**Multiple records**: This is normal - one order can generate multiple executions as it gets filled in pieces.
