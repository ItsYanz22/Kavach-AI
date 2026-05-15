# ---------- FRONTEND BUILD ----------
FROM node:20 AS frontend

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ .
RUN npm run build

# ---------- BACKEND ----------
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (includes agents/, routes/, services/)
COPY backend ./backend

# Copy built frontend static files
COPY --from=frontend /app/frontend/dist ./backend/static

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run backend (serves frontend + API from same container)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
