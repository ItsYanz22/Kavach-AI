# Kavach AI – Deployment & Configuration Guide
## Complete Guide to Fixing "Failed to Fetch" Issues

---

## QUICK DIAGNOSIS: "Failed to Fetch" Error

The "Failed to Fetch" error during login typically means the frontend cannot reach the backend API.

### Root Causes Checklist:
- ❌ Backend not running
- ❌ Wrong API URL (frontend pointing to wrong host/port)
- ❌ CORS not configured correctly
- ❌ Network connectivity issue
- ❌ Mixed HTTP/HTTPS (insecure requests from HTTPS page)

### Immediate Fix:
1. Check browser console (F12) for specific error messages
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check API_BASE value in console: Open browser DevTools → Console → type `API_BASE`
4. Verify CORS headers in network tab

---

## 📍 SCENARIO 1: LOCAL DEVELOPMENT (Recommended for Debugging)

### Setup: Frontend & Backend on Same Machine

```
Frontend: http://localhost:5173 (Vite dev server)
Backend:  http://localhost:8000 (Uvicorn)
```

### Step 1: Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Copy .env file
cp backend/.env.example backend/.env

# Start backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Frontend Setup (NEW TERMINAL)
```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional, can be empty for local dev)
echo "VITE_BACKEND_URL=" > .env.local

# Start frontend dev server
npm run dev
```

### Step 3: Verify Connection

**In Browser Console (F12):**
```javascript
API_BASE  // Should output: "http://localhost:8000"
getBackendUrl()  // Should output: "http://localhost:8000"
getWsUrl()  // Should output: "ws://localhost:8000/ws/war-room"
```

**Test Login:**
1. Open http://localhost:5173
2. Go to Login page
3. Use test credentials (or signup first)
4. Check browser Network tab for API calls
5. Verify CORS headers are present

### Troubleshooting Local Dev:

**Error: "Failed to Fetch"**
```bash
# 1. Is backend running on :8000?
curl http://localhost:8000/health

# 2. Can you reach it from frontend machine?
# (should return {"status": "healthy", ...})

# 3. Check CORS in response headers:
curl -i -X OPTIONS http://localhost:8000/api/auth/login \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST"
```

**Error: "API error 401"**
- Credentials incorrect
- Password too short (min 8 chars)
- User doesn't exist

**Error: "API error 404"**
- API endpoint changed
- Check backend routers are loaded
- Verify /api/auth/login endpoint exists

---

## 🐳 SCENARIO 2: DOCKER COMPOSE (For Docker Testing)

### Prerequisites:
- Docker installed and running
- Docker Compose installed

### Setup:

```bash
# 1. Start containers
docker-compose up --build

# 2. Wait for output showing services are ready
# Backend: "✅ KAVACH AI 2.0 IS READY TO SERVE"
# Frontend: "ready in XXms"

# 3. Open http://localhost:5173 in browser
```

### How Docker Networking Works:

```
Host Machine:
  - Frontend: http://localhost:5173
  - Backend:  http://localhost:8000

Inside Docker Network (kavach-network):
  - Frontend Container: http://kavach-frontend:5173
  - Backend Container: http://kavach-backend:8000
  - Frontend → Backend: http://backend:8000 (DNS name)
```

### Environment Variables in docker-compose.yml:

```yaml
backend:
  environment:
    # Backend container DNS name for CORS
    - CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

frontend:
  environment:
    # Inside container, use Docker service name
    - VITE_BACKEND_URL=http://backend:8000
    # Tell Vite to listen on all interfaces
    - VITE_HOST=0.0.0.0
```

### API URL Resolution in Docker:

**Frontend running inside container sees:**
- `import.meta.env.VITE_BACKEND_URL` = `"http://backend:8000"`
- So API calls go to: `http://backend:8000/api/auth/login`
- Docker DNS resolves `backend` → `kavach-backend` container IP
- ✅ Request succeeds!

**From Host Machine (localhost:5173):**
- Browser sees VITE_BACKEND_URL not set (only in container env)
- Fallback: Frontend uses `getApiBase()` logic
- dev mode → `http://localhost:8000`
- ✅ Request succeeds!

