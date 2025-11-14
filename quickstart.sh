#!/bin/bash
# Quick Start Script for Context Engine

set -e  # Exit on error

echo "=================================="
echo "Context Engine Quick Start"
echo "=================================="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi
echo "✓ Python version OK: $(python3 --version)"
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo

# Download embedding model (this will be cached)
echo "Downloading embedding model (first time only)..."
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" 2>/dev/null
echo "✓ Embedding model ready"
echo

# Create necessary directories
echo "Creating directories..."
mkdir -p data/embeddings data/sessions logs
echo "✓ Directories created"
echo

echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo
echo "Quick Start Commands:"
echo
echo "  1. Index a directory:"
echo "     python main.py index ./your_project"
echo
echo "  2. Query for context:"
echo "     python main.py query \"your question\""
echo
echo "  3. Interactive mode:"
echo "     python main.py interactive"
echo
echo "  4. Get help:"
echo "     python main.py --help"
echo
echo "For more information, see README.md"
echo
