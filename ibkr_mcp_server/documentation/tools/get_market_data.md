# get_market_data

## Overview
Get live stock prices for US and international markets with intelligent auto-detection of exchanges and currencies.
Supports major global exchanges including NYSE, NASDAQ, XETRA, LSE, TSE, SEHK, and ASX.
Automatically determines the correct exchange and currency for international symbols like ASML, SAP, Toyota.

Handles mixed symbol queries seamlessly - you can request AAPL, ASML, and Toyota in a single call 
and get properly routed market data for each exchange and currency.

## Parameters

**symbols**: Comma-separated list of stock symbols. Examples:
• US stocks: "AAPL,TSLA,GOOGL"
• International: "ASML,SAP,7203" (auto-detects exchanges)
• Mixed: "AAPL,ASML,TSLA" (US and international combined)
• Explicit format: "ASML.AEB.EUR,SAP.XETRA.EUR" (force specific exchange)

**auto_detect**: Enable automatic exchange/currency detection (defaults to True)
- True: System determines best exchange for each symbol
- False: Uses explicit symbol.exchange.currency format

Supported exchanges and regions:
- **US**: NYSE, NASDAQ (symbols like AAPL, TSLA, GOOGL)
- **Europe**: XETRA (SAP), LSE (VOD), AEB (ASML), SWX (NESN)
- **Asia**: TSE (7203=Toyota), SEHK (00700=Tencent), KSE (005930=Samsung)
- **Others**: ASX (CBA), KFX (NOVO-B)

## Examples

### US stock prices
```python
get_market_data("AAPL,TSLA,GOOGL")
```
Returns live prices for Apple, Tesla, Google from US exchanges

### International stocks (auto-detect)
```python
get_market_data("ASML,SAP,7203")
```
Auto-detects: ASML→AEB/EUR, SAP→XETRA/EUR, 7203→TSE/JPY

### Mixed US and international
```python
get_market_data("AAPL,ASML,TSLA,SAP")
```
Seamlessly handles both US stocks and European stocks

### Explicit exchange specification
```python
get_market_data("ASML.AEB.EUR,VOD.LSE.GBP", auto_detect=False)
```
Forces specific exchange and currency routing

### Single international stock
```python
get_market_data("00700")
```
Gets Tencent price from Hong Kong Stock Exchange in HKD

## Workflow

**Multi-Market Portfolio Monitoring:**

1. **Create watchlist**: Combine your US and international holdings
2. **Regular price checks**: Monitor all positions in single call
3. **Currency awareness**: Note which prices are in EUR, GBP, JPY, etc.
4. **Performance comparison**: Track relative performance across markets
5. **Entry/exit timing**: Use live prices for trading decisions

**International Investment Research:**
1. **Symbol discovery**: Use resolve_symbol to find exchanges
2. **Price monitoring**: Track target stocks across global markets
3. **Market hours awareness**: Understand when each exchange is open
4. **Currency impact**: Consider FX rates alongside stock prices
5. **Volume analysis**: Compare liquidity across different exchanges

**Pre-Trade Workflow:**
1. **Check current prices**: Get live market data before placing orders
2. **Verify symbols**: Ensure correct symbol/exchange combinations
3. **Compare currencies**: Use convert_currency for multi-currency analysis
4. **Set appropriate limits**: Use current prices to set realistic order prices

## Troubleshooting

### "Could not qualify contract" for international symbol
• Symbol may not be available in paper trading account
• Check spelling and format - some symbols are numeric (7203, 005930)
• Use resolve_symbol to find correct exchange
• Some exotic stocks may require live trading account access

### "Zero prices returned" (All price fields show 0.0)
• IBKR Error 10089: Real-time data subscription required
• Paper accounts often lack real-time market data subscriptions  
• System automatically falls back to delayed data when available
• Look for "data_type": "delayed" in response metadata

### "Last price shows NaN" or empty
• Common in paper trading for international stocks
• IBKR may not provide real-time data for all international symbols
• US stocks typically have complete data even in paper trading
• Bid/ask prices may still be available when last price is missing

### "Auto-detection failed"
• Symbol not in international database - use explicit format
• Try SYMBOL.SMART.USD for US-traded ADRs
• Some symbols may trade on multiple exchanges
• Use resolve_symbol to see available options

### "Market data subscription required"
• Some international exchanges require paid data subscriptions
• Paper trading accounts have limited international data access
• Error code 10089 or 354 indicates subscription needed
• Consider switching to major international symbols (ASML, SAP)

### "Prices in wrong currency"
• International stocks return prices in local currency (EUR, GBP, JPY)
• Use convert_currency to convert to your base currency
• Check exchange field to understand which market you're seeing
• Some stocks trade on multiple exchanges in different currencies

## Related Tools
• resolve_symbol - Find exchange and currency for symbols
• convert_currency - Convert international prices to your base currency
• get_forex_rates - Monitor currency exchange rates
• get_portfolio - See your current positions needing price updates
• get_connection_status - Check IBKR connectivity if data seems stale
