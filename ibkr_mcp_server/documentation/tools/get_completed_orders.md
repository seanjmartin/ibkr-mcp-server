# get_completed_orders

View your recently completed trades and transactions.

## Overview

The `get_completed_orders` tool retrieves your trading history, showing all orders that have been fully or partially executed. This includes market orders, limit orders, stop losses, and any other order types that have been filled by the exchange.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | string | No | Specific account ID to query. If not provided, uses your current active account |

## Usage Examples

### Basic Usage
```
get_completed_orders()
```
Shows all completed orders for your current account.

### Account-Specific Query
```
get_completed_orders(account="DUH905195")
```
Shows completed orders for a specific account.

## Response Format

The tool returns a list of completed order objects with comprehensive details:

### Order Identification
- **order_id**: Unique IBKR order identifier
- **client_id**: API client ID that placed the order
- **order_ref**: Custom order reference string

### Contract Information
- **symbol**: Stock, forex pair, or instrument symbol
- **exchange**: Trading exchange (SMART, NYSE, AEB, etc.)
- **currency**: Base currency of the instrument

### Order Details
- **action**: BUY or SELL
- **quantity**: Total order quantity (shares/units)
- **order_type**: Order type (MKT, LMT, STP, STP LMT, TRAIL)
- **limit_price**: Limit price (if applicable)
- **aux_price**: Auxiliary price for stop orders
- **time_in_force**: Order duration (DAY, GTC, IOC, FOK)

### Execution Status
- **status**: Current order status
- **filled**: Number of shares filled
- **remaining**: Number of shares remaining
- **avg_fill_price**: Average execution price
- **commission**: Trading commission charged

### Account Information
- **account**: Account ID that placed the order

## Example Response

```json
[
  {
    "order_id": 12345,
    "symbol": "AAPL",
    "exchange": "SMART",
    "currency": "USD",
    "action": "BUY",
    "quantity": 100,
    "order_type": "MKT",
    "limit_price": null,
    "aux_price": null,
    "time_in_force": "DAY",
    "status": "Filled",
    "filled": 100,
    "remaining": 0,
    "avg_fill_price": 150.25,
    "commission": 1.50,
    "account": "DUH905195",
    "order_ref": "",
    "client_id": 5
  }
]
```

## IBKR API Data Structure Considerations

**Important Technical Details:** The `get_completed_orders` tool has been optimized to handle IBKR API data structure limitations:

### Data Source Mapping 
- **order_id**: Uses `order.permId` (not `orderStatus.orderId` which is 0 for completed orders)
- **filled**: Uses `order.filledQuantity` (not `orderStatus.filled` which is 0 for completed orders)  
- **quantity**: Uses `order.totalQuantity` or `order.filledQuantity` if total is 0
- **avg_fill_price**: Calculated from available execution data, may be 0 for some orders

### IBKR API Limitations
The `reqCompletedOrdersAsync()` API does not provide complete execution details for historical completed orders:

- **avg_fill_price may be 0**: For many completed orders, detailed execution pricing is not available
- **orderStatus fields are zeros**: The `orderStatus` object contains zeros for `filled`, `orderId`, etc. in completed orders
- **Limited execution detail**: For comprehensive execution prices and fill information, use `get_executions()` instead

### Why Some Data May Be Limited
IBKR's completed orders API focuses on order structure rather than execution quality. The trade objects returned contain:
- ✅ **Available**: Order details, filled quantities, basic status
- ❌ **Limited**: Detailed execution prices, commission breakdowns, venue information
- ❌ **Zero/Empty**: Fields in `orderStatus` object (not used by this tool)

### For Detailed Execution Analysis
If you need comprehensive execution data including:
- Exact fill prices for each execution
- Execution timestamps and venues  
- Commission breakdowns
- Price improvement analysis

Use the `get_executions()` tool instead, which queries IBKR's execution API specifically.

## Common Use Cases

- **Trading Review**: Analyze your recent trading activity
- **Performance Analysis**: Calculate profits and losses from executed trades
- **Tax Reporting**: Gather transaction data for tax purposes
- **Commission Tracking**: Monitor trading costs and fees
- **Order Verification**: Confirm that orders were executed as expected

