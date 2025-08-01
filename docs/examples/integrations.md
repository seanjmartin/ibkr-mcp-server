# Integration Examples

Examples of integrating the IBKR MCP Server with external systems and custom workflows.

## Overview

This guide demonstrates how to integrate IBKR MCP Server capabilities with other systems, create custom workflows, and build automated trading applications. These examples are for advanced users familiar with programming and system integration.

## Claude Desktop Integration Patterns

### Multi-Tool Workflow Integration

**Objective:** Combine IBKR trading with other Claude tools for comprehensive analysis

```
Investment Research Workflow:
1. "Search the web for recent news about ASML semiconductor outlook"
2. "Check ASML current stock price and 52-week range" (IBKR)
3. "Get EUR/USD rate for currency impact analysis" (IBKR)
4. "Search my Google Drive for ASML research notes"
5. "Set a price alert stop loss if I decide to buy ASML" (IBKR)

Portfolio Review Workflow:
1. "Check my Google Calendar for portfolio review meeting"
2. "Show me my current IBKR portfolio performance" (IBKR)
3. "Create a portfolio summary document in Google Docs"
4. "Set up stop losses on underperforming positions" (IBKR)
5. "Schedule follow-up calendar reminder"
```

### Document-Driven Trading

**Objective:** Use documents to drive trading decisions

```
Research-Based Trading:
1. "Analyze my investment thesis document from Google Drive"
2. "Get current quotes for stocks mentioned in the thesis" (IBKR)
3. "Compare actual performance vs thesis predictions"
4. "Update stop losses based on revised outlook" (IBKR)
5. "Create updated research summary in Google Docs"

Financial Planning Integration:
1. "Review my financial planning spreadsheet from Google Drive"
2. "Check current portfolio value and allocation" (IBKR)
3. "Calculate rebalancing needs based on target allocation"
4. "Convert international positions to USD for planning" (IBKR)
5. "Update planning document with current values"
```

## Custom Application Integration

### Python Integration Example

**Objective:** Build custom Python application using IBKR data

```python
# Custom Portfolio Analyzer
import subprocess
import json
import pandas as pd

class IBKRPortfolioAnalyzer:
    def __init__(self):
        self.claude_command = ["claude-desktop-cli"]  # Hypothetical CLI
    
    def get_portfolio_data(self):
        """Get current portfolio from IBKR via Claude"""
        result = subprocess.run(
            self.claude_command + ["Show me my detailed portfolio with all positions"],
            capture_output=True,
            text=True
        )
        # Parse Claude's response to extract portfolio data
        return self.parse_portfolio_response(result.stdout)
    
    def get_forex_rates(self, currency_pairs):
        """Get current forex rates"""
        pairs_str = ",".join(currency_pairs)
        result = subprocess.run(
            self.claude_command + [f"Get forex rates for {pairs_str}"],
            capture_output=True,
            text=True
        )
        return self.parse_forex_response(result.stdout)
    
    def calculate_currency_exposure(self):
        """Calculate total currency exposure"""
        portfolio = self.get_portfolio_data()
        forex_rates = self.get_forex_rates(["EURUSD", "GBPUSD", "USDJPY"])
        
        # Convert all positions to USD
        usd_values = {}
        for position in portfolio:
            if position['currency'] == 'USD':
                usd_values[position['symbol']] = position['market_value']
            else:
                # Convert using forex rates
                rate = forex_rates.get(f"{position['currency']}USD", 1.0)
                usd_values[position['symbol']] = position['market_value'] * rate
        
        return usd_values
    
    def generate_risk_report(self):
        """Generate comprehensive risk analysis"""
        exposure = self.calculate_currency_exposure()
        
        # Calculate position sizes as % of portfolio
        total_value = sum(exposure.values())
        position_weights = {k: v/total_value for k, v in exposure.items()}
        
        # Identify risk concentrations
        large_positions = {k: v for k, v in position_weights.items() if v > 0.1}
        
        return {
            'total_portfolio_usd': total_value,
            'position_weights': position_weights,
            'concentration_risk': large_positions,
            'currency_breakdown': self.calculate_currency_breakdown()
        }

# Usage Example
analyzer = IBKRPortfolioAnalyzer()
risk_report = analyzer.generate_risk_report()
print(f"Portfolio Value: ${risk_report['total_portfolio_usd']:,.2f}")
print(f"Large Positions: {risk_report['concentration_risk']}")
```

### Excel/Spreadsheet Integration

**Objective:** Connect IBKR data to Excel for advanced analysis

