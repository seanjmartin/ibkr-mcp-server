# MCP Tools Reference

Complete reference for all 23 MCP tools available in the IBKR MCP Server.

## 📊 Portfolio & Account Management (5 Tools)

### `get_portfolio`
View current portfolio positions with P&L analysis.

**Parameters:**
- `account` (optional): Account ID to retrieve portfolio for

**Returns:**
- Position details (symbol, quantity, market value)
- Unrealized P&L ($ and %)
- Average cost and current price
- Multi-currency positions

**Example:**
```
"Show me my current portfolio"
→ Returns all positions with current market values
```

### `get_account_summary`
Get account balances and key financial metrics.

**Parameters:**
- `account` (optional): Account ID to retrieve summary for

**Returns:**
- Available funds in multiple currencies
- Total portfolio value
- Buying power
- Margin requirements
- Currency breakdown

**Example:**
```
"What's my account balance?"
→ Shows USD: $50,000, EUR: €5,000, etc.
```

### `get_accounts`
List all available IBKR accounts and current account status.

**Parameters:** None

**Returns:**
- Account IDs and descriptions
- Current active account
- Account types (paper/live)
- Currency settings

**Example:**
```
"Show me all my IBKR accounts"
→ Lists DU1234567 (Paper), U7654321 (Live)
```

### `switch_account`
Change active trading account.

**Parameters:**
- `account_id` (required): Target account ID

**Returns:**
- Switch confirmation
- New active account details
- Available features

**Example:**
```
"Switch to my live account U7654321"
→ Switches active account with confirmation
```

### `get_connection_status`
Check IBKR connection status and system health.

**Parameters:** None

**Returns:**
- Connection status (connected/disconnected)
- Server details and latency
- Account information
- System capabilities

**Example:**
```
"Check my IBKR connection"
→ Connected to Paper Trading (port 7497)
```

## 📈 Market Data & Analysis (2 Tools)

### `get_market_data`
Get live quotes for stocks worldwide with intelligent exchange detection.

**Parameters:**
- `symbols` (required): Comma-separated stock symbols
- `auto_detect` (optional): Enable automatic exchange/currency detection (default: True)

**Features:**
- **Auto-Detection**: AAPL→SMART/USD, ASML→AEB/EUR, 7203→TSE/JPY
- **Mixed Queries**: US, European, Asian stocks in one request
- **Real-time Data**: Last, bid, ask, volume, change

**Examples:**
```
"Get quotes for Apple, ASML, and Toyota"
→ AAPL: $180.50 (SMART/USD)
→ ASML: €650.80 (AEB/EUR)  
→ 7203: ¥2,450 (TSE/JPY)

"What's Tesla trading at?"
→ TSLA: $245.30 +$3.20 (+1.32%)
```

### `resolve_international_symbol`
Look up exchange and currency information for international stocks.

**Parameters:**
- `symbol` (required): Stock symbol to resolve
- `exchange` (optional): Filter by specific exchange
- `currency` (optional): Filter by currency

**Returns:**
- Primary exchange and currency
- Alternative listings
- Company information
- Trading hours

**Example:**
```
"Where does ASML trade?"
→ Primary: AEB (Amsterdam) in EUR
→ Alternative: NASDAQ as ASML in USD
```

## 💱 Forex & Currency (2 Tools)

### `get_forex_rates`
Get real-time forex rates for 21 currency pairs.

**Parameters:**
- `currency_pairs` (required): Comma-separated forex pairs

**Supported Pairs:**
- **Major (7)**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- **Cross (14)**: EURGBP, EURJPY, GBPJPY, CHFJPY, EURCHF, AUDJPY, CADJPY, NZDJPY, EURAUD, EURNZD, GBPAUD, GBPNZD, AUDCAD, AUDNZD

**Returns:**
- Live bid/ask/last prices
- Daily change and percentage
- Pip values and spreads
- Market session information

**Examples:**
```
"What's the EUR/USD rate?"
→ EURUSD: 1.0856 (Bid: 1.0855, Ask: 1.0857)

"Show me major forex pairs"
→ Lists all 7 major pairs with live rates
```

### `convert_currency`
Convert amounts between any of 13 supported currencies using live rates.

