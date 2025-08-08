# Order Placement and Management

## Overview
Complete order management system for placing, monitoring, and managing trades across all supported markets. 
Provides full trading workflow from order placement through execution tracking and position management.

The order management system includes 6 core tools that handle every aspect of trade execution and management, 
plus 3 additional tools for monitoring existing orders and executions.

## Core Order Tools (6 Tools)

### Order Placement (3 Tools)
**place_market_order** - Immediate execution at current market price
• Best for: Quick entries/exits when timing matters more than price
• Speed: Fastest execution, typically fills immediately
• Risk: No price control - you get current market price

**place_limit_order** - Execution only at specified price or better  
• Best for: Targeting specific entry/exit prices
• Control: Exact price control, won't fill at worse prices
• Risk: May not fill if market doesn't reach your price

**place_bracket_order** - Complete trade with entry, stop, and target
• Best for: Systematic trading with predefined risk/reward
• Automation: Automatic stop loss and profit target placement
• Risk: Comprehensive trade management in single order

### Order Management (3 Tools)
**modify_order** - Change quantity, price, or time-in-force
• Faster than cancelling and re-placing orders
• Maintains queue priority at the exchange
• Can adjust multiple parameters simultaneously

**cancel_order** - Remove unfilled orders that are no longer needed
• Immediate cancellation for most unfilled orders
• Essential for changing market conditions
• Works with all order types

**get_order_status** - Detailed information about any order
• Real-time execution status and fill information
• Track partial fills and remaining quantities
• Monitor order lifecycle from placement to completion

## Order Monitoring Tools (3 Tools)

**get_open_orders** - View all currently pending orders
• See all unfilled orders across your account
• Monitor order queue and working status
• Identify orders that may need modification or cancellation

**get_completed_orders** - Review recently executed trades
• Track filled and cancelled orders
• Analyze execution quality and timing
• Review trading activity and performance

**get_executions** - Detailed execution information
• Venue-specific execution details
• Commission and fee breakdown
• Price improvement analysis

## Order Types and Capabilities

### Market Orders (place_market_order)
• **Execution**: Immediate at current market price
• **Use Cases**: Quick entries, emergency exits, high-liquidity stocks
• **Advantages**: Speed, guaranteed execution
• **Disadvantages**: No price control, possible slippage

### Limit Orders (place_limit_order)
• **Execution**: Only at limit price or better
• **Use Cases**: Target prices, avoiding volatility, price-sensitive trades
• **Advantages**: Price control, better fills possible
• **Disadvantages**: May not execute, requires patience

### Bracket Orders (place_bracket_order)
• **Execution**: Entry + automatic stop loss + profit target
• **Use Cases**: Systematic trading, risk management, unattended trading
• **Advantages**: Complete trade management, consistent risk control
• **Disadvantages**: More complex, requires three price levels

## Time-in-Force Options

**DAY Orders** - Expire at end of trading session
• Default for most orders
• Good for intraday strategies
• Automatically cancelled if not filled by market close

**GTC (Good Till Cancelled)** - Remain active until filled or cancelled
• Perfect for longer-term targets
• Stay active across multiple trading sessions
• Require manual cancellation

**IOC (Immediate or Cancel)** - Fill immediately or cancel
• For quick execution attempts
• Cancels any unfilled portion immediately
• Good for testing liquidity

**FOK (Fill or Kill)** - Fill completely or cancel entirely
• All-or-nothing execution
• Useful for large orders requiring complete fills
• Avoids partial execution issues

## Trading Workflows

### Basic Trading Workflow
1. **Market Research**: Check prices with get_market_data
2. **Order Placement**: Use appropriate order type for strategy
3. **Execution Monitoring**: Track with get_order_status
4. **Position Management**: Monitor fills and remaining orders
5. **Strategy Adjustment**: Modify or cancel as needed

### Systematic Trading Workflow
1. **Setup**: Define entry, stop, and target prices
2. **Bracket Placement**: Use place_bracket_order for complete trade
3. **Monitoring**: Track all three order components
4. **Completion**: Let bracket automatically manage the trade
5. **Analysis**: Review execution quality and results