### Docker Troubleshooting:

**Containers won't start:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild without cache
docker-compose build --no-cache
```

**"Failed to Fetch" from localhost:5173:**
```bash
# 1. Check containers are running
docker ps

# 2. Test backend from host
curl http://localhost:8000/health

# 3. Check frontend environment
docker-compose exec frontend printenv | grep VITE

# 4. Rebuild frontend with correct env
docker-compose build --no-cache frontend
```

**CORS Error in Browser:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Fix:**
```yaml
# Update backend service environment:
environment:
  - CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## ☁️ SCENARIO 3: GOOGLE CLOUD RUN (Production Deployment)

### Architecture in Cloud Run:

```
Client Browser
    ↓ https://my-app.run.app
┌─────────────────────┐
│  Cloud Run Service  │
│  ┌───────────────┐  │
│  │  Frontend     │  │ (served from backend/static/)
│  │  (React SPA)  │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │  Backend      │  │ (FastAPI)
│  │  (FastAPI)    │  │
│  └───────────────┘  │
└─────────────────────┘
```

**Key Point:** Frontend and backend share same origin (same URL, same port)
→ CORS not needed! Same-origin policy automatically allows it.

### Deployment Steps:

```bash
# 1. Build Docker image (using Dockerfile.production)
docker build -f Dockerfile.production -t kavach-ai:prod .

# 2. Test locally
docker run -p 8080:8080 kavach-ai:prod

# 3. Deploy to Cloud Run
gcloud run deploy kavach-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars=GROQ_API_KEY=your_key \
  --set-env-vars=JWT_SECRET_KEY=your_secret
```

### Dockerfile.production Key Points:

```dockerfile
# Stage 1: Build frontend (Vite)
# → Outputs to frontend/dist/

# Stage 2: Runtime
# → Copy frontend/dist/ to backend/static/
# → FastAPI serves /static/* files
# → FastAPI has SPA fallback for index.html
```

### Frontend API URL Logic in Production:

```typescript
// In browser on Cloud Run (https://my-app.run.app):
isDev = false
import.meta.env.VITE_BACKEND_URL = undefined  (not set in build)
API_BASE = window.location.origin  
         = "https://my-app.run.app"

// API calls:
POST https://my-app.run.app/api/auth/login  ✅ Same origin!
```

### Cloud Run Configuration:

**.env variables to set:**
```bash
# Required
GROQ_API_KEY=<your_key>
JWT_SECRET_KEY=<32-char-secret>

# Optional (Cloud Run sets PORT automatically to 8080)
ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./kavach.db

# CORS (should match your Cloud Run domain)
CORS_ORIGINS=https://my-app.run.app,https://my-app-staging.run.app
```

### Cloud Run Troubleshooting:

**"Failed to Fetch" on Cloud Run:**
1. Check API_BASE in browser console
   - Should be: `https://my-app.run.app`
   - NOT: `http://localhost:8000`

2. Check frontend/static/ directory exists
   ```bash
   gcloud run exec kavach-ai --command=ls -la /app/backend/static/
   ```

3. Check Cloud Run logs
   ```bash
   gcloud run logs read kavach-ai --limit 50
   ```

4. Verify backend is running
   ```bash
   curl https://my-app.run.app/health
   ```

**Static files not serving:**
- Verify frontend built successfully in Dockerfile
- Check backend/static/ has index.html
- Verify SPA fallback route in main.py

---

## 🔧 ENVIRONMENT VARIABLE QUICK REFERENCE

### For Local Development:
```bash
# Backend (.env)
GROQ_API_KEY=your_key
DATABASE_URL=sqlite:///./kavach.db
ENVIRONMENT=local

# Frontend (.env.local) - usually empty, let it auto-detect
VITE_BACKEND_URL=
```

### For Docker Compose:
```bash
# Backend (docker-compose.yml service.environment)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ENVIRONMENT=docker-dev

# Frontend (docker-compose.yml service.environment)
VITE_BACKEND_URL=http://backend:8000
VITE_HOST=0.0.0.0
```

