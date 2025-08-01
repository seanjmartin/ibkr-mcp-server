"""Enhanced MCP tools for IBKR functionality with Forex, International Markets, and Stop Loss Management."""

import json
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest

from .client import ibkr_client
from .utils import validate_symbols, IBKRError
from .safety_framework import safety_manager


# ============ SAFETY VALIDATION WRAPPER ============

async def safe_trading_operation(operation_type: str, operation_data: dict, operation_func) -> dict:
    """Safety-enhanced trading operation wrapper for all MCP tools."""
    # Pre-flight safety checks
    validation = safety_manager.validate_trading_operation(operation_type, operation_data)
    
    if not validation["is_safe"]:
        return {
            "success": False,
            "error": "Safety validation failed",
            "details": validation["errors"],
            "warnings": validation.get("warnings", [])
        }
    
    # If safety checks pass, execute the operation
    try:
        result = await operation_func()
        
        # Log successful operation
        if hasattr(result, 'get') and result.get('success', True):
            safety_manager.audit_logger.log_system_event("OPERATION_SUCCESS", {
                "operation_type": operation_type,
                "operation_data": operation_data
            })
        
        return result
    except Exception as e:
        # Log failed operation
        safety_manager.audit_logger.log_system_event("OPERATION_FAILED", {
            "operation_type": operation_type,
            "operation_data": operation_data,
            "error": str(e)
        })
        raise


# ============ TRADING OPERATION CLASSIFICATION ============

TRADING_OPERATIONS = {
    # Stop loss management (all require safety validation)
    "place_stop_loss": "order_placement",
    "modify_stop_loss": "order_modification", 
    "cancel_stop_loss": "order_cancellation",
    
    # Account switching (requires account verification)
    "switch_account": "account_operation",
}

# Market data operations (no safety validation needed, but rate limited)
MARKET_DATA_OPERATIONS = {
    "get_market_data": "market_data",
    "get_forex_rates": "market_data", 
    "convert_currency": "market_data",
    "resolve_international_symbol": "market_data",
}

# Safe operations (no validation needed)
SAFE_OPERATIONS = {
    "get_portfolio", "get_account_summary", "get_accounts", "get_connection_status",
    "get_open_orders", "get_completed_orders", "get_executions", "get_stop_losses",
    "get_tool_documentation"
}


# Create the server instance
server = Server("ibkr-mcp")


