# resolve_symbol

## Overview
Universal symbol resolution for all global exchanges with advanced fuzzy search capabilities.
Intelligently resolves stocks by symbol, company name, or alternative identifiers (CUSIP/ISIN)
across US and international markets. Enhanced with confidence scoring for ambiguous matches.

Supports company name resolution ("Apple" → "AAPL", "Microsoft" → "MSFT") and systematic ambiguity handling with confidence scoring. Provides unified global coverage with advanced fuzzy search capabilities for all exchanges.

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
- **Universal**: "SMART" for intelligent routing (works worldwide)
- **US**: "NYSE", "NASDAQ", "ARCA", "BATS", "IEX"
- **Europe**: "FRANKFURT"/"XETRA", "LONDON"/"LSE", "AMSTERDAM"/"AEB", "PARIS"/"SBF", "MILAN"/"BVME", "SWISS"/"EBS", "STOCKHOLM"/"SFB"
- **Asia**: "TOKYO"/"TSEJ", "HONGKONG"/"SEHK", "SINGAPORE"/"SGX", "INDIA"/"NSE", "AUSTRALIA"/"ASX"
- **Canada**: "TORONTO"/"TSE" (not TSX)
- **Advanced**: Supports standard exchange names, MIC codes, and IBKR-specific codes
- **Fallback**: Automatically tries exchange aliases if initial exchange fails

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

### International stock with exchange mapping
```python
resolve_symbol("ASML", exchange="AMSTERDAM")
```
Returns: Automatically maps AMSTERDAM → AEB, finds ASML on AEB/EUR, confidence 1.0