## Key Differences from get_executions

| Aspect | `get_completed_orders` | `get_executions` |
|--------|------------------------|-------------------|
| **Data Level** | Order-level summary | Execution-level detail |
| **Granularity** | One record per order | Multiple records per order (if partially filled) |
| **IBKR API Call** | `reqCompletedOrdersAsync()` | `reqExecutionsAsync()` |
| **Returns** | `List[Trade]` objects | `List[Fill]` objects |
| **Price Info** | Average fill price | Exact execution prices for each fill |
| **Commission** | Total commission | Commission per execution |
| **Timing** | Order completion time | Individual execution timestamps |
| **Focus** | Order management | Execution quality analysis |
| **Record Count** | One per order | Multiple per order (if filled in pieces) |
| **Filtering** | Account only | Account, symbol, days_back |
| **API Reliability** | May timeout (5s limit) | More robust |

## When to Use Each Tool

### Use `get_completed_orders` When You Need:
- **Order Management**: Review what orders have been filled
- **Portfolio Review**: High-level trading activity summary
- **Trading Activity Reports**: General transaction history
- **Order Verification**: Confirm orders executed as expected
- **P&L Attribution**: Order-level profit/loss analysis
- **Tax Reporting**: Simplified transaction records
- **Commission Tracking**: Total trading costs per order

### Use `get_executions` When You Need:
- **Execution Quality Analysis**: Understand how your orders were filled
- **Price Improvement Tracking**: See actual execution prices vs. quotes
- **Market Impact Analysis**: Study how large orders affected prices
- **Venue Performance**: Compare execution quality across exchanges
- **Detailed Commission Analysis**: Fee breakdown per execution
- **Regulatory Compliance**: Detailed audit trail for reporting

## Practical Example: Order vs Execution Views

**Scenario:** You place a market order to buy 1,000 shares of AAPL

### `get_completed_orders` Response (1 record - Summary View):
```json
[
  {
    "order_id": 123,
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 1000,
    "order_type": "MKT",
    "status": "Filled",
    "filled": 1000,
    "remaining": 0,
    "avg_fill_price": 180.05,
    "commission": 1.00,
    "account": "DUH905195"
  }
]
```

### `get_executions` Response (3 records - Detailed View):
```json
[
  {
    "order_id": 123, "shares": 400, "price": 180.00, 
    "time": "14:30:01", "exchange": "NASDAQ"
  },
  {
    "order_id": 123, "shares": 300, "price": 180.05, 
    "time": "14:30:02", "exchange": "NASDAQ"  
  },
  {
    "order_id": 123, "shares": 300, "price": 180.10, 
    "time": "14:30:03", "exchange": "ARCA"
  }
]
```

**Key Insight:** The order view shows you the summary (average price $180.05), while the execution view reveals the order was filled in 3 pieces at different prices and venues.

## Order Status Meanings

- **Filled**: Order completely executed
- **PartiallyFilled**: Order partially executed, remainder cancelled
- **Cancelled**: Order cancelled before execution
- **Expired**: Order expired without execution

## Technical Notes

- Includes 5-second timeout handling due to IBKR API behavior
- May timeout and return empty list when no completed orders exist
- Uses defensive programming for field access with optimized data extraction
- Only shows orders that have been submitted to the exchange
- Paper trading accounts may show simulated fills
- Historical data availability depends on your account type
- Real money accounts typically have more detailed execution data

## Workflow Integration

### Use Both Tools Together:
```
1. "Show me my completed orders today" (get_completed_orders)
2. "Get execution details for order #12345" (get_executions) 
3. "Analyze execution quality vs market conditions"
```

### Analysis Workflow:
```
1. Review order-level performance with get_completed_orders
2. Drill down to execution details with get_executions for specific orders
3. Compare execution prices to market data for quality analysis
```

## Related Tools

- `get_open_orders` - View pending orders
- `get_executions` - Detailed execution information
- `get_portfolio` - Current positions and P&L
- `get_account_summary` - Overall account performance

## Troubleshooting

**No orders returned**: If you see an empty list, you may not have completed any trades recently, or you may need to specify the correct account ID.

**Limited data**: Paper trading accounts may have simplified transaction data compared to live accounts.
