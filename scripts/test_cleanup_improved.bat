@echo off
cd /d C:\Users\sean\Documents\Projects\ibkr-mcp-server
echo Testing improved client ID management...
echo.
echo === Test 1: Connection with improved cleanup ===
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingConnection::test_paper_connection_status -v -s --tb=short -x
echo.
echo === Test 2: Immediate second connection ===
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingConnection::test_paper_connection_status -v -s --tb=short -x
echo.
echo === Test 3: Account summary ===
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingConnection::test_paper_account_summary -v -s --tb=short -x
echo.
echo All tests completed. Check if client IDs are properly released.
