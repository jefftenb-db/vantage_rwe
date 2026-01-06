#!/bin/bash
# Quick restart script for Vantage RWE

echo "🛑 Stopping all services..."

# Kill all related processes
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
pkill -f "concurrently" 2>/dev/null

# Wait for graceful shutdown
sleep 2

# Force-kill anything still on the ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ Services stopped"
echo ""
echo "🚀 Starting services..."
echo ""

# Restart
npm run start


