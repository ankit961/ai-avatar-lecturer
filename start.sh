#!/bin/bash

# Doctor Avatar Generator - Startup Script

echo "🚀 Starting Doctor Avatar Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "🔍 Checking installation..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo "✅ Installation verified!"
    echo "🌐 Starting API server..."
    python backend/app.py
else
    echo "❌ Installation check failed. Please install dependencies:"
    echo "   pip install -r requirements.txt"
    exit 1
fi
