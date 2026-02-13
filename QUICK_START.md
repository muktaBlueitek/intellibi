# Quick Start Guide - Run IntelliBI Project

## ⚠️ Prerequisites

1. **Start Docker Desktop** - Must be running first!
2. **Python 3.10+** installed
3. **Node.js 18+** installed

## 🚀 Quick Start (3 Terminal Windows)

### Terminal 1: Database
```bash
cd /Users/muktajaiswal/BlueItek
docker compose up -d db
```

### Terminal 2: Backend
```bash
cd /Users/muktajaiswal/BlueItek/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Create test users
python scripts/create_test_user.py

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Frontend
```bash
cd /Users/muktajaiswal/BlueItek/frontend

# Install dependencies (first time only)
npm install

# Start frontend dev server
npm run dev
```

## ✅ Verify It's Working

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Should return: `{"status":"healthy"}`

2. **Test Login API:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```
   Should return a JSON with `access_token`

3. **Open in Browser:**
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs

## 🔑 Login Credentials

- **Admin:** username=`admin`, password=`admin123`
- **User:** username=`user`, password=`user123`

## 🐛 Troubleshooting

### Docker Not Running
```bash
# Check Docker status
docker ps

# If error, start Docker Desktop application
```

### Backend Won't Start
- Check if port 8000 is in use: `lsof -i :8000`
- Make sure virtual environment is activated
- Check backend logs for errors

### Frontend Won't Start
- Check if port 3000 is in use: `lsof -i :3000`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Database Connection Error
- Make sure Docker database is running: `docker ps | grep intellibi-db`
- Check database logs: `docker compose logs db`

### Login Not Working
1. Make sure test users exist:
   ```bash
   cd backend
   source venv/bin/activate
   python scripts/create_test_user.py
   ```

2. Check browser console (F12) for errors
3. Check Network tab to see if login request is being sent
4. Verify backend is running and accessible

## 📝 Notes

- Backend runs on: http://localhost:8000
- Frontend runs on: http://localhost:3000
- Database runs in Docker on port 5432
- All services must be running for the app to work
