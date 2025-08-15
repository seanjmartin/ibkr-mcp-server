# IBKR MCP Server Documentation

Welcome to the comprehensive documentation for the IBKR MCP Server - a professional-grade global trading platform for Claude AI.

## 📚 Documentation Structure

### **Getting Started**
- [Quick Start Guide](guides/quick-start.md) - Get up and running in 5 minutes
- [Deployment Guide](guides/deployment.md) - Complete deployment and configuration guide ⭐

### **User Guides**
- [Trading Guide](guides/trading.md) - Complete trading workflows and examples
- [Forex Trading](guides/forex.md) - Currency trading and conversion
- [International Markets](guides/international.md) - Global stock trading
- [Risk Management](guides/risk-management.md) - Stop losses and portfolio protection
- [Paper Trading](guides/paper-trading.md) - Safe testing and learning
- [Claude Desktop User Testing](guides/claude-desktop-user-testing.md) - Real user experience testing ⭐
- [Deployment Guide](guides/deployment.md) - Production deployment and configuration

### **API Reference**
- [API Quick Reference](api/API_QUICK_REFERENCE.md) - Essential commands and examples ⭐
- [MCP Tools Reference](api/tools.md) - Complete tool documentation (23 tools)

### **Examples & Tutorials**
- [Basic Usage Examples](examples/basic-usage.md) - Common operations
- [Advanced Trading Examples](examples/advanced-trading.md) - Complex workflows
- [Integration Examples](examples/integrations.md) - Custom implementations
- [Troubleshooting Examples](examples/troubleshooting.md) - Common issues and solutions

### **Architecture & Development**
- [System Architecture](architecture/system-architecture.md) - Complete technical architecture
- [Safety Measures & Risk Management](architecture/safety-measures.md) - Comprehensive safety framework
- [Testing Strategy & Implementation](architecture/testing-strategy.md) - Complete testing approach

### **Reference**
- [Supported Markets](reference/markets.md) - Complete list of supported exchanges and currencies
- [Changelog](../CHANGELOG.md) - Version history and changes



## 🌍 Global Coverage

### **Markets Supported**
- **12 Exchanges**: US, European, Asian, and Pacific markets
- **21 Forex Pairs**: Major and cross currency pairs
- **29 Currencies**: Multi-currency trading and conversion
- **23 International Symbols**: Pre-configured global stocks

### **Key Features**
- **Real-time Market Data**: Live quotes with intelligent exchange detection
- **Complete Trading Platform**: Market, limit, and bracket order execution
- **Professional Order Management**: Place, modify, cancel, and monitor all order types
- **Advanced Risk Management**: Stop losses, bracket orders, trailing stops
- **Multi-currency Accounts**: Trade in multiple currencies seamlessly
- **Paper Trading**: Full compatibility with IBKR paper accounts
- **Safety Framework**: Comprehensive protection and audit logging

## Complete MCP Tools (23 Total)

### **Portfolio & Account Management (5 tools)**
- `get_portfolio` - View current positions with P&L analysis
- `get_account_summary` - Account balances and metrics
- `get_accounts` - List all available IBKR accounts
- `switch_account` - Change active trading account
- `get_connection_status` - IBKR connection health and system status

### **Market Data & Analysis (2 tools)**
- `get_market_data` - Live quotes for stocks worldwide with intelligent exchange detection
- `resolve_symbol` - Unified symbol resolution with fuzzy search and company data

### **Forex & Currency (2 tools)**
- `get_forex_rates` - Real-time forex rates for 21 currency pairs
- `convert_currency` - Multi-currency conversion with live rates

### **Risk Management (4 tools)**
- `place_stop_loss` - Create stop orders for loss protection
- `get_stop_losses` - View all active stop loss orders
- `modify_stop_loss` - Adjust existing stop loss orders
- `cancel_stop_loss` - Remove stop loss orders

### **Order History & Tracking (3 tools)**
- `get_open_orders` - View pending orders
- `get_completed_orders` - Order-level trade history (summary)
- `get_executions` - Execution-level details (individual fills)

### **Order Placement & Management (6 tools)**
- `place_market_order` - Execute market orders for immediate execution
- `place_limit_order` - Place limit orders with price control
- `place_bracket_order` - Advanced bracket orders (entry + stop + target)
- `cancel_order` - Cancel pending orders
- `modify_order` - Modify existing orders (quantity, price, time-in-force)
- `get_order_status` - Get comprehensive order status information

### **Documentation (1 tool)**
- `get_tool_documentation` - Built-in help system for all tools

### **Common Usage Examples**
```
"Check my IBKR connection status"           # Connection management
"Show me my current portfolio"              # Portfolio overview
"Get quotes for Apple, ASML, and Toyota"   # Global market data
"What's the EUR/USD rate?"                  # Forex rates
"Convert $5000 to Euros"                    # Currency conversion
"Buy 100 shares of Apple at market price"  # Market order
"Set a stop loss on my Apple position"     # Risk management
"Show me my pending orders"                 # Order tracking
"Cancel my pending order #12345"           # Order management
```

## 🆘 Getting Help

- **Issues**: Search [Common Problems](examples/troubleshooting.md)
- **API Reference**: Complete [Tools Documentation](api/tools.md)
- **Examples**: Browse [Usage Examples](examples/basic-usage.md)

---

**Last Updated**: August 2025 | **Version**: 2.0.0 | **Status**: Production Ready
