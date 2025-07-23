#!/bin/bash

set -e

echo "🚀 Setting up IBKR MCP Server..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📚 Installing dependencies..."
pip install -e .

# Install development dependencies if requested
if [[ "$1" == "--dev" ]]; then
    echo "🛠️ Installing development dependencies..."
    pip install -e ".[dev]"
    
    # Setup pre-commit hooks
    pre-commit install
    echo "✅ Pre-commit hooks installed"
fi

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env with your IBKR settings"
fi

# Test installation
echo "🧪 Testing installation..."
python -c "import ibkr_mcp_server; print('✅ Package installed successfully')"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your IBKR settings"
echo "2. Start TWS/IB Gateway with API enabled"
echo "3. Test: python -m ibkr_mcp_server.main --test"
echo "4. Add to Claude Desktop/Code configuration"
echo ""
echo "📖 See README.md for detailed instructions"
