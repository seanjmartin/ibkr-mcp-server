@echo off
REM Claude Desktop Configuration Helper for IBKR MCP Server
REM This script helps configure Claude Desktop for user testing

echo.
echo ===============================================
echo Claude Desktop Configuration Helper
echo IBKR MCP Server User Testing Setup
echo ===============================================
echo.

REM Get current directory
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

REM Find Claude Desktop config directory
set "CLAUDE_CONFIG_DIR=%APPDATA%\Claude"
set "CLAUDE_CONFIG_FILE=%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"

echo Current Project Directory: %PROJECT_DIR%
echo Claude Config Directory: %CLAUDE_CONFIG_DIR%
echo Claude Config File: %CLAUDE_CONFIG_FILE%
echo.

REM Check if Claude Desktop is installed
if not exist "%CLAUDE_CONFIG_DIR%" (
    echo ERROR: Claude Desktop configuration directory not found!
    echo Please install Claude Desktop first.
    echo Expected location: %CLAUDE_CONFIG_DIR%
    echo.
    pause
    exit /b 1
)

REM Create config directory if it doesn't exist
if not exist "%CLAUDE_CONFIG_DIR%" (
    mkdir "%CLAUDE_CONFIG_DIR%"
    echo Created Claude config directory: %CLAUDE_CONFIG_DIR%
)

REM Check if config file already exists
if exist "%CLAUDE_CONFIG_FILE%" (
    echo.
    echo WARNING: Claude Desktop config file already exists!
    echo Current file: %CLAUDE_CONFIG_FILE%
    echo.
    echo Would you like to:
    echo 1. Backup existing config and create new one
    echo 2. View current config
    echo 3. Exit without changes
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        copy "%CLAUDE_CONFIG_FILE%" "%CLAUDE_CONFIG_FILE%.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%"
        echo Backed up existing config to %CLAUDE_CONFIG_FILE%.backup.*
    ) else if "%choice%"=="2" (
        echo.
        echo Current Claude Desktop Configuration:
        echo ===================================
        type "%CLAUDE_CONFIG_FILE%"
        echo.
        pause
        exit /b 0
    ) else (
        echo Exiting without changes.
        pause
        exit /b 0
    )
)

REM Find Python executable
echo Locating Python executable...
set "PYTHON_EXE="

REM Check common Python locations
if exist "C:\Python313\python.exe" (
    set "PYTHON_EXE=C:\Python313\python.exe"
) else if exist "C:\Python312\python.exe" (
    set "PYTHON_EXE=C:\Python312\python.exe"
) else if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
) else (
    REM Try to find python in PATH
    where python.exe >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%i in ('where python.exe') do set "PYTHON_EXE=%%i"
    ) else (
        echo ERROR: Python executable not found!
        echo Please install Python 3.9+ or update the script with your Python path.
        echo Common locations: C:\Python313\python.exe
        pause
        exit /b 1
    )
)

echo Found Python: %PYTHON_EXE%

REM Escape backslashes for JSON
set "PYTHON_EXE_JSON=%PYTHON_EXE:\=\\%"
set "PROJECT_DIR_JSON=%PROJECT_DIR:\=\\%"

echo.
echo Creating Claude Desktop configuration...

REM Create the JSON configuration
(
echo {
echo   "mcpServers": {
echo     "ibkr": {
echo       "command": "%PYTHON_EXE_JSON%",
echo       "args": ["-m", "ibkr_mcp_server.main"],
echo       "cwd": "%PROJECT_DIR_JSON%",
echo       "env": {
echo         "LOG_LEVEL": "INFO"
echo       }
echo     }
echo   }
echo }
) > "%CLAUDE_CONFIG_FILE%"

echo.
echo SUCCESS: Claude Desktop configuration created!
echo Config file: %CLAUDE_CONFIG_FILE%
echo.
echo Configuration Details:
echo - Python: %PYTHON_EXE%
echo - Project: %PROJECT_DIR%
echo - Log Level: INFO
echo.
echo NEXT STEPS:
echo 1. Restart Claude Desktop to load the new configuration
echo 2. Start IB Gateway and login to your paper account
echo 3. Open a new conversation in Claude Desktop
echo 4. Test with: "Check my IBKR connection status"
echo.
echo For detailed testing instructions, see:
echo docs\guides\claude-desktop-user-testing.md
echo.
pause
