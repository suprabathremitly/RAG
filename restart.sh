#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                     🔄 RESTARTING RAG SERVER 🔄                              ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Kill any existing uvicorn processes
echo "🛑 Stopping any existing servers..."
pkill -9 -f "uvicorn" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Stopped existing server"
else
    echo "   ℹ️  No existing server found"
fi

# Step 2: Wait a moment for port to be released
echo ""
echo "⏳ Waiting for port to be released..."
sleep 2

# Step 3: Check if port 8000 is still in use
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   ⚠️  Port 8000 still in use. Force killing..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Step 4: Verify port is free
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   ❌ ERROR: Port 8000 is still in use!"
    echo "   Try manually: lsof -ti:8000 | xargs kill -9"
    exit 1
else
    echo "   ✅ Port 8000 is free"
fi

# Step 5: Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "   ✅ Virtual environment activated"
else
    echo "   ❌ ERROR: Virtual environment not found!"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Step 6: Check if .env file exists
echo ""
echo "🔍 Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✅ .env file found"
else
    echo "   ⚠️  WARNING: .env file not found!"
    echo "   Creating from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your OPENAI_API_KEY"
fi

# Step 7: Start the server
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                     🚀 STARTING SERVER 🚀                                    ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Server will be available at:"
echo "   🌐 Main UI:      http://localhost:8000"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   ❤️  Health:       http://localhost:8000/api/health"
echo ""
echo "🛑 To stop: Press Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

