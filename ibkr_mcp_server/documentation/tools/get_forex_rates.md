# get_forex_rates

## Overview
Get real-time exchange rates for major currency pairs from Interactive Brokers. 
Supports 21+ currency pairs across 29 currencies including majors (EURUSD, GBPUSD), crosses (EURGBP, EURJPY), 
and exotic currencies through conversion tools. Returns bid, ask, and last prices with precise timestamps.

The system automatically caches rates for 5 seconds to optimize performance while 
ensuring fresh data. In paper trading environments where IBKR may return NaN values, 
the system seamlessly falls back to realistic mock rates for testing purposes.

## Parameters

**currency_pairs**: Comma-separated list of currency pairs. Examples:
• Single pair: "EURUSD"
• Multiple pairs: "EURUSD,GBPUSD,USDJPY"  
• All majors: "EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,USDCAD,NZDUSD"

Supported pairs include:
- **Major Pairs**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- **Cross Pairs**: EURGBP, EURJPY, GBPJPY, CHFJPY, EURCHF, AUDJPY, CADJPY, NZDJPY
- **Exotic Pairs**: EURNZD, GBPAUD, GBPNZD, AUDCAD, AUDNZD

Format must be exactly 6 characters (3-letter base + 3-letter quote currency).

## Examples

### Get single currency pair
```python
get_forex_rates('EURUSD')
```
Returns EUR/USD rate with bid: 1.0856, ask: 1.0858, last: 1.0857

### Monitor multiple major pairs  
```python
get_forex_rates('EURUSD,GBPUSD,USDJPY')
```
Returns rates for all three pairs in a single request

### Track cross-currency opportunities
```python
get_forex_rates('EURGBP,EURJPY,GBPJPY') 
```
Useful for identifying arbitrage opportunities between related pairs

## Workflow

**Basic Forex Rate Monitoring Workflow:**

1. **Start with major pairs**: Begin with EURUSD, GBPUSD for liquid markets
2. **Check rates frequently**: Forex markets move quickly, check every few minutes
3. **Compare bid/ask spreads**: Tighter spreads indicate better liquidity
4. **Use for conversion planning**: Check rates before using convert_currency tool
5. **Monitor related pairs**: If trading EUR, watch both EURUSD and EURGBP

**Integration with other tools:**
• Use rates to inform convert_currency operations
• Monitor rates before placing forex orders (when trading enabled)
• Track multiple pairs to understand market correlations

## Troubleshooting

### "Last price shows NaN"
• Normal in paper trading - IBKR doesn't provide all data for test accounts
• System automatically uses realistic mock rates for conversions
• Bid/ask prices usually still available and accurate

### "Invalid forex pair error"
• Check spelling - must be exactly 6 characters (EURUSD not EUR/USD)
• Verify pair is supported - use get_tool_documentation('forex') for full list
• Some exotic pairs may not be available in paper trading

### "Rate seems stale"
• Rates cached for 5 seconds for performance
• If markets are closed, rates reflect last trading session
• Forex markets trade 24/5, closed weekends

### "Connection timeout"
• Check IBKR Gateway connection with get_connection_status
• Retry after a few seconds - temporary network issues common
• During market volatility, IBKR systems may be slower

## Related Tools
• convert_currency - Use live rates for currency conversion
• get_connection_status - Check IBKR connection if rates fail
• get_market_data - Get stock prices alongside forex rates