# Define all tools (6 original + 8 new = 14 total)
TOOLS = [
    # ============ ORIGINAL TOOLS ============
    Tool(
        name="get_portfolio",
        description="View your current stock positions, quantities, and profit/loss across all holdings",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_account_summary", 
        description="Check your account balance, buying power, and key financial metrics",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="switch_account",
        description="Switch between different IBKR accounts if you have multiple accounts",
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Account ID to switch to"}
            },
            "required": ["account_id"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_accounts",
        description="List all available IBKR accounts and see which one is currently active", 
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False}
    ),
    Tool(
        name="get_market_data",
        description="Get live stock prices for any company worldwide - auto-detects exchange/currency or use SYMBOL.EXCHANGE.CURRENCY format to force specific exchange (e.g., ASML.AEB.EUR for Amsterdam, ASML.SMART.USD for US ADR)",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated symbols: simple (AAPL,ASML,7203) for auto-detection, or explicit format (ASML.AEB.EUR,SAP.XETRA.EUR) to force exchange/currency"},
                "auto_detect": {"type": "boolean", "description": "Auto-detect exchange and currency", "default": True}
            },
            "required": ["symbols"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_connection_status",
        description="Check if you're connected to IBKR and view connection details",
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False}
    ),
    
    # ============ FOREX TRADING TOOLS ============
    Tool(
        name="get_forex_rates",
        description="Get live exchange rates for 20+ currency pairs (EURUSD, GBPUSD, USDJPY, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "currency_pairs": {
                    "type": "string", 
                    "description": "Comma-separated forex pairs (e.g., EURUSD,GBPUSD,USDJPY)"
                }
            },
            "required": ["currency_pairs"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="convert_currency",
        description="Convert money between currencies using live exchange rates (USD to EUR, GBP to JPY, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to convert"},
                "from_currency": {"type": "string", "description": "Source currency code (e.g., USD)"},
                "to_currency": {"type": "string", "description": "Target currency code (e.g., EUR)"}
            },
            "required": ["amount", "from_currency", "to_currency"],
            "additionalProperties": False
        }
    ),
    
    # ============ INTERNATIONAL TRADING TOOLS ============

    Tool(
        name="resolve_international_symbol",
        description="Look up which exchange and currency an international stock trades on (finds ASML->AEB/EUR, SAP->XETRA/EUR)",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol to resolve"},
                "exchange": {"type": "string", "description": "Specific exchange code (optional)"},
                "currency": {"type": "string", "description": "Specific currency code (optional)"}
            },
            "required": ["symbol"],
            "additionalProperties": False
        }
    ),
    
    # ============ STOP LOSS MANAGEMENT TOOLS ============
    Tool(
        name="place_stop_loss",
        description="Set automatic sell orders to limit losses - sells your stock if price drops below your chosen level",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"},
                "exchange": {"type": "string", "description": "Exchange code", "default": "SMART"},
                "currency": {"type": "string", "description": "Currency code", "default": "USD"},
                "action": {"type": "string", "description": "Order action (BUY/SELL)", "default": "SELL"},
                "quantity": {"type": "integer", "description": "Number of shares"},
                "stop_price": {"type": "number", "description": "Stop trigger price"},
                "order_type": {"type": "string", "description": "Stop order type (STP/STP LMT/TRAIL)", "default": "STP"},
                "limit_price": {"type": "number", "description": "Limit price for STP LMT orders"},
                "trail_amount": {"type": "number", "description": "Trail amount for TRAIL orders"},
                "trail_percent": {"type": "number", "description": "Trail percentage for TRAIL orders"},
                "time_in_force": {"type": "string", "description": "Time in force (GTC/DAY)", "default": "GTC"}
            },
            "required": ["symbol", "quantity", "stop_price"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_stop_losses",
        description="View all your active stop loss orders and their current status",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID filter"},
                "symbol": {"type": "string", "description": "Symbol filter"},
                "status": {"type": "string", "description": "Order status filter (active/open/all)", "default": "active"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="modify_stop_loss",
        description="Change the trigger price or quantity of an existing stop loss order",
        inputSchema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID to modify"},
                "stop_price": {"type": "number", "description": "New stop price"},
                "quantity": {"type": "integer", "description": "New quantity"},
                "limit_price": {"type": "number", "description": "New limit price (for STP LMT)"},
                "trail_amount": {"type": "number", "description": "New trail amount"},
                "trail_percent": {"type": "number", "description": "New trail percentage"},
                "time_in_force": {"type": "string", "description": "New time in force"}
            },
            "required": ["order_id"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="cancel_stop_loss",
        description="Remove a stop loss order you no longer want",
        inputSchema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID to cancel"}
            },
            "required": ["order_id"],
            "additionalProperties": False
        }
    ),
    
    # ============ ORDER MANAGEMENT TOOLS ============
    Tool(
        name="get_open_orders",
        description="View all your pending orders that haven't been filled yet",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID filter (optional)"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_completed_orders",
        description="View your recently completed trades and transactions",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID filter (optional)"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_executions",
        description="View detailed execution information for your trades",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID filter (optional)"},
                "symbol": {"type": "string", "description": "Symbol filter (optional)"}
            },
            "additionalProperties": False
        }
    ),
    
    # ============ DOCUMENTATION TOOL ============
    Tool(
        name="get_tool_documentation",
        description="Get comprehensive documentation for any IBKR tool with examples, workflows, and troubleshooting. Ask about specific tools ('get_forex_rates') or categories ('forex', 'stop_loss', 'international'). Essential for understanding tool capabilities and parameters.",
        inputSchema={
            "type": "object",
            "properties": {
                "tool_or_category": {
                    "type": "string", 
                    "description": "Tool name (e.g., 'get_forex_rates') or category ('forex', 'stop_loss', 'international', 'portfolio')"
                },
                "aspect": {
                    "type": "string", 
                    "description": "Optional focus: 'overview', 'examples', 'parameters', 'workflow', 'troubleshooting', 'related_tools'",
                    "enum": ["overview", "examples", "parameters", "workflow", "troubleshooting", "related_tools", "all"]
                }
            },
            "required": ["tool_or_category"],
            "additionalProperties": False
        }
    )
]


# Register tools list handler
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