### For Cloud Run:
```bash
# Backend (Cloud Run env vars)
GROQ_API_KEY=your_key
JWT_SECRET_KEY=your_secret
ENVIRONMENT=production
CORS_ORIGINS=https://my-app.run.app

# Frontend (built into dist during build, no runtime env needed)
# VITE_BACKEND_URL is not set → uses window.location.origin
```

---

## 🧪 TESTING CHECKLIST

### ✅ Test Local Development:
- [ ] Backend running on :8000
- [ ] Frontend running on :5173
- [ ] Signup works
- [ ] Login works
- [ ] WebSocket connects (/ws/war-room)
- [ ] Dashboard loads
- [ ] Detection works

### ✅ Test Docker Compose:
- [ ] Containers start without errors
- [ ] Frontend accessible on http://localhost:5173
- [ ] Signup works
- [ ] Login works
- [ ] WebSocket connects
- [ ] Backend logs show requests
- [ ] Database persists (kavach.db)

### ✅ Test Cloud Run:
- [ ] Frontend loads
- [ ] API requests work (check Network tab)
- [ ] Login works
- [ ] WebSocket connects (should be wss://)
- [ ] HTTPS (not HTTP)
- [ ] Logs show successful requests

---

## 🚨 COMMON ISSUES & FIXES

| Issue | Cause | Fix |
|-------|-------|-----|
| "Failed to Fetch" on login | Backend not running | Start backend on :8000 |
| CORS error in console | Frontend origin not in CORS_ORIGINS | Add to CORS config |
| WebSocket fails | Using ws:// from HTTPS page | Use wss:// for prod |
| Static files 404 | frontend/dist not copied | Check Dockerfile COPY |
| API returns 401 | Token invalid/expired | Clear localStorage, re-login |
| API returns 404 | Endpoint doesn't exist | Check router prefix (/api) |
| Slow requests | Network latency | Check container resources |

---

## 📋 DEPLOYMENT CHECKLIST

### Before Local Testing:
- [ ] `.env` configured with GROQ_API_KEY
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] No port conflicts (8000, 5173)

### Before Docker Testing:
- [ ] Docker running
- [ ] docker-compose.yml environment vars correct
- [ ] .env files created
- [ ] No container name conflicts

### Before Cloud Run:
- [ ] Dockerfile.production builds successfully
- [ ] frontend/dist/ created
- [ ] backend/static/ contains index.html
- [ ] JWT_SECRET_KEY set (not default)
- [ ] CORS_ORIGINS set correctly
- [ ] Database strategy chosen (SQLite or Cloud SQL)

---

## 📚 Related Files

- [backend/main.py](../backend/main.py) - CORS config, static serving
- [frontend/src/lib/api.ts](../frontend/src/lib/api.ts) - API URL logic
- [frontend/src/auth/AuthContext.tsx](../frontend/src/auth/AuthContext.tsx) - Login logic
- [docker-compose.yml](../docker-compose.yml) - Docker dev setup
- [Dockerfile](../Dockerfile) - Docker dev image
- [Dockerfile.production](../Dockerfile.production) - Cloud Run image

---

## ☁️ SCENARIO 4: RENDER DEPLOYMENT (Production-Ready)

### Why Render?
- Free tier with generous limits
- Automatic deployments from GitHub
- Built-in SSL/HTTPS
- WebSocket support (critical for War Room)
- PostgreSQL database available
- One-click rollback

### Prerequisites:
1. GitHub account with your repo pushed
2. Render account (free at render.com)
3. Groq API key from console.groq.com
4. 5-10 minutes setup time

### Step 1: Create Render Account & Link GitHub

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repos
4. Accept terms

### Step 2: Deploy Backend Service

1. In Render dashboard: **New +** → **Web Service**
2. Select your GitHub repo
3. Configure:
   ```
   Name:           kavach-ai-backend
   Environment:    Docker
   Region:         Closest to you (us-east-1, eu-west-1, etc.)
   Branch:         main
   Dockerfile Path: ./Dockerfile
   ```
4. **Create Web Service**
5. Wait for build (~5-10 minutes)

### Step 3: Set Environment Variables

