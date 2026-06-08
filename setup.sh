#!/bin/bash

# LLM QnA Bot Setup Script
# Sets up Python virtual environment and installs dependencies

set -e  # Exit on error

echo "🚀 LLM QnA Bot - Setup Script"
echo "================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ Pip upgraded"

# Install requirements
echo ""
echo "📥 Installing dependencies..."
echo "   This may take a few minutes on first run..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Download models
echo ""
python3 setup.py

echo ""
echo "================================"
echo "✨ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Run interactive mode:"
echo "   python -m src.main --mode interactive"
echo ""
echo "3. Or try a single question:"
echo "   python -m src.main --question 'What is Python?' --role qa"
echo ""
echo "4. For more examples, see README.md"
echo ""
echo "🎉 Enjoy experimenting with LLMs!"
