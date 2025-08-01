# get_tool_documentation

## Overview
Get comprehensive documentation for any IBKR tool with examples, workflows, and troubleshooting.
Ask about specific tools or entire categories to understand capabilities and usage patterns.
Essential for learning the system and getting the most out of all available tools.

Access detailed documentation including parameter explanations, real-world examples,
step-by-step workflows, common troubleshooting solutions, and related tool suggestions.

## Parameters

**tool_or_category**: Tool name or category to get documentation for (required)
- Specific tools: "get_forex_rates", "place_stop_loss", "get_portfolio"
- Categories: "forex", "stop_loss", "international", "portfolio"
- Case-insensitive: "GET_FOREX_RATES" = "get_forex_rates"

**aspect**: Focus on specific documentation section (optional, defaults to "all")
- "overview" - What the tool does and key capabilities
- "parameters" - Detailed parameter explanations and examples
- "examples" - Real-world usage examples and code snippets  
- "workflow" - Step-by-step processes and best practices
- "troubleshooting" - Common issues and solutions
- "related_tools" - Tools that work well together
- "all" - Complete documentation (default)

## Examples

### Get complete tool documentation
```python
get_tool_documentation("get_forex_rates")
```
Returns comprehensive documentation for forex rates tool

### Learn about a category
```python
get_tool_documentation("stop_loss")
```  
Returns overview of all stop loss management tools and workflows

### Focus on specific aspect
```python
get_tool_documentation("place_stop_loss", "examples")
```
Returns only examples section for stop loss placement

### Troubleshooting focus
```python
get_tool_documentation("get_market_data", "troubleshooting")
```
Returns common issues and solutions for market data

### Workflow guidance
```python
get_tool_documentation("forex", "workflow")
```
Returns step-by-step forex trading workflows

## Workflow

**Learning New Tools:**

1. **Start with overview**: Get high-level understanding of tool capabilities
2. **Study parameters**: Understand required vs optional parameters
3. **Try examples**: Practice with provided code examples
4. **Follow workflows**: Use step-by-step processes for complex operations
5. **Troubleshoot issues**: Reference common problems and solutions

**Category Exploration:**
1. **Browse categories**: Explore "forex", "stop_loss", "international", "portfolio"
2. **Understand relationships**: See how tools work together
3. **Learn workflows**: Master complete processes, not just individual tools
4. **Advanced techniques**: Combine multiple tools for sophisticated strategies

**Problem-Solving Process:**
1. **Check troubleshooting**: Look for your specific issue in documentation
2. **Review examples**: Find similar usage patterns to your needs
3. **Understand workflows**: Ensure you're following recommended processes
4. **Related tools**: Consider if other tools might help solve the problem

## Available Documentation

**Tool Categories:**
- **forex** - Currency trading and conversion tools
- **stop_loss** - Risk management and order protection
- **international** - Global markets and multi-currency trading
- **portfolio** - Account and position management

**Individual Tools:**
- **Market Data**: get_market_data, get_forex_rates, resolve_international_symbol
- **Portfolio**: get_portfolio, get_account_summary, get_accounts, switch_account
- **Risk Management**: place_stop_loss, get_stop_losses, modify_stop_loss, cancel_stop_loss
- **Currency**: convert_currency, get_forex_rates
- **System**: get_connection_status, get_tool_documentation

## Related Tools
This tool helps you learn about all other tools - it's the gateway to understanding
the complete IBKR MCP system. Use it whenever you need help with any functionality.