### Active Management Workflow
1. **Multiple Orders**: Place various limit orders at different levels
2. **Market Monitoring**: Watch price action and order fills
3. **Dynamic Adjustment**: Modify orders based on market movement
4. **Risk Control**: Cancel orders that no longer fit strategy
5. **Optimization**: Continuously refine order placement

## Safety and Risk Management

### Built-in Protections
• **Kill Switch Integration**: All order tools respect emergency halt
• **Daily Limits**: Maximum orders per day (configurable)
• **Size Limits**: Maximum shares/value per order
• **Rate Limiting**: Prevents excessive order frequency
• **Account Verification**: Paper account enforcement (when enabled)

### Order Validation
• **Symbol Verification**: Ensures tradeable symbols only
• **Price Validation**: Reasonable prices vs current market
• **Balance Checks**: Sufficient buying power for purchases
• **Position Checks**: Adequate shares for sell orders
• **Market Hours**: Awareness of market sessions and limitations

### Risk Management Best Practices
• **Position Sizing**: Never risk more than 1-2% of account per trade
• **Stop Losses**: Always use protective stops (manual or bracket)
• **Diversification**: Avoid concentration in single stocks or sectors
• **Order Monitoring**: Regularly check order status and executions
• **Emergency Procedures**: Know how to quickly cancel all orders

## International Trading

### Multi-Market Support
• **US Markets**: SMART routing across all major exchanges
• **European Markets**: Direct access to XETRA, LSE, AEB, SWX
• **Asian Markets**: TSE, SEHK, KSE for major stocks
• **Currency Handling**: Automatic currency detection and conversion

### International Order Considerations
• **Market Hours**: Different trading sessions across time zones
• **Currency Risk**: Orders execute in local currency (EUR, JPY, etc.)
• **Settlement**: T+2 settlement across most international markets
• **Regulations**: Different market rules and order types by country

## Performance Optimization

### Order Efficiency
• **Smart Routing**: Use SMART exchange for best US execution
• **Queue Priority**: Modify orders instead of cancelling/replacing
• **Batch Operations**: Plan multiple orders efficiently
• **Market Timing**: Place orders during high liquidity periods

### Cost Management
• **Commission Optimization**: Consider costs in order sizing
• **Bid-Ask Spreads**: Use limit orders to avoid wide spreads
• **Market Impact**: Size orders appropriately for stock liquidity
• **International Costs**: Factor in currency conversion costs

## Common Use Cases

### Day Trading
• **Market Orders**: Quick entries and exits
• **IOC Orders**: Test liquidity without commitment
• **Active Monitoring**: Frequent order status checks
• **Rapid Adjustment**: Quick modifications based on market movement

### Swing Trading
• **Limit Orders**: Target specific entry and exit levels
• **GTC Orders**: Multi-day trade management
• **Bracket Orders**: Systematic risk/reward management
• **Position Scaling**: Multiple orders for position building

### Long-term Investing
• **Limit Orders**: Patient accumulation at target prices
• **GTC Orders**: Long-term entry strategies
• **Stop Losses**: Portfolio protection on large positions
• **Periodic Rebalancing**: Regular position adjustments

## Troubleshooting

### Common Order Issues
• **Orders Not Filling**: Check limit prices vs market
• **Insufficient Funds**: Verify buying power before ordering
• **Symbol Errors**: Confirm symbol spelling and availability
• **Market Hours**: Consider trading session limitations
• **Order Rejection**: Review order parameters and limits

### Execution Problems
• **Partial Fills**: Monitor remaining quantities
• **Price Slippage**: Use limit orders for price control
• **Commission Surprises**: Understand fee structure
• **Currency Impact**: Factor in FX movements for international trades

## Related Tools
• **Market Data**: get_market_data, resolve_international_symbol
• **Account Management**: get_account_summary, get_portfolio
• **Risk Management**: place_stop_loss, get_stop_losses, modify_stop_loss
• **Currency Tools**: get_forex_rates, convert_currency
• **Documentation**: get_tool_documentation for detailed help

The order management system provides complete trading functionality from simple market orders to sophisticated bracket orders with automatic risk management. Use the appropriate tool based on your trading style, risk tolerance, and market conditions.
