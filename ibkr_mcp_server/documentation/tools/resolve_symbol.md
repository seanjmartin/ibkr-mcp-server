# resolve_symbol

## Overview
Universal symbol resolution for all global exchanges with advanced fuzzy search capabilities.
Intelligently resolves stocks by symbol, company name, or alternative identifiers (CUSIP/ISIN)
across US and international markets. Enhanced with confidence scoring for ambiguous matches.

**Key Enhancement**: Now supports company name resolution ("Apple" → "AAPL", "Microsoft" → "MSFT")
and systematic ambiguity handling with confidence scoring. Provides unified global coverage
with advanced fuzzy search capabilities for all exchanges.

Finds exchange routing and currency for any symbol including AAPL (SMART/USD), ASML (AEB/EUR),
Toyota (TSE/JPY), and provides intelligent suggestions for partial or company name inputs.

## Parameters

**symbol**: Symbol, company name, or identifier to resolve (required)
- Exact symbols: "AAPL", "ASML", "7203" 
- Company names: "Apple", "Microsoft", "Tesla"
- Alternative IDs: CUSIP, ISIN, FIGI codes
- Partial symbols: "APP" (finds AAPL candidates)
- Case-insensitive and typo-tolerant

**exchange**: Target exchange preference (optional, default: SMART)
- US: "SMART" for intelligent routing
- Europe: "AEB", "XETRA", "LSE", "SBF", "SWX", "KFX"  
- Asia: "TSE", "SEHK", "KSE", "ASX"
- Used for disambiguation when multiple matches exist

**currency**: Target currency preference (optional, default: USD)
- Primary: "USD", "EUR", "GBP", "JPY", "CHF"
- Others: "AUD", "CAD", "HKD", "KRW", "DKK"
- Influences confidence scoring for ambiguous symbols

**max_results**: Maximum matches to return (optional, default: 5, max: 16)
- 1: Single best match only (highest confidence)
- 5: Balanced results for analysis  
- 16: Complete fuzzy search results (maximum allowed)

**fuzzy_search**: Enable company name matching (optional, default: true)
- true: "Apple" → "AAPL", handles typos and company names
- false: Exact symbol matching only (faster, more precise)

**include_alternatives**: Include CUSIP/ISIN data (optional, default: false)
- true: Returns alternative identifiers in response
- false: Basic symbol resolution only (smaller response)

**prefer_native_exchange**: Prefer native exchange over US ADRs (optional, default: false)
- true: Prioritizes home country exchanges (SAP on XETRA vs NYSE, ASML on AEB vs NASDAQ)
- false: Defaults to US ADRs via SMART routing (convenient for USD trading)

## Examples

### Universal symbol resolution
```python
resolve_symbol("AAPL")
```
Returns: SMART/USD routing, full Apple Inc. details, confidence 1.0

### Company name to symbol
```python
resolve_symbol("Apple")  
```
Returns: AAPL match with SMART/USD, confidence 0.95, company name mapping

### International stock with fuzzy search  
```python
resolve_symbol("ASML")
```
Returns: AEB/EUR routing, ASML Holding NV details, confidence 1.0

### Ambiguous symbol resolution
```python
resolve_symbol("APP", max_results=3)
```
Returns: Multiple matches ranked by confidence (AAPL, APP, etc.)

### Alternative identifier lookup
```python
resolve_symbol("037833100", include_alternatives=true)
```
Returns: AAPL via CUSIP lookup with full alternative ID data

### Company name with exchange preference
```python  
resolve_symbol("Microsoft", exchange="SMART")
```
Returns: MSFT with SMART/USD routing, confidence 0.98

### Partial symbol matching
```python
resolve_symbol("MICR", max_results=5, fuzzy_search=true)
```
Returns: MSFT and other Microsoft-related symbols ranked by confidence

### International company name
```python
resolve_symbol("Toyota", max_results=2)
```
Returns: 7203 (TSE/JPY) and potentially TM (NYSE/USD ADR) with confidence scores

### Native vs US ADR preference
```python
resolve_symbol("ASML", prefer_native_exchange=False)  # Default
```
Returns: ASML on SMART (USD) - US ADR version

```python
resolve_symbol("ASML", prefer_native_exchange=True)
```
Returns: ASML on AEB (EUR) - Amsterdam native listing

### Cache management and performance monitoring
```python
resolve_symbol("CACHE_STATS")
```
Returns: Comprehensive cache performance metrics, API call statistics, and fuzzy search accuracy

```python
resolve_symbol("CLEAR_CACHE")
```
Returns: Cache cleared confirmation and reset performance counters

## Response Format

Enhanced response with confidence scoring and multiple match support:

```json
{
  "matches": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "conid": 265598,
      "exchange": "SMART",
      "primary_exchange": "NASDAQ", 
      "currency": "USD",
      "country": "United States",
      "confidence": 1.0,
      "resolution_method": "exact_symbol"
    }
  ],
  "query_info": {
    "original_query": "apple",
    "fuzzy_search_used": true,
    "total_matches": 1
  },
  "cache_info": {
    "cache_hit": false,
    "cache_key": "aapl_smart_usd"
  }
}
```

Additional fields when `include_alternatives=true`:
```json
{
  "symbol": "AAPL",
  "isin": "US0378331005",
  "cusip": "037833100",
  "trading_hours": "09:30-16:00 EST"
}
```

## Confidence Scoring

Matches are ranked by confidence score (0.0 to 1.0):

**1.0 - Perfect Match**
- Exact symbol match with preferred exchange/currency
- "AAPL" → AAPL on SMART/USD

**0.8-0.9 - High Confidence**  
- Company name resolution to primary symbol
- "Apple" → AAPL, "Microsoft" → MSFT

