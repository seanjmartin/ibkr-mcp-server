# IBKR MCP Server - Technical Architecture

## System Architecture

### **Core Components**

#### **IBKRClient (client.py)**
The enhanced central client manages all IBKR API interactions with 17 methods:

**Portfolio & Account Methods:**
- `get_portfolio()` - Portfolio positions with P&L
- `get_account_summary()` - Account balances and metrics
- `get_accounts()` - Available account list
- `switch_account()` - Account switching
- `get_connection_status()` - Connection status and details

**Market Data Methods:**
- `get_market_data()` - Global market data with auto-detection
- `resolve_international_symbol()` - Symbol-to-exchange resolution

**Forex Methods:**
- `get_forex_rates()` - Real-time forex rates with caching
- `convert_currency()` - Multi-currency conversion engine

**Risk Management Methods:**
- `place_stop_loss()` - Stop loss order placement
- `get_stop_losses()` - Active stop loss retrieval
- `modify_stop_loss()` - Order modification
- `cancel_stop_loss()` - Order cancellation

**Order Management Methods:**
- `get_open_orders()` - Pending orders
- `get_completed_orders()` - Trade history
- `get_executions()` - Execution details

**Documentation Method:**
- `get_tool_documentation()` - Comprehensive help system

#### **Trading Managers (trading/ directory)**

**ForexManager (trading/forex.py)**
- **Rate Caching**: 5-second intelligent cache for forex rates
- **Conversion Engine**: Direct/inverse/cross-currency calculations
- **Mock Rate System**: Paper trading compatibility with realistic fallback rates
- **Validation**: Comprehensive forex pair format and availability checking

**InternationalManager (trading/international.py)**
- **Symbol Database**: 25+ international stocks with exchange/currency mapping
- **Auto-Detection**: Intelligent SYMBOL → EXCHANGE/CURRENCY resolution
- **Market Data**: Multi-currency contract creation and qualification
- **Exchange Validation**: Trading hours and market status checking

**StopLossManager (trading/stop_loss.py)**
- **Order Types**: Basic stop, stop-limit, trailing stop orders
- **Order Monitoring**: Real-time state tracking and updates
- **Bracket Orders**: Entry + stop loss + take profit combinations
- **Risk Management**: Position-based calculations and validation

#### **Reference Data System (data/ directory)**

**Forex Pairs Database (data/forex_pairs.py)**
- **20+ Currency Pairs**: Major, cross, and exotic pairs
- **Trading Metadata**: Pip values, minimum sizes, spreads, market hours
- **Validation Functions**: Format checking and pair availability

**International Symbols Database (data/international_symbols.py)**
- **25+ International Stocks**: European, Asian, and other global markets
- **Complete Metadata**: Exchange, currency, name, country, sector, ISIN
- **Lookup Functions**: Symbol resolution and filtering capabilities

**Exchange Information (data/exchange_info.py)**
- **Global Exchanges**: XETRA, LSE, TSE, SEHK, ASX, AEB, SWX, KFX
- **Trading Hours**: Local market hours with timezone information
- **Settlement Rules**: T+1, T+2, T+3 settlement cycles
- **Currency Information**: Primary currencies for each exchange

#### **Safety Framework**

**Enhanced Configuration (enhanced_config.py)**
- **Master Safety Controls**: All trading disabled by default
- **Account Verification**: Paper trading enforcement
- **Order Limits**: Size, value, daily count restrictions
- **Rate Limiting**: API usage controls
- **Emergency Controls**: Kill switch configuration

**Enhanced Validators (enhanced_validators.py)**
- **TradingSafetyValidator**: Core safety checks and account verification
- **ForexValidator**: Currency pair and forex order validation
- **InternationalValidator**: Symbol format and exchange validation
- **StopLossValidator**: Stop loss order parameter validation

**Safety Framework (safety_framework.py)**
- **TradingAuditLogger**: Complete operation audit trail
- **EmergencyKillSwitch**: Instant trading halt capability
- **RateLimiter**: Operation-specific rate limiting
- **DailyLimitsTracker**: Daily order and volume tracking

#### **Documentation System (documentation/ directory)**

**Documentation Processor (documentation/doc_processor.py)**
- **Query Processing**: Smart parsing of tool and category requests
- **File Management**: Individual tool documentation loading
- **Aspect Filtering**: Focus on specific sections (examples, troubleshooting)
- **Category Support**: Grouped documentation for related tools

**Tool Documentation (documentation/tools/)**
- **17 Individual Files**: Complete documentation for each MCP tool
- **Rich Content**: Overview, parameters, examples, workflows, troubleshooting
- **Maintainable Structure**: Separate files for easy updates

**Category Documentation (documentation/categories/)**
- **Forex Trading**: Complete forex workflow documentation
- **Stop Loss Management**: Risk management concept documentation

## Data Flow Architecture

### **Request Processing Flow**
```
Claude Request → MCP Tool → Input Validation → Safety Checks → Business Logic → IBKR API → Response Formatting → Claude
```

