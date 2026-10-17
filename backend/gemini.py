"""Google Gemini API client — used instead of Ollama when LLM_PROVIDER=gemini.

Requests are spaced GEMINI_MIN_INTERVAL seconds apart (process-wide) to stay
under free-tier rate limits, and 429/5xx responses are retried with backoff.
"""
from __future__ import annotations

import logging
import threading
import time

import httpx

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_EMBED_MODEL, GEMINI_MIN_INTERVAL, EMBED_DIM

log = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MAX_ATTEMPTS = 6
EMBED_BATCH_SIZE = 100

_throttle_lock = threading.Lock()
_last_request = 0.0


def _throttle():
    global _last_request
    with _throttle_lock:
        wait = _last_request + GEMINI_MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request = time.monotonic()


def _post(path: str, body: dict, timeout: float) -> dict:
    if not GEMINI_API_KEY:
        raise httpx.ConnectError("GEMINI_API_KEY is not set")

    last_error: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        _throttle()
        try:
            resp = httpx.post(
                f"{BASE_URL}/{path}",
                json=body,
                headers={"x-goog-api-key": GEMINI_API_KEY},
                timeout=timeout,
            )
        except httpx.TransportError as e:
            last_error = e
            log.warning("Gemini request failed (attempt %d/%d): %s", attempt + 1, MAX_ATTEMPTS, e)
            time.sleep(min(2 ** attempt, 30))
            continue

        if resp.status_code == 429 or resp.status_code >= 500:
            last_error = httpx.HTTPStatusError(
                f"Gemini HTTP {resp.status_code}: {resp.text[:200]}", request=resp.request, response=resp
            )
            wait = min(5 * 2 ** attempt, 60)
            log.warning("Gemini HTTP %s, retrying in %ss (attempt %d/%d)", resp.status_code, wait, attempt + 1, MAX_ATTEMPTS)
            time.sleep(wait)
            continue

        if resp.status_code >= 400:
            log.error("Gemini HTTP %s: %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()
        return resp.json()

    raise last_error


def generate(prompt: str, system: str | None = None, json_mode: bool = False,
             temperature: float = 0.3, max_tokens: int = 1024, timeout: float = 120.0) -> str:
    """Single-turn text generation. Returns the response text."""
    config = {
        "temperature": temperature,
        # Ollama limits were tuned for slow CPU inference; give Gemini headroom
        "maxOutputTokens": max(max_tokens * 4, 2048),
    }
    if json_mode:
        config["responseMimeType"] = "application/json"
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": config,
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    data = _post(f"{GEMINI_MODEL}:generateContent", body, timeout)
    candidates = data.get("candidates") or []
    if not candidates:
        log.warning("Gemini returned no candidates: %s", data.get("promptFeedback"))
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def embed(texts: list[str], timeout: float = 120.0) -> list[list[float]]:
    """Embed texts in batches. Returns one EMBED_DIM vector per text."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        body = {
            "requests": [
                {
                    "model": f"models/{GEMINI_EMBED_MODEL}",
                    "content": {"parts": [{"text": t}]},
                    "outputDimensionality": EMBED_DIM,
                }
                for t in batch
            ]
        }
        data = _post(f"{GEMINI_EMBED_MODEL}:batchEmbedContents", body, timeout)
        vectors.extend(e["values"] for e in data["embeddings"])
    return vectors
