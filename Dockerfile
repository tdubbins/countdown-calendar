# Multi-stage Dockerfile for integrated production image
# Combines frontend (Ionic Vue) and backend (Flask) into a single container

# =============================================================================
# Stage 1: Build Frontend
# =============================================================================
FROM node:18-alpine AS frontend-build

WORKDIR /frontend

# Copy package files for dependency caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ .

# Build for production (API calls go to same origin /api)
ENV VITE_API_BASE_URL=/api
RUN npm run build

# =============================================================================
# Stage 2: Production Backend with Frontend
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy built frontend from stage 1 into static folder
COPY --from=frontend-build /frontend/dist ./static

# Create data directory for JSON storage
RUN mkdir -p data/calendars

# Environment variables for production
ENV FLASK_ENV=production
ENV SERVE_STATIC=true

# Expose port
EXPOSE 5001

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--threads", "4", "run:app"]