### **Market Data Flow**
```
Symbol Request → Symbol Resolution → Contract Creation → IBKR Qualification → Market Data Request → Rate Limiting → Caching → Response
```

### **Trading Operation Flow**
```
Trading Request → Safety Validation → Account Verification → Order Limits Check → IBKR Order Placement → State Monitoring → Audit Logging
```

## Key Architectural Patterns

### **Modular Manager Pattern**
Each trading domain has a dedicated manager:
- **Separation of Concerns**: Domain-specific logic isolated
- **Single Responsibility**: Each manager focuses on specific functionality
- **Testability**: Individual managers can be unit tested
- **Extensibility**: Easy to add new trading domains

### **Safety-First Design**
Multiple layers of protection:
- **Configuration-Driven**: All safety controlled by settings
- **Fail-Safe Defaults**: Everything disabled until explicitly enabled
- **Defense in Depth**: Multiple validation layers
- **Audit Trail**: Complete operation logging

### **Intelligent Caching**
Performance optimization through caching:
- **Forex Rates**: 5-second cache with automatic expiration
- **Symbol Resolution**: Database lookup with memory caching
- **Contract Qualification**: Results cached for session duration
- **Memory Management**: Automatic cleanup and garbage collection

### **Error Handling Strategy**
Comprehensive error management:
- **Domain-Specific Exceptions**: ForexError, InternationalTradingError, StopLossError
- **Graceful Degradation**: Partial failures don't crash system
- **Error Context**: Detailed messages with actionable information
- **Fallback Systems**: Mock data for paper trading limitations

## Performance Characteristics

### **Response Times**
- **Market Data**: Sub-second for cached data, 2-3 seconds for fresh data
- **Currency Conversion**: <1 second with intelligent caching
- **Symbol Resolution**: <1 second database lookup
- **Order Operations**: 1-2 seconds for validation and placement

### **Memory Usage**
- **Efficient Caching**: 5-second forex cache, automatic cleanup
- **Database Lookups**: In-memory symbol resolution
- **Connection Management**: Single persistent IBKR connection
- **Resource Cleanup**: Proper disposal of temporary objects

### **API Rate Management**
- **Intelligent Throttling**: Respects IBKR 50 messages/second limit
- **Operation Batching**: Multiple symbols in single requests
- **Cache Optimization**: Reduces unnecessary API calls
- **Error Recovery**: Automatic retry with exponential backoff

## Integration Points

### **IBKR API Integration**
- **ib-async 2.0.1**: Full compatibility with latest library
- **Contract Types**: Stock, Forex, Index contract support
- **Order Types**: Market, Limit, Stop, Stop-Limit, Trailing Stop
- **Real-Time Data**: Live market data subscriptions

### **MCP Protocol Integration**
- **Tool Registration**: Automatic discovery of all 17 tools
- **Schema Validation**: Proper parameter validation
- **Error Responses**: Structured error messages
- **Documentation**: Built-in help system

### **Claude Desktop Integration**
- **Natural Language**: Tools work with conversational requests
- **Context Awareness**: Understanding of portfolio and market context
- **Error Guidance**: Helpful error messages and suggestions
- **Educational**: Explains complex trading concepts

## Security Architecture

### **Authentication & Authorization**
- **IBKR Credentials**: Secure API key management
- **Account Verification**: Paper vs live account detection
- **Permission Checks**: Feature-specific enablement flags
- **Audit Logging**: Complete operation tracking

### **Data Protection**
- **Input Validation**: Comprehensive parameter checking
- **SQL Injection**: N/A (no database queries)
- **Command Injection**: Validated inputs only
- **Information Disclosure**: Sensitive data redaction in logs

### **Trading Safety**
- **Order Limits**: Size, value, and count restrictions
- **Risk Management**: Position size and portfolio percentage limits
- **Emergency Controls**: Kill switch for crisis situations
- **Paper Trading**: Safe testing environment

## Deployment Architecture

### **Development Environment**
- **Python 3.13.2**: Latest Python with enhanced performance
- **Virtual Environment**: Isolated dependency management
- **IB Gateway**: Paper trading connection for safe testing
- **Local Configuration**: Development-specific settings

### **Production Considerations**
- **Live Trading**: Enhanced safety for real money operations
- **Market Data Subscriptions**: Exchange-specific data fees
- **High Availability**: Connection monitoring and auto-recovery
- **Backup & Recovery**: Configuration and state backup

## Extension Points

### **Adding New Trading Domains**
1. Create new manager in `trading/` directory
2. Add domain-specific data in `data/` directory
3. Integrate manager in `IBKRClient`
4. Add MCP tools in `tools.py`
5. Create documentation in `documentation/`

### **Adding New Markets**
1. Update `international_symbols.py` with new symbols
2. Add exchange information to `exchange_info.py`
3. Enhance validation in `enhanced_validators.py`
4. Update documentation

### **Adding New Order Types**
1. Extend `StopLossManager` with new order logic
2. Add validation in `StopLossValidator`
3. Create new MCP tools if needed
4. Update documentation

This architecture provides a solid foundation for professional-grade global trading capabilities while maintaining flexibility for future enhancements.
