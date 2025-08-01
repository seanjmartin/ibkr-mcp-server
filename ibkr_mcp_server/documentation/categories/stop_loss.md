# Stop Loss Management

## Overview
Comprehensive risk management system for protecting your investment positions through 
automated stop loss orders. Includes basic stops, stop-limits, trailing stops, 
and complete order lifecycle management for sophisticated risk control.

**Core Philosophy:** Preserve capital first, maximize profits second. Stop losses are 
essential tools for limiting downside risk while allowing upside participation.

**Safety Integration:** All stop loss operations are protected by comprehensive safety 
validation, trading permissions, and order size limits.

## Tools
• place_stop_loss - Set automatic sell orders to limit losses
• get_stop_losses - View active stop loss orders and status
• modify_stop_loss - Adjust existing stop orders dynamically
• cancel_stop_loss - Remove stop orders when closing positions

## Order Types

**Basic Stop (STP)**
• Becomes market order when stop price hit
• Guarantees execution but not price
• Best for liquid stocks with tight spreads

**Stop Limit (STP LMT)**
• Becomes limit order when stop price hit
• Controls execution price but not guarantee
• Protects against gap downs but may not execute

**Trailing Stop (TRAIL)**
• Dynamically adjusts with favorable price moves
• Trails by fixed dollar amount or percentage
• Locks in profits while maintaining upside potential

## Workflow

**Complete Risk Management Process:**

**Phase 1: Position Entry Planning**
1. Determine maximum acceptable loss (typically 2% of account)
2. Calculate position size based on stop distance
3. Plan stop price before entering position
4. Consider volatility and typical price swings

**Phase 2: Stop Loss Implementation**
1. Place stop immediately after position entry
2. Use place_stop_loss with appropriate parameters
3. Record order ID for future reference
4. Verify stop appears in get_stop_losses

**Phase 3: Dynamic Management**
1. Monitor positions with get_stop_losses regularly
2. Tighten stops as positions become profitable
3. Use modify_stop_loss to adjust trigger levels
4. Consider trailing stops for trending positions

**Phase 4: Exit Management**
1. Cancel stops before manual position closure
2. Review stop performance for strategy improvement
3. Analyze which stop types work best for your style
4. Refine stop placement rules based on results

## Best Practices

**Position Sizing Rules:**
• Never risk more than 2% of account per position
• Calculate position size: Account × 0.02 ÷ Stop Distance
• Adjust position size if stop would be too wide
• Consider volatility when setting stop distances

**Stop Placement Guidelines:**
• Set stops below support levels, not at round numbers
• Allow for normal price fluctuations and noise
• Use technical analysis to identify logical stop levels
• Consider average true range (ATR) for stop distances

**Order Type Selection:**
• Use basic stops for liquid, trending stocks
• Use stop-limits during volatile market conditions
• Use trailing stops for strong trending positions
• Avoid stops during earnings or major news events

**Monitoring Schedule:**
• Check stops daily during active trading periods
• Review stop performance weekly
• Adjust stops after significant price moves
• Cancel stops before major news events if concerned

## Risk Considerations

**Stop Loss Limitations:**
• Gaps can cause execution below stop price
• Market volatility may trigger premature stops
• Trailing stops can be complex during sideways markets
• Stop hunting by market makers possible

**Market Conditions Impact:**
• Volatile markets increase stop trigger risk
• Trending markets favor trailing stops
• Range-bound markets may stop you out frequently
• News events can gap through stops

**Psychological Factors:**
• Emotional attachment may prevent proper stop setting
• Fear of being stopped out can lead to wide stops
• Overconfidence may lead to no stops at all
• FOMO can cause premature stop adjustments

## Integration with Portfolio Management

**Portfolio-Wide Risk Control:**
• Use with get_portfolio to see unprotected positions
• Calculate total portfolio risk exposure
• Ensure diversification of stop strategies
• Monitor correlation of stop distances

**Multi-Currency Considerations:**
• International positions need currency-appropriate stops
• Use convert_currency to standardize risk calculations
• Consider FX volatility in stop placement
• Account for different market characteristics