**Parameters:**
- `amount` (required): Amount to convert
- `from_currency` (required): Source currency code
- `to_currency` (required): Target currency code

**Supported Currencies (13):**
USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD, HKD, KRW, DKK, SEK, NOK

**Conversion Methods:**
- **Direct**: Using available forex pair (EUR→USD via EURUSD)
- **Inverse**: Calculating from inverse pair (USD→EUR via 1/EURUSD)
- **Cross-Currency**: Via USD for complex conversions (GBP→JPY)

**Examples:**
```
"Convert $1000 to Euros"
→ $1,000 USD = €921.35 EUR (Rate: 1.0856)

"How much is £500 in Japanese Yen?"
→ £500 GBP = ¥91,250 JPY (via USD cross-rate)
```

## 🛡️ Risk Management (4 Tools)

### `place_stop_loss`
Set automatic sell orders to limit losses and protect profits.

**Parameters:**
- `symbol` (required): Stock symbol
- `action` (required): BUY or SELL
- `quantity` (required): Number of shares
- `stop_price` (required): Trigger price
- `exchange` (optional): Exchange routing (default: "SMART")
- `currency` (optional): Currency for the order (default: "USD")
- `order_type` (optional): STP, STP LMT, TRAIL (default: "STP")
- `limit_price` (optional): For stop-limit orders
- `trail_amount` (optional): For trailing stops - dollar amount
- `trail_percent` (optional): For trailing stops - percentage
- `time_in_force` (optional): Order duration - "GTC" or "DAY"

**Order Types:**
- **STP**: Basic stop order (market execution when triggered)
- **STP LMT**: Stop-limit order (limit execution when triggered)
- **TRAIL**: Trailing stop (follows price by percentage)

**Examples:**
```
"Set a stop loss on my AAPL at $180"
→ Places stop order to sell at $180

"Place a trailing stop on Tesla with 5% trail"
→ Places trailing stop that follows price up
```

### `get_stop_losses`
View all existing stop loss orders and their status.

**Parameters:**
- `account` (optional): Filter by specific account ID
- `symbol` (optional): Filter by specific symbol
- `status` (optional): Filter by order status (default: "active")

**Returns:**
- Order details (symbol, quantity, stop price)
- Order status (active, triggered, cancelled)
- Current distance from market price
- Risk metrics

**Example:**
```
"Show me all my stop losses"
→ AAPL: 100 shares, Stop at $180 (-2.3% from current)
→ TSLA: 50 shares, Trailing 5% (currently $233.25)
```

### `modify_stop_loss`
Adjust existing stop loss orders.

**Parameters:**
- `order_id` (required): Order ID to modify
- `new_stop_price` (optional): Updated trigger price for the stop loss
- `new_quantity` (optional): Updated quantity for the stop loss
- `new_limit_price` (optional): Updated limit price for stop-limit orders
- `new_time_in_force` (optional): Updated order duration ("GTC" or "DAY")
- `new_trail_amount` (optional): Updated trailing amount for trailing stops
- `new_trail_percent` (optional): Updated trailing percentage

**Returns:**
- Modification confirmation
- Updated order details
- New risk metrics

**Examples:**
```
"Move my AAPL stop loss to $185"
→ Updates existing stop order to new price

"Change my Tesla trailing stop to 8%"
→ Adjusts trailing percentage for dynamic protection

"Reduce my Microsoft stop quantity to 50 shares"
→ Modifies position size protection
```

### `cancel_stop_loss`
Remove existing stop loss orders.

**Parameters:**
- `order_id` (required): Order ID to cancel

**Returns:**
- Cancellation confirmation
- Final order status
- Impact on portfolio risk

**Example:**
```
"Cancel my Tesla stop loss order"
→ Removes protection, confirms cancellation
```

## 🛒 Order Placement & Management (6 Tools) 🆕

### `place_market_order`
Execute market orders for immediate execution at current market price.

**Parameters:**
- `symbol` (required): Stock symbol (e.g., AAPL, MSFT)
- `action` (required): Order action (BUY/SELL)
- `quantity` (required): Number of shares (minimum: 1)
- `exchange` (optional): Exchange code (default: SMART)
- `currency` (optional): Currency code (default: USD)

**Returns:**
- Order confirmation with order ID
- Execution details
- Order status and timing
- Account impact

