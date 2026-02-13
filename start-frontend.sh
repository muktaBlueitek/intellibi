#!/bin/bash

# Start Frontend Server
echo "Starting IntelliBI Frontend..."

cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start the frontend dev server
echo "Starting Vite dev server on http://localhost:3000"
npm run dev
