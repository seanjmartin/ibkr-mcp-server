# Claude Desktop User Testing - Quick Start Checklist

## Pre-Testing Setup (5 minutes)

### 1. Verify IBKR Paper Account Setup
- [ ] IB Gateway running and logged into paper account (DU* prefix)
- [ ] API enabled (ActiveX and Socket Clients checked)
- [ ] Port 7497 configured for paper trading
- [ ] Trusted IP 127.0.0.1 added

### 2. Configure Claude Desktop
**Option A - Automated Setup:**
```bash
# Run the setup script from project root
scripts\setup-claude-desktop.bat
```

**Option B - Manual Setup:**
- [ ] Edit `%APPDATA%\Claude\claude_desktop_config.json`
- [ ] Add IBKR MCP server configuration (see guide)
- [ ] Verify Python path and project directory

### 3. Restart Claude Desktop
- [ ] Close Claude Desktop completely
- [ ] Reopen Claude Desktop
- [ ] Open new conversation

## Initial Testing (10 minutes)

### Basic Connection Tests
```
1. "Check my IBKR connection status"
   Expected: Paper trading connection, DU* account

2. "Show me all my IBKR accounts"  
   Expected: List of accounts with current marked

3. "Show me my current portfolio"
   Expected: Portfolio display (may be empty)

4. "What's my account balance?"
   Expected: Account balances in multiple currencies
```

### Market Data Tests  
```
5. "What's Apple trading at right now?"
   Expected: Real-time AAPL quote with prices

6. "Get quotes for Apple, ASML, and Toyota"
   Expected: Mixed US/EU/Asian markets with auto-detection

7. "What's the EUR/USD rate?"
   Expected: Live forex rate with bid/ask
```

## Trading Tests (15 minutes)

### Order Placement
```
8. "Buy 5 shares of Apple at current market price"
   Expected: Market order executed, order ID returned

9. "Place a limit order to buy 3 shares of Microsoft at $400"
   Expected: Limit order placed, working status

10. "Show me my pending orders"
    Expected: List of open orders with details
```

### Order Management
```
11. "Cancel my Microsoft limit order"
    Expected: Order cancelled successfully

12. "Check the status of my Apple order"
    Expected: Order status with execution details
```

### Risk Management
```
13. "Set a stop loss on my Apple position at $170"
    Expected: Stop loss order placed

14. "Show me all my stop loss orders"
    Expected: Active stop orders with protection levels
```

## Advanced Features (10 minutes)

### International Trading
```
15. "Get quote for ASML"
    Expected: Dutch stock (AEB/EUR) with auto-detection

16. "Where does ASML trade?"
    Expected: Exchange and currency information
```

### Currency Operations
```
17. "Convert $1000 to Euros"
    Expected: Currency conversion with live rates

18. "Show me major forex pairs"  
    Expected: List of major currency pairs with rates
```

### Portfolio Management
```
19. "Show me my portfolio performance"
    Expected: Updated portfolio with new positions

20. "What's my total account value?"
    Expected: Comprehensive account summary
```

## Success Criteria

### ✅ Technical Success
- [ ] All commands execute without errors
- [ ] Real-time data appears current and accurate
- [ ] Orders execute in paper account
- [ ] Safety limits are enforced (max 10 shares, $500 value)
- [ ] Response times under 10 seconds

### ✅ User Experience Success  
- [ ] Natural language commands work intuitively
- [ ] Error messages are clear and helpful
- [ ] System feels responsive and professional
- [ ] Trading workflow feels natural
- [ ] Safety features provide confidence

## Troubleshooting Quick Fixes

### Connection Issues
```
"Check my IBKR connection status"
→ If failed: Restart IB Gateway, verify API settings
```

### Order Issues  
```
→ If rejected: Check order size (max 10 shares)
→ If too large: Check order value (max $500)
→ If account error: Verify paper account (DU prefix)
```

### Tool Access Issues
```
→ If tools not available: Restart Claude Desktop
→ If still issues: Check claude_desktop_config.json syntax
```

## What You're Testing

This tests the **complete end-user experience**:
- Real Claude Desktop integration
- Actual IBKR paper account trading  
- All 23 MCP tools through natural language
- Safety framework protection
- Error handling and recovery

## Key Differences from Automated Tests

| Automated Tests | User Testing |
|----------------|--------------|
| Tests individual functions | Tests complete user workflows |
| Uses test mocks | Uses real IBKR API |
| Validates technical correctness | Validates user experience |
| Checks error codes | Checks error messages |
| Performance benchmarks | Usability assessment |

## Time Investment

- **Setup:** 5 minutes
- **Basic Testing:** 10 minutes  
- **Trading Tests:** 15 minutes
- **Advanced Features:** 10 minutes
- **Total:** ~40 minutes for comprehensive testing

## Expected Outcomes

After successful testing:
- ✅ Confidence in real-world user experience
- ✅ Validation of natural language trading
- ✅ Proof of safety framework effectiveness  
- ✅ Identification of any UX improvements needed
- ✅ Ready for live trading deployment consideration

---

**Remember:** You're testing with real paper money - orders will execute in your IBKR account, but with virtual funds only.
