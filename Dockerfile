# Production image for Render (free tier, 512 MB RAM).
# Uses the Gemini API instead of local Ollama models; the FastAPI backend also
# serves the built React frontend.

# ── Frontend build ──────────────────────────────────────────
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Runtime ─────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends espeak-ng ffmpeg fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
# Merge the fresh build over static/ (keeps stock-videos, bg-images, sound-effects)
COPY --from=frontend /frontend/dist/ ./static/

RUN mkdir -p data/embeddings data/audio_cache data/video_cache

ENV LLM_PROVIDER=gemini \
    FFMPEG_THREADS=1 \
    PYTHONUNBUFFERED=1

# Render provides $PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
