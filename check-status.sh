#!/bin/bash

echo "=== IntelliBI Project Status ==="
echo ""

# Check Docker
echo "1. Docker Status:"
if docker ps &>/dev/null; then
    echo "   ✓ Docker is running"
    if docker ps | grep -q intellibi-db; then
        echo "   ✓ Database container is running"
    else
        echo "   ✗ Database container is NOT running"
        echo "   Run: docker compose up -d db"
    fi
else
    echo "   ✗ Docker is NOT running"
    echo "   Please start Docker Desktop"
fi
echo ""

# Check Backend
echo "2. Backend Status:"
if curl -s http://localhost:8000/api/v1/health &>/dev/null; then
    echo "   ✓ Backend is running on http://localhost:8000"
else
    echo "   ✗ Backend is NOT running"
    echo "   Run: ./start-backend.sh"
fi
echo ""

# Check Frontend
echo "3. Frontend Status:"
if curl -s http://localhost:3000 &>/dev/null; then
    echo "   ✓ Frontend is running on http://localhost:3000"
else
    echo "   ✗ Frontend is NOT running"
    echo "   Run: ./start-frontend.sh"
fi
echo ""

echo "=== Access URLs ==="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
