#!/bin/bash
# FPL Toolkit Quick Setup (No AI) - For immediate development

set -e

echo "🚀 Quick setup FPL Toolkit (without AI dependencies)..."

# Check Python version
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Python 3.10+ required"
    exit 1
fi

echo "✅ Python $(python3 --version | cut -d' ' -f2) detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install ONLY core + web dependencies (skip AI for speed)
echo "📚 Installing FPL Toolkit (core + web, no AI)..."
pip install -e ".[dev,web,postgresql]"

# Create .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created"
fi

# Initialize database
echo "🗄️ Initializing database..."
python -m fpl_toolkit.cli init

echo ""
echo "🎉 Quick setup complete! (AI features disabled)"
echo ""
echo "📋 To start developing:"
echo "  source venv/bin/activate"
echo "  fpl-toolkit serve --reload"
echo ""
echo "💡 To add AI later: pip install -e '.[ai]'"
