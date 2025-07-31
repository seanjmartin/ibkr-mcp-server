# IBKR MCP Server Update Plan

## 🔍 Current Status Analysis

### ✅ What's Working
- **Connection**: Successfully connects to IB Gateway on port 7497
- **Authentication**: Paper trading account DUH905195 is recognized
- **Basic Structure**: MCP server framework is properly set up
- **Environment**: Virtual environment and dependencies are installed
- **Claude Integration**: Already configured in Claude Desktop config

### ❌ Issues Identified

#### 1. **Account Summary API Incompatibility**
```
Error: IB.reqAccountSummaryAsync() takes 1 positional argument but 3 were given
```
- **Root Cause**: Code written for older ib-async API
- **Current Version**: ib-async 2.0.1 (latest)
- **Fix Needed**: Update method call syntax

#### 2. **Short Selling Methods Missing**
```
Error: 'IB' object has no attribute 'reqShortableSharesAsync'
```
- **Root Cause**: Method doesn't exist in current ib-async
- **Alternative**: Need to find equivalent functionality or remove feature

#### 3. **Market Data Tools Missing**
- **Issue**: No `get_market_data` tool implemented
- **Need**: Add real-time quotes functionality using `reqTickersAsync`

#### 4. **Parameter Handling Issues**
```
Error: 'list' object has no attribute 'includeExpired'
```
- **Root Cause**: Incorrect object types being passed to API methods

## 📋 Available ib-async API Methods (v2.0.1)

### Account Methods
```python
# ✅ Available methods:
ib.reqAccountSummaryAsync()          # No parameters needed
ib.reqPositionsAsync()               # Get all positions
ib.reqAccountUpdatesAsync(account)   # Account updates
ib.managedAccounts()                 # List accounts
```

### Market Data Methods
```python
# ✅ Available methods:
ib.reqTickersAsync(*contracts)       # Real-time quotes
ib.reqMktData(contract)              # Market data subscription
ib.qualifyContractsAsync(*contracts) # Validate contracts
ib.reqHistoricalDataAsync(...)       # Historical data
```

### Position Methods
```python
# ✅ Available methods:
ib.reqPositionsAsync()               # All positions
ib.positions                         # Current positions list
ib.portfolio()                       # Portfolio items
```

## 🛠️ Required Fixes

### 1. **Fix Account Summary Tool**

**Current Code Issue:**
```python
# ❌ This is wrong:
summary = await ibkr_client.ib.reqAccountSummaryAsync(account, tags)
```

**Correct Implementation:**
```python
# ✅ This should work:
summary = await ibkr_client.ib.reqAccountSummaryAsync()
# Then filter by account if needed
```

### 2. **Add Market Data Tool**

**New Tool Needed:**
```python
Tool(
    name="get_market_data",
    description="Get real-time market quotes for securities",
    inputSchema={
        "type": "object",
        "properties": {
            "symbols": {"type": "string", "description": "Comma-separated symbols (e.g., AAPL,TSLA,GOOGL)"}
        },
        "required": ["symbols"],
        "additionalProperties": False
    }
)
```

**Implementation:**
```python
async def get_market_data(symbols_str: str):
    symbols = [s.strip() for s in symbols_str.split(',')]
    contracts = []
    
    for symbol in symbols:
        stock = Stock(symbol, 'SMART', 'USD')
        contracts.append(stock)
    
    # Qualify contracts first
    qualified = await ib.qualifyContractsAsync(*contracts)
    
    # Get tickers
    tickers = await ib.reqTickersAsync(*qualified)
    
    return format_ticker_data(tickers)
```

### 3. **Fix Portfolio Tool**

**Update Implementation:**
```python
async def get_portfolio(account=None):
    positions = await ib.reqPositionsAsync()
    
    if account:
        # Filter by specific account
        positions = [p for p in positions if p.account == account]
    
    return format_positions(positions)
```

### 4. **Remove/Replace Short Selling Tools**

**Options:**
1. **Remove entirely** - Short selling data may not be available via API
2. **Replace with margin requirements** - Use available margin methods
3. **Use alternative data sources** - External APIs for short interest

## 📁 File Structure to Update

```
ibkr-mcp-server/
├── ibkr_mcp_server/
│   ├── client.py        # ← Main fixes needed here
│   ├── tools.py         # ← Add market data tool
│   ├── config.py        # ← May need updates
│   └── main.py          # ← Minor fixes
├── .env                 # ← Already configured
└── README.md            # ← Update with new features
```

## 🎯 Implementation Priority

### Phase 1: Critical Fixes
1. **Fix account summary** - Enable cash balance viewing
2. **Fix portfolio tool** - Show positions correctly
3. **Add basic market data** - Get real-time quotes

### Phase 2: Enhanced Features
1. **Add historical data** - Price charts
2. **Improve error handling** - Better user messages
3. **Add position sizing** - Portfolio analysis

### Phase 3: Advanced Features
1. **Order placement** - Buy/sell functionality (with safety)
2. **Real-time updates** - Live portfolio monitoring
3. **Risk management** - Position limits and alerts

## 🧪 Testing Strategy

### Connection Test
```python
# Test with client ID 2 to avoid conflicts
await ib.connectAsync('127.0.0.1', 7497, clientId=2)
```

### API Method Testing
```python
# Test each method individually:
summary = await ib.reqAccountSummaryAsync()
positions = await ib.reqPositionsAsync()
contracts = await ib.qualifyContractsAsync(Stock('AAPL', 'SMART', 'USD'))
tickers = await ib.reqTickersAsync(*contracts)
```

## 📋 Next Steps

1. **Create new project folder** - Start with clean fork
2. **Update client.py** - Fix API method calls
3. **Add market data tool** - Implement quotes functionality
4. **Test thoroughly** - Verify each tool works
5. **Update documentation** - Reflect new capabilities
6. **Deploy and configure** - Update Claude Desktop config

## 🔧 Development Environment

- **Python**: 3.13.2 ✅
- **ib-async**: 2.0.1 ✅
- **IB Gateway**: Running on port 7497 ✅
- **Account**: DUH905195 (paper trading) ✅
- **API Access**: Read-only enabled ✅

## 💡 Key Insights

1. **Library is current** - ib-async 2.0.1 is latest, no upgrade needed
2. **API changed significantly** - Method signatures are different
3. **Some features unavailable** - Short selling data may not be accessible
4. **Connection works** - Core infrastructure is solid
5. **Framework is good** - MCP structure doesn't need changes

Ready to start the update project! 🚀