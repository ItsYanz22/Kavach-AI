# 🛡️ Kavach AI — Cyber Safety Simulator

Kavach AI is an interactive multi-agent cyber safety simulator designed to help users experience and understand real-world cyber scams before they happen in reality.

Built during the **Google Cloud Gen AI Academy APAC 2026 Edition**, Kavach AI focuses on transforming cybersecurity awareness from passive learning into active decision-making.

---

## 🌐 Live Deployment

🚀 Live App:
https://kavach-ai-131822542029.us-central1.run.app/

📦 GitHub Repository:
https://github.com/ItsYanz22/Kavach-AI

---

# 🚨 Problem Statement

Modern cybercrime has evolved rapidly:

* AI-generated scam calls
* Deepfake impersonation
* OTP phishing
* UPI frauds
* Fake KYC alerts
* Investment scams
* Social engineering attacks

Most users are aware these scams exist.

But awareness alone is not enough.

The real challenge is:

> Can users identify and respond correctly *in the moment*?

Kavach AI addresses this gap through realistic, interactive cyber attack simulations.

---

# 💡 What Kavach AI Does

Kavach AI simulates real-world scam conversations inside an immersive “War Room” environment where users interact with dynamic scam scenarios.

Instead of static tutorials, users:

* receive scam messages
* analyze suspicious behavior
* make decisions
* experience consequences safely
* learn cyber safety interactively

The system recreates:

* phishing attacks
* fake bank alerts
* KYC scams
* QR scams
* internship frauds
* fake investment opportunities
* OTP theft attempts
* digital arrest scams
* social engineering attacks

---

# ⚙️ Core Features

## 🧠 Multi-Agent AI Architecture

Kavach AI uses a workflow-driven agentic system:

* **Infiltrator Agent** → Generates scam scenarios
* **Forensic Agent** → Analyzes threats and explains red flags
* **Mentor Agent** → Guides users with safe responses
* **Coordinator Agent** → Orchestrates the simulation flow

---

## 🎭 Realistic War Room Simulator

* WhatsApp-style scam conversations
* Dynamic escalation
* Emotional manipulation tactics
* Realistic Indian cyber fraud patterns
* Decision-based interactions
* Consequence simulation

---

## 🔍 Scam Analysis System

Users can:

* analyze messages
* detect phishing patterns
* identify malicious intent
* understand scam psychology
* receive safety recommendations

---

## 🚫 Interactive User Actions

The War Room supports:

* Ignore
* Block Sender
* Report Scam
* Analyse Message
* Dangerous actions (OTP sharing, payment simulation)

Each action changes the scenario dynamically.

---

## ☁️ Cloud-Native Deployment

* Dockerized architecture
* Google Cloud Run deployment
* FastAPI backend
* React + Vite frontend
* WebSocket real-time communication
* Production-ready infrastructure

---

# 🏗️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 18 • TypeScript • Vite • TailwindCSS • Framer Motion • Shadcn UI |
| **Backend** | FastAPI • Python 3.11 • Uvicorn • WebSockets • SQLAlchemy ORM |
| **Database** | SQLite (Local) • PostgreSQL (Production) |
| **AI/LLM** | Groq API • Mixtral-8x7b-32768 • Llama-3.3-70b-versatile • Multi-Agent Orchestration |
| **Real-time** | WebSocket Protocol • JSON-based Message Streaming |
| **Authentication** | JWT • Bearer Token • Bcrypt |
| **Cloud** | Google Cloud Run • Cloud Build • Secret Manager • Artifact Registry |
| **DevOps** | Docker • Multi-stage Build • Cloud-native Deployment |
| **Monitoring** | Structured JSON Logging • Health Checks • Performance Metrics |

### Featured Components
- **Multi-Agent System**: Infiltrator, Forensic, Mentor agents with workflow coordination
- **Achievement System**: Badge tracking with 8+ milestone types
- **Dynamic Scenario Generation**: AI-powered scam simulation with psychological depth
- **Real-time War Room**: Interactive WebSocket-based scam simulation

---

# 🧩 Architecture Overview

```text
User Input
   ↓
Detection Agent
   ↓
Forensic Analysis
   ↓
Action Recommendation
   ↓
War Room Simulation
   ↓
Learning & Feedback Loop
```

---

# 🚀 Deployment

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/ItsYanz22/Kavach-AI.git
cd Kavach-AI
```

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

### 4. Configure Environment Variables

Create `.env` inside backend:

```env
GROQ_API_KEY=your_key
ENVIRONMENT=development
```

### 5. Run Backend

```bash
uvicorn main:app --reload
```

### 6. Run Frontend

```bash
npm run dev
```

---

# 🐳 Docker Deployment

```bash
docker build -f Dockerfile.production -t kavach-ai .
docker run -p 8080:8080 kavach-ai
```

---

# ☁️ Google Cloud Run Deployment

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/kavach-ai

gcloud run deploy kavach-ai \
  --image gcr.io/PROJECT_ID/kavach-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

# 🧠 Key Learnings

* Multi-agent systems require robust orchestration
* Realistic cyber simulations demand psychological depth
* Deployment challenges are often harder than development
* WebSocket state management is critical in real-time systems
* Production-grade AI systems need strong error recovery

---

# 👥 Team

🎨 Frontend — Simran Das
⚙️ Backend — Twisha Salver
🤖 Agentic AI — Priyanshu Sahoo
☁️ Deployment & Cloud — Bhargavi Sadanand

---

# 🌍 Vision

Kavach AI aims to make cybersecurity education:

* interactive
* immersive
* practical
* accessible

Because in cybersecurity:

> knowing about scams is not enough —
> users must learn how to react under pressure.

---

# 📜 License

MIT License

---

# ⭐ Support

If you found this project interesting:

* star the repository
* share feedback
* contribute improvements
* help spread cyber awareness

Together, we can make the internet safer.
