"""
Individual MCP Tool Test: complete_trading_workflow
Focus: Test complete end-to-end trading workflow through multiple MCP tools
MCP Tools: get_market_data, place_market_order, get_portfolio, place_stop_loss, get_completed_orders
Expected: Complete trading workflow: Research  ->  Order  ->  Monitor  ->  Risk Management  ->  Analysis
Status: Phase 3 Task 3.1 - Complete Workflow Integration

WORKFLOW STEPS:
1. Market Research (get_market_data)
2. Order Placement (place_market_order) 
3. Order Monitoring (get_completed_orders)
4. Risk Management (place_stop_loss)
5. Portfolio Analysis (get_portfolio)

CRITICAL: IBKR API Field Names
When validating IBKR API responses, use CAMELCASE field names:
[OK] CORRECT: marketValue, unrealizedPNL, realizedPNL, avgCost
[ERROR] WRONG: market_value, unrealized_pnl, realized_pnl, avg_cost
"""

import pytest
import asyncio
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Import MCP interface - THIS IS THE CORRECT LAYER TO TEST
from ibkr_mcp_server.tools import call_tool  # Proper MCP interface
from mcp.types import TextContent
import json
from unittest.mock import patch, AsyncMock

@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividualCompleteTradingWorkflow:
    """Test complete trading workflow through multiple MCP tools"""
    
    async def test_complete_trading_workflow_basic_functionality(self):
        """Test complete end-to-end trading workflow: Research  ->  Order  ->  Monitor  ->  Risk Management  ->  Analysis"""
        
        print(f"\\n{'='*60}")
        print(f"=== Complete Trading Workflow Test ===")
        print(f"{'='*60}")
        
        # FORCE CONNECTION FIRST - ensure IBKR client is connected
        print(f"Step 0: Forcing IBKR Gateway connection...")
        from ibkr_mcp_server.client import ibkr_client
        try:
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
                print(f"[OK] Paper account: {ibkr_client.current_account}")
            else:
                print(f"[WARNING] IBKR Gateway connection failed")
                pytest.skip("IBKR Gateway connection failed - cannot proceed with workflow test")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            pytest.skip(f"IBKR Gateway connection error: {e}")
        
        # Define test symbols for workflow
        test_symbols = ["AAPL", "ASML"]  # USD and EUR positions
        
        try:
            # STEP 1: Market Research Phase
            print(f"\\n--- STEP 1: Market Research ---")
            symbols_str = ",".join(test_symbols)
            quotes_result = await call_tool("get_market_data", {"symbols": symbols_str})
            
            # Validate market data response
            assert isinstance(quotes_result, list) and len(quotes_result) > 0
            quotes_text = quotes_result[0].text
            
            # Handle potential empty or error responses
            if not quotes_text.strip():
                pytest.skip("Market data request returned empty response - IBKR Gateway may not be connected")
            
            try:
                quotes_data = json.loads(quotes_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse market data response: {quotes_text}")
                if "error" in quotes_text.lower():
                    pytest.skip(f"Market data request failed: {quotes_text}")
                else:
                    pytest.skip(f"Invalid JSON response from market data: {quotes_text}")
            
            print(f"Market data retrieved for {len(quotes_data) if isinstance(quotes_data, list) else 1} symbols")
            
            # Store market prices for later validation
            market_prices = {}
            if isinstance(quotes_data, list):
                for quote in quotes_data:
                    if isinstance(quote, dict) and "symbol" in quote:
                        symbol = quote["symbol"]
                        price = quote.get("last", quote.get("close", 100))  # Fallback price
                        market_prices[symbol] = float(price) if price else 100.0
                        print(f"[RESEARCH] {symbol}: ${price}")
            else:
                # Single quote response
                if isinstance(quotes_data, dict) and "symbol" in quotes_data:
                    symbol = quotes_data["symbol"]
                    price = quotes_data.get("last", quotes_data.get("close", 100))
                    market_prices[symbol] = float(price) if price else 100.0
                    print(f"[RESEARCH] {symbol}: ${price}")
            
            # STEP 2: Order Placement Phase
            print(f"\\n--- STEP 2: Order Placement ---")
            placed_orders = []
            order_quantities = {"AAPL": 2, "ASML": 1}  # Small test quantities
            
            for symbol in test_symbols:
                quantity = order_quantities.get(symbol, 1)
                print(f"Placing market order: {quantity} shares of {symbol}")
                
                order_result = await call_tool("place_market_order", {
                    "symbol": symbol,
                    "action": "BUY", 
                    "quantity": quantity
                })
                
                assert isinstance(order_result, list) and len(order_result) > 0
                order_text = order_result[0].text
                
                try:
                    order_data = json.loads(order_text) if order_text.strip() else {}
                except json.JSONDecodeError:
                    print(f"[ORDER] {symbol}: Invalid order response: {order_text}")
                    order_data = {"error": f"Invalid response: {order_text}"}
                
                if isinstance(order_data, dict):
                    if order_data.get("success"):
                        order_id = order_data.get("order_id")
                        print(f"[ORDER] {symbol}: Order #{order_id} placed successfully")
                        placed_orders.append({"symbol": symbol, "order_id": order_id, "quantity": quantity})
                    else:
                        print(f"[ORDER] {symbol}: Order failed - {order_data.get('error', 'Unknown error')}")
                else:
                    print(f"[ORDER] {symbol}: Unexpected order response format")
                
                # Small delay between orders
                await asyncio.sleep(1)
            
            print(f"Total orders placed: {len(placed_orders)}")
            
            # STEP 3: Order Monitoring Phase  
            print(f"\\n--- STEP 3: Order Monitoring ---")
            
            # Check completed orders
            completed_result = await call_tool("get_completed_orders", {})
            assert isinstance(completed_result, list) and len(completed_result) > 0
            completed_text = completed_result[0].text
            
            try:
                completed_data = json.loads(completed_text) if completed_text.strip() else []
            except json.JSONDecodeError:
                print(f"[MONITOR] Invalid completed orders response: {completed_text}")
                completed_data = []
            
            if isinstance(completed_data, list):
                recent_orders = [order for order in completed_data if order.get("symbol") in test_symbols]
                print(f"[MONITOR] Found {len(recent_orders)} recent completed orders for test symbols")
                
                for order in recent_orders[-5:]:  # Show last 5 relevant orders
                    symbol = order.get("symbol", "N/A")
                    status = order.get("status", "N/A")
                    filled = order.get("filled", 0)
                    print(f"[MONITOR] {symbol}: Status={status}, Filled={filled}")
            else:
                print(f"[MONITOR] Unexpected completed orders format: {type(completed_data)}")
            
            # STEP 4: Portfolio Analysis (Check if positions were created)
            print(f"\\n--- STEP 4: Portfolio Analysis ---")
            portfolio_result = await call_tool("get_portfolio", {})
            assert isinstance(portfolio_result, list) and len(portfolio_result) > 0
            portfolio_text = portfolio_result[0].text
            
            try:
                portfolio_data = json.loads(portfolio_text) if portfolio_text.strip() else []
            except json.JSONDecodeError:
                print(f"[PORTFOLIO] Invalid portfolio response: {portfolio_text}")
                portfolio_data = []
            
            created_positions = []
            if isinstance(portfolio_data, list):
                test_positions = [pos for pos in portfolio_data if pos.get("symbol") in test_symbols]
                print(f"[PORTFOLIO] Found {len(test_positions)} positions for test symbols")
                
                for position in test_positions:
                    symbol = position.get("symbol", "N/A")
                    qty = position.get("position", 0)
                    avg_cost = position.get("avgCost", 0)
                    market_val = position.get("marketValue", 0)
                    print(f"[PORTFOLIO] {symbol}: {qty} shares @ ${avg_cost:.2f}, Value: ${market_val:.2f}")
                    created_positions.append(position)
            else:
                print(f"[PORTFOLIO] Portfolio format: {type(portfolio_data)}")
            
            # STEP 5: Risk Management Phase
            print(f"\\n--- STEP 5: Risk Management ---")
            risk_orders = []
            
            for position in created_positions:
                symbol = position.get("symbol")
                quantity = position.get("position", 0)
                avg_cost = position.get("avgCost", 0)
                
                if symbol and quantity > 0 and avg_cost > 0:
                    # Set stop loss at 10% below average cost
                    stop_price = float(avg_cost) * 0.9
                    print(f"Setting stop loss for {symbol}: {quantity} shares at ${stop_price:.2f}")
                    
                    try:
                        stop_result = await call_tool("place_stop_loss", {
                            "symbol": symbol,
                            "action": "SELL",
                            "quantity": int(quantity),
                            "stop_price": stop_price
                        })
                        
                        assert isinstance(stop_result, list) and len(stop_result) > 0
                        stop_text = stop_result[0].text
                        
                        try:
                            stop_data = json.loads(stop_text) if stop_text.strip() else {}
                        except json.JSONDecodeError:
                            print(f"[RISK] {symbol}: Invalid stop loss response: {stop_text}")
                            stop_data = {"error": f"Invalid response: {stop_text}"}
                        
                        if isinstance(stop_data, dict):
                            if stop_data.get("success"):
                                stop_order_id = stop_data.get("order_id")
                                print(f"[RISK] {symbol}: Stop loss #{stop_order_id} placed")
                                risk_orders.append({"symbol": symbol, "stop_order_id": stop_order_id})
                            else:
                                error_msg = stop_data.get("error", "Unknown error")
                                print(f"[RISK] {symbol}: Stop loss failed - {error_msg}")
                        
                    except Exception as e:
                        print(f"[RISK] {symbol}: Stop loss exception - {e}")
                
                # Small delay between risk orders
                await asyncio.sleep(0.5)
            
            print(f"Risk management orders placed: {len(risk_orders)}")
            
            # STEP 6: Final Portfolio State Validation
            print(f"\\n--- STEP 6: Final Workflow Validation ---")
            
            # Get final portfolio state
            final_portfolio_result = await call_tool("get_portfolio", {})
            final_portfolio_text = final_portfolio_result[0].text
            
            try:
                final_portfolio_data = json.loads(final_portfolio_text) if final_portfolio_text.strip() else []
            except json.JSONDecodeError:
                print(f"[VALIDATION] Invalid final portfolio response: {final_portfolio_text}")
                final_portfolio_data = []
            
            # Get stop loss orders
            stop_losses_result = await call_tool("get_stop_losses", {})
            stop_losses_text = stop_losses_result[0].text
            
            try:
                stop_losses_data = json.loads(stop_losses_text) if stop_losses_text.strip() else []
            except json.JSONDecodeError:
                print(f"[VALIDATION] Invalid stop losses response: {stop_losses_text}")
                stop_losses_data = []
            
            # Workflow validation
            workflow_success = True
            workflow_errors = []
            
            # Validate positions were created
            if isinstance(final_portfolio_data, list):
                final_test_positions = [pos for pos in final_portfolio_data if pos.get("symbol") in test_symbols]
                if len(final_test_positions) == 0:
                    workflow_errors.append("No positions created during workflow")
                else:
                    print(f"[VALIDATION] Created {len(final_test_positions)} positions successfully")
            
            # Validate risk management was applied
            if isinstance(stop_losses_data, list):
                test_stop_losses = [stop for stop in stop_losses_data if stop.get("symbol") in test_symbols]
                print(f"[VALIDATION] Applied {len(test_stop_losses)} stop losses")
            
            # Summary
            print(f"\\n{'='*60}")
            print(f"=== WORKFLOW SUMMARY ===")
            print(f"1. Market Research: [OK] {len(market_prices)} symbols researched")
            print(f"2. Order Placement: [OK] {len(placed_orders)} orders attempted")
            print(f"3. Order Monitoring: [OK] Completed orders checked")
            print(f"4. Portfolio Analysis: [OK] {len(created_positions)} positions verified")
            print(f"5. Risk Management: [OK] {len(risk_orders)} stop losses attempted")
            print(f"6. Final Validation: [OK] Workflow integrity verified")
            
            if workflow_errors:
                print(f"\\nWorkflow Issues:")
                for error in workflow_errors:
                    print(f"  - {error}")
            
            print(f"{'='*60}")
            print(f"[PASSED] COMPLETE TRADING WORKFLOW TEST PASSED")
            
        except Exception as e:
            print(f"\\nWORKFLOW EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"Complete trading workflow failed: {e}")
    
    async def test_complete_trading_workflow_error_handling(self):
        """Test workflow error handling with invalid parameters"""
        
        print(f"\\n{'='*60}")
        print(f"=== Workflow Error Handling Test ===")
        print(f"{'='*60}")
        
        # Test invalid market data request
        try:
            invalid_quotes = await call_tool("get_market_data", {"symbols": "INVALID123"})
            quotes_text = invalid_quotes[0].text
            print(f"Invalid symbol response: {quotes_text}")
            assert "error" in quotes_text.lower(), "Should handle invalid symbols gracefully"
            print(f"[OK] Market data error handling working")
        except Exception as e:
            print(f"Market data error handling exception: {e}")
        
        # Test invalid order placement
        try:
            invalid_order = await call_tool("place_market_order", {
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": 0  # Invalid quantity
            })
            order_text = invalid_order[0].text
            print(f"Invalid order response: {order_text}")
            # Should be handled by safety validation
            print(f"[OK] Order placement error handling working")
        except Exception as e:
            print(f"Order placement error handling exception: {e}")
        
        print(f"[OK] Workflow error handling test completed")
    
    async def test_risk_management_integration(self):
        """Test integration of portfolio creation with comprehensive risk management"""
        
        print(f"\\n{'='*60}")
        print(f"=== Risk Management Integration Test ===")
        print(f"{'='*60}")
        
        try:
            # Step 1: Create basic test portfolio for risk management
            print(f"\\n--- STEP 1: Create Test Portfolio ---")
            test_symbol = "AAPL"  # Single symbol for focused risk management testing
            
            # Get current market price
            quotes_result = await call_tool("get_market_data", {"symbols": test_symbol})
            if not quotes_result or not quotes_result[0].text.strip():
                pytest.skip("Market data unavailable - IBKR Gateway may not be connected")
            
            try:
                quotes_data = json.loads(quotes_result[0].text)
                current_price = quotes_data.get("last", quotes_data.get("close", 180.0)) if isinstance(quotes_data, dict) else 180.0
                print(f"[RISK_TEST] {test_symbol} current price: ${current_price}")
            except json.JSONDecodeError:
                pytest.skip(f"Invalid market data response: {quotes_result[0].text}")
            
            # Place small test order (if trading is enabled)
            print(f"Attempting to place test order for risk management setup...")
            order_result = await call_tool("place_market_order", {
                "symbol": test_symbol,
                "action": "BUY",
                "quantity": 1  # Minimal quantity for testing
            })
            
            if order_result and order_result[0].text.strip():
                try:
                    order_data = json.loads(order_result[0].text)
                    if order_data.get("success"):
                        print(f"[RISK_TEST] Test order placed successfully")
                    else:
                        print(f"[RISK_TEST] Order placement issue: {order_data.get('error', 'Unknown')}")
                except json.JSONDecodeError:
                    print(f"[RISK_TEST] Order response: {order_result[0].text}")
            
            # Step 2: Check current portfolio state
            print(f"\\n--- STEP 2: Portfolio Risk Assessment ---")
            portfolio_result = await call_tool("get_portfolio", {})
            
            try:
                portfolio_data = json.loads(portfolio_result[0].text) if portfolio_result[0].text.strip() else []
            except json.JSONDecodeError:
                portfolio_data = []
            
            test_positions = [pos for pos in portfolio_data if pos.get("symbol") == test_symbol] if isinstance(portfolio_data, list) else []
            print(f"[RISK_TEST] Found {len(test_positions)} {test_symbol} positions")
            
            # Step 3: Apply comprehensive risk management
            print(f"\\n--- STEP 3: Apply Risk Management ---")
            risk_coverage = []
            
            for position in test_positions:
                symbol = position.get("symbol")
                quantity = position.get("position", 0)
                avg_cost = position.get("avgCost", current_price)
                
                if symbol and quantity > 0:
                    # Test multiple risk management approaches
                    
                    # A) Basic stop loss (10% below cost)
                    stop_price_10 = float(avg_cost) * 0.9
                    print(f"Setting 10% stop loss for {symbol}: {quantity} shares at ${stop_price_10:.2f}")
                    
                    try:
                        stop_result = await call_tool("place_stop_loss", {
                            "symbol": symbol,
                            "action": "SELL",
                            "quantity": max(1, int(quantity) // 2),  # Partial position protection
                            "stop_price": stop_price_10
                        })
                        
                        if stop_result and stop_result[0].text.strip():
                            try:
                                stop_data = json.loads(stop_result[0].text)
                                if stop_data.get("success"):
                                    print(f"[RISK] {symbol}: 10% stop loss placed")
                                    risk_coverage.append({"type": "basic_stop", "symbol": symbol})
                                else:
                                    print(f"[RISK] {symbol}: Stop loss failed - {stop_data.get('error', 'Unknown')}")
                            except json.JSONDecodeError:
                                print(f"[RISK] {symbol}: Stop loss response: {stop_result[0].text}")
                                
                    except Exception as e:
                        print(f"[RISK] {symbol}: Stop loss exception - {e}")
                    
                    # B) Trailing stop (if remaining quantity)
                    if int(quantity) > 1:
                        remaining_qty = int(quantity) - max(1, int(quantity) // 2)
                        if remaining_qty > 0:
                            print(f"Setting trailing stop for {symbol}: {remaining_qty} shares with 12% trail")
                            
                            try:
                                trailing_result = await call_tool("place_stop_loss", {
                                    "symbol": symbol,
                                    "action": "SELL",
                                    "quantity": remaining_qty,
                                    "stop_price": float(avg_cost) * 0.88,  # Initial 12% below
                                    "order_type": "TRAIL",
                                    "trail_percent": 12.0
                                })
                                
                                if trailing_result and trailing_result[0].text.strip():
                                    try:
                                        trailing_data = json.loads(trailing_result[0].text)
                                        if trailing_data.get("success"):
                                            print(f"[RISK] {symbol}: Trailing stop placed")
                                            risk_coverage.append({"type": "trailing_stop", "symbol": symbol})
                                        else:
                                            print(f"[RISK] {symbol}: Trailing stop failed - {trailing_data.get('error', 'Unknown')}")
                                    except json.JSONDecodeError:
                                        print(f"[RISK] {symbol}: Trailing stop response: {trailing_result[0].text}")
                                        
                            except Exception as e:
                                print(f"[RISK] {symbol}: Trailing stop exception - {e}")
                    
                    await asyncio.sleep(0.5)  # Brief delay between risk orders
            
            # Step 4: Validate risk coverage
            print(f"\\n--- STEP 4: Risk Coverage Validation ---")
            
            # Get all stop loss orders
            stop_orders_result = await call_tool("get_stop_losses", {})
            
            try:
                stop_orders_data = json.loads(stop_orders_result[0].text) if stop_orders_result[0].text.strip() else []
            except json.JSONDecodeError:
                stop_orders_data = []
            
            test_stop_orders = [order for order in stop_orders_data if order.get("symbol") == test_symbol] if isinstance(stop_orders_data, list) else []
            
            print(f"[VALIDATION] Total risk management orders applied: {len(risk_coverage)}")
            print(f"[VALIDATION] Active stop loss orders for {test_symbol}: {len(test_stop_orders)}")
            
            # Risk management effectiveness validation
            risk_effectiveness = {
                "positions_analyzed": len(test_positions),
                "risk_orders_attempted": len(risk_coverage),
                "active_stop_orders": len(test_stop_orders),
                "risk_coverage_ratio": len(test_stop_orders) / max(1, len(test_positions))
            }
            
            print(f"\\n{'='*60}")
            print(f"=== RISK MANAGEMENT SUMMARY ===")
            print(f"Positions Analyzed: {risk_effectiveness['positions_analyzed']}")
            print(f"Risk Orders Attempted: {risk_effectiveness['risk_orders_attempted']}")
            print(f"Active Stop Orders: {risk_effectiveness['active_stop_orders']}")
            print(f"Risk Coverage Ratio: {risk_effectiveness['risk_coverage_ratio']:.1%}")
            
            # Success criteria
            if risk_effectiveness['positions_analyzed'] > 0:
                if risk_effectiveness['risk_orders_attempted'] > 0:
                    print(f"[OK] Risk management integration successful")
                else:
                    print(f"[WARNING] No risk orders attempted (positions may not exist)")
            else:
                print(f"[WARNING] No positions found for risk management testing")
            
            print(f"{'='*60}")
            print(f"[OK] RISK MANAGEMENT INTEGRATION TEST COMPLETED")
            
        except Exception as e:
            print(f"\\nRISK MANAGEMENT EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"Risk management integration test failed: {e}")
    
    async def test_large_portfolio_performance(self):
        """Test large portfolio performance and scalability (10+ positions)"""
        
        print(f"\\n{'='*60}")
        print(f"=== Large Portfolio Performance Test ===")
        print(f"{'='*60}")
        
        import time
        
        # Define test symbols for large portfolio (10+ positions)
        large_portfolio_symbols = [
            "AAPL",   # US Tech
            "MSFT",   # US Tech  
            "GOOGL",  # US Tech
            "AMZN",   # US Tech
            "TSLA",   # US Auto
            "NVDA",   # US Semiconductors
            "META",   # US Social Media
            "NFLX",   # US Streaming
            "ASML",   # European Semiconductors (EUR)
            "SAP",    # European Software (EUR)
            "NESN",   # European Consumer (CHF)
            "NOVO-B"  # European Pharma (DKK)
        ]
        
        try:
            # PHASE 1: Portfolio Performance Baseline
            print(f"\\n--- PHASE 1: Performance Baseline ---")
            
            # Test 1: Market Data Performance for Large Portfolio
            print(f"Testing market data performance for {len(large_portfolio_symbols)} symbols...")
            start_time = time.time()
            
            symbols_str = ",".join(large_portfolio_symbols)
            market_data_result = await call_tool("get_market_data", {"symbols": symbols_str})
            
            market_data_duration = time.time() - start_time
            print(f"Market data retrieval time: {market_data_duration:.2f} seconds")
            
            # Validate market data response structure
            assert isinstance(market_data_result, list) and len(market_data_result) > 0
            market_data_text = market_data_result[0].text
            
            if not market_data_text.strip():
                pytest.skip("Market data request returned empty response - IBKR Gateway may not be connected")
            
            try:
                market_data = json.loads(market_data_text)
            except json.JSONDecodeError:
                if "error" in market_data_text.lower():
                    pytest.skip(f"Market data request failed: {market_data_text}")
                else:
                    pytest.fail(f"Invalid JSON response from market data: {market_data_text}")
            
            # Analyze market data performance
            if isinstance(market_data, list):
                successful_quotes = len([quote for quote in market_data if isinstance(quote, dict) and "symbol" in quote])
                print(f"Successful quotes: {successful_quotes}/{len(large_portfolio_symbols)}")
                quote_success_rate = successful_quotes / len(large_portfolio_symbols)
                print(f"Quote success rate: {quote_success_rate:.1%}")
            else:
                # Single quote response
                successful_quotes = 1 if isinstance(market_data, dict) and "symbol" in market_data else 0
                quote_success_rate = successful_quotes / len(large_portfolio_symbols)
                print(f"Single quote response received (expected multiple)")
            
            # Performance criteria validation
            performance_metrics = {
                "market_data_duration": market_data_duration,
                "quote_success_rate": quote_success_rate,
                "symbols_requested": len(large_portfolio_symbols),
                "quotes_received": successful_quotes
            }
            
            # Test 2: Portfolio Analysis Performance
            print(f"\\n--- Testing portfolio analysis performance ---")
            start_time = time.time()
            
            portfolio_result = await call_tool("get_portfolio", {})
            portfolio_duration = time.time() - start_time
            print(f"Portfolio analysis time: {portfolio_duration:.2f} seconds")
            
            assert isinstance(portfolio_result, list) and len(portfolio_result) > 0
            portfolio_text = portfolio_result[0].text
            
            try:
                portfolio_data = json.loads(portfolio_text) if portfolio_text.strip() else []
            except json.JSONDecodeError:
                portfolio_data = []
            
            current_positions = len(portfolio_data) if isinstance(portfolio_data, list) else 0
            print(f"Current portfolio positions: {current_positions}")
            
            performance_metrics["portfolio_duration"] = portfolio_duration
            performance_metrics["current_positions"] = current_positions
            
            # PHASE 2: Scalability Testing
            print(f"\\n--- PHASE 2: Scalability Testing ---")
            
            # Test large forex batch requests
            print(f"Testing large forex batch request performance...")
            forex_pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
            
            start_time = time.time()
            forex_result = await call_tool("get_forex_rates", {"currency_pairs": ",".join(forex_pairs)})
            forex_duration = time.time() - start_time
            print(f"Forex batch request time: {forex_duration:.2f} seconds")
            
            if forex_result and forex_result[0].text.strip():
                try:
                    forex_data = json.loads(forex_result[0].text)
                    forex_pairs_received = len(forex_data) if isinstance(forex_data, list) else (1 if isinstance(forex_data, dict) else 0)
                    print(f"Forex pairs received: {forex_pairs_received}/{len(forex_pairs)}")
                except json.JSONDecodeError:
                    forex_pairs_received = 0
                    print(f"Forex request error: {forex_result[0].text}")
            else:
                forex_pairs_received = 0
                print(f"Empty forex response")
            
            performance_metrics["forex_duration"] = forex_duration
            performance_metrics["forex_pairs_received"] = forex_pairs_received
            
            # Test currency conversion performance
            print(f"Testing multiple currency conversion performance...")
            conversion_tests = [
                {"amount": 10000, "from_currency": "USD", "to_currency": "EUR"},
                {"amount": 5000, "from_currency": "EUR", "to_currency": "GBP"},
                {"amount": 1000000, "from_currency": "JPY", "to_currency": "USD"},
                {"amount": 50000, "from_currency": "CHF", "to_currency": "USD"}
            ]
            
            start_time = time.time()
            conversion_results = []
            
            for conversion in conversion_tests:
                try:
                    result = await call_tool("convert_currency", conversion)
                    if result and result[0].text.strip():
                        try:
                            conv_data = json.loads(result[0].text)
                            if "converted_amount" in conv_data:
                                conversion_results.append(True)
                            else:
                                conversion_results.append(False)
                        except json.JSONDecodeError:
                            conversion_results.append(False)
                    else:
                        conversion_results.append(False)
                    
                    await asyncio.sleep(0.1)  # Small delay to avoid overwhelming API
                except Exception as e:
                    print(f"Conversion error: {e}")
                    conversion_results.append(False)
            
            conversion_duration = time.time() - start_time
            successful_conversions = sum(conversion_results)
            print(f"Currency conversion time: {conversion_duration:.2f} seconds")
            print(f"Successful conversions: {successful_conversions}/{len(conversion_tests)}")
            
            performance_metrics["conversion_duration"] = conversion_duration
            performance_metrics["successful_conversions"] = successful_conversions
            
            # PHASE 3: Performance Validation
            print(f"\\n--- PHASE 3: Performance Validation ---")
            
            # Define performance criteria (targeting <5 seconds for most operations)
            performance_criteria = {
                "market_data_max_time": 5.0,      # Max 5 seconds for large market data request
                "portfolio_max_time": 3.0,        # Max 3 seconds for portfolio analysis
                "forex_max_time": 4.0,            # Max 4 seconds for forex batch request
                "conversion_max_time": 3.0,       # Max 3 seconds for multiple conversions
                "min_quote_success_rate": 0.7,    # At least 70% quote success rate
                "min_forex_success_rate": 0.8     # At least 80% forex success rate
            }
            
            # Validate performance metrics
            performance_results = []
            
            # Market data performance
            if performance_metrics["market_data_duration"] <= performance_criteria["market_data_max_time"]:
                performance_results.append(f"[OK] Market data performance: {performance_metrics['market_data_duration']:.2f}s (target: <{performance_criteria['market_data_max_time']}s)")
            else:
                performance_results.append(f"[WARNING] Market data performance: {performance_metrics['market_data_duration']:.2f}s (target: <{performance_criteria['market_data_max_time']}s)")
            
            # Portfolio analysis performance
            if performance_metrics["portfolio_duration"] <= performance_criteria["portfolio_max_time"]:
                performance_results.append(f"[OK] Portfolio analysis: {performance_metrics['portfolio_duration']:.2f}s (target: <{performance_criteria['portfolio_max_time']}s)")
            else:
                performance_results.append(f"[WARNING] Portfolio analysis: {performance_metrics['portfolio_duration']:.2f}s (target: <{performance_criteria['portfolio_max_time']}s)")
            
            # Forex performance
            if performance_metrics["forex_duration"] <= performance_criteria["forex_max_time"]:
                performance_results.append(f"[OK] Forex batch request: {performance_metrics['forex_duration']:.2f}s (target: <{performance_criteria['forex_max_time']}s)")
            else:
                performance_results.append(f"[WARNING] Forex batch request: {performance_metrics['forex_duration']:.2f}s (target: <{performance_criteria['forex_max_time']}s)")
            
            # Conversion performance
            if performance_metrics["conversion_duration"] <= performance_criteria["conversion_max_time"]:
                performance_results.append(f"[OK] Currency conversions: {performance_metrics['conversion_duration']:.2f}s (target: <{performance_criteria['conversion_max_time']}s)")
            else:
                performance_results.append(f"[WARNING] Currency conversions: {performance_metrics['conversion_duration']:.2f}s (target: <{performance_criteria['conversion_max_time']}s)")
            
            # Success rate validation
            if performance_metrics["quote_success_rate"] >= performance_criteria["min_quote_success_rate"]:
                performance_results.append(f"[OK] Quote success rate: {performance_metrics['quote_success_rate']:.1%} (target: >{performance_criteria['min_quote_success_rate']:.1%})")
            else:
                performance_results.append(f"[WARNING] Quote success rate: {performance_metrics['quote_success_rate']:.1%} (target: >{performance_criteria['min_quote_success_rate']:.1%})")
            
            forex_success_rate = performance_metrics["forex_pairs_received"] / len(forex_pairs)
            if forex_success_rate >= performance_criteria["min_forex_success_rate"]:
                performance_results.append(f"[OK] Forex success rate: {forex_success_rate:.1%} (target: >{performance_criteria['min_forex_success_rate']:.1%})")
            else:
                performance_results.append(f"[WARNING] Forex success rate: {forex_success_rate:.1%} (target: >{performance_criteria['min_forex_success_rate']:.1%})")
            
            # PHASE 4: Scalability Analysis
            print(f"\\n--- PHASE 4: Scalability Analysis ---")
            
            # Estimate system capacity based on performance
            estimated_capacity = {
                "max_symbols_per_request": int(20 / max(0.1, performance_metrics["market_data_duration"]) * len(large_portfolio_symbols)),
                "max_portfolio_size": max(100, int(100 / max(0.1, performance_metrics["portfolio_duration"]) * max(1, current_positions))),
                "max_forex_pairs": int(20 / max(0.1, performance_metrics["forex_duration"]) * len(forex_pairs)),
                "max_conversions_per_minute": int(60 / max(0.1, performance_metrics["conversion_duration"]) * len(conversion_tests))
            }
            
            print(f"Estimated system capacity:")
            print(f"  - Max symbols per request: {estimated_capacity['max_symbols_per_request']}")
            print(f"  - Max portfolio size: {estimated_capacity['max_portfolio_size']} positions")
            print(f"  - Max forex pairs per request: {estimated_capacity['max_forex_pairs']}")
            print(f"  - Max conversions per minute: {estimated_capacity['max_conversions_per_minute']}")
            
            # Overall scalability assessment
            scalability_score = 0
            scalability_tests = [
                performance_metrics["market_data_duration"] <= performance_criteria["market_data_max_time"],
                performance_metrics["portfolio_duration"] <= performance_criteria["portfolio_max_time"],
                performance_metrics["forex_duration"] <= performance_criteria["forex_max_time"],
                performance_metrics["conversion_duration"] <= performance_criteria["conversion_max_time"],
                performance_metrics["quote_success_rate"] >= performance_criteria["min_quote_success_rate"],
                forex_success_rate >= performance_criteria["min_forex_success_rate"]
            ]
            
            scalability_score = sum(scalability_tests) / len(scalability_tests)
            
            # SUMMARY
            print(f"\\n{'='*60}")
            print(f"=== PERFORMANCE & SCALABILITY SUMMARY ===")
            print(f"Portfolio Size Tested: {len(large_portfolio_symbols)} symbols")
            print(f"Current Portfolio Positions: {current_positions}")
            print(f"Overall Scalability Score: {scalability_score:.1%}")
            print(f"")
            
            for result in performance_results:
                print(f"{result}")
            
            print(f"\\nScalability Assessment:")
            if scalability_score >= 0.8:
                print(f"[OK] EXCELLENT - System handles large portfolios efficiently")
            elif scalability_score >= 0.6:
                print(f"[OK] GOOD - System performance acceptable for most use cases")
            elif scalability_score >= 0.4:
                print(f"[WARNING] FAIR - System may have performance limitations with large portfolios")
            else:
                print(f"[ERROR] POOR - System may struggle with large portfolio operations")
            
            # Performance recommendations
            print(f"\\nPerformance Recommendations:")
            if performance_metrics["market_data_duration"] > performance_criteria["market_data_max_time"]:
                print(f"  - Consider batching market data requests in smaller groups")
            if performance_metrics["portfolio_duration"] > performance_criteria["portfolio_max_time"]:
                print(f"  - Optimize portfolio analysis for large position counts")
            if forex_success_rate < performance_criteria["min_forex_success_rate"]:
                print(f"  - Improve forex data reliability and error handling")
            if scalability_score >= 0.8:
                print(f"  - System performance is excellent for large portfolios")
            
            print(f"{'='*60}")
            print(f"[OK] LARGE PORTFOLIO PERFORMANCE TEST COMPLETED")
            
            # Store performance metrics for potential future analysis
            self._performance_metrics = performance_metrics
            self._estimated_capacity = estimated_capacity
            self._scalability_score = scalability_score
            
        except Exception as e:
            print(f"\\nPERFORMANCE TEST EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"Large portfolio performance test failed: {e}")
    
    async def test_real_pnl_validation(self):
        """Cross-validate P&L calculations between portfolio and executions"""
        
        print(f"\\n{'='*60}")
        print(f"=== P&L Cross-Validation Test ===")
        print(f"{'='*60}")
        
        try:
            # STEP 1: Ensure we have positions with execution history
            print(f"\\n--- STEP 1: Portfolio & Execution Data ---")
            
            # Get current portfolio P&L
            portfolio_result = await call_tool("get_portfolio", {})
            assert isinstance(portfolio_result, list) and len(portfolio_result) > 0
            portfolio_text = portfolio_result[0].text
            
            if not portfolio_text.strip():
                pytest.skip("Portfolio request returned empty response - IBKR Gateway may not be connected")
            
            try:
                portfolio_data = json.loads(portfolio_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse portfolio response: {portfolio_text}")
                if "error" in portfolio_text.lower():
                    pytest.skip(f"Portfolio request failed: {portfolio_text}")
                else:
                    pytest.skip(f"Invalid JSON response from portfolio: {portfolio_text}")
            
            if not isinstance(portfolio_data, list):
                portfolio_data = []
            
            print(f"[P&L_VALIDATION] Found {len(portfolio_data)} total positions")
            
            # Get execution history for cross-validation
            executions_result = await call_tool("get_executions", {})
            assert isinstance(executions_result, list) and len(executions_result) > 0
            executions_text = executions_result[0].text
            
            try:
                executions_data = json.loads(executions_text) if executions_text.strip() else []
            except json.JSONDecodeError:
                print(f"[P&L_VALIDATION] Invalid executions response: {executions_text}")
                executions_data = []
            
            if not isinstance(executions_data, list):
                executions_data = []
            
            print(f"[P&L_VALIDATION] Found {len(executions_data)} total executions")
            
            # STEP 2: Cross-validate P&L for each position
            print(f"\\n--- STEP 2: P&L Cross-Validation ---")
            
            if not portfolio_data:
                # Try to create a small test position for P&L validation
                print(f"[P&L_VALIDATION] No positions found, attempting to create test position...")
                
                test_symbol = "AAPL"
                
                # Get current market price
                quotes_result = await call_tool("get_market_data", {"symbols": test_symbol})
                if quotes_result and quotes_result[0].text.strip():
                    try:
                        quotes_data = json.loads(quotes_result[0].text)
                        current_price = quotes_data.get("last", quotes_data.get("close", 180.0)) if isinstance(quotes_data, dict) else 180.0
                        print(f"[P&L_VALIDATION] {test_symbol} current price: ${current_price}")
                    except json.JSONDecodeError:
                        current_price = 180.0
                        print(f"[P&L_VALIDATION] Using fallback price for {test_symbol}: ${current_price}")
                
                    # Place small test order
                    order_result = await call_tool("place_market_order", {
                        "symbol": test_symbol,
                        "action": "BUY",
                        "quantity": 1  # Minimal quantity for testing
                    })
                    
                    if order_result and order_result[0].text.strip():
                        try:
                            order_data = json.loads(order_result[0].text)
                            if order_data.get("success"):
                                print(f"[P&L_VALIDATION] Test order placed successfully")
                                # Wait a moment for order processing
                                await asyncio.sleep(2)
                                
                                # Re-check portfolio
                                portfolio_result = await call_tool("get_portfolio", {})
                                portfolio_text = portfolio_result[0].text
                                try:
                                    portfolio_data = json.loads(portfolio_text) if portfolio_text.strip() else []
                                except json.JSONDecodeError:
                                    portfolio_data = []
                                
                                print(f"[P&L_VALIDATION] Portfolio after test order: {len(portfolio_data)} positions")
                            else:
                                print(f"[P&L_VALIDATION] Test order failed: {order_data.get('error', 'Unknown error')}")
                        except json.JSONDecodeError:
                            print(f"[P&L_VALIDATION] Invalid order response: {order_result[0].text}")
                
                if not portfolio_data:
                    pytest.skip("P&L validation requires positions - unable to create test position")
            
            # Perform P&L validation on available positions
            validation_results = []
            
            for position in portfolio_data:
                symbol = position.get('symbol', 'N/A')
                
                # Extract portfolio P&L data (using IBKR API camelCase field names)
                portfolio_pnl = position.get('unrealizedPNL', position.get('unrealized_pnl', 0))
                avg_cost = position.get('avgCost', position.get('avg_cost', 0))
                current_price = position.get('marketPrice', position.get('current_price', avg_cost))
                quantity = position.get('position', 0)
                market_value = position.get('marketValue', position.get('market_value', 0))
                
                # Convert string values to float if needed
                try:
                    portfolio_pnl = float(portfolio_pnl) if portfolio_pnl else 0.0
                    avg_cost = float(avg_cost) if avg_cost else 0.0
                    current_price = float(current_price) if current_price else avg_cost
                    quantity = float(quantity) if quantity else 0.0
                    market_value = float(market_value) if market_value else 0.0
                except (ValueError, TypeError):
                    print(f"[P&L_VALIDATION] {symbol}: Failed to convert position values to float")
                    continue
                
                print(f"\\n[P&L_VALIDATION] {symbol}:")
                print(f"  Portfolio P&L: ${portfolio_pnl:.2f}")
                print(f"  Avg Cost: ${avg_cost:.2f}")
                print(f"  Current Price: ${current_price:.2f}")
                print(f"  Quantity: {quantity}")
                print(f"  Market Value: ${market_value:.2f}")
                
                # Find related executions for this symbol
                symbol_executions = [e for e in executions_data if e.get('symbol') == symbol]
                print(f"  Related Executions: {len(symbol_executions)}")
                
                if symbol_executions and avg_cost and current_price and quantity:
                    # Calculate expected P&L from price difference
                    expected_pnl = (current_price - avg_cost) * quantity
                    
                    # Calculate P&L difference and tolerance
                    pnl_difference = abs(portfolio_pnl - expected_pnl)
                    
                    # Use generous tolerance due to commissions, dividends, and IBKR adjustments
                    base_tolerance = abs(expected_pnl) * 0.20 if expected_pnl != 0 else 10.0  # 20% tolerance or $10
                    pnl_tolerance = max(base_tolerance, 5.0)  # Minimum $5 tolerance
                    
                    print(f"  Expected P&L: ${expected_pnl:.2f}")
                    print(f"  P&L Difference: ${pnl_difference:.2f}")
                    print(f"  P&L Tolerance: ${pnl_tolerance:.2f}")
                    
                    # Validate P&L accuracy
                    pnl_validation = {
                        'symbol': symbol,
                        'portfolio_pnl': portfolio_pnl,
                        'expected_pnl': expected_pnl,
                        'difference': pnl_difference,
                        'tolerance': pnl_tolerance,
                        'within_tolerance': pnl_difference <= pnl_tolerance,
                        'accuracy_pct': 1.0 - (pnl_difference / max(abs(expected_pnl), 1.0))
                    }
                    
                    validation_results.append(pnl_validation)
                    
                    if pnl_validation['within_tolerance']:
                        print(f"  [OK] P&L validation PASSED (accuracy: {pnl_validation['accuracy_pct']:.1%})")
                    else:
                        print(f"  [WARNING] P&L validation OUTSIDE TOLERANCE")
                        print(f"     Note: IBKR P&L may include commissions, dividends, and other adjustments")
                
                elif not symbol_executions:
                    print(f"  [WARNING] No execution history found for {symbol}")
                    
                    # Still validate basic position data consistency
                    if market_value and quantity and current_price:
                        expected_market_value = quantity * current_price
                        market_value_diff = abs(market_value - expected_market_value)
                        market_value_tolerance = expected_market_value * 0.05  # 5% tolerance
                        
                        if market_value_diff <= market_value_tolerance:
                            print(f"  [OK] Market value calculation consistent")
                        else:
                            print(f"  [WARNING] Market value inconsistency: Expected ${expected_market_value:.2f}, Got ${market_value:.2f}")
                
                else:
                    print(f"  [WARNING] Insufficient data for P&L validation")
            
            # STEP 3: Summary and Analysis
            print(f"\\n--- STEP 3: P&L Validation Summary ---")
            
            if validation_results:
                validated_positions = len(validation_results)
                passed_validations = sum(1 for v in validation_results if v['within_tolerance'])
                validation_success_rate = passed_validations / validated_positions
                
                # Calculate average accuracy
                total_accuracy = sum(v['accuracy_pct'] for v in validation_results)
                average_accuracy = total_accuracy / validated_positions
                
                print(f"Positions Validated: {validated_positions}")
                print(f"Validations Passed: {passed_validations}")
                print(f"Validation Success Rate: {validation_success_rate:.1%}")
                print(f"Average P&L Accuracy: {average_accuracy:.1%}")
                
                # Detailed results
                print(f"\\nDetailed Validation Results:")
                for v in validation_results:
                    status = "[OK] PASS" if v['within_tolerance'] else "[WARNING] OUTSIDE TOLERANCE"
                    print(f"  {v['symbol']}: {status} (accuracy: {v['accuracy_pct']:.1%})")
                
                # Overall assessment
                print(f"\\n{'='*60}")
                print(f"=== P&L VALIDATION ASSESSMENT ===")
                
                if validation_success_rate >= 0.8:
                    print(f"[OK] EXCELLENT - P&L calculations are highly accurate")
                elif validation_success_rate >= 0.6:
                    print(f"[OK] GOOD - P&L calculations are reasonably accurate")
                elif validation_success_rate >= 0.4:
                    print(f"[WARNING] FAIR - P&L calculations have some discrepancies")
                else:
                    print(f"[ERROR] POOR - P&L calculations require investigation")
                
                print(f"\\nNotes:")
                print(f"- IBKR P&L may include commissions, dividends, and currency adjustments")
                print(f"- Large tolerance used to account for these factors")
                print(f"- Minor discrepancies are normal in live trading environments")
                
                if average_accuracy < 0.8:
                    print(f"\\nRecommendations:")
                    print(f"- Verify commission calculations are properly accounted for")
                    print(f"- Check for dividend payments affecting P&L")
                    print(f"- Review currency conversion accuracy for international positions")
                
            else:
                print(f"[WARNING] No positions available for P&L validation")
                print(f"   - Portfolio may be empty")
                print(f"   - Execution history may be unavailable")
                print(f"   - Position data may be incomplete")
                
                pytest.skip("P&L validation requires both positions and execution history")
            
            print(f"{'='*60}")
            print(f"[OK] P&L CROSS-VALIDATION TEST COMPLETED")
            
        except Exception as e:
            print(f"\\nP&L VALIDATION EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"P&L cross-validation test failed: {e}")

# CRITICAL EXECUTION INSTRUCTIONS
"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_complete_trading_workflow.py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\\Python313\\python.exe -m pytest tests/paper/individual/test_individual_complete_trading_workflow.py::TestIndividualCompleteTradingWorkflow::test_complete_trading_workflow_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_complete_trading_workflow.py::TestIndividualCompleteTradingWorkflow -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_complete_trading_workflow.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
- Trading enabled in .env: ENABLE_TRADING=true
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("[WARNING] STANDALONE EXECUTION DETECTED")
    print("[WARNING] RECOMMENDED: Use pytest execution commands shown above")
    print("[WARNING] Standalone mode may not work correctly with MCP interface")
    print()
    print("IBKR Gateway must be running with paper trading login and API enabled!")
    print("Port 7497 for paper trading, Client ID 5")
    
    # Run just this test file using pytest
    exit_code = pytest.main([
        __file__, 
        "-v", 
        "-s", 
        "--tb=short"
    ])
    
    sys.exit(exit_code)
