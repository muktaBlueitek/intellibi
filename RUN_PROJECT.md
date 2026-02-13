# How to Run IntelliBI Project

## Prerequisites

1. **Docker Desktop** - Must be running for the database
2. **Python 3.10+** - For backend
3. **Node.js 18+** - For frontend
4. **npm** - For frontend dependencies

## Quick Start

### Option 1: Using Scripts (Recommended)

1. **Start Database:**
   ```bash
   docker compose up -d db
   ```

2. **Start Backend** (in one terminal):
   ```bash
   chmod +x start-backend.sh
   ./start-backend.sh
   ```
   Backend will run on: http://localhost:8000

3. **Start Frontend** (in another terminal):
   ```bash
   chmod +x start-frontend.sh
   ./start-frontend.sh
   ```
   Frontend will run on: http://localhost:3000

### Option 2: Manual Steps

#### Backend Setup:

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start database (if not running)
cd ..
docker compose up -d db
cd backend

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Troubleshooting

### Docker Issues:
- Make sure Docker Desktop is running
- Check with: `docker ps`

### npm Permission Issues:
```bash
sudo chown -R $(whoami) ~/.npm
```

### Database Connection Issues:
- Ensure database container is running: `docker ps | grep intellibi-db`
- Check logs: `docker compose logs db`

### Backend Issues:
- Check if port 8000 is available
- Verify virtual environment is activated
- Check backend logs for errors

### Frontend Issues:
- Check if port 3000 is available
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check browser console for errors

## Environment Variables

### Backend (.env in backend/):
```
OPENAI_API_KEY=your_key_here  # Optional, for chatbot
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

### Frontend (.env in frontend/):
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```
