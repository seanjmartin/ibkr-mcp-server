# System Architecture

Comprehensive technical architecture for the IBKR MCP Server - a professional global trading platform.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Desktop                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────────────┐
│                 IBKR MCP Server                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   23 MCP    │  │  Enhanced   │  │    Safety Framework    │  │
│  │    Tools    │  │   Client    │  │   Audit & Protection   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Trading   │  │ API Cache   │  │      Validation        │  │
│  │  Managers   │  │  & Helpers  │  │      Framework         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ ib-async 2.0.1
┌─────────────────────▼───────────────────────────────────────────┐
│                Interactive Brokers API                         │
│     ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐     │
│     │ US Markets  │ │   Global    │ │       Forex         │     │
│     │ SMART/USD   │ │  Markets    │ │    IDEALPRO        │     │
│     └─────────────┘ └─────────────┘ └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### **1. Enhanced IBKR Client (client.py)**

The central orchestrator with **29 methods** managing all IBKR interactions:

#### **Connection Management (5 methods)**
- `__init__()` - Initialize client with enhanced configuration
- `is_paper` - Property to detect paper trading mode
- `_ensure_connected()` - Automatic connection management with retry
- `connect()` - Establish IBKR connection with manager initialization
- `disconnect()` - Clean shutdown with resource cleanup

#### **Account Management (4 methods)**
- `get_accounts()` - Retrieve all available IBKR accounts
- `switch_account()` - Change active trading account
- `get_account_summary()` - Multi-currency account balances and metrics
- `get_connection_status()` - Connection health and system status

#### **Portfolio Management (2 methods)**
- `get_portfolio()` - Real-time positions with P&L analysis
- `_calculate_portfolio_totals()` - Private method for portfolio aggregation

#### **Market Data (4 methods)**
- `get_market_data()` - Global market data with intelligent exchange detection
- `resolve_symbol()` - **NEW: Direct IBKR API symbol resolution** with real company data, fuzzy search, and confidence scoring
- `_qualify_contracts()` - Private contract qualification
- `_format_market_data()` - Private data formatting

#### **Forex Trading (3 methods)**
- `get_forex_rates()` - Real-time forex rates with caching
- `convert_currency()` - Multi-currency conversion engine
- `_get_forex_rate()` - Private rate retrieval

#### **Risk Management (4 methods)**
- `place_stop_loss()` - Advanced stop loss order placement
- `get_stop_losses()` - Active stop loss monitoring
- `modify_stop_loss()` - Dynamic order modification
- `cancel_stop_loss()` - Order cancellation

#### **Order Management (3 methods)**
- `get_open_orders()` - Pending order monitoring
- `get_completed_orders()` - Trade execution history
- `get_executions()` - Detailed execution analysis

#### **Internal Management (4 methods)**
- `_initialize_trading_managers()` - Initialize specialized managers
- `_on_disconnect()` - Handle connection loss
- `_setup_event_handlers()` - Configure IBKR event handlers
- `_handle_error()` - Centralized error management

## 📊 Current vs Previous Architecture Status

### **✅ What's Current:**
- **29 methods** in IBKRClient (was incorrectly documented as 17)
- **23 MCP tools** providing Claude Desktop interface
- **3 Trading Managers**: Forex, International, Stop Loss
- **Live API Integration**: 21 forex pairs, dynamic symbol resolution via IBKR API, 12 exchanges
- **Safety Framework**: Multi-layer protection with audit logging
- **Documentation System**: Self-documenting help system

### **🔄 What Needed Updating:**
- **Method Count**: Updated from 17 to accurate count of 29
- **Architecture Details**: Complete component breakdown
- **Data Flow**: Accurate request/response pipelines
- **Performance Metrics**: Current system capabilities
- **Extension Points**: How to add new features

### **🚀 Recent Major Improvements:**

#### **Symbol Resolution Overhaul (August 2025)**
- **Removed**: Static database dependency (`international_symbols.py` - 350 lines deleted)
- **Added**: Direct IBKR API integration using `reqContractDetailsAsync`
- **Improvement**: Real company names instead of guessed data
  - **Before**: `"AAPL (guessed US stock)"`
  - **After**: `"Apple Inc."` with ISIN `US0378331005`
- **Performance**: Reduced from 4 API calls to 1 per symbol
- **Accuracy**: 100% real IBKR metadata vs synthetic guesses
- **Methods Updated**: `_resolve_exact_symbol()` completely rewritten
- **Files Removed**: Database imports, guessing logic, static symbol database

#### **Architecture Benefits:**
- **Reduced Complexity**: No more database/fallback/guessing chain
- **Better Reliability**: Direct IBKR source of truth
- **Enhanced Data Quality**: Real alternative IDs (CUSIP, ISIN) from IBKR
- **Improved Performance**: Single API call per symbol resolution
- **Future-Proof**: Scales automatically with IBKR's symbol coverage

### **📍 Document Location Fixed:**
- **Old**: `TECHNICAL_ARCHITECTURE.md` in root (wrong location)
- **New**: `docs/architecture/system-architecture.md` (proper GitHub docs structure)

This updated architecture document now accurately reflects the current implementation and provides comprehensive technical details for developers and system administrators.
