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

# Pre-rendered Explore feed reels (built by .github/workflows/seed-reels.yml).
# Skipped if the release asset doesn't exist yet.
ARG SEED_REELS_URL=https://github.com/eshabhandari-art/verso-ai/releases/download/seed-reels/seed-reels.tar.gz
RUN python -c "\
import sys, tarfile, urllib.request; \
resp = urllib.request.urlopen(sys.argv[1], timeout=300); \
tarfile.open(fileobj=resp, mode='r|gz').extractall('.'); \
print('Seed reels downloaded')" "${SEED_REELS_URL}" || echo "No seed reels found, skipping"

# Demo story reels ("Mira and the Lighthouse"), also shown in Explore.
ARG DEMO_REELS_URL=https://github.com/eshabhandari-art/verso-ai/releases/download/seed-reels/demo-reels.tar.gz?v=1
RUN python -c "import sys, tarfile, urllib.request; resp = urllib.request.urlopen(sys.argv[1], timeout=300); tarfile.open(fileobj=resp, mode='r|gz').extractall('.'); print('Demo reels downloaded')" "${DEMO_REELS_URL}" || echo "No demo reels found, skipping"

ENV LLM_PROVIDER=gemini \
    FFMPEG_THREADS=1 \
    VIDEO_WORKERS=1 \
    LOW_MEMORY_VIDEO=1 \
    PYTHONUNBUFFERED=1

# Render provides $PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
