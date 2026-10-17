"""Load pre-rendered gold-standard reels into the database at startup.

The bundle (manifest.json + videos/) is produced by scripts/export_seed_reels.py.
On hosts without persistent storage (e.g. Render free tier) the database starts
empty on every boot, so this re-creates the Explore feed each time.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from database import get_db

log = logging.getLogger(__name__)

SEED_DIR = Path(os.getenv("SEED_REELS_DIR", Path(__file__).parent / "seed_reels"))
DEMO_DIR = Path(os.getenv("DEMO_REELS_DIR", Path(__file__).parent / "demo_reels"))
DEMO_FILENAME = "Mira and the Lighthouse.docx"


def seed_gold_reels() -> int:
    """Insert seed reels if the bundle exists and none are loaded yet. Returns count inserted."""
    return _seed_bundle(SEED_DIR, "__gold_standard__") + _seed_bundle(DEMO_DIR, DEMO_FILENAME)


def _seed_bundle(bundle_dir: Path, filename: str) -> int:
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        return 0

    conn = get_db()
    try:
        if conn.execute("SELECT 1 FROM uploads WHERE filename = ? AND doc_type = 'seed'", (filename,)).fetchone():
            return 0

        reels = json.loads(manifest_path.read_text(encoding="utf-8"))
        cur = conn.execute(
            "INSERT INTO uploads (user_id, filename, status, doc_type, subject_category) "
            "VALUES (1, ?, 'done', 'seed', 'general')",
            (filename,),
        )
        upload_id = cur.lastrowid

        inserted = 0
        for reel in reels:
            video_path = bundle_dir / "videos" / reel["video"]
            if not video_path.exists():
                continue
            conn.execute(
                "INSERT INTO reels (upload_id, title, summary, narration, one_liner, category, keywords, "
                "video_path, source_text, bg_image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    upload_id,
                    reel["title"],
                    reel["summary"],
                    reel.get("narration"),
                    reel.get("one_liner"),
                    reel.get("category"),
                    reel.get("keywords"),
                    str(video_path),
                    reel.get("source_text"),
                    reel.get("bg_image"),
                ),
            )
            inserted += 1
        conn.commit()
        log.info("Seeded %d reels from %s", inserted, bundle_dir)
        return inserted
    finally:
        conn.close()
