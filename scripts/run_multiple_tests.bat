@echo off
cd /d C:\Users\sean\Documents\Projects\ibkr-mcp-server
echo Testing multiple paper trading tests...
echo.
echo === Test 1: Connection Status ===
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingConnection::test_paper_connection_status -v -s --tb=short -x
echo.
echo === Test 2: Account Summary ===
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingConnection::test_paper_account_summary -v -s --tb=short -x
echo.
echo === Test 3: US Market Data ===
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingMarketData::test_us_market_data -v -s --tb=short -x
echo.
echo All tests completed.
