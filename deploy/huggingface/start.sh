#!/usr/bin/env bash
# Container entrypoint for Hugging Face Spaces: start Ollama, wait for it, then the API.
set -e

ollama serve > /tmp/ollama.log 2>&1 &

echo "Waiting for Ollama..."
until curl -s http://127.0.0.1:11434/api/tags > /dev/null; do sleep 1; done
echo "Ollama is up."

cd /home/user/app
exec uvicorn main:app --host 0.0.0.0 --port 7860
