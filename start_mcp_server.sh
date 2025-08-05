#!/bin/bash

# RAG Chatbot MCP Server Startup Script
# This script starts the MCP server with proper configuration

set -e  # Exit on any error

echo "🚀 Starting RAG Chatbot MCP Server"
echo "=================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating a virtual environment first:"
    echo "   python -m venv venv && source venv/bin/activate"
fi

# Check if required dependencies are installed
echo "🔍 Checking dependencies..."

# Check for critical packages
python -c "import fastapi" 2>/dev/null || {
    echo "❌ FastAPI not found. Installing dependencies..."
    pip install -r requirements.txt
}

python -c "import uvicorn" 2>/dev/null || {
    echo "❌ Uvicorn not found. Installing dependencies..."
    pip install -r requirements.txt
}

echo "✅ Dependencies checked"

# Check for environment file
if [ -f ".env" ]; then
    echo "✅ Environment file (.env) found"
else
    echo "⚠️  Warning: No .env file found"
    echo "   Some features may not work without proper configuration"
    echo "   See MCP_SERVER_GUIDE.md for configuration details"
fi

# Set default port if not specified
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "🌐 Server will start on: http://$HOST:$PORT"
echo "📖 MCP Manifest will be available at: http://$HOST:$PORT/.well-known/mcp/manifest.json"
echo "🔍 Health check available at: http://$HOST:$PORT/health"

# Create log directory if it doesn't exist
mkdir -p logs

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down MCP server..."
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Start the server
echo ""
echo "🎯 Starting server..."
echo "   Press Ctrl+C to stop"
echo ""

# Start the server with logging
python mcp_server.py \
    --host "$HOST" \
    --port "$PORT" \
    2>&1 | tee "logs/mcp_server_$(date +%Y%m%d_%H%M%S).log"