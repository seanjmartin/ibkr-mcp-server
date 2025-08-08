# place_limit_order

## Overview
Place limit orders to buy or sell securities at a specific price or better. Limit orders provide price control over execution speed - your order will only be filled if the market price reaches your specified limit price or better.

Perfect for targeting specific entry/exit prices, avoiding market volatility, and maintaining precise control over transaction costs. Works across all supported markets with appropriate local currency pricing.

## Parameters

**symbol**: Stock symbol or currency pair to trade
• US stocks: "AAPL", "TSLA", "GOOGL"  
• International: "ASML" (auto-detects AEB/EUR), "7203" (Toyota on TSE)
• Forex pairs: "EURUSD", "GBPJPY" (25,000 minimum size)

**action**: Order action type
• "BUY" - Purchase securities at limit price or lower
• "SELL" - Sell securities at limit price or higher

**quantity**: Number of shares or units to trade
• Stocks: Whole number of shares (e.g., 100, 500)
• Forex: Minimum 25,000 units (e.g., 25000, 50000)
• Maximum per order: configured via MAX_ORDER_SIZE setting

**price**: Limit price for order execution
• Buy orders: Will execute at limit price or LOWER (better price)
• Sell orders: Will execute at limit price or HIGHER (better price)
• Use local currency: USD for US stocks, EUR for ASML, JPY for Toyota

**time_in_force**: Order duration (optional, defaults to "DAY")
• "DAY" - Order expires at end of trading day if not filled
• "GTC" - Good Till Cancelled, remains active until filled or cancelled
• "IOC" - Immediate Or Cancel, fill immediately or cancel unfilled portion
• "FOK" - Fill Or Kill, fill complete order immediately or cancel entire order

**currency**: Trading currency (optional, auto-detected)
• US stocks: "USD" (default)
• International: Auto-detected ("EUR" for ASML, "JPY" for 7203)
• Manual override: Specify if needed for multi-listed stocks

**exchange**: Trading exchange (optional, auto-detected)
• US stocks: "SMART" (intelligent routing, default)
• International: Auto-detected ("AEB" for ASML, "TSE" for 7203)
• Manual override: Specify for stocks trading on multiple exchanges

## Examples

### Target entry price
```python
place_limit_order("AAPL", "BUY", 100, 175.50)
```
Buys 100 shares of Apple only if price drops to $175.50 or lower

### Profit-taking exit
```python
place_limit_order("TSLA", "SELL", 50, 250.00)
```
Sells 50 shares of Tesla only if price rises to $250.00 or higher

### International stock with limit
```python
place_limit_order("ASML", "BUY", 25, 640.00)
```
Buys 25 shares of ASML only if price drops to €640.00 or lower

### Good-till-cancelled order
```python
place_limit_order("GOOGL", "BUY", 10, 2750.00, "GTC")
```
Order remains active until filled or manually cancelled

### Forex limit order  
```python
place_limit_order("EURUSD", "BUY", 50000, 1.0850)
```
Buys €50,000 only if EUR/USD rate rises to 1.0850 or higher

### Immediate-or-cancel order
```python
place_limit_order("MSFT", "SELL", 200, 420.00, "IOC")
```
Sells up to 200 shares immediately at $420+ or cancels unfilled portion

## Workflow

**Strategic Entry Planning:**
1. **Technical analysis**: Identify target entry price using charts/indicators
2. **Current price check**: Use get_market_data to see distance from target
3. **Limit order placement**: Set buy limit below current market price
4. **Order monitoring**: Use get_order_status to track fill progress
5. **Adjustment strategy**: Modify price if market moves away from target

**Profit-Taking Strategy:**
1. **Position review**: Check current holdings with get_portfolio
2. **Target price setting**: Determine profitable exit price level
3. **Limit order placement**: Set sell limit above current market price
4. **Market monitoring**: Watch price action toward your target
5. **Risk management**: Consider stop losses on remaining position

**Range Trading Strategy:**
1. **Support/resistance identification**: Find key price levels
2. **Buy at support**: Place limit buy orders at support levels
3. **Sell at resistance**: Place limit sell orders at resistance levels
4. **GTC orders**: Use Good Till Cancelled for longer-term targets
5. **Position management**: Scale in/out with multiple limit orders

## Safety Features

### Automatic Protection
• **Kill Switch**: All order placement disabled if emergency mode active
• **Daily Limits**: Maximum orders per day enforced (default: 50)
• **Size Limits**: Maximum shares/value per order (configurable)
• **Rate Limiting**: Maximum order frequency protection (5 orders/minute)
• **Account Verification**: Paper account verification (when enabled)

### Order Validation
• **Price Validation**: Ensures limit price is reasonable vs current market
• **Quantity Validation**: Positive integers only, within size limits
• **Symbol Verification**: Confirms symbol exists and is tradeable
• **Account Balance**: Sufficient buying power check for buy limit orders
• **Position Check**: Adequate shares available for sell limit orders

### Risk Management Integration
• **Automatic Audit**: All orders logged for compliance tracking
• **Safety Wrapper**: All trading operations use safety framework
• **Configuration Control**: Trading must be enabled via ENABLE_TRADING=true
• **Emergency Halt**: Kill switch can instantly stop all trading

## Troubleshooting

### "Limit price too far from market"
• Check current market price with get_market_data
• Ensure limit price is reasonable (within 10-20% of market typically)
• IBKR may reject prices deemed too far from current market
• Consider using market order if you need immediate execution

### "Order not filling at limit price"
• Market hasn't reached your limit price yet - be patient
• Check order status with get_order_status for partial fills
• Consider adjusting limit price closer to market if urgent
• Review market depth and volume at your price level

### "Day order expired unfilled"
• Market didn't reach your limit price during trading session
• Consider using GTC (Good Till Cancelled) for longer-term targets
• Re-evaluate if your limit price target is realistic
• Place new order with adjusted price if needed

### "Insufficient buying power for limit buy"
• Buying power reserved when limit buy order is placed
• Check available cash with get_account_summary
• Cancel unnecessary pending orders to free up buying power
• Reduce order quantity to fit available funds

### "IOC order cancelled - not filled"
• Immediate-Or-Cancel orders require immediate liquidity at limit price
• No shares available at your limit price in that moment
• Try regular DAY or GTC order instead for better fill probability
• Consider adjusting limit price closer to current bid/ask

### "Symbol not tradeable during extended hours"
• Some symbols have limited extended hours trading
• Order will be queued until regular market hours
• Use get_market_data to check current market session
• Consider market hours limitations for international stocks

## Related Tools
• get_market_data - Check current prices to set appropriate limits
• get_account_summary - Verify buying power before placing buy limits
• get_portfolio - Review positions before placing sell limits  
• get_order_status - Monitor execution and fill progress
• modify_order - Adjust limit price if market conditions change
• cancel_order - Remove order if strategy changes
• place_market_order - Alternative for immediate execution without price control
• place_bracket_order - Advanced order combining limit entry with stop/target
