@echo off
cd /d C:\Users\sean\Documents\Projects\ibkr-mcp-server
echo Testing individual paper trading tests with 10-second timeout...
echo ================================================================
echo CRITICAL: Any test taking >10 seconds is HANGING and will be terminated
echo Expected: All tests should complete in <2 seconds if healthy
echo ================================================================
echo.

echo Test 1: Basic Connection (test_client_id_5.py) - Expected: <2s
timeout 10 pytest tests\paper\test_client_id_5.py::TestWorkingPaperClientId5::test_connection_and_accounts -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 2: Connection Status Tool (test_client_id_5.py) - Expected: <2s
timeout 10 pytest tests\paper\test_client_id_5.py::TestWorkingPaperClientId5::test_connection_status_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 3: Account Summary Tool - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_account_summary_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 4: Portfolio Tool - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_portfolio_tool -v -s --tb=short  
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 5: Market Data Tool (AAPL - US Stock) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_market_data_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 6: International Market Data (ASML - Netherlands) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_international_market_data_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 7: Forex Rates Tool (EURUSD) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_forex_rates_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 8: Currency Conversion Tool (USD to EUR) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_currency_conversion_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 9: Symbol Resolution Tool (ASML) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_symbol_resolution_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 10: Get Stop Losses Tool (Read-Only) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_get_stop_losses_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 11: Get Completed Orders Tool (Read-Only) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_get_completed_orders_tool -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 12: Invalid Currency Conversion (Error Handling) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingMCPTools::test_invalid_currency_conversion -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 13: Invalid Symbol Handling (Error Handling) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingErrorHandling::test_invalid_symbol_handling -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo Test 14: Invalid Forex Pair Handling (Error Handling) - Expected: <2s
timeout 10 pytest tests\paper\test_mcp_tools_paper.py::TestPaperTradingErrorHandling::test_invalid_forex_pair_handling -v -s --tb=short
echo Exit code: %ERRORLEVEL% (124 = timeout/hanging)
timeout 2 >nul 2>&1
echo.

echo ================================================================
echo All individual tests completed!
echo.
echo RESULTS ANALYSIS:
echo - Exit code 0 = SUCCESS (test passed)
echo - Exit code 1 = TEST FAILED (test ran but failed)
echo - Exit code 124 = TIMEOUT/HANGING (test took >10 seconds)
echo.
echo Next Steps:
echo 1. Review any hanging tests (exit code 124)
echo 2. Request IBKR Gateway logs for Client ID 5 during hanging tests
echo 3. Fix event loop and connection issues
echo 4. Achieve 100%% individual test success rate
echo ================================================================