**0.6-0.7 - Good Match**
- Partial symbol match or alternative exchange
- "APP" → AAPL, ASML on NASDAQ vs AEB

**0.4-0.5 - Moderate Match**
- Fuzzy company name match or distant similarity
- "Appl" → AAPL, partial company name matches

**0.1-0.3 - Low Confidence**
- Weak similarity, consider with caution
- Very partial matches or distant alternatives

## Cache Management Commands

Special administrative commands available through the resolve_symbol tool:

### CACHE_STATS - Performance Monitoring
```python
resolve_symbol("CACHE_STATS")
```

**Purpose**: View comprehensive cache and performance metrics

**Returns:**
- Cache hit/miss statistics and memory usage
- API call count tracking and hourly patterns  
- Fuzzy search accuracy and confidence metrics
- Performance targets vs actual (cache hit rate, response times)
- Memory management and cleanup statistics

**Use Cases:**
- Monitor system performance over time
- Verify cache effectiveness for frequently used symbols
- Track API usage patterns and optimization opportunities
- Analyze fuzzy search accuracy and improvement areas

### CLEAR_CACHE - Cache Reset
```python
resolve_symbol("CLEAR_CACHE")
```

**Purpose**: Clear symbol resolution cache and reset performance counters

**Returns:**
- Confirmation of cache clearance
- Reset performance statistics summary
- Memory freed and cleanup completion status

**Use Cases:**
- Fresh start for performance testing
- Clear stale cache entries after market data updates
- Reset metrics for new measurement periods
- Troubleshoot cache-related issues

**Note**: Cache clearing affects all symbol resolution performance until cache rebuilds through normal usage.

## Workflow

**Enhanced Symbol Research:**

1. **Smart lookup**: Use fuzzy search for company names and partial symbols
2. **Ambiguity resolution**: Review confidence scores for multiple matches
3. **Exchange optimization**: Select best exchange based on confidence and preference
4. **Alternative ID tracking**: Use CUSIP/ISIN for institutional integration
5. **Market data integration**: Use resolved symbols with get_market_data

**Global Trading Preparation:**
1. **Universal resolution**: Single tool for all markets (US and international)
2. **Fuzzy matching**: Handle typos and company name variations  
3. **Currency planning**: Understand currency denomination via confidence scoring
4. **Exchange routing**: Optimal exchange selection via confidence ranking
5. **Portfolio integration**: Consistent symbol format for all holdings

**Native Exchange vs ADR Strategy:**
1. **ADR Benefits (default)**: Trade international stocks in USD during US hours
2. **Native Exchange Benefits**: Direct access to home market liquidity and pricing
3. **Currency Considerations**: Avoid USD conversion when holding EUR/JPY/GBP
4. **Timing Flexibility**: Access markets during local trading hours
5. **Cost Analysis**: Compare fees between native and ADR trading

**Intelligent Research Workflow:**
1. **Flexible input**: Company names, partial symbols, or exact identifiers
2. **Multiple matches**: Review alternatives for optimal selection
3. **Confidence validation**: Use scoring to verify match quality
4. **Alternative tracking**: Access CUSIP/ISIN for compliance/institutional use
5. **Global coverage**: Single tool handles US, European, Asian, and other markets

## Troubleshooting

### "No matches found"
• Try fuzzy_search=true for company name matching
• Check spelling of company names or symbols
• Try broader search terms (partial company names)
• Some very new or delisted stocks may not be available
• Verify symbol format for international stocks (include leading zeros)

### "Too many matches, unclear which is correct"
• Increase max_results to see full range of options
• Review confidence scores - choose matches >0.8 for high confidence
• Use exchange parameter to filter by preferred market
• Check currency to distinguish between ADRs and native listings
• Compare primary_exchange field to identify main listing

### "Confidence scores seem low"
• Fuzzy search may be finding distant matches
• Try exact symbol if you know it (set fuzzy_search=false)
• Check for typos in company names
• Some partial matches naturally have lower confidence
• Confidence <0.5 suggests uncertain match quality

### "Alternative IDs not appearing"
• Set include_alternatives=true to enable CUSIP/ISIN data
• Not all stocks have complete alternative identifier coverage
• Focus on larger, institutional-grade stocks for best coverage
• Alternative IDs are most complete for US and major European stocks

### "Company name not resolving"
• Try variations: "Apple Inc", "Apple", "Apple Computer"
• Some companies may be indexed by different legal names
• Try partial company names: "Apple" instead of "Apple Inc."
• Fuzzy search works best with 4+ character company name fragments
• International companies may need English names: "Toyota" not "トヨタ"

### "Multiple exchange listings confusing"
• Same company may trade on multiple exchanges (ASML on AEB and NASDAQ)
• Compare currency and exchange to choose appropriate listing
• Primary listing usually has highest confidence score
• Consider trading hours, liquidity, and currency preferences
• Use exchange parameter to force specific market

## Related Tools
• get_market_data - Get live prices using resolved symbols
• convert_currency - Convert prices between resolved currencies  
• get_forex_rates - Monitor currency rates for international positions
• get_portfolio - View holdings with consistent symbol formatting
• place_market_order - Trade using resolved symbols and exchanges
• place_limit_order - Place orders with proper exchange routing



## Supported Global Coverage

**US Markets:** All NASDAQ, NYSE, AMEX stocks via SMART routing
**European Markets:** AEB, XETRA, LSE, SBF, SWX, KFX exchanges  
**Asian Markets:** TSE, SEHK, KSE, ASX exchanges
**Fuzzy Search:** 2000+ major company names mapped to symbols
**Alternative IDs:** CUSIP/ISIN support for institutional integration
**Real-time Integration:** Live data via IBKR API with intelligent caching