```vba
' VBA Example for Excel Integration
Sub UpdatePortfolioData()
    Dim claudeResponse As String
    Dim portfolioData As Variant
    
    ' Call Claude Desktop with IBKR command
    claudeResponse = CallClaude("Show me my portfolio with current values")
    
    ' Parse response and update Excel cells
    portfolioData = ParsePortfolioResponse(claudeResponse)
    
    ' Update portfolio worksheet
    Dim ws As Worksheet
    Set ws = Worksheets("Portfolio")
    
    ' Clear existing data
    ws.Range("A2:F100").Clear
    
    ' Fill with new data
    Dim i As Integer
    For i = 0 To UBound(portfolioData)
        ws.Cells(i + 2, 1) = portfolioData(i)("Symbol")
        ws.Cells(i + 2, 2) = portfolioData(i)("Quantity")
        ws.Cells(i + 2, 3) = portfolioData(i)("Price")
        ws.Cells(i + 2, 4) = portfolioData(i)("MarketValue")
        ws.Cells(i + 2, 5) = portfolioData(i)("PnL")
        ws.Cells(i + 2, 6) = portfolioData(i)("Currency")
    Next i
    
    ' Update timestamp
    ws.Range("H1") = "Last Updated: " & Now()
End Sub

Function CallClaude(command As String) As String
    ' Implementation depends on how you interface with Claude Desktop
    ' This could be through COM, file I/O, or HTTP API
    ' Return the response from Claude
End Function
```

## Automated Trading Systems

### Systematic Momentum Strategy

**Objective:** Build automated momentum-based trading system

```
Daily Automation Workflow:

Morning Routine (9:00 AM EST):
1. "Check my IBKR connection and account status"
2. "Get quotes for my momentum universe: AAPL, MSFT, GOOGL, AMZN, TSLA"
3. "Calculate 20-day performance for each stock"
4. "Rank stocks by momentum strength"

Position Management (9:30 AM EST):
5. "Review my current momentum positions"
6. "Check if any positions have fallen below momentum threshold"
7. "Set stop losses on any new momentum positions"
8. "Update trailing stops based on new highs"

Risk Management (Throughout Day):
9. "Monitor portfolio for any stop loss triggers"
10. "Check if daily trading limits are being approached"
11. "Verify total position size stays within risk limits"

End of Day (4:00 PM EST):
12. "Review day's trading performance"
13. "Update stop loss levels based on closing prices"
14. "Prepare momentum rankings for next day"
```

### International Market Rotation

**Objective:** Rotate capital between global markets based on performance

```
Weekly Market Analysis:

Step 1: Global Market Assessment
"Get quotes for regional representatives:
- US: SPY equivalent positions
- Europe: ASML, SAP, NESN
- Asia: 7203, 005930, 00700"

Step 2: Currency Impact Analysis
"Get forex rates: EUR/USD, USD/JPY, USD/CHF"
"Calculate currency-adjusted returns for each region"

Step 3: Relative Strength Ranking
"Compare regional performance over 1-month, 3-month periods"
"Identify strongest and weakest regions"

Step 4: Rotation Decision
"Overweight strongest region by 10%"
"Underweight weakest region by 10%"
"Maintain neutral weight on middle performer"

Step 5: Implementation
"Calculate required position adjustments"
"Set stop losses on new positions"
"Monitor currency hedging needs"
```

## Risk Management Automation

### Dynamic Stop Loss System

**Objective:** Automatically adjust stop losses based on market conditions

```
Volatility-Adjusted Stop Loss System:

Daily Volatility Assessment:
1. "Get quotes for VIX or volatility indicators"
2. "Calculate current volatility vs historical average"
3. "Determine volatility regime (low/normal/high)"

Stop Loss Adjustment Rules:
4. Low Volatility (VIX < 15): "Use 8% stop losses"
5. Normal Volatility (VIX 15-25): "Use 12% stop losses"  
6. High Volatility (VIX > 25): "Use 15% stop losses"

Implementation:
7. "Show me all current stop loss orders"
8. "Modify stop losses based on new volatility regime"
9. "Set new stop losses on unprotected positions"

Monitoring:
10. "Check for any triggered stops during market hours"
11. "Adjust stops if volatility regime changes intraday"
12. "Review stop loss effectiveness weekly"
```

### Portfolio Heat Map System

**Objective:** Visual portfolio risk monitoring and alerts

```
Risk Monitoring Dashboard:

Position Size Analysis:
1. "Show me my portfolio with position sizes"
2. "Identify positions > 10% of portfolio"
3. "Calculate concentration risk metrics"

Sector Concentration:
4. "Analyze my portfolio by sector"
5. "Identify over-concentrations (>25% in any sector)"
6. "Flag sector rotation opportunities"

Currency Risk:
7. "Convert all positions to USD equivalent"
8. "Calculate total currency exposure by currency"
9. "Assess currency hedging needs"

Geographic Diversification:
10. "Break down portfolio by country/region"
11. "Identify geographic concentration risks"
12. "Monitor geopolitical risk factors"

Alert System:
13. "If any position >15%: Alert for rebalancing"
14. "If sector >30%: Alert for diversification"
15. "If currency exposure >40%: Alert for hedging"
```

