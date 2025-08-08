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
│  │   Trading   │  │ Reference   │  │      Validation        │  │
│  │  Managers   │  │    Data     │  │      Framework         │  │
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
- `resolve_international_symbol()` - Symbol-to-exchange resolution
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
- **Complete Reference Data**: 21 forex pairs, 23 international symbols, 12 exchanges
- **Safety Framework**: Multi-layer protection with audit logging
- **Documentation System**: Self-documenting help system

### **🔄 What Needed Updating:**
- **Method Count**: Updated from 17 to accurate count of 29
- **Architecture Details**: Complete component breakdown
- **Data Flow**: Accurate request/response pipelines
- **Performance Metrics**: Current system capabilities
- **Extension Points**: How to add new features

### **📍 Document Location Fixed:**
- **Old**: `TECHNICAL_ARCHITECTURE.md` in root (wrong location)
- **New**: `docs/architecture/system-architecture.md` (proper GitHub docs structure)

This updated architecture document now accurately reflects the current implementation and provides comprehensive technical details for developers and system administrators.
