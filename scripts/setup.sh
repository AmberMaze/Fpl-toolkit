#!/bin/bash
# FPL Toolkit Development Setup Script

set -e

echo "🚀 Setting up FPL Toolkit development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing FPL Toolkit with all features..."
pip install -e ".[dev,web,ai,postgresql]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created from .env.example"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️ Initializing database..."
python -m fpl_toolkit.cli init

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
pytest tests/ --tb=short -q

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Start API server: fpl-toolkit serve --reload"
echo "  3. Start Streamlit app: fpl-toolkit streamlit"
echo "  4. Run tests: pytest"
echo "  5. Format code: black src/ tests/"
echo "  6. Lint code: ruff check src/ tests/"
echo ""
echo "🌐 Available commands:"
echo "  • fpl-toolkit --help        # Show all CLI commands"
echo "  • fpl-toolkit serve         # Start FastAPI server"
echo "  • fpl-toolkit streamlit     # Start Streamlit app"
echo "  • fpl-toolkit init          # Initialize database"
echo ""