## Data Export and Analysis

### Portfolio Analytics Export

**Objective:** Export IBKR data for external analysis

```
Data Collection Workflow:

1. Portfolio Data Export:
"Show me detailed portfolio with all metrics"
[Export to CSV/JSON format for analysis]

2. Historical Performance:
"Get performance data for all positions"
[Track over time for trend analysis]

3. Risk Metrics:
"Calculate portfolio beta, volatility, Sharpe ratio"
[Export for risk management analysis]

4. Currency Analysis:
"Get all forex rates affecting my portfolio"
[Export for currency impact analysis]

5. Transaction History:
"Show me all trades and executions for this month"
[Export for performance attribution]
```

### Custom Reporting System

**Objective:** Generate automated portfolio reports

```
Monthly Portfolio Report Generation:

Executive Summary:
1. "Portfolio value and monthly performance"
2. "Top winners and losers for the month"
3. "Currency impact on total returns"

Detailed Analysis:
4. "Position-by-position performance breakdown"
5. "Risk metrics and concentration analysis"
6. "Stop loss effectiveness review"

Market Context:
7. "Compare portfolio performance to market indices"
8. "Analyze international market contributions"
9. "Review forex impact on international positions"

Forward Looking:
10. "Current stop loss protection levels"
11. "Upcoming earnings and events for holdings"
12. "Rebalancing recommendations"
```

## API Integration Patterns

### RESTful API Wrapper

**Objective:** Create REST API wrapper around IBKR MCP functionality

```python
# Flask API Example
from flask import Flask, jsonify, request
import subprocess
import json

app = Flask(__name__)

class IBKRMCPWrapper:
    def __init__(self):
        self.claude_cmd = ["claude-desktop-cli"]  # Hypothetical
    
    def execute_ibkr_command(self, command):
        """Execute IBKR command via Claude and return structured response"""
        try:
            result = subprocess.run(
                self.claude_cmd + [command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return self.parse_response(result.stdout)
        except Exception as e:
            return {"error": str(e)}

ibkr = IBKRMCPWrapper()

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio positions"""
    response = ibkr.execute_ibkr_command("Show me my current portfolio")
    return jsonify(response)

@app.route('/api/quotes/<symbols>', methods=['GET'])
def get_quotes(symbols):
    """Get quotes for specified symbols"""
    command = f"Get quotes for {symbols}"
    response = ibkr.execute_ibkr_command(command)
    return jsonify(response)

@app.route('/api/forex/<pairs>', methods=['GET'])
def get_forex_rates(pairs):
    """Get forex rates for specified pairs"""
    command = f"Get forex rates for {pairs}"
    response = ibkr.execute_ibkr_command(command)
    return jsonify(response)

@app.route('/api/stop-loss', methods=['POST'])
def place_stop_loss():
    """Place stop loss order"""
    data = request.json
    symbol = data.get('symbol')
    price = data.get('price')
    command = f"Set a stop loss on {symbol} at ${price}"
    response = ibkr.execute_ibkr_command(command)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Webhook Integration

**Objective:** Respond to external events with IBKR actions

```python
# Webhook Handler Example
from flask import Flask, request
import hmac
import hashlib
import json

app = Flask(__name__)

@app.route('/webhook/price-alert', methods=['POST'])
def handle_price_alert():
    """Handle price alerts from external systems"""
    data = request.json
    
    # Verify webhook signature (security)
    signature = request.headers.get('X-Signature')
    if not verify_signature(data, signature):
        return "Unauthorized", 401
    
    # Extract alert data
    symbol = data.get('symbol')
    price = data.get('current_price')
    alert_type = data.get('alert_type')
    
    # Execute appropriate IBKR action
    if alert_type == 'stop_loss_trigger':
        command = f"Check my {symbol} stop loss orders"
        response = execute_ibkr_command(command)
    
    elif alert_type == 'buy_signal':
        command = f"Get quote for {symbol} and check buying power"
        response = execute_ibkr_command(command)
    
    elif alert_type == 'volatility_spike':
        command = f"Tighten stop losses due to volatility in {symbol}"
        response = execute_ibkr_command(command)
    
    return jsonify({"status": "processed", "response": response})

