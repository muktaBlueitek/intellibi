# Troubleshooting Guide

## Common Errors and Solutions

### 1. Backend Errors

#### "Cannot connect to database"
**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Make sure Docker is running
docker ps

# Start database
docker compose up -d db

# Wait a few seconds, then try again
```

#### "Module not found" errors
**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### "Port already in use"
**Error:** `Address already in use` or `port 8000 is already in use`

**Solution:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### 2. Frontend Errors

#### "Cannot find module" errors
**Error:** `Cannot find module 'react'` or similar

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### "Port 3000 already in use"
**Error:** `Port 3000 is already in use`

**Solution:**
```bash
# Find and kill process
lsof -ti:3000 | xargs kill -9

# Or change port in vite.config.ts
```

#### "Network Error" or "CORS Error"
**Error:** `Network Error` or `CORS policy` error

**Solution:**
- Make sure backend is running on http://localhost:8000
- Check if API_BASE_URL is correct in frontend
- Backend should allow CORS (check main.py)

### 3. Authentication Errors

#### "Incorrect username or password"
**Error:** Login fails even with correct credentials

**Solution:**
```bash
# Create/verify test users
cd backend
source venv/bin/activate
python scripts/create_test_user.py
```

#### "401 Unauthorized"
**Error:** Getting 401 errors after login

**Solution:**
- Check if token is being stored: `localStorage.getItem('token')` in browser console
- Verify token is being sent in Authorization header
- Check backend logs for JWT errors

### 4. Database Errors

#### "relation does not exist"
**Error:** `relation "users" does not exist`

**Solution:**
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

#### "Migration errors"
**Error:** Alembic migration fails

**Solution:**
```bash
# Check current migration status
alembic current

# Upgrade to latest
alembic upgrade head

# If stuck, check migration files
alembic history
```

### 5. Docker Errors

#### "Cannot connect to Docker daemon"
**Error:** Docker daemon not running

**Solution:**
- Start Docker Desktop application
- Wait for it to fully start
- Verify: `docker ps`

#### "Port already allocated"
**Error:** Port 5432 already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :5432

# Stop conflicting service or change port in docker-compose.yml
```

## How to Get Help

When reporting an error, please provide:

1. **Error Message:** Copy the full error message
2. **Where it occurs:** Backend terminal, frontend terminal, or browser console
3. **Steps to reproduce:** What were you doing when it happened?
4. **Environment:**
   - Operating System
   - Python version: `python3 --version`
   - Node version: `node --version`
   - Docker version: `docker --version`

## Quick Diagnostic Commands

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check if database is running
docker ps | grep intellibi-db

# Check backend logs
# (look at the terminal where uvicorn is running)

# Check frontend console
# (open browser DevTools F12, check Console tab)

# Test login API directly
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Still Having Issues?

1. Check all services are running:
   - Docker database: `docker ps`
   - Backend: http://localhost:8000/api/v1/health
   - Frontend: http://localhost:3000

2. Check logs:
   - Backend terminal output
   - Browser console (F12)
   - Network tab in browser DevTools

3. Verify environment:
   - Virtual environment activated for backend
   - Dependencies installed (backend and frontend)
   - Database migrations run
