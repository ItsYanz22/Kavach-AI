# Stage 1: Build React frontend
FROM node:18-alpine AS frontend
WORKDIR /frontend
COPY kavach_frontend/package*.json ./
RUN npm install
COPY kavach_frontend/ .
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

# Copy backend code (includes agents/)
COPY kavach_backend/ ./kavach_backend/

# Copy built frontend into backend's static folder
COPY --from=frontend /frontend/dist ./kavach_backend/static

# Install Python dependencies
RUN pip install --no-cache-dir -r kavach_backend/requirements.txt

# Cloud Run uses PORT env variable
ENV PORT=8080
EXPOSE 8080

# Run from the kavach_backend directory so imports resolve correctly
WORKDIR /app/kavach_backend
CMD ["python", "main.py"]
