# Kavach AI – Complete Deployment Guide

> **Production-ready guide for deploying Kavach AI Cyber-Safety system to Google Cloud Run**

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Local Setup & Testing](#local-setup--testing)
3. [Docker Build & Test](#docker-build--test)
4. [Google Cloud Setup](#google-cloud-setup)
5. [Deployment Steps](#deployment-steps)
6. [Environment Variables](#environment-variables)
7. [Database Setup](#database-setup)
8. [Custom Domain](#custom-domain)
9. [Monitoring & Analytics](#monitoring--analytics)
10. [Agent Architecture](#agent-architecture)
11. [Recommended Cloud Run Settings](#recommended-cloud-run-settings)
12. [Future Enhancements](#future-enhancements)

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│     User Browser (Frontend)         │
│  (React/Vite @ http://kavach.ai)   │
└──────────────┬──────────────────────┘
               │ HTTPS
               ↓
┌─────────────────────────────────────┐
│     Google Cloud Run Container      │
│  (Single Python 3.11 Container)     │
├─────────────────────────────────────┤
│  FastAPI Backend (Port 8080)        │
│  ├─ /health (Health check)         │
│  ├─ /detect (Scam Detection)       │
│  ├─ /explain (Deep Analysis)       │
│  ├─ /defense (Defense Strategies)  │
│  ├─ /war-room (Live Incident Mode) │
│  └─ / (Serves React Frontend)      │
├─────────────────────────────────────┤
│  Agents System                      │
│  ├─ Infiltrator (Attack Simulator) │
│  ├─ Forensic (Scam Analyst)        │
│  └─ Mentor (Defense Coach)         │
├─────────────────────────────────────┤
│  Logging & Analytics                │
│  ├─ logs/                          │
│  ├─ analytics/                     │
│  └─ threat_history/                │
└──────────────┬──────────────────────┘
               │
               ├─→ Database (Supabase PostgreSQL)
               ├─→ LLM API (Groq / Gemini)
               └─→ Threat Intelligence APIs
```

### Why Single Container?

✅ **Simpler deployment** - One image, one service  
✅ **Shared context** - Backend has direct access to frontend assets  
✅ **Reduced latency** - No network hop between frontend and backend  
✅ **Cloud Run optimized** - Designed for stateless containers  
✅ **Cost efficient** - One container = one billing unit  

---

## Local Setup & Testing

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Docker
docker --version

# Google Cloud CLI
gcloud --version
```

### Step 1: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build frontend (outputs to dist/)
npm run build

# OR run development server (port 5173)
npm run dev
```

### Step 2: Setup Backend

```bash
cd ../backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add your API keys:
# - GEMINI_API_KEY or GROQ_API_KEY
# - DATABASE_URL (for production)
```

### Step 3: Run Backend Locally

```bash
# From backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# OR directly
python main.py
```

**Test:** `curl http://localhost:8000/health`

### Step 4: Test Frontend + Backend Together

```bash
# In separate terminal from backend directory
# Frontend needs to know backend URL
export VITE_API_URL=http://localhost:8000

cd ../frontend
npm run dev
```

Visit: `http://localhost:5173`

---

## Docker Build & Test

### Build Docker Image

```bash
# From project root
docker build -t kavach-ai:latest .

# Verify image was created
docker images | grep kavach-ai
```

### Run Container Locally

```bash
# Run container
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key_here \
  kavach-ai:latest

# Test in browser/curl
curl http://localhost:8080/health
```

**Expected Response:**
```json
{"success": true, "data": {"status": "ok"}, "message": "Server healthy"}
```

### Full Endpoint Test

```bash
# Health check
curl http://localhost:8080/health

# Scam detection
curl -X POST http://localhost:8080/detect \
  -H "Content-Type: application/json" \
  -d '{"text":"Click here to claim your prize!"}'

# Frontend is served at root
curl http://localhost:8080/
```

**If everything works locally → Ready for Cloud Deployment** ✅

---

## Google Cloud Setup

### Step 1: Install Google Cloud CLI

```bash
# Download from:
https://cloud.google.com/sdk/docs/install

# After installation, authenticate
gcloud auth login

# List your projects
gcloud projects list
```

### Step 2: Create Google Cloud Project

Option A: **Via Console** (UI)
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Click "Create Project"
- Name: `kavach-ai`
- Click "Create"

Option B: **Via CLI**
```bash
gcloud projects create kavach-ai --name="Kavach AI"
```

### Step 3: Enable Required APIs

```bash
# Set your project ID
export PROJECT_ID=kavach-ai
gcloud config set project $PROJECT_ID

# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API (optional, for image storage)
gcloud services enable containerregistry.googleapis.com
```

### Step 4: Set Default Region

```bash
# Use your preferred region (asia-south1 for India)
gcloud config set run/region asia-south1

# List available regions
gcloud run regions list
```

---

## Deployment Steps

### Option A: One-Command Deploy (Easiest)

```bash
# From project root
gcloud run deploy kavach-ai \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars GEMINI_API_KEY=your_key_here

# Google Cloud automatically:
# ✅ Reads Dockerfile
# ✅ Builds image
# ✅ Pushes to registry
# ✅ Deploys to Cloud Run
# ✅ Generates HTTPS URL
```

**Output Example:**
```
Service [kavach-ai] revision [kavach-ai-00001] has been deployed
and is serving 100 percent of traffic.
Service URL: https://kavach-ai-xxxxx-asia-south1.a.run.app
```

### Option B: Deploy to Existing Service (Updates)

```bash
gcloud run deploy kavach-ai \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080
```

### Option C: Manual Build & Push (Advanced)

```bash
# Build image
docker build -t gcr.io/$PROJECT_ID/kavach-ai:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/kavach-ai:latest

# Deploy from registry
gcloud run deploy kavach-ai \
  --image gcr.io/$PROJECT_ID/kavach-ai:latest \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080
```

---

## Environment Variables

### Set Environment Variables

```bash
gcloud run services update kavach-ai \
  --region asia-south1 \
  --set-env-vars=GEMINI_API_KEY=your_actual_key,\
DATABASE_URL=your_db_url,\
GROQ_API_KEY=your_groq_key,\
ENVIRONMENT=production
```

### Required Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini API | `AIzaSy...` |
| `GROQ_API_KEY` | Groq LLM API | `gsk_...` |
| `DATABASE_URL` | PostgreSQL (Supabase) | `postgresql://...` |
| `PORT` | Container port (auto: 8080) | `8080` |
| `ENVIRONMENT` | dev/staging/production | `production` |

### Access Environment Variables in Code

```python
import os

API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./kavach.db")
ENV = os.getenv("ENVIRONMENT", "development")
```

---

## Database Setup

### Option 1: Supabase (Recommended - Free Tier)

**Why Supabase?**
- ✅ PostgreSQL database
- ✅ Free tier includes 500MB storage
- ✅ Built-in authentication
- ✅ Real-time subscriptions
- ✅ Easy scaling

**Setup:**

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create project in region closest to your users
4. Go to **Settings** → **Database** → Copy connection string
5. Export as environment variable:

```bash
gcloud run services update kavach-ai \
  --set-env-vars DATABASE_URL='postgresql://user:password@host/dbname'
```

### Option 2: Google Cloud SQL

```bash
# Create Cloud SQL instance
gcloud sql instances create kavach-db \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region asia-south1

# Create database
gcloud sql databases create kavach \
  --instance kavach-db

# Get connection string
gcloud sql instances describe kavach-db
```

### Option 3: Keep SQLite (Development Only)

```python
# In backend/database.py
import sqlite3
DATABASE_URL = "sqlite:///./kavach.db"
```

**Note:** SQLite is single-file, perfect for dev but not for production multi-instance deployments.

---

## Custom Domain

### Add Custom Domain to Cloud Run

**Prerequisites:**
- Domain registered (e.g., kavachai.tech)
- DNS access

**Steps:**

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click your service `kavach-ai`
3. Click **Manage Custom Domains**
4. Click **Add Mapping**
5. Select your domain (or add new)
6. Verify ownership in DNS settings
7. Wait for SSL certificate generation (5-10 min)

**Manual DNS Update:**

```bash
# Cloud Run will give you a CNAME record
# Add to your DNS provider:

# In DNS settings, add CNAME:
# Name: kavachai.tech
# Target: ghs.googlehosted.com

# Or add A record:
# Name: kavachai.tech
# IP: 216.239.32.21  (Google's IP)
```

---

## Monitoring & Analytics

### View Logs

```bash
# Real-time logs
gcloud run logs read kavach-ai --region asia-south1 --limit 100

# Stream logs
gcloud run logs read kavach-ai --region asia-south1 --follow

# JSON format
gcloud run logs read kavach-ai --region asia-south1 --format json
```

### Accessing Local Logs

```bash
# Frontend requests & detections
cat backend/logs/app.log

# Threat history
cat backend/logs/threat_history/threats_20260515.jsonl

# Agent analytics
cat backend/analytics/agent_outputs_20260515.jsonl

# User decisions
cat backend/analytics/decisions_20260515.jsonl
```

### Using Logger Module

```python
from logger import log_detection, log_user_decision, log_agent_output, get_analytics_summary

# Log a detection
log_detection(
    user_input="Click here to win!",
    classification="SCAM",
    confidence=0.95,
    agent="Forensic"
)

# Get analytics
summary = get_analytics_summary(days=7)
print(summary)
# {'total_detections': 150, 'scam_count': 105, 'safe_count': 45, ...}
```

### Set Up Alerts

```bash
# In Cloud Run console:
# 1. Go to your service
# 2. Click "Monitoring"
# 3. Create alert policy for:
#    - Error rate > 5%
#    - Response time > 5s
#    - Request count drops to 0
```

---

## Agent Architecture

### Current Single-Prompt Model ❌

```
User Input
    ↓
One Giant Prompt
    ↓
One LLM Call
    ↓
One Response
```

**Problems:**
- Expensive LLM calls
- Limited context switching
- Inflexible routing

### Recommended Multi-Agent Model ✅

```
User Input
    ↓
Coordinator Agent
├─ Classify threat type
├─ Determine severity
└─ Route to specialized agent
    ↓
    ├─→ Infiltrator Agent (Attack simulation)
    │   └─ Demonstrates attack technique
    │
    ├─→ Forensic Agent (Analysis)
    │   └─ Decomposes scam tactics
    │
    └─→ Mentor Agent (Defense)
        └─ Teaches counter-measures
    ↓
Response to User
```

### Implementation Example

```python
# backend/agents/coordinator.py

from agent_manager import AgentManager

class CoordinatorAgent:
    def __init__(self):
        self.coordinator = AgentManager("Coordinator")
        self.infiltrator = AgentManager("Infiltrator")
        self.forensic = AgentManager("Forensic")
        self.mentor = AgentManager("Mentor")
    
    def process_input(self, user_input: str):
        # Step 1: Classify threat
        classification = self.coordinator.send_message(
            f"Classify this message as PHISHING, MALWARE, SCAM, or SAFE: {user_input}"
        )
        
        # Step 2: Route to specialized agent
        if "SCAM" in classification:
            analysis = self.forensic.send_message(
                f"Deep analyze this scam: {user_input}"
            )
            defense = self.mentor.send_message(
                f"Teach user how to defend against: {analysis}"
            )
            return {"analysis": analysis, "defense": defense}
        
        return {"classification": classification}
```

---

## Recommended Cloud Run Settings

### Memory & CPU Configuration

| Use Case | Memory | CPU | Concurrency |
|----------|--------|-----|-------------|
| Development | 512MB | 1 | 2 |
| **Production** | **2GB** | **2** | **10** |
| High Traffic | 4GB | 4 | 50 |
| Premium | 8GB | 4 | 100 |

### Set Cloud Run Configuration

```bash
gcloud run services update kavach-ai \
  --region asia-south1 \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 10 \
  --timeout 3600 \
  --max-instances 100
```

### Autoscaling

```bash
# Cloud Run automatically scales from 0 to max-instances
# Default behavior (free tier friendly):
# - Scales down to 0 when no traffic
# - Scales up on demand
# - You only pay for compute time used

# To require minimum instances (costs more):
gcloud run services update kavach-ai \
  --region asia-south1 \
  --min-instances 2
```

---

## Future Enhancements

### Phase 1: Quick Wins (Week 1)

- [ ] Add Redis caching for LLM responses
- [ ] Implement JWT authentication
- [ ] Add user history tracking
- [ ] Create admin dashboard

### Phase 2: AI Optimization (Week 2-3)

- [ ] Implement vector database (Pinecone/Weaviate)
- [ ] Add RAG (Retrieval-Augmented Generation)
- [ ] Multi-turn conversation memory
- [ ] Agent chain optimization

### Phase 3: Advanced Features (Month 2)

- [ ] WebSocket support for live threat monitoring
- [ ] Real-time threat intelligence integration
- [ ] Mobile app integration
- [ ] Team collaboration features

### Phase 4: Scale & Monetize (Month 3+)

- [ ] API tier pricing
- [ ] Enterprise SSO
- [ ] Advanced analytics dashboard
- [ ] Threat feed API
- [ ] Compliance certifications (ISO, GDPR)

---

## Troubleshooting

### Deploy fails: "Permission denied"

```bash
# Ensure you're authenticated
gcloud auth login

# Check project is set
gcloud config get-value project

# Ensure APIs are enabled
gcloud services list --enabled | grep run
```

### Container crashes

```bash
# Check logs
gcloud run logs read kavach-ai --region asia-south1

# Common issues:
# - Missing API keys (set env vars)
# - Port binding (must use 8080)
# - Timeout (increase --timeout)
```

### Frontend shows 404

```bash
# Ensure frontend/dist exists
npm run build  # In frontend directory

# Dockerfile must copy dist correctly:
# COPY --from=frontend /app/frontend/dist ./backend/static
```

### LLM API Rate Limit

```bash
# Check env variable is set
echo $GEMINI_API_KEY

# Or in gcloud:
gcloud run services describe kavach-ai --region asia-south1

# May need to upgrade API quota
# Go to: https://console.cloud.google.com/apis/dashboard
```

---

## Quick Reference

### Deployment Checklist

- [ ] Frontend built: `npm run build` in frontend/
- [ ] .env file configured with API keys
- [ ] Dockerfile tested locally: `docker build -t kavach-ai .`
- [ ] Google Cloud project created
- [ ] Cloud Run API enabled
- [ ] Deployed: `gcloud run deploy kavach-ai --source .`

### Common Commands

```bash
# Deploy
gcloud run deploy kavach-ai --source . --region asia-south1 --allow-unauthenticated

# View logs
gcloud run logs read kavach-ai --region asia-south1 --limit 100

# Update env vars
gcloud run services update kavach-ai --set-env-vars KEY=VALUE

# View service status
gcloud run services describe kavach-ai --region asia-south1

# Delete service (cleanup)
gcloud run services delete kavach-ai --region asia-south1
```

---

**Last Updated:** May 15, 2026  
**Status:** Production Ready ✅  
**Maintained by:** Kavach AI Team