**Example:**
```
"Buy 100 shares of Apple at market price"
→ Places immediate market order for AAPL
```

### `place_limit_order`
Place limit orders with price control and time-in-force options.

**Parameters:**
- `symbol` (required): Stock symbol
- `action` (required): BUY or SELL
- `quantity` (required): Number of shares
- `price` (required): Limit price
- `time_in_force` (optional): DAY, GTC, IOC, FOK (default: DAY)
- `currency` (optional): Trading currency (auto-detected)
- `exchange` (optional): Trading exchange (auto-detected)

**Returns:**
- Order confirmation with order ID
- Order parameters and status
- Estimated execution probability
- Market price comparison

**Example:**
```
"Place a limit order to buy Tesla at $240"
→ Places limit order with price control
```

### `place_bracket_order`
Advanced bracket orders with entry, stop loss, and profit target.

**Parameters:**
- `symbol` (required): Stock symbol
- `action` (required): BUY or SELL
- `quantity` (required): Number of shares
- `entry_price` (required): Entry limit price
- `stop_price` (required): Stop loss price
- `target_price` (required): Profit target price

**Returns:**
- Parent and child order IDs
- Complete bracket structure
- Risk/reward analysis
- Order status tracking

**Example:**
```
"Place bracket order: buy ASML at €640, stop €620, target €680"
→ Creates complete risk-managed position
```

### `cancel_order`
Cancel pending orders by order ID.

**Parameters:**
- `order_id` (required): Order ID to cancel

**Returns:**
- Cancellation confirmation
- Final order status
- Timing information
- Account impact

**Example:**
```
"Cancel my pending order #12345"
→ Cancels specified order
```

### `modify_order`
Modify existing orders (quantity, price, time-in-force).

**Parameters:**
- `order_id` (required): Order ID to modify
- `quantity` (optional): New quantity
- `price` (optional): New price (for limit orders)
- `time_in_force` (optional): New time in force

**Returns:**
- Modification confirmation
- Updated order details
- Previous vs new parameters
- Status tracking

**Example:**
```
"Modify order #12345 to 200 shares at $185"
→ Updates existing order parameters
```

### `get_order_status`
Get comprehensive status information for any order by its ID.

**Parameters:**
- `order_id` (required): Unique order identifier to query
  - Integer value from original order placement response
  - Available from place_market_order, place_limit_order, place_bracket_order results
  - Also available from get_open_orders or get_completed_orders
  - Must be exact order ID belonging to your account

**Returns:**
- **Order identification**: Order ID, symbol, exchange, currency
- **Order parameters**: Action (BUY/SELL), type, quantity, prices, time in force
- **Execution details**: Status, filled quantity, remaining quantity, average fill price
- **Timing information**: Submit time, last update, fill time, expiry time
- **Commission data**: Trading fees and execution costs

**Order Status Values:**
- **Active**: Submitted, Working, PartiallyFilled
- **Completed**: Filled, Cancelled, Expired, Rejected
- **Processing**: PendingSubmit, PendingCancel, PendingModify

**Examples:**
```
"Check the status of order #12345"
→ Returns complete order status with execution details

"Get status for my Apple order"
→ First find order ID from get_open_orders, then check status
```

**Use Cases:**
- Monitor order execution progress after placement
- Check fill prices and quantities for completed orders
- Diagnose why orders aren't executing as expected
- Track partial fills and remaining quantities

## 📋 Order History & Tracking (3 Tools)

### `get_open_orders`
View all pending orders that haven't been filled yet.

**Parameters:**
- `account` (optional): Filter by account

**Returns:**
- Order details (symbol, type, quantity, price)
- Order status and time in force
- Estimated fill probability
- Time submitted

**Example:**
```
"Show me my pending orders"
→ AAPL: Buy 100 @ $175 (Limit, GTC)
→ EURUSD: Sell 25,000 @ 1.0800 (Limit, DAY)
```

### `get_completed_orders`
View recently completed trades and filled orders.

**Parameters:**
- `account` (optional): Filter by specific account ID

**Returns:**
- Complete order information including:
  - Order details: order_id, symbol, exchange, currency
  - Trade specifics: action, quantity, order_type, limit_price, aux_price
  - Status information: status, filled, remaining, avg_fill_price
  - Financial data: commission, time_in_force
  - Metadata: account, order_ref, client_id

