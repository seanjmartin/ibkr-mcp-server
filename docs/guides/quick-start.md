# Quick Start Guide

Get the IBKR MCP Server running with Claude Desktop in 5 minutes.

## Prerequisites

- Python 3.9+ (tested with 3.13.2)
- Interactive Brokers account (paper or live)
- IB Gateway or TWS installed
- Claude Desktop

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/seanjmartin/ibkr-mcp-server.git
cd ibkr-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure IBKR Connection

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```bash
   # IBKR Connection
   IBKR_HOST=127.0.0.1
   IBKR_PORT=7497                    # Paper: 7497, Live: 7496
   IBKR_IS_PAPER=true
   
   # Safety Settings (start with these)
   ENABLE_TRADING=false              # Keep disabled initially
   ENABLE_FOREX_TRADING=false
   ENABLE_INTERNATIONAL_TRADING=false
   ENABLE_STOP_LOSS_ORDERS=false
   ```

## Step 3: Start IB Gateway

1. **Launch IB Gateway** (or TWS)
2. **Configure API Settings:**
   - Enable "ActiveX and Socket Clients"
   - Add 127.0.0.1 to trusted IPs
   - Set socket port to 7497 (paper) or 7496 (live)
3. **Log in** to your IBKR account

## Step 4: Configure Claude Desktop

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ibkr": {
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["-m", "ibkr_mcp_server.main"],
      "cwd": "C:\\path\\to\\ibkr-mcp-server",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note:** Update the paths to match your installation directory.

## Step 5: Test Connection

1. **Restart Claude Desktop**
2. **Open a new conversation**
3. **Test with these commands:**

```
"Check my IBKR connection status"
→ Should show connected to paper trading account

"Show me my portfolio"
→ Should display your paper trading positions

"Get a quote for Apple stock"
→ Should return real-time AAPL quote
```

## Step 6: Enable Trading (Optional)

⚠️ **Only after successful testing with Step 5**

1. **Edit `.env` file:**
   ```bash
   ENABLE_TRADING=true               # Enable basic trading
   ENABLE_FOREX_TRADING=true         # Enable forex
   ENABLE_INTERNATIONAL_TRADING=true # Enable global stocks
   ENABLE_STOP_LOSS_ORDERS=true      # Enable risk management
   ```

2. **Restart Claude Desktop**

3. **Test trading commands:**
   ```
   "What's the current EUR/USD rate?"
   → Should show live forex rate
   
   "Convert $1000 to Euros"
   → Should perform currency conversion
   
   "Get quotes for Apple, ASML, and Toyota"
   → Should show mixed US/European/Japanese stocks
   
   "Buy 1 share of Apple at current market price"
   → Should place test market order
   
   "Set a limit order for Microsoft at $400"
   → Should place test limit order
   
   "Show me my pending orders"
   → Should display active orders
   
   "Cancel my test orders"
   → Should cancel pending orders
   ```

## Available Tools (23 Total)

Once connected, you have access to:

### **Portfolio & Account**
- View portfolio positions and P&L
- Check account balances in multiple currencies
- Switch between IBKR accounts
- Monitor connection status

### **Market Data**
- Get live quotes for any stock worldwide
- Resolve international symbols to exchanges
- Real-time forex rates for 21 currency pairs

### **Order Placement & Trading**
- Place market orders for immediate execution
- Place limit orders with price control
- Place bracket orders (entry + stop + target)
- Cancel and modify existing orders
- Check order status and execution details

### **Currency & Forex**
- Convert between 29 supported currencies
- Get live forex rates with bid/ask spreads
- Cross-currency calculations

### **Risk Management** (when enabled)
- Place stop loss orders
- Set bracket orders (entry + stop + target)
- Modify and cancel existing orders
- View all risk management positions

## Example Conversations

```
You: "Show me my current portfolio"
Claude: Uses get_portfolio tool to display your positions

You: "What's ASML trading at right now?"
Claude: Uses get_market_data, auto-detects it's Dutch (AEB/EUR)

You: "Convert €5000 to US dollars"
Claude: Uses convert_currency with live EUR/USD rate

You: "Set a stop loss on my Tesla position at $200"
Claude: Uses place_stop_loss (if trading enabled)
```

## Safety Features

The system includes multiple safety layers:

- **Trading Disabled by Default**: Must be explicitly enabled
- **Paper Trading Verification**: Prevents accidental live trading
- **Order Limits**: Configurable size and value restrictions
- **Complete Audit Trail**: Every operation logged
- **Emergency Kill Switch**: Instant trading halt capability

## Next Steps

1. **Explore**: Try different market data queries
2. **Learn**: Read the [Trading Guide](trading.md) for workflows
3. **Practice**: Use paper trading to learn risk management
4. **Advanced**: Check [Examples](../examples/basic-usage.md) for more use cases

## Troubleshooting

**Connection Issues:**
- Verify IB Gateway is running and logged in
- Check port configuration (7497 vs 7496)
- Ensure API is enabled in IB Gateway settings

**Tool Errors:**
- Check safety settings in `.env` file
- Verify account type (paper vs live)
- Review logs for detailed error messages

**Need Help?**
- Check [Troubleshooting Guide](../examples/troubleshooting.md)
- Review [Configuration Reference](../reference/configuration.md)
- See [Common Problems](faq.md)

---

🎉 **Congratulations!** You now have a professional global trading platform integrated with Claude AI.
