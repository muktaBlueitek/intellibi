#!/bin/bash

# Start Backend Server
echo "Starting IntelliBI Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Check if database is running (Docker)
if ! docker ps | grep -q intellibi-db; then
    echo "Starting database with Docker..."
    cd ..
    docker compose up -d db
    echo "Waiting for database to be ready..."
    sleep 5
    cd backend
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the backend server
echo "Starting FastAPI server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
