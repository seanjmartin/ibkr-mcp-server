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

## Common Use Cases

- **Trading Review**: Analyze your recent trading activity
- **Performance Analysis**: Calculate profits and losses from executed trades
- **Tax Reporting**: Gather transaction data for tax purposes
- **Commission Tracking**: Monitor trading costs and fees
- **Order Verification**: Confirm that orders were executed as expected

## Order Status Meanings

- **Filled**: Order completely executed
- **PartiallyFilled**: Order partially executed, remainder cancelled
- **Cancelled**: Order cancelled before execution
- **Expired**: Order expired without execution

## Notes

- Only shows orders that have been submitted to the exchange
- Paper trading accounts may show simulated fills
- Historical data availability depends on your account type
- Real money accounts typically have more detailed execution data

## Related Tools

- `get_open_orders` - View pending orders
- `get_executions` - Detailed execution information
- `get_portfolio` - Current positions and P&L
- `get_account_summary` - Overall account performance

## Troubleshooting

**No orders returned**: If you see an empty list, you may not have completed any trades recently, or you may need to specify the correct account ID.

**Limited data**: Paper trading accounts may have simplified transaction data compared to live accounts.