In Render dashboard → kavach-ai-backend → **Environment** → **Add Environment Variable**

Add each one (all required):

| Key | Value | Notes |
|-----|-------|-------|
| `PORT` | `8080` | Don't change |
| `ENVIRONMENT` | `production` | For Render |
| `DEBUG_MODE` | `false` | Security |
| `GROQ_API_KEY` | `gsk_xxx...` | Get from console.groq.com |
| `JWT_SECRET_KEY` | `your_secret_here_min32chars` | Change to random string |
| `CORS_ORIGINS` | `https://your-app.onrender.com` | Will update after deploy |
| `DATABASE_URL` | *(optional)* | SQLite used by default |

**For CORS_ORIGINS:**
- After first deploy, go to your service URL
- Replace `your-app` with actual service name
- If hosting frontend separately: add that URL too

Example:
```
https://kavach-ai-backend.onrender.com,https://your-vercel-frontend.vercel.app
```

### Step 4: Monitor First Deployment

1. In Render dashboard, go to **Events** tab
2. Watch build logs
3. Look for: **Service is live** ✅
4. Test health endpoint:
   ```
   curl https://your-service-name.onrender.com/health
   ```
   Should return: `{"status": "healthy", ...}`

### Step 5: Deploy Frontend (Optional)

If deploying frontend to Render too:

1. **New +** → **Static Site**
2. Connect same GitHub repo
3. Build command: `cd frontend && npm install && npm run build`
4. Publish directory: `frontend/dist`
5. **Create Static Site**
6. After deploy, update backend `CORS_ORIGINS` with frontend URL

### Common Render Issues & Fixes

**"Build failed"**
- Check build logs in Events
- Usually: missing dependencies
- Solution: Ensure frontend/package-lock.json is committed

**"Service crashed"**
- Check logs in Events tab
- Common: GROQ_API_KEY missing or invalid
- Solution: Verify all env vars are set

**"504 Gateway Timeout"**
- Render free tier has memory limits
- Deploy during off-peak hours
- Use PostgreSQL instead of SQLite for better performance

**WebSocket fails after 55 seconds**
- Render idle timeout
- Backend auto-restarts properly
- War Room auto-reconnects (expected)

**"Failed to Fetch" from frontend**
- Check CORS_ORIGINS includes frontend URL
- Verify HTTPS (not HTTP)
- Check frontend has correct API URL

### Render Free Tier Limitations

| Limit | Impact | Workaround |
|-------|--------|-----------|
| 750 hrs/month | Service sleeps after 15 min idle | Paid plan removes sleep |
| 0.5 CPU | Slow builds | Use builds when fresh |
| 512 MB RAM | No large LLM models | Use API instead (Groq ✓) |
| SQLite only | Database resets | Use PostgreSQL addon |

### Upgrading Render Plan

If you outgrow free tier:
1. Render → Account → Plans
2. Choose Starter ($12/month minimum)
3. Service automatically upgrades (no rebuild needed)

### Monitoring on Render

**Check service health:**
- Render dashboard → Metrics tab
- Shows CPU, memory, response times

**View logs:**
- Render dashboard → Logs tab
- Real-time streaming
- Searchable by keyword

**Auto-redeploy on GitHub push:**
- Already enabled by default
- Push to main → auto-builds and deploys
- Takes 5-10 minutes

---

## 📞 Support

If you're still seeing "Failed to Fetch" errors:

1. **Enable debug logging:**
   ```typescript
   // In browser console:
   localStorage.setItem('debug', 'true')
   location.reload()
   ```

2. **Check all network requests:**
   - Open DevTools (F12)
   - Go to Network tab
   - Try login
   - Look for red X on /api/auth/login request
   - Click it and check Response tab

3. **Check backend logs:**
   ```bash
   # Local development:
   # Look at terminal where you ran uvicorn
   
   # Docker:
   docker-compose logs backend
   
   # Cloud Run:
   gcloud run logs read kavach-ai
   ```

4. **Check API is working:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"password123"}'
   ```

---

**Last Updated:** 2026-05-16
**Version:** Kavach AI 2.0
