# place_bracket_order

## Overview
Place advanced bracket orders that combine entry, stop loss, and profit target in a single order structure. 
Bracket orders provide complete trade management by automatically setting protective stops and profit targets when the main order fills.

Perfect for systematic trading with predefined risk/reward ratios. Eliminates need to manually place stop and target orders after entry, reducing execution risk and ensuring consistent trade management.

## Parameters

**symbol**: Stock symbol or currency pair to trade
• US stocks: "AAPL", "TSLA", "GOOGL"
• International: "ASML" (auto-detects AEB/EUR), "7203" (Toyota on TSE)
• Forex pairs: "EURUSD", "GBPJPY" (25,000 minimum size)

**action**: Order action for main entry order
• "BUY" - Purchase securities with protective stop below and target above
• "SELL" - Sell securities with protective stop above and target below

**quantity**: Number of shares or units for the entire bracket
• Stocks: Whole number of shares (e.g., 100, 500)
• Forex: Minimum 25,000 units (e.g., 25000, 50000)
• All three orders (entry, stop, target) use same quantity
• Maximum per order: configured via MAX_ORDER_SIZE setting

**entry_price**: Limit price for initial entry order
• Main order price - must be reasonable vs current market
• Buy brackets: typically set below current market price
• Sell brackets: typically set above current market price
• Use local currency (USD for US stocks, EUR for ASML, etc.)

**stop_price**: Stop loss price for risk management
• Protective stop triggered if position moves against you
• Buy brackets: stop_price must be BELOW entry_price
• Sell brackets: stop_price must be ABOVE entry_price
• Distance from entry determines maximum loss per share

**target_price**: Profit target price for position exit
• Limit order to capture profits at predetermined level
• Buy brackets: target_price must be ABOVE entry_price
• Sell brackets: target_price must be BELOW entry_price
• Distance from entry determines profit goal per share

**time_in_force**: Duration for entire bracket (optional, defaults to "DAY")
• "DAY" - All orders expire at end of trading session
• "GTC" - Good Till Cancelled, bracket remains active until filled/cancelled
• Note: All three orders (entry, stop, target) use same time-in-force

## Examples

### Basic buy bracket with 2:1 risk/reward
```python
place_bracket_order("AAPL", "BUY", 100, 175.00, 170.00, 185.00)
```
Entry: Buy 100 AAPL at $175, Stop: $170 (-$5), Target: $185 (+$10)

### Sell bracket for profit taking
```python
place_bracket_order("TSLA", "SELL", 50, 250.00, 260.00, 235.00)
```
Entry: Sell 50 TSLA at $250, Stop: $260 (-$10), Target: $235 (+$15)

### International stock bracket
```python
place_bracket_order("ASML", "BUY", 25, 640.00, 620.00, 680.00)
```
Entry: Buy 25 ASML at €640, Stop: €620 (-€20), Target: €680 (+€40)

### GTC bracket order
```python
place_bracket_order("GOOGL", "BUY", 10, 2750.00, 2650.00, 2900.00, "GTC")
```
Bracket remains active until filled or manually cancelled

### Forex bracket trade
```python
place_bracket_order("EURUSD", "BUY", 50000, 1.0850, 1.0800, 1.0950)
```
Entry: Buy €50K at 1.0850, Stop: 1.0800 (-50 pips), Target: 1.0950 (+100 pips)

### Tight risk management bracket
```python
place_bracket_order("MSFT", "BUY", 100, 420.00, 415.00, 430.00)
```
Smaller risk/reward: Entry $420, Stop $415 (-$5), Target $430 (+$10)

## Workflow

**Complete Trade Planning:**
1. **Market analysis**: Identify entry level using technical/fundamental analysis
2. **Risk calculation**: Determine maximum acceptable loss per share
3. **Profit target setting**: Set realistic profit goal (often 2:1 or 3:1 risk/reward)
4. **Bracket placement**: Execute entire trade plan in single order
5. **Hands-off management**: Let bracket handle position automatically

