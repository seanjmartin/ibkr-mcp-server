@echo off
echo 🚀 Setting up IBKR MCP Server...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
pip install --upgrade pip

REM Install package
echo 📚 Installing dependencies...
pip install -e .

REM Install dev dependencies if requested
if "%1"=="--dev" (
    echo 🛠️ Installing development dependencies...
    pip install -e ".[dev]"
)

REM Copy environment file
if not exist .env (
    echo ⚙️ Creating environment file...
    copy .env.example .env
    echo 📝 Please edit .env with your IBKR settings
)

REM Test installation
echo 🧪 Testing installation...
python -c "import ibkr_mcp_server; print('✅ Package installed successfully')"

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env with your IBKR settings
echo 2. Start TWS/IB Gateway with API enabled  
echo 3. Test: python -m ibkr_mcp_server.main --test
echo 4. Add to Claude Desktop/Code configuration
echo.
echo 📖 See README.md for detailed instructions
pause
