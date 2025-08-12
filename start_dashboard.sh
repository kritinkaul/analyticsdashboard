#!/bin/bash
# Quick start script for the Business Analytics Dashboard

echo "🚀 Business Analytics Dashboard - Quick Start"
echo "============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo " Starting Streamlit dashboard..."
echo "🌐 Dashboard will be available at: http://localhost:8501"
echo "💡 Press Ctrl+C to stop the dashboard"
echo ""

# Start the Streamlit dashboard
streamlit run dashboard.py