@app.route('/webhook/economic-event', methods=['POST'])
def handle_economic_event():
    """Handle economic calendar events"""
    data = request.json
    
    event_type = data.get('event_type')
    impact = data.get('impact')  # high/medium/low
    
    if event_type == 'fed_meeting' and impact == 'high':
        # Implement risk-off procedures
        commands = [
            "Check my portfolio risk exposure",
            "Review stop loss protection levels",
            "Consider activating emergency protocols if needed"
        ]
        
        responses = []
        for command in commands:
            response = execute_ibkr_command(command)
            responses.append(response)
        
        return jsonify({"status": "risk_management_executed", "responses": responses})
    
    return jsonify({"status": "event_noted"})

def verify_signature(data, signature):
    """Verify webhook signature for security"""
    secret = "your_webhook_secret"
    computed_signature = hmac.new(
        secret.encode(),
        json.dumps(data).encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, computed_signature)

def execute_ibkr_command(command):
    """Execute IBKR command via Claude integration"""
    # Implementation depends on your Claude integration method
    pass
```

## Performance Monitoring Integration

### System Health Dashboard

**Objective:** Monitor IBKR MCP Server health and performance

```
Health Check System:

Connection Monitoring:
1. "Check IBKR connection status every 5 minutes"
2. "Alert if connection drops"
3. "Auto-reconnect attempts"
4. "Log connection stability metrics"

Performance Tracking:
5. "Monitor response times for market data requests"
6. "Track order execution latencies"
7. "Measure system resource usage"
8. "Alert on performance degradation"

Safety System Monitoring:
9. "Check kill switch status"
10. "Monitor daily trading limits usage"
11. "Track safety violations and patterns"
12. "Alert on unusual safety events"

Portfolio Health:
13. "Monitor total portfolio value changes"
14. "Track stop loss coverage percentage"
15. "Alert on large position movements"
16. "Check currency exposure changes"
```

### Logging and Analytics Integration

**Objective:** Integrate with logging and analytics systems

```python
# Logging Integration Example
import logging
import json
from datetime import datetime

class IBKRAnalyticsLogger:
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Configure structured logging for IBKR operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ibkr_analytics.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IBKRAnalytics')
    
    def log_trade_decision(self, symbol, action, reasoning):
        """Log trading decisions for analysis"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'trade_decision',
            'symbol': symbol,
            'action': action,
            'reasoning': reasoning,
            'portfolio_value': self.get_portfolio_value()
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_risk_event(self, event_type, details):
        """Log risk management events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'risk_event',
            'risk_event_type': event_type,
            'details': details,
            'portfolio_risk_metrics': self.get_risk_metrics()
        }
        self.logger.warning(json.dumps(log_entry))
    
    def log_performance_metrics(self):
        """Log daily performance metrics"""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'performance_metrics',
            'portfolio_value': self.get_portfolio_value(),
            'daily_pnl': self.get_daily_pnl(),
            'positions_count': self.get_positions_count(),
            'stop_loss_coverage': self.get_stop_loss_coverage()
        }
        self.logger.info(json.dumps(metrics))
    
    def get_portfolio_value(self):
        """Get current portfolio value via IBKR"""
        # Implementation to call IBKR via Claude
        pass
    
    def get_risk_metrics(self):
        """Calculate current risk metrics"""
        # Implementation to calculate risk metrics
        pass
```

## Best Practices for Integration

### Security Considerations

1. **API Security:**
   - Use secure authentication for external APIs
   - Implement rate limiting to prevent abuse
   - Validate all inputs and sanitize outputs
   - Use HTTPS for all external communications

2. **Trading Security:**
   - Implement additional confirmation for large trades
   - Use paper trading for testing integrations
   - Maintain audit logs of all automated actions
   - Implement circuit breakers for automated systems

3. **Data Protection:**
   - Encrypt sensitive trading data
   - Secure API keys and credentials
   - Implement access controls
   - Regular security audits

### Error Handling and Resilience

1. **Robust Error Handling:**
   - Graceful degradation when services unavailable
   - Retry mechanisms with exponential backoff
   - Comprehensive error logging
   - Alerting on critical failures

2. **System Resilience:**
   - Health checks and monitoring
   - Automatic failover mechanisms
   - Data validation and integrity checks
   - Regular backup and recovery testing

### Testing and Validation

1. **Integration Testing:**
   - Test all integration points thoroughly
   - Use paper trading for financial operations
   - Validate data accuracy and completeness
   - Performance testing under load

2. **Continuous Monitoring:**
   - Real-time system health monitoring
   - Performance metrics tracking
   - Error rate monitoring
   - User experience metrics

---

**Important:** These integration examples are for educational purposes and demonstrate the flexibility of the IBKR MCP Server. Always thoroughly test integrations in paper trading mode before deploying to live trading environments. Consider the security, reliability, and regulatory implications of any automated trading system.
