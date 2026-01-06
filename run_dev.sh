#!/bin/bash
# Development runner script for OMOP Cohort Builder

echo "🚀 Starting OMOP Cohort Builder Development Environment"
echo "======================================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "   Creating from .env.example..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "   Please edit backend/.env with your Databricks credentials"
        exit 1
    else
        echo "   ❌ Error: .env.example not found"
        exit 1
    fi
fi

# Function to check if port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use"
    read -p "   Kill the process and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9
        echo "   ✅ Port 8000 freed"
    else
        echo "   ❌ Cannot start backend on port 8000"
        exit 1
    fi
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use"
    read -p "   Kill the process and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:3000 | xargs kill -9
        echo "   ✅ Port 3000 freed"
    else
        echo "   ❌ Cannot start frontend on port 3000"
        exit 1
    fi
fi

# Create logs directory
mkdir -p logs

echo ""
echo "📦 Checking dependencies..."

# Check backend dependencies
cd backend
if [ ! -d "venv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r ../requirements.txt
cd ..

# Check frontend dependencies
cd frontend
if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install
fi
cd ..

echo "   ✅ Dependencies ready"
echo ""

# Start backend
echo "🔧 Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level info > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "   Backend PID: $BACKEND_PID"
echo "   Logs: logs/backend.log"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"

# Wait for backend to start
echo ""
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend started successfully
if ! check_port 8000; then
    echo "   ❌ Backend failed to start. Check logs/backend.log"
    exit 1
fi
echo "   ✅ Backend is running"

# Start frontend
echo ""
echo "🎨 Starting Frontend (React)..."
cd frontend
BROWSER=none npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: logs/frontend.log"
echo "   URL: http://localhost:3000"

# Wait for frontend to start
echo ""
echo "⏳ Waiting for frontend to start..."
sleep 5

# Check if frontend started successfully
if ! check_port 3000; then
    echo "   ❌ Frontend failed to start. Check logs/frontend.log"
    kill $BACKEND_PID
    exit 1
fi
echo "   ✅ Frontend is running"

# Success message
echo ""
echo "======================================================="
echo "✅ OMOP Cohort Builder is running!"
echo "======================================================="
echo ""
echo "📍 Access Points:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 Process IDs:"
echo "   • Backend:  $BACKEND_PID"
echo "   • Frontend: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   • Backend:  tail -f logs/backend.log"
echo "   • Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   • Kill backend:  kill $BACKEND_PID"
echo "   • Kill frontend: kill $FRONTEND_PID"
echo "   • Kill both:     kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop services and exit..."
echo ""

# Save PIDs to file for easy cleanup
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; rm -f logs/*.pid; echo '✅ Services stopped'; exit 0" INT

# Keep script running
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "⚠️  Backend process died. Check logs/backend.log"
        kill $FRONTEND_PID 2>/dev/null
        rm -f logs/*.pid
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚠️  Frontend process died. Check logs/frontend.log"
        kill $BACKEND_PID 2>/dev/null
        rm -f logs/*.pid
        exit 1
    fi
    
    sleep 5
done

