# Quick Start Guide – Kavach AI

Get up and running with Kavach AI in under 10 minutes.

---

## 1️⃣ Prerequisites

Ensure you have:
- **Python 3.11+** → `python --version`
- **Node.js 18+** → `node --version`
- **Docker** (optional) → `docker --version`
- **API Key** (Gemini or Groq) → Get free key from [google.com/ai](https://google.com/ai)

---

## 2️⃣ Local Development Setup (5 min)

### Clone & Navigate

```bash
cd kavach-ai-cyber-safety
```

### Setup Backend

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GEMINI_API_KEY=your_key_here" > .env

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Expected Output:**
```
VITE v5.x ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Test It

Open browser:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`

---

## 3️⃣ Docker Build & Run (3 min)

### Build Image

```bash
# From project root
docker build -t kavach-ai .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key_here \
  kavach-ai:latest
```

### Test

```bash
# Health check
curl http://localhost:8080/health

# Full app
open http://localhost:8080
```

---

## 4️⃣ Deploy to Cloud (Cloud Run)

### One-Command Deploy

```bash
# Ensure you're authenticated
gcloud auth login

# Set project
export PROJECT_ID=kavach-ai
gcloud config set project $PROJECT_ID

# Deploy!
gcloud run deploy kavach-ai \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

**Output Example:**
```
Service URL: https://kavach-ai-xxxxx-asia-south1.a.run.app
```

Open in browser → Done! 🎉

---

## 5️⃣ Test Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Detect Scam
```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{"text":"Click here to claim your prize!"}'
```

### Explain Scam
```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"text":"Verify your account: https://bit.ly/totally-legit"}'
```

---

## Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `GEMINI_API_KEY` | ✅ | `AIzaSy...` |
| `GROQ_API_KEY` | (Alternative) | `gsk_...` |
| `DATABASE_URL` | ❌ | `postgresql://...` |
| `PORT` | ❌ | `8080` |

Get free API key: https://google.com/ai

---

## 📁 Project Structure

```
kavach-ai-cyber-safety/
├── frontend/              # React/Vite UI
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/               # Python API
│   ├── agents/           # AI agents
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── main.py           # Entry point
│   └── requirements.txt
├── Dockerfile            # Single container
├── docker-compose.yml    # (Optional) Multi-container
├── .dockerignore
├── DEPLOYMENT.md         # Full deployment guide
├── AGENT_ARCHITECTURE.md # Agent design
└── README.md
```

---

## 🚀 Next Steps

1. **Test Locally** → Follow steps 1-2 above
2. **Build Docker** → Step 3
3. **Deploy to Cloud** → Step 4
4. **Configure Domain** → See DEPLOYMENT.md
5. **Advanced Setup** → See AGENT_ARCHITECTURE.md

---

## 🐛 Troubleshooting

### "Module not found" Error

```bash
# Ensure dependencies are installed
cd backend
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "API Key Invalid"

```bash
# Check your key is set
echo $GEMINI_API_KEY

# Set it if missing
export GEMINI_API_KEY=your_actual_key_here

# For Docker:
docker run -e GEMINI_API_KEY=your_key ...
```

### "Port already in use"

```bash
# Use different port
uvicorn main:app --port 9000

# Or kill process using port 8000
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

### "Frontend shows 404"

```bash
# Build frontend first
cd frontend
npm run build

# Then restart backend
cd ../backend
python main.py
```

---

## 📚 Full Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** – Complete deployment guide with Cloud Run setup
- **[AGENT_ARCHITECTURE.md](./AGENT_ARCHITECTURE.md)** – Advanced agent design & optimization
- **[README.md](./README.md)** – Project overview

---

## ❓ Need Help?

```bash
# See all available API endpoints
http://localhost:8000/docs  # Swagger UI

# Check backend logs
tail -f backend/logs/app.log

# View analytics
cat backend/analytics/*.jsonl
```

---

**Happy Deploying! 🚀**

Questions? Check DEPLOYMENT.md or AGENT_ARCHITECTURE.md.
