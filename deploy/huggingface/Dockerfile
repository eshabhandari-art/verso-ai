# Single-container image for Hugging Face Spaces (Docker SDK).
# Runs Ollama + the FastAPI backend, which also serves the built React frontend.
# The Space only needs this file and README.md; the code is cloned from GitHub at build time.

# ── Source ──────────────────────────────────────────────────
FROM alpine/git:latest AS src
ARG REPO=https://github.com/eshabhandari-art/verso-ai.git
ARG REF=main
RUN git clone --depth 1 --branch ${REF} ${REPO} /src

# ── Frontend build ──────────────────────────────────────────
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY --from=src /src/frontend/package.json /src/frontend/package-lock.json ./
RUN npm ci
COPY --from=src /src/frontend/ ./
RUN npm run build

# ── Runtime ─────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends espeak-ng ffmpeg fonts-dejavu-core curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Ollama binary + runtime libs from the official image
COPY --from=ollama/ollama:latest /usr/bin/ollama /usr/bin/ollama
COPY --from=ollama/ollama:latest /usr/lib/ollama /usr/lib/ollama

# Spaces run the container as uid 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    OLLAMA_HOST=http://127.0.0.1:11434 \
    OLLAMA_MODELS=/home/user/.ollama/models \
    OLLAMA_MAX_LOADED_MODELS=1 \
    OLLAMA_NUM_PARALLEL=1 \
    PYTHONUNBUFFERED=1

# Bake models into the image so a cold start doesn't re-download ~3 GB
RUN ollama serve > /tmp/ollama.log 2>&1 & \
    until curl -s http://127.0.0.1:11434/api/tags > /dev/null; do sleep 1; done && \
    ollama pull qwen2.5:1.5b && \
    ollama pull qwen2.5:3b && \
    ollama pull nomic-embed-text && \
    pkill ollama || true

WORKDIR /home/user/app

COPY --from=src --chown=user /src/backend/requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

COPY --from=src --chown=user /src/backend/ ./
# Merge the fresh build over static/ (keeps stock-videos, bg-images, sound-effects)
COPY --from=frontend --chown=user /frontend/dist/ ./static/
COPY --from=src --chown=user /src/deploy/huggingface/start.sh /home/user/start.sh

RUN mkdir -p data/embeddings data/audio_cache data/video_cache tts/models

# Piper voice models (same as backend/Dockerfile)
RUN python -c "\
import urllib.request, os; \
os.makedirs('tts/models', exist_ok=True); \
hf = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en'; \
models = [('en_GB/jenny_dioco/medium', 'en_GB-jenny_dioco-medium'), ('en_US/libritts_r/medium', 'en_US-libritts_r-medium')]; \
[urllib.request.urlretrieve(f'{hf}/{m}/{p}{e}', f'tts/models/{p}{e}') for m, p in models for e in ['.onnx', '.onnx.json']]; \
print('Piper voice models downloaded')"

EXPOSE 7860
CMD ["bash", "/home/user/start.sh"]
