#!/bin/bash
# IntelliBI Deployment Script
# Usage: ./scripts/deploy.sh [dev|prod]

set -e

MODE=${1:-dev}

echo "IntelliBI Deployment - Mode: $MODE"

if [ "$MODE" = "prod" ]; then
  echo "Production deployment"
  if [ ! -f .env ]; then
    echo "Error: .env file required for production. Copy .env.example and set values."
    exit 1
  fi
  docker-compose -f docker-compose.prod.yml build --no-cache
  docker-compose -f docker-compose.prod.yml up -d
  echo "Production stack started. Backend: http://localhost:8000, Frontend: http://localhost:3000"
elif [ "$MODE" = "dev" ]; then
  echo "Development deployment"
  docker-compose up -d db
  echo "PostgreSQL started. Run backend and frontend locally: cd backend && uvicorn app.main:app; cd frontend && npm run dev"
else
  echo "Usage: ./scripts/deploy.sh [dev|prod]"
  exit 1
fi
