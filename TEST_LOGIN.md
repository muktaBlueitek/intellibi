# Testing Login - Troubleshooting Guide

## Quick Fix: Create Test Users

Run this command to create/verify test users:

```bash
cd backend
source venv/bin/activate  # If using virtual environment
python scripts/create_test_user.py
```

Or run the full seed script:

```bash
cd backend
source venv/bin/activate
python scripts/seed_data.py
```

## Test Credentials

### Admin User:
- **Username:** `admin`
- **Password:** `admin123`

### Regular User:
- **Username:** `user`
- **Password:** `user123`

## Verify Backend is Running

1. Check if backend is accessible:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. Test login endpoint directly:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

   Should return a JSON with `access_token` and `token_type`.

## Common Issues

### 1. Users Don't Exist
- **Solution:** Run the seed script or create_test_user.py

### 2. Database Not Connected
- **Solution:** Make sure Docker database is running:
  ```bash
  docker compose up -d db
  ```

### 3. Backend Not Running
- **Solution:** Start the backend server:
  ```bash
  cd backend
  source venv/bin/activate
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

### 4. CORS Issues
- **Solution:** Check if frontend is making requests to correct backend URL
- Default: `http://localhost:8000/api/v1`

### 5. Password Hash Mismatch
- **Solution:** Run create_test_user.py to reset passwords

## Debug Steps

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try to login
4. Check the login request:
   - Status code (should be 200)
   - Response body (should have access_token)
   - Request payload (should have username and password)

5. Check browser console for JavaScript errors

## Manual API Test

Test the login API directly using curl:

```bash
# Test admin login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Expected response:
# {"access_token":"eyJ...","token_type":"bearer"}
```

If this works but the frontend doesn't, the issue is in the frontend code or CORS.
