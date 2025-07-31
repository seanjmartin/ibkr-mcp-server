# IBKR Stop Loss Capabilities - Comprehensive Analysis

## 🎯 Executive Summary

**EXCELLENT SUPPORT** - IBKR provides comprehensive stop loss functionality through the ib-async API with full international market support.

## ✅ Available Stop Loss Order Types

### 1. **Basic Stop Order (Market Stop)**
```python
StopOrder('SELL', 100, 45.50)
# Sells 100 shares at market price when stock drops to $45.50
```
- **Trigger**: Stock price hits stop price
- **Execution**: Market order (immediate fill)
- **Risk**: May fill below stop price in fast markets

### 2. **Stop Limit Order** 
```python
StopLimitOrder('SELL', 100, stopPrice=45.50, lmtPrice=45.00)
# Triggers at $45.50, places limit sell at $45.00
```
- **Trigger**: Stock price hits stop price ($45.50)
- **Execution**: Limit order at specified price ($45.00)
- **Advantage**: Price protection
- **Risk**: May not fill if market gaps below limit price

### 3. **Trailing Stop Order**
```python
trailing_stop = Order()
trailing_stop.orderType = 'TRAIL'
trailing_stop.auxPrice = 2.00  # Trails $2.00 below highest price
# OR
trailing_stop.trailPercent = 5.0  # Trails 5% below highest price
```
- **Dynamic**: Adjusts stop price as stock rises
- **Dollar Amount**: Fixed dollar trail ($2.00)
- **Percentage**: Percentage-based trail (5%)
- **Benefit**: Captures more upside while maintaining protection

### 4. **Bracket Orders (Stop Loss + Take Profit)**
```python
parent = MarketOrder('BUY', 100)
take_profit = LimitOrder('SELL', 100, 55.0)
stop_loss = StopOrder('SELL', 100, 45.0)
bracket = BracketOrder(parent, take_profit, stop_loss)
```
- **Complete Solution**: Entry + profit target + stop loss
- **One-Cancels-Other**: When one side fills, other cancels
- **Risk Management**: Automatic profit taking and loss limiting

## 🛠️ Advanced Stop Loss Features

### **Time in Force Options**
- **GTC**: Good Till Cancelled (persists until filled/cancelled)
- **DAY**: Expires at market close
- **GTD**: Good Till Date (specify expiration)
- **IOC**: Immediate or Cancel
- **FOK**: Fill or Kill

### **Extended Hours Trading**
```python
stop_order.outsideRth = True  # Allow after-hours execution
```
- Execute stop losses outside regular trading hours
- Critical for overnight risk management
- Especially important for international markets

### **Order Attributes**
```python
advanced_stop = Order()
advanced_stop.action = 'SELL'
advanced_stop.totalQuantity = 100
advanced_stop.orderType = 'STP'
advanced_stop.auxPrice = 45.50         # Stop trigger price
advanced_stop.tif = 'GTC'              # Good Till Cancelled
advanced_stop.outsideRth = True        # After-hours allowed
advanced_stop.allOrNone = False        # Allow partial fills
advanced_stop.transmit = True          # Submit immediately
```

## 🌍 International Market Support

### **Multi-Currency Stop Losses**
```python
# European stock (EUR)
eu_stock = Stock('ASML', 'AEB', 'EUR')
eu_stop = StopOrder('SELL', 50, 650.0)  # €650 stop

# Asian stock (JPY)  
asia_stock = Stock('7203', 'TSE', 'JPY')
asia_stop = StopOrder('SELL', 100, 2800)  # ¥2800 stop

# UK stock (GBP)
uk_stock = Stock('VOD', 'LSE', 'GBP')
uk_stop = StopOrder('SELL', 200, 120.0)  # £120 stop
```

### **Exchange-Specific Considerations**
- **Trading Hours**: Stop losses respect local market hours
- **Currency Precision**: Automatic handling of currency decimals
- **Settlement**: Local currency settlement with auto-conversion
- **Regulations**: Compliance with local exchange rules

## 📊 Order Management & Monitoring

### **Reading Existing Stop Losses**
```python
# Get all open orders (including stop losses)
open_orders = await ib.reqOpenOrdersAsync()

# Get completed orders  
completed = await ib.reqCompletedOrdersAsync()

# Current orders property
all_current_orders = ib.orders
open_orders_list = ib.openOrders
```

### **Order State Monitoring**
- **PreSubmitted**: Order received but not yet submitted
- **Submitted**: Order submitted to exchange
- **Filled**: Order completely executed
- **Cancelled**: Order cancelled
- **PendingCancel**: Cancellation request pending
- **ApiCancelled**: Cancelled via API

### **Modifying Stop Losses**
```python
# Cancel existing stop loss
await ib.cancelOrder(existing_stop_order)

# Place new stop loss
new_stop = StopOrder('SELL', 100, new_stop_price)
await ib.placeOrder(contract, new_stop)

# What-if analysis (test without placing)
result = await ib.whatIfOrderAsync(contract, stop_order)
```