### Exchange alias resolution
```python
resolve_symbol("SAP", exchange="XETRA")  
```
Returns: Maps XETRA → IBIS, finds SAP on IBIS/EUR, shows resolved_via_alias=true

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
      "symbol": "SAP",
      "name": "SAP SE",
      "conid": 14204,
      "exchange": "IBIS",
      "primary_exchange": "IBIS", 
      "currency": "EUR",
      "country": "Germany",
      "confidence": 1.0,
      "resolution_method": "exchange_alias"
    }
  ],
  "query_info": {
    "original_query": "SAP",
    "original_exchange": "XETRA",
    "actual_exchange": "IBIS",
    "resolved_via_alias": true,
    "exchanges_tried": ["XETRA", "IBIS"],
    "total_matches": 1
  },
  "cache_info": {
    "cache_hit": false,
    "cache_key": "sap_xetra_eur"
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

## Exchange Mapping & Fallback Strategy

**CRITICAL FEATURE**: resolve_symbol includes comprehensive exchange mapping that automatically handles IBKR's non-standard exchange codes and provides intelligent fallback resolution.

### Standard Exchange Names Work Automatically

You can use familiar exchange names, and the system automatically maps them to IBKR's internal codes:

```python
# All of these work automatically:
resolve_symbol("SAP", exchange="FRANKFURT")     # → FWB/FWB2
resolve_symbol("SAP", exchange="XETRA")         # → IBIS/IBIS2  
resolve_symbol("ASML", exchange="AMSTERDAM")    # → AEB
resolve_symbol("Toyota", exchange="TOKYO")      # → TSEJ
resolve_symbol("RY", exchange="TORONTO")        # → TSE (not TSX!)
resolve_symbol("Apple", exchange="NYSE")        # → NYSE/ARCA
```

### Comprehensive Exchange Mappings

**German Exchanges** (validated working):
- `FRANKFURT` → `FWB` (domestic) + `FWB2` (foreign)
- `XETRA` → `IBIS` (stocks) + `IBIS2` (ETFs)
- `TRADEGATE` → `TGATE` (TRADEGATE name fails, TGATE works)
- `GETTEX` → `GETTEX` (direct mapping)

**UK Exchanges**:
- `LONDON` → `LSE` (stocks) + `LSEETF` (ETFs)
- `LSE` → includes both stock and ETF segments

**European Exchanges** (validated working):
- `MILAN`/`BIT`/`MIL` → `BVME` (only BVME works for Italian stocks)
- `SWISS`/`SWX` → `EBS` (SWX fails, EBS works)
- `STOCKHOLM`/`OMX` → `SFB` (OMX fails, SFB works)
- `AMSTERDAM` → `AEB` (Dutch stocks)
- `PARIS` → `SBF` (French stocks)

**North American Exchanges** (validated working):
- `TORONTO`/`TSX` → `TSE` (TSX fails, TSE works for Canadian stocks)
- `NYSE` → `NYSE` + `ARCA` (routing variants)
- `NASDAQ` → `NASDAQ` + `ISLAND` (routing variants)

**Asian Exchanges** (validated working):
- `TOKYO` → `TSEJ` (TSE fails for Japanese stocks, TSEJ works)
- `HONGKONG` → `SEHK` (Hong Kong stocks)
- `SINGAPORE` → `SGX` (Singapore stocks)
- `INDIA`/`BSE` → `NSE` (BSE fails, NSE works for Indian stocks)
- `AUSTRALIA` → `ASX` (Australian stocks)

**Market Identifier Code (MIC) Support**:
- `XNYS` → `NYSE` (NYSE MIC code)
- `XNAS` → `NASDAQ` (NASDAQ MIC code)
- `XLON` → `LSE`/`LSEETF` (London MIC)
- `XTKS` → `TSEJ` (Tokyo MIC)
- `XMIL` → `BVME` (Milan MIC)
- All major MIC codes automatically mapped

### Cascading Resolution Logic

When you specify an exchange, the system tries multiple approaches:

1. **Direct Exchange**: Try your requested exchange first
2. **Exchange Aliases**: Try known working alternatives for that region
3. **SMART Fallback**: Use IBKR's intelligent routing as last resort

**Example Resolution Path**:
```python
resolve_symbol("SAP", exchange="XETRA")
# 1. Try XETRA → fails (not recognized by IBKR)
# 2. Try IBIS → works! (found SAP)
# 3. Return success with resolved_via_alias=true
```

### Multi-Segment Exchange Support

Some exchanges have different codes for different security types:

**German Market Segments**:
- `IBIS`: German stocks (SAP, BMW work)
- `IBIS2`: ETFs (VWCE works, SAP fails)
- `FWB`: German domestic stocks  
- `FWB2`: Foreign stocks on Frankfurt

**UK Market Segments**:
- `LSE`: Regular UK stocks
- `LSEETF`: UK-listed ETFs

**US Market Routing**:
- `NYSE`: Primary NYSE stocks
- `ARCA`: NYSE Arca (ETFs and some stocks)
- `NASDAQ`: NASDAQ stocks  
- `ISLAND`: Alternative NASDAQ routing

### Exchange Resolution Metadata

The response includes detailed information about exchange resolution:

```json
{
  "query_info": {
    "original_exchange": "XETRA",
    "actual_exchange": "IBIS", 
    "resolved_via_alias": true,
    "exchanges_tried": ["XETRA", "IBIS", "IBIS2"],
    "resolution_method": "exchange_alias"
  }
}
```

**Resolution Methods**:
- `exact_exchange`: Your requested exchange worked directly
- `exchange_alias`: Mapped to a working alternative
- `smart_routing`: Fell back to SMART routing
- `exchange_fallback_smart`: Used SMART after exchange failures

### Regional Exchange Recommendations

**For German Stocks**: Use `FRANKFURT` or `XETRA` - automatically maps to working codes
**For UK Stocks**: Use `LONDON` or `LSE` - includes ETF segment support
**For Swiss Stocks**: Use `SWISS` - automatically maps to `EBS` (SWX doesn't work)
**For Canadian Stocks**: Use `TORONTO` - automatically maps to `TSE` (TSX doesn't work)
**For Japanese Stocks**: Use `TOKYO` - automatically maps to `TSEJ` (TSE doesn't work for Japan)
**For Italian Stocks**: Use `MILAN` - automatically maps to `BVME` (BIT/MIL don't work)
**For Indian Stocks**: Use `INDIA` - automatically maps to `NSE` (BSE doesn't work)

### Troubleshooting Exchange Issues

**"Exchange not found" or "No matches"**:
- The system automatically tries alternatives, so this usually indicates the symbol doesn't exist
- Try `SMART` routing for broader search
- Verify symbol spelling and format

**"Resolved via alias" in response**:
- This is normal and expected - means system found working alternative
- Your requested exchange was mapped to a working IBKR code
- No action needed, resolution was successful

**Want to see all alternatives**:
- Use `max_results=10` to see multiple exchange options
- Compare `exchange` and `primary_exchange` fields
- Use `prefer_native_exchange=true` for international stocks

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

### "Exchange code not working"
• System automatically tries working alternatives - if it still fails, the symbol likely doesn't exist
• Standard names work: use "FRANKFURT" not "FWB", "TOKYO" not "TSEJ"
• MIC codes are supported: "XNYS", "XLON", "XTKS" automatically mapped
• Check resolved_via_alias in response to see what exchange actually worked
• Some exchanges only work for specific security types (stocks vs ETFs)

### "Getting different exchange than expected"
• Check query_info.resolved_via_alias and actual_exchange in response  
• System maps to working IBKR codes automatically (XETRA → IBIS, TSX → TSE)
• This is normal behavior - your symbol was found on a working exchange
• Use prefer_native_exchange=true for international stocks to prioritize home market

## Related Tools
• get_market_data - Get live prices using resolved symbols
• convert_currency - Convert prices between resolved currencies  
• get_forex_rates - Monitor currency rates for international positions
• get_portfolio - View holdings with consistent symbol formatting
• place_market_order - Trade using resolved symbols and exchanges
• place_limit_order - Place orders with proper exchange routing



## Supported Global Coverage

**140+ Exchange Mappings Worldwide with Intelligent Fallback:**

### **Europe (30+ codes)**
- **Germany**: FRANKFURT→FWB/FWB2, XETRA→IBIS/IBIS2, TRADEGATE→TGATE, GETTEX
- **UK**: LONDON→LSE/LSEETF, all MIC codes (XLON) supported
- **Switzerland**: SWISS/SWX→EBS (validated: SWX fails, EBS works)
- **Italy**: MILAN/BIT/MIL→BVME (validated: BIT/MIL fail, BVME works)
- **Sweden**: STOCKHOLM/OMX→SFB (validated: OMX fails, SFB works) 
- **Netherlands**: AMSTERDAM→AEB, France: PARIS→SBF
- **Nordics**: Oslo→OSE, Copenhagen→KFX/CPH, Helsinki→HEX
- **Others**: Vienna→VIX, Warsaw→WSE, Brussels→BEL

### **North America (10+ codes)**
- **US**: NYSE/ARCA, NASDAQ/ISLAND, BATS, IEX (with routing variants)
- **Canada**: TORONTO/TSX→TSE (validated: TSX fails, TSE works)
- **MIC Codes**: XNYS→NYSE, XNAS→NASDAQ (all major MIC codes supported)

### **Asia-Pacific (25+ codes)**
- **Japan**: TOKYO→TSEJ (validated: TSE fails for Japan, TSEJ works)
- **China**: Shanghai→SSE, Shenzhen→SZSE
- **India**: INDIA/BSE→NSE (validated: BSE fails, NSE works)
- **Others**: SEHK (HK), SGX (Singapore), ASX (Australia), KSE (Korea), TWSE (Taiwan)

### **Global & Emerging (15+ codes)**
- **Latin America**: B3/BVMF (Brazil), MEXI (Mexico)
- **Middle East**: TASE (Israel), TADAWUL (Saudi), EGX (Egypt)
- **Africa**: JSE (South Africa)
- **Special**: SMART (universal), IDEALPRO (forex)

### **Advanced Features**
- **Exchange Alias Mapping**: 140+ exchange codes with validated fallbacks
- **MIC Code Support**: All major Market Identifier Codes automatically mapped
- **Cascading Resolution**: Original→Aliases→SMART fallback ensures high success rate
- **Multi-Segment Support**: Different codes for stocks vs ETFs (IBIS/IBIS2, LSE/LSEETF)
- **Validation-Based**: All mappings based on real IBKR API testing
- **Transparent Resolution**: Clear feedback about which exchange actually worked
- **Fuzzy Search**: 2000+ major company names mapped to symbols
- **Alternative IDs**: CUSIP/ISIN support for institutional integration
- **Real-time Integration**: Live data via IBKR API with intelligent caching
- **Global Currency Support**: USD, EUR, GBP, JPY, CHF, AUD, CAD, and 25+ others
