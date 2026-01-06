#!/bin/bash
# Start script for Databricks Apps deployment
# This script starts the FastAPI backend which serves both API and React static files

set -e  # Exit on error

echo "=== Starting Vantage RWE application ==="
echo "Current directory: $(pwd)"

echo "=== Attempting to start server ==="

# Get the absolute path to the project root
PROJECT_ROOT="$(pwd)"
echo "Project root: $PROJECT_ROOT"

# Use the Python from the virtual environment (Databricks creates .venv)
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    echo "Using Python from .venv"
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
elif [ -f "$PROJECT_ROOT/.venv/bin/python3" ]; then
    echo "Using Python3 from .venv"
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python3"
else
    echo "WARNING: .venv not found, using system Python"
    PYTHON_CMD="python3"
fi

echo "Python: $PYTHON_CMD"
$PYTHON_CMD --version

cd backend

# Start uvicorn using the venv Python (which has access to installed packages)
# Databricks Apps expects port 8000 by default
echo "Starting uvicorn server on port 8000..."
echo "Command: $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"
exec $PYTHON_CMD -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --log-level info

