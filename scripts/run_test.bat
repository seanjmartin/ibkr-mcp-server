@echo off
cd /d C:\Users\sean\Documents\Projects\ibkr-mcp-server
C:\Users\sean\Documents\Projects\ibkr-mcp-server\venv\Scripts\python.exe -m pytest tests\paper\test_paper_trading_integration.py::TestPaperTradingConnection::test_paper_connection_status -v -s --tb=short
