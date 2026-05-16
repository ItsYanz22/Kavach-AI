# ============================================================================
# KAVACH AI - DEVELOPMENT DOCKERFILE
# ============================================================================
# Multi-stage build for local development with Docker Compose
# Supports hot-reload for both frontend and backend
# ============================================================================

# ────────────────────────────────────────────────────────────────────────────
# Stage: Frontend Build (Node.js + Vite)
# ────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend

WORKDIR /app/frontend

# Copy package files first for better Docker layer caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps --no-optional

# Copy all frontend source code
COPY frontend/ .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server with proper host binding
# The app inside the container needs to listen on 0.0.0.0 to be accessible from outside
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]


# ────────────────────────────────────────────────────────────────────────────
# Stage: Python Backend (Alpine-based Python)
# ────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend

# Production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install dependencies
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import fastapi, uvicorn, pydantic; print('✓ FastAPI stack verified')"

# Copy backend code
COPY backend/ ./backend/

# Expose backend port
EXPOSE 8000

# Run Uvicorn with auto-reload for development
# --reload enables hot-reload when files change
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
