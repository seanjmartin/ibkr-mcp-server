# MCP Tools Reference

Complete reference for all 17 MCP tools available in the IBKR MCP Server.

## 📊 Portfolio & Account Management (5 Tools)

### `get_portfolio`
View current portfolio positions with P&L analysis.

**Parameters:** None (optional account filter)

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

**Parameters:** None (optional account filter)

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
- `order_type` (optional): STP, STP LMT, TRAIL
- `limit_price` (optional): For stop-limit orders
- `trail_percent` (optional): For trailing stops

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
- `symbol` (optional): Filter by specific symbol
- `account` (optional): Filter by account

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
- `stop_price` (optional): New stop price
- `quantity` (optional): New quantity
- `trail_percent` (optional): New trailing percentage

**Returns:**
- Modification confirmation
- Updated order details
- New risk metrics

**Example:**
```
"Move my AAPL stop loss to $185"
→ Updates existing stop order to new price
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

## 📋 Order Management (3 Tools)

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
View recently executed trades and filled orders.

**Parameters:**
- `account` (optional): Filter by account

**Returns:**
- Execution details (symbol, quantity, fill price)
- Execution time and venue
- Commission and fees
- Trade P&L

**Example:**
```
"Show me my recent trades"
→ TSLA: Bought 50 @ $245.30 (14:32 EST)
→ GBPUSD: Sold 25,000 @ 1.2654 (11:45 EST)
```

### `get_executions`
Get detailed execution information for specific trades.

**Parameters:**
- `symbol` (optional): Filter by symbol
- `account` (optional): Filter by account

**Returns:**
- Detailed execution reports
- Venue and routing information
- Price improvement analysis
- Commission breakdown

**Example:**
```
"Show me execution details for my Apple trades"
→ Detailed breakdown of AAPL executions with venues
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

**Examples:**
```
"How do I use forex trading?"
→ Complete forex workflow documentation

"Show me examples for stop loss orders"
→ Practical examples and use cases

"Help with get_market_data tool"
→ Complete tool documentation with parameters
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
