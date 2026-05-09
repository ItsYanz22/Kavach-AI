# 🛡️ Kavach AI Ecosystem

<p align="center">
  <b>Built for the Gen AI Hackathon</b><br>
  <i>An interactive cybercrime survival simulator and holistic AI-powered digital defense platform.</i>
</p>

---

## 🚨 The Problem

- ⚔️ **Tactical Ignorance**: People know the *name* of a scam (e.g., UPI Scam) but not the *trick* (e.g., “Request” vs. “Pay”).
- 🎭 **AI-Enhanced Fraud**: Deepfakes and AI voice cloning are emerging as our biggest threats, but current education hasn’t caught up.
- 📜 **Static Advice**: Reading lists of “Safety Tips” doesn’t build the reflex to spot scams in real-time.

## 💡 The Solution: Kavach Agentic Ecosystem

Kavach AI is not just an awareness tool; it's a dynamic training and defense platform. Our ecosystem uses three specialized LLM agents to simulate, dissect, and defend against cyber attacks:

1. 🕵️ **The Infiltrator Agent**  
   - Acts as a simulated scammer, throwing dynamic, real-time threat scenarios via WebSockets.  
   - Sends fake SMS, phishing emails, or AI-generated voice scams in a safe environment.

2. 🔍 **The Forensic Agent**  
   - Breaks down the attack step-by-step.  
   - Analyzes suspicious messages, highlights fake URLs, and explains the attacker psychology.

3. 🛡️ **The Defense Mentor**  
   - Evaluates your security posture in real-time.  
   - Guides users through safe responses and calculates an ongoing "Security Health Score."

---

## ✨ Key Features

- 🧪 **Interactive War Room**: Face live, simulated threats to build reflexes, not just awareness.
- 💬 **Forensic Message Scanner**: Paste suspicious text or links to get an instant, AI-driven breakdown.
- 🛡️ **Dynamic Dashboards**: Real-time evaluation of your cybersecurity health.
- ⚡ **Unified Architecture**: A beautiful React frontend backed by a high-performance FastAPI and Agentic Websocket deployment.

---

## 🛠️ Technology Stack

- **Frontend**: React, Vite, Tailwind CSS / Custom CSS, WebSockets.
- **Backend / Orchestrator**: FastAPI, Python, Uvicorn.
- **AI Core**: Google Gemini model integrating dynamic prompts and live session data.
- **Deployment**: Docker, Google Cloud Run ready.

---

## 🚀 Getting Started (Run Locally)

The entire ecosystem (Frontend, REST routes, and Agentic WebSockets) runs unified on **Port 8000** for seamless usage. You can be up and running in minutes!

### Prerequisites
- Python 3.11+
- Node.js 18+
- Your **Groq API Key**

### 1. Clone the repository
```bash
git clone <repository-url>
cd kavach-ai-cyber-safety
```

### 2. Configure API Key
Create a `.env` file in the backend directory. This is crucial for the AI Agents.
```bash
# kavach_backend/.env
GROQ_API_KEY=your_actual_api_key_here
```

### 3. Quick Start (Windows)
We provide a unified batch script that effortlessly builds the frontend and runs the backend orchestrator.
```bat
run_integrated.bat
```

**Alternative: Manual Start**
If you prefer to start them manually or are on Mac/Linux:
```bash
# Terminal 1: Build Frontend
cd kavach_frontend
npm install
npm run build

# Terminal 2: Run Unified Backend
cd ../kavach_backend
# Copy the built UI to the backend static folder
xcopy ..\kavach_frontend\dist static /E /I /Y   # Use `cp -r` on Linux/Mac
pip install -r requirements.txt
python main.py
```

### 4. Access the Platform
Navigate to **http://localhost:8000** in your browser. The application will automatically connect to WebSockets and initialize the AI Agents!

---

## ☁️ Deployment (Cloud Ready in Minutes)

Kavach AI is fully Dockerized and optimized for platforms like Google Cloud Run.

### 1. Build the Production Image
Ensure your Docker daemon is running, then execute:
```bash
docker build -t kavach-ai-ecosystem .
```

### 2. Run Locally via Docker (Verification)
```bash
docker run -p 8000:8000 --env GEMINI_API_KEY=your_actual_api_key kavach-ai-ecosystem
```

### 3. Deploy to Google Cloud Run
Since the application is packaged natively for port 8000, you can push it immediately to GCP:
```bash
# Submit build to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/kavach-ai

# Deploy to Cloud Run
gcloud run deploy kavach-ai --image gcr.io/PROJECT-ID/kavach-ai --platform managed --port 8000 --allow-unauthenticated
```
*(Ensure you securely configure the `GEMINI_API_KEY` environmental variable in the Google Cloud Console).*

---

### API Endpoints Reference

- **UI Dashboard**: `http://localhost:8000/`
- **Health Check**: `GET /health`
- **Live War Room Stream**: `WS /ws/war-room`
- **Mentorship Score**: `GET /health-score`
- **Message Analyzer**: `POST /detect`