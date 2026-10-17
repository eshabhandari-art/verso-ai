import os
import secrets
from pathlib import Path

# ── JWT Secret ──────────────────────────────────────────────
_ENV_FILE = Path(os.path.dirname(__file__)) / ".env"


def _get_env(name: str, default: str = "") -> str:
    """Return a setting from the environment, falling back to the .env file."""
    val = os.getenv(name)
    if val:
        return val
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return default


def _get_or_create_jwt_secret() -> str:
    """Return JWT secret from env, .env file, or generate one."""
    val = _get_env("JWT_SECRET")
    if val:
        return val
    # Generate and persist
    generated = secrets.token_hex(32)
    with open(_ENV_FILE, "a") as f:
        f.write(f"\nJWT_SECRET={generated}\n")
    return generated


JWT_SECRET: str = _get_or_create_jwt_secret()

# Ollama
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL: str = "nomic-embed-text"
EMBED_DIM: int = 768

# LLM provider — "ollama" (local models) or "gemini" (Google Gemini API)
LLM_PROVIDER: str = _get_env("LLM_PROVIDER", "ollama").lower()
GEMINI_API_KEY: str = _get_env("GEMINI_API_KEY")
GEMINI_MODEL: str = _get_env("GEMINI_MODEL", "gemini-flash-lite-latest")
GEMINI_EMBED_MODEL: str = _get_env("GEMINI_EMBED_MODEL", "gemini-embedding-001")
GEMINI_MIN_INTERVAL: float = float(_get_env("GEMINI_MIN_INTERVAL", "4"))  # seconds between requests

# Chunking
CHUNK_MAX_CHARS: int = 500
CHUNK_OVERLAP_CHARS: int = 50

# RAG retrieval
TOP_K: int = 3

# Paths
DATA_DIR: Path = Path("data")
EMBEDDINGS_DIR: Path = DATA_DIR / "embeddings"
AUDIO_CACHE_DIR: Path = DATA_DIR / "audio_cache"
VIDEO_CACHE_DIR: Path = DATA_DIR / "video_cache"

# Stock assets
STOCK_VIDEOS_DIR: Path = Path(os.path.dirname(__file__)) / "static" / "stock-videos"
SOUND_EFFECTS_DIR: Path = Path(os.path.dirname(__file__)) / "static" / "sound-effects"

# TTS — "piper" (neural, high quality) or "espeak" (formant, robotic fallback)
TTS_ENGINE: str = os.getenv("TTS_ENGINE", "piper")

# Piper TTS (neural voice)
PIPER_MODEL_DIR: Path = Path(os.path.dirname(__file__)) / "tts" / "models"
PIPER_MODEL: str = "en_GB-jenny_dioco-medium.onnx"  # warm British female — best Piper narrator
PIPER_SPEAKER_ID = None  # int or None
# Multi-speaker model for voice variety across reels
PIPER_MULTI_MODEL: str = "en_US-libritts_r-medium.onnx"

# espeak-ng fallback
ESPEAK_CMD: str = "espeak-ng"
ESPEAK_VOICE: str = "en"
ESPEAK_SPEED: int = 130
ESPEAK_PITCH: int = 50
ESPEAK_GAP: int = 4

# LLM — multi-model routing
LLM_MODEL: str = "qwen2.5:3b"  # legacy default, used by generate_reel_script / chat
CLASSIFICATION_MODEL: str = os.getenv("CLASSIFICATION_MODEL", "qwen2.5:1.5b")
REEL_MODEL: str = os.getenv("REEL_MODEL", "qwen2.5:1.5b")
CHAT_MODEL: str = os.getenv("CHAT_MODEL", "qwen2.5:3b")
LLM_TIMEOUT: float = 300.0

# Chat
MAX_EXCHANGES_PER_DOC: int = 10

# Timeouts — tuned for CPU-only (8GB). Override via env for faster machines.
# At ~4 tok/s on CPU, 800 tokens ≈ 200s + model load. Allow 300s per LLM call.
OLLAMA_EMBED_TIMEOUT: float = 60.0  # extra time for model load on single-model Ollama
REEL_LLM_TIMEOUT: float = float(os.getenv("REEL_LLM_TIMEOUT", "300"))       # per single-topic LLM call
CLASSIFICATION_TIMEOUT: float = float(os.getenv("CLASSIFICATION_TIMEOUT", "90"))
PIPELINE_TIMEOUT: float = float(os.getenv("PIPELINE_TIMEOUT", "3600"))       # 60 min total
STALE_UPLOAD_MINUTES: int = int(os.getenv("STALE_UPLOAD_MINUTES", "30"))
