# place_market_order

## Overview
Execute market orders for immediate buying or selling of securities at the current market price. 
Market orders prioritize speed of execution over price control - your order will be filled at the best available price when it reaches the exchange.

Perfect for entering or exiting positions quickly when timing is more important than getting a specific price. 
Works across all supported markets including US stocks, international equities, and forex.

## Parameters

**symbol**: Stock symbol or currency pair to trade
• US stocks: "AAPL", "TSLA", "GOOGL"
• International: "ASML" (auto-detects AEB/EUR), "7203" (Toyota on TSE)
• Forex pairs: "EURUSD", "GBPJPY" (25,000 minimum size)

**action**: Order action type
• "BUY" - Purchase securities
• "SELL" - Sell securities (requires existing position)

**quantity**: Number of shares or units to trade
• Stocks: Whole number of shares (e.g., 100, 500)  
• Forex: Minimum 25,000 units (e.g., 25000, 50000)
• Maximum per order: configured via MAX_ORDER_SIZE setting

**currency**: Trading currency (optional, default: "USD")
• Default: "USD" for all stocks unless specified
• Override: Specify currency for non-USD stocks ("EUR", "JPY", etc.)
• Note: System uses default USD, manual specification required for other currencies

**exchange**: Trading exchange (optional, default: "SMART")  
• Default: "SMART" (intelligent routing) for all stocks
• Override: Specify exchange for multi-listed stocks ("AEB", "TSE", etc.)
• Note: System uses default SMART routing, manual specification required for specific exchanges

## Examples

### Basic US stock purchase
```python
place_market_order("AAPL", "BUY", 100)
```
Buys 100 shares of Apple at current market price

### International stock purchase
```python
place_market_order("ASML", "BUY", 50)
```
Buys 50 shares of ASML at current EUR price on Amsterdam exchange

### Position exit
```python  
place_market_order("TSLA", "SELL", 75)
```
Sells 75 shares of Tesla from existing position

### Forex trading
```python
place_market_order("EURUSD", "BUY", 50000)
```
Buys €50,000 worth of EUR/USD at current market rate

### Large order
```python
place_market_order("GOOGL", "BUY", 500)
```
Buys 500 shares of Google - check MAX_ORDER_SIZE limits

## Workflow

**Quick Entry Strategy:**
1. **Market research**: Check current price with get_market_data
2. **Position sizing**: Determine appropriate quantity based on account balance
3. **Market order placement**: Execute trade at current market price
4. **Immediate confirmation**: Get order ID and initial status
5. **Monitor execution**: Use get_order_status to track fill progress

**Position Exit Strategy:**
1. **Portfolio review**: Check current positions with get_portfolio
2. **Exit decision**: Determine quantity to sell (partial or full position)
3. **Market exit**: Execute sell order at current market price
4. **Execution tracking**: Monitor order completion and final price
5. **P&L analysis**: Review realized gains/losses

**International Trading:**
1. **Symbol research**: Use resolve_symbol for exchange info
2. **Currency consideration**: Check forex rates with get_forex_rates
3. **Market order placement**: Execute at local market price
4. **Currency impact**: Consider FX exposure from international holdings
5. **Performance tracking**: Monitor both stock and currency performance

## Safety Features

### Automatic Protection
• **Kill Switch**: All order placement disabled if emergency mode active
• **Daily Limits**: Maximum orders per day enforced (default: 50)
• **Size Limits**: Maximum shares/value per order (configurable)
• **Rate Limiting**: Maximum order frequency protection (5 orders/minute)
• **Account Verification**: Paper account verification (when enabled)

### Order Validation
• **Symbol Verification**: Ensures symbol exists and is tradeable
• **Quantity Validation**: Positive integers only, within size limits
• **Account Balance**: Sufficient buying power check for purchases
• **Position Check**: Adequate shares available for sell orders
• **Market Hours**: Warning if market is closed (order held until open)

### Risk Management Integration
• **Automatic Audit**: All orders logged for compliance tracking
• **Safety Wrapper**: All trading operations use safety framework
• **Configuration Control**: Trading must be enabled via ENABLE_TRADING=true
• **Emergency Halt**: Kill switch can instantly stop all trading

## Troubleshooting

### "Insufficient buying power" 
• Check available cash with get_account_summary
• Reduce order quantity or add funds to account
• Consider market price impact on total order value
• Account for margin requirements on larger orders

### "Insufficient shares for sell order"
• Check current position with get_portfolio  
• Verify you own the stock you're trying to sell
• Reduce sell quantity to match or be less than current position
• Account for any existing sell orders that reduce available shares

### "Symbol not found" or "Contract qualification failed"
• Verify symbol spelling and format
• Use resolve_symbol for international stocks
• Some symbols may not be available in paper trading
• Try SMART exchange for US stocks, specific exchange for international

### "Order rejected - Market closed"
• Order will be held and executed when market opens
• Check trading hours for specific exchange
• Use get_connection_status to verify market session info
• Consider using limit orders instead during off-hours

### "Trading not enabled" or "Safety validation failed"
• Check that ENABLE_TRADING=true in configuration
• Verify kill switch is not active
• Check daily trading limits haven't been exceeded  
• Review any safety violations in audit logs

### "Rate limit exceeded"
• Wait 1 minute before placing next order (5 orders/minute max)
• Batch multiple orders if possible
• Check for any system issues causing excessive order attempts
• Review order frequency patterns in audit logs

## Related Tools
• get_market_data - Check current prices before placing orders
• get_account_summary - Verify buying power and available funds
• get_portfolio - Review current positions before selling
• get_order_status - Track execution status after order placement
• cancel_order - Cancel order if placed incorrectly
• place_limit_order - Alternative with price control instead of speed
• place_bracket_order - Advanced order with built-in stop loss and profit target