**Systematic Trading Strategy:**
1. **Setup standardization**: Use consistent risk/reward ratios (e.g., always 2:1)
2. **Position sizing**: Calculate shares based on fixed dollar risk amount
3. **Bracket execution**: Place bracket with predetermined parameters
4. **Performance tracking**: Monitor bracket order execution and results
5. **Strategy refinement**: Adjust risk/reward ratios based on results

**Risk Management Automation:**
1. **Entry confirmation**: Main order fills and establishes position
2. **Automatic protection**: Stop loss immediately active after fill
3. **Profit capture**: Target order ready to execute at profit level
4. **Position monitoring**: Use get_order_status to track all three orders
5. **Completion handling**: Either stop or target will close position

## Bracket Order Mechanics

### Order Sequence
1. **Entry Order**: Limit order at entry_price (main order)
2. **Stop Loss**: Activated only AFTER entry order fills
3. **Profit Target**: Activated only AFTER entry order fills
4. **OCO Relationship**: Stop and target are One-Cancels-Other

### Execution Flow
• Entry order works first - stop and target remain inactive
• When entry fills, stop and target orders automatically activate
• If stop triggers, target order is cancelled
• If target fills, stop order is cancelled
• Position is automatically closed by either stop or target

### Risk/Reward Calculation
```
Risk per share = |entry_price - stop_price|
Reward per share = |target_price - entry_price|
Risk/Reward Ratio = Reward / Risk

Example: Entry $100, Stop $95, Target $110
Risk = $5, Reward = $10, Ratio = 2:1
```

## Safety Features

### Automatic Protection
• **Kill Switch**: All bracket order placement disabled if emergency mode active
• **Daily Limits**: Bracket orders count as multiple orders toward daily limits
• **Size Limits**: Total quantity must be within MAX_ORDER_SIZE
• **Rate Limiting**: Bracket placement subject to order frequency limits
• **Account Verification**: Paper account verification (when enabled)

### Parameter Validation
• **Price Relationship**: Ensures stop/target prices are logical vs entry price
• **Quantity Validation**: Positive integers only, within configured limits
• **Symbol Verification**: Confirms symbol exists and supports bracket orders
• **Account Balance**: Sufficient buying power for entry order
• **Risk Limits**: Validates risk amount is reasonable vs account size

### Risk Management Integration
• **Automatic Stop Loss**: Built-in position protection from trade inception
• **Position Limits**: Bracket size must fit within overall position limits
• **Audit Logging**: Complete bracket order history logged
• **Emergency Controls**: Kill switch can halt bracket order placement

## Troubleshooting

### "Invalid price relationship" 
• For BUY brackets: entry_price > stop_price and target_price > entry_price
• For SELL brackets: entry_price < stop_price and target_price < entry_price
• Check price logic - stop should limit loss, target should capture profit
• Verify you haven't accidentally swapped stop and target prices

### "Bracket orders not supported for this symbol"
• Some international symbols may not support bracket orders
• Forex pairs may have different bracket order rules
• Try individual orders (place_limit_order + place_stop_loss) instead
• Check symbol capabilities with IBKR directly

### "Entry order price too far from market"
• Entry price may be too far from current market price
• Check current price with get_market_data
• Adjust entry price closer to current market levels
• Some exchanges limit how far orders can be from market

### "Stop price too close to entry price"
• Exchange may require minimum distance between entry and stop
• Increase stop price distance from entry price
• Check symbol's minimum tick size requirements
• Consider using percentage-based stop distances

### "Insufficient buying power for bracket"
• Buying power reserved for full entry order amount
• Check available cash with get_account_summary
• Reduce bracket quantity to fit available funds
• Cancel other pending orders to free up buying power

### "Only entry order filled, stop/target not working"
• This is normal behavior - entry fills first
• Stop and target activate automatically after entry fills
• Use get_order_status to verify stop/target order IDs
• Check that stop/target orders show "Working" status

## Related Tools
• get_market_data - Check current prices for bracket price planning
• get_account_summary - Verify buying power before placing brackets
• get_order_status - Monitor all three bracket order components
• get_open_orders - See bracket orders before entry fills
• modify_order - Adjust bracket component prices if needed
• cancel_order - Cancel entire bracket or individual components
• place_limit_order - Alternative for entry without automatic stop/target
• place_stop_loss - Manual stop placement if bracket not suitable