**Features:**
- 5-second timeout handling for IBKR API reliability
- Empty list returned when no completed orders exist
- Full order lifecycle information

**Example:**
```
"Show me my recent completed orders"
→ Returns completed order data or empty list for new accounts
```

### `get_executions`
Get detailed execution information for specific trades.

**Parameters:**
- `account` (optional): Filter by specific account ID
- `symbol` (optional): Filter by specific symbol
- `days_back` (optional): Number of days to search back (default: 7)

**Returns:**
- Comprehensive execution data including:
  - Execution identifiers: execution_id, order_id, client_id, perm_id
  - Contract details: symbol, exchange, currency, security_type
  - Trade specifics: side, shares, price, average_price
  - Market data: liquidation, cumulative_quantity, last_liquidity
  - Execution metadata: order_ref, ev_rule, ev_multiplier, model_code
  - Timing: execution time (sorted most recent first)
  - Account information: account number

**Features:**
- Automatic sorting by execution time (most recent first)
- Flexible filtering by account and/or symbol
- Configurable historical range via days_back parameter

**Example:**
```
"Show me execution details for my Apple trades"
→ Detailed AAPL execution data with venue and timing information

"Get my executions from the last 30 days"
→ All executions with days_back parameter
```

## 📚 Documentation (1 Tool)

### `get_tool_documentation`
Access comprehensive help system for all tools.

**Parameters:**
- `tool_or_category` (required): Tool name or category
- `aspect` (optional): Focus area (examples, parameters, troubleshooting)

**Categories:**
- **forex**: Forex trading and currency conversion
- **stop_loss**: Risk management and order protection
- **portfolio**: Account and position management
- **international**: Global market trading
- **order_placement**: Order placement and management 🆕

**Examples:**
```
"How do I use forex trading?"
→ Complete forex workflow documentation

"Show me examples for stop loss orders"
→ Practical examples and use cases

"Help with get_market_data tool"
→ Complete tool documentation with parameters

"Help with order placement"
→ Complete order management workflow documentation 🆕
```

## 🔧 Tool Usage Patterns

### **Portfolio Review**
```
1. "Check my connection status"
2. "Show me my portfolio"
3. "What's my account balance?"
```

### **Market Analysis**
```
1. "Get quotes for AAPL, MSFT, GOOGL"
2. "What's the EUR/USD rate?"
3. "Convert my EUR balance to USD"
```

### **Order Placement & Management** 🆕
```
1. "Get quote for AAPL" → Research
2. "Buy 100 shares of AAPL at market price" → Execute
3. "Check status of order #12345" → Monitor
4. "Modify order to 150 shares at $185" → Adjust
5. "Set stop loss at $180" → Protect
```

### **Complete Trading Workflow** 🆕
```
1. "Check my buying power"
2. "Get quotes for AAPL, TSLA, MSFT"
3. "Buy 100 AAPL at market price"
4. "Place bracket order: buy Tesla at $240, stop $220, target $260"
5. "Set trailing stop on Microsoft with 8% trail"
6. "Show all my orders and positions"
```

### **Risk Management Setup**
```
1. "Set stop losses on all my positions at 10% below cost"
2. "Show me my current stop orders"
3. "Place a trailing stop on Tesla with 8% trail"
```

### **Global Trading**
```
1. "Get quotes for ASML, SAP, Toyota"
2. "Where does ASML trade?"
3. "Convert €10,000 to USD for US trades"
```

## 🚨 Safety & Limitations

### **Trading Controls**
- All trading must be explicitly enabled in configuration
- Order size and value limits enforced
- Daily order count restrictions
- Paper trading verification required

### **Market Data**
- Real-time data subject to exchange subscriptions
- Some international stocks may have delayed quotes
- Paper accounts have limited real-time access

### **Risk Management**
- Stop losses don't guarantee execution price
- Market gaps can result in slippage
- Orders may not execute during market closures

---

**Next Steps:**
- [Trading Guide](../guides/trading.md) - Complete trading workflows
- [Examples](../examples/basic-usage.md) - Practical use cases
- [Configuration](../reference/configuration.md) - Customize settings