## 🔧 Implementation Requirements for MCP Server

### **Current Status: NOT IMPLEMENTED**
The MCP server currently has NO stop loss functionality:
- ❌ No order placement tools
- ❌ No stop loss management
- ❌ No order reading capabilities
- ❌ No order modification tools

### **Required MCP Tools for Complete Stop Loss Support**

#### **1. Place Stop Loss Orders**
```python
Tool(
    name="place_stop_loss",
    description="Place stop loss order for existing position",
    inputSchema={
        "symbol": str,
        "exchange": str, 
        "currency": str,
        "quantity": int,
        "stop_price": float,
        "order_type": str,  # 'STP', 'STP LMT', 'TRAIL'
        "limit_price": float,  # For stop-limit orders
        "trail_amount": float,  # For trailing stops
        "trail_percent": float,  # For trailing stops
        "time_in_force": str,  # 'GTC', 'DAY', etc.
        "outside_rth": bool
    }
)
```

#### **2. Read Existing Stop Losses**
```python
Tool(
    name="get_stop_losses",
    description="Get all existing stop loss orders",
    inputSchema={
        "account": str,  # Optional
        "symbol": str,   # Optional filter
        "status": str    # 'open', 'all', 'filled'
    }
)
```

#### **3. Modify Stop Loss Orders**
```python
Tool(
    name="modify_stop_loss", 
    description="Update existing stop loss order",
    inputSchema={
        "order_id": int,
        "new_stop_price": float,
        "new_quantity": int,
        "new_tif": str
    }
)
```

#### **4. Cancel Stop Loss Orders**
```python
Tool(
    name="cancel_stop_loss",
    description="Cancel existing stop loss order", 
    inputSchema={
        "order_id": int,
        "symbol": str  # Optional for validation
    }
)
```

#### **5. Bracket Order Management**
```python
Tool(
    name="place_bracket_order",
    description="Place entry order with stop loss and take profit",
    inputSchema={
        "entry_order": dict,     # Parent order details
        "take_profit_price": float,
        "stop_loss_price": float,
        "symbol": str,
        "exchange": str,
        "currency": str
    }
)
```

## 📋 Stop Loss Best Practices Support

### **Portfolio-Wide Stop Loss Management**
```python
Tool(
    name="set_portfolio_stop_losses",
    description="Set stop losses for all positions in portfolio",
    inputSchema={
        "stop_loss_percent": float,  # e.g., 10% below current price
        "exclude_symbols": list,     # Symbols to skip
        "trailing": bool,           # Use trailing stops
        "outside_rth": bool
    }
)
```

### **Dynamic Stop Loss Adjustment**
```python
Tool(
    name="adjust_stop_losses",
    description="Automatically adjust stops based on profit/loss",
    inputSchema={
        "trigger_profit_percent": float,  # When to start adjusting
        "new_stop_percent": float,        # New stop level
        "symbols": list                   # Specific symbols or all
    }
)
```

## 🎯 Implementation Priority

### **Phase 1: Basic Stop Loss (HIGH PRIORITY)**
1. `place_stop_loss` - Basic stop and stop-limit orders
2. `get_stop_losses` - Read existing orders
3. `cancel_stop_loss` - Cancel orders

### **Phase 2: Advanced Features (MEDIUM PRIORITY)**  
1. `modify_stop_loss` - Update existing orders
2. Trailing stop support
3. International currency handling

### **Phase 3: Portfolio Management (LOWER PRIORITY)**
1. `place_bracket_order` - Complete order management
2. `set_portfolio_stop_losses` - Bulk operations
3. Advanced risk management tools

## 🔍 Testing Requirements

### **Paper Trading Validation**
1. Verify stop loss orders can be placed on paper account
2. Test order state transitions
3. Validate international currency support
4. Test bracket order functionality

### **Order Reading Accuracy** 
1. Ensure all order types are properly parsed
2. Verify stop prices and attributes are correct
3. Test filtering by symbol/status
4. Validate order modification capabilities

## 📊 Final Assessment

### **✅ IBKR Platform Capabilities: EXCELLENT**
- Complete stop loss order type support
- Advanced features (trailing, bracket orders)
- International market compatibility
- Comprehensive order management API

### **❌ Current MCP Implementation: NONE**
- No stop loss tools implemented
- No order placement capability
- No order reading functionality
- No risk management features

### **🛠️ Implementation Effort: MODERATE**
- API foundation is solid
- Order types well-documented
- International support built-in
- Comprehensive testing required

**CONCLUSION**: IBKR provides world-class stop loss capabilities through ib-async. The MCP server needs significant enhancement to expose these features, but the underlying infrastructure is robust and ready for implementation.
