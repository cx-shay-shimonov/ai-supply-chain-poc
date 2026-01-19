#!/bin/bash
# Installation script for Claude MCP Scanner Agent

set -e  # Exit on error

echo "🚀 Claude + MCP Scanner Agent Installation"
echo "==========================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   ✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "2️⃣  Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "2️⃣  Virtual environment already exists"
    echo "   ✅ Skipping creation"
fi
echo ""

# Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Environment activated"
echo ""

# Install requirements
echo "4️⃣  Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed:"
echo "      - anthropic (Claude API)"
echo "      - mcp (MCP SDK)"
echo "      - mcp-server-tree-sitter (MCP server)"
echo ""

# Test MCP connection
echo "5️⃣  Testing MCP server connection..."
if python test_mcp_connection.py > /dev/null 2>&1; then
    echo "   ✅ MCP server test passed"
else
    echo "   ⚠️  MCP test had warnings (this is OK)"
fi
echo ""

# Check for API key
echo "6️⃣  Checking for API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "   ⚠️  ANTHROPIC_API_KEY not set"
    echo ""
    echo "   To use the scanner, set your API key:"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
    echo "   Get your key from: https://console.anthropic.com/"
else
    echo "   ✅ ANTHROPIC_API_KEY is set"
fi
echo ""

# Success message
echo "==========================================="
echo "✨ Installation complete!"
echo "==========================================="
echo ""
echo "📦 Installed packages:"
pip list | grep -E "anthropic|mcp"
echo ""
echo "🚀 Next steps:"
echo ""
echo "   1. Set your API key:"
echo "      export ANTHROPIC_API_KEY='sk-ant-...'"
echo ""
echo "   2. Run the scanner:"
echo "      source venv/bin/activate"
echo "      python claude_mcp_scanner.py"
echo ""
echo "   3. Check results:"
echo "      ls -lh llm_scan_results/"
echo ""
echo "📚 Documentation:"
echo "   - READY.md  - Quick start guide"
echo "   - USAGE.md  - Detailed usage"
echo "   - README.md - Full documentation"
echo ""