# Register tool call handler with enhanced routing for new tools
@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls with enhanced routing for forex, international, and stop loss tools."""
    try:
        # ============ ORIGINAL TOOLS ============
        if name == "get_portfolio":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_portfolio(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting portfolio: {str(e)}"
                )]
                
        elif name == "get_account_summary":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_account_summary(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting account summary: {str(e)}"
                )]
                
        elif name == "switch_account":
            account_id = arguments["account_id"]
            try:
                # Use safety wrapper for account switching (requires account verification)
                result = await safe_trading_operation(
                    operation_type="account_operation",
                    operation_data=arguments,
                    operation_func=lambda: ibkr_client.switch_account(account_id)
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error switching account: {str(e)}"
                )]
                
        elif name == "get_accounts":
            try:
                result = await ibkr_client.get_accounts()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting accounts: {str(e)}"
                )]
                
        elif name == "get_market_data":
            symbols = arguments["symbols"]
            auto_detect = arguments.get("auto_detect", True)
            try:
                # Check rate limits for market data requests
                if not safety_manager.rate_limiter.check_rate_limit("market_data"):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": "Rate limit exceeded for market data requests",
                            "details": "Too many market data requests in the last minute"
                        }, indent=2)
                    )]
                
                result = await ibkr_client.get_market_data(symbols, auto_detect)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting market data: {str(e)}"
                )]
                
        elif name == "get_connection_status":
            try:
                result = await ibkr_client.get_connection_status()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting connection status: {str(e)}"
                )]
                
        elif name == "get_open_orders":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_open_orders(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting open orders: {str(e)}"
                )]
        
        # ============ FOREX TRADING TOOLS ============
        elif name == "get_forex_rates":
            currency_pairs = arguments["currency_pairs"]
            try:
                # Check rate limits for forex data requests
                if not safety_manager.rate_limiter.check_rate_limit("market_data"):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": "Rate limit exceeded for forex data requests",
                            "details": "Too many market data requests in the last minute"
                        }, indent=2)
                    )]
                
                result = await ibkr_client.get_forex_rates(currency_pairs)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting forex rates: {str(e)}"
                )]
                
        elif name == "convert_currency":
            amount = arguments["amount"]
            from_currency = arguments["from_currency"]
            to_currency = arguments["to_currency"]
            try:
                result = await ibkr_client.convert_currency(amount, from_currency, to_currency)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error converting currency: {str(e)}"
                )]
        
        # ============ INTERNATIONAL TRADING TOOLS ============

        elif name == "resolve_international_symbol":
            symbol = arguments["symbol"]
            exchange = arguments.get("exchange")
            currency = arguments.get("currency")
            try:
                result = await ibkr_client.resolve_international_symbol(symbol, exchange, currency)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error resolving international symbol: {str(e)}"
                )]
        
        # ============ STOP LOSS MANAGEMENT TOOLS ============
        elif name == "place_stop_loss":
            try:
                # Use safety wrapper for stop loss placement
                result = await safe_trading_operation(
                    operation_type="stop_loss_placement",
                    operation_data=arguments,
                    operation_func=lambda: ibkr_client.place_stop_loss(**arguments)
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error placing stop loss: {str(e)}"
                )]
                
        elif name == "get_stop_losses":
            account = arguments.get("account")
            symbol = arguments.get("symbol")
            status = arguments.get("status", "active")
            try:
                result = await ibkr_client.get_stop_losses(account, symbol, status)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting stop losses: {str(e)}"
                )]
                
        elif name == "modify_stop_loss":
            order_id = arguments["order_id"]
            changes = {k: v for k, v in arguments.items() if k != "order_id"}
            try:
                # Use safety wrapper for stop loss modification
                result = await safe_trading_operation(
                    operation_type="order_modification",
                    operation_data=arguments,
                    operation_func=lambda: ibkr_client.modify_stop_loss(order_id, **changes)
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error modifying stop loss: {str(e)}"
                )]
                
        elif name == "cancel_stop_loss":
            order_id = arguments["order_id"]
            try:
                # Use safety wrapper for stop loss cancellation
                result = await safe_trading_operation(
                    operation_type="order_cancellation",
                    operation_data=arguments,
                    operation_func=lambda: ibkr_client.cancel_stop_loss(order_id)
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error cancelling stop loss: {str(e)}"
                )]
        
        elif name == "get_completed_orders":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_completed_orders(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting completed orders: {str(e)}"
                )]
                
        elif name == "get_executions":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_executions(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting trade executions: {str(e)}"
                )]
        
        # ============ DOCUMENTATION TOOL ============
        elif name == "get_tool_documentation":
            try:
                from .documentation.doc_processor import doc_processor
                
                tool_or_category = arguments.get('tool_or_category', '').strip()
                aspect = arguments.get('aspect', 'all').strip()
                
                if not tool_or_category:
                    return [TextContent(
                        type="text",
                        text="Please specify a tool name or category. Examples: 'get_forex_rates', 'forex', 'stop_loss'"
                    )]
                
                documentation = doc_processor.get_documentation(tool_or_category, aspect)
                
                return [TextContent(type="text", text=documentation)]
                
            except Exception as e:
                return [TextContent(
                    type="text", 
                    text=f"Documentation error: {str(e)}"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]
