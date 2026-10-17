#!/usr/bin/env python3
"""Export rendered gold-standard reels into a seed bundle.

Writes <out>/manifest.json and <out>/videos/<n>.mp4, which seed.py loads into
the database at startup (used by the Render deployment).

Usage:
    cd backend && python scripts/export_seed_reels.py --out seed_reels
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)
os.chdir(BACKEND_DIR)

from database import get_db  # noqa: E402

FIELDS = ["title", "summary", "narration", "one_liner", "category", "keywords", "source_text", "bg_image"]


def _compress(src: str, dst: str):
    """Re-encode to 720p so the bundle stays small (~3 MB/reel instead of ~17 MB)."""
    result = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", src,
         "-vf", "scale=720:1280", "-c:v", "libx264", "-preset", "medium", "-crf", "28",
         "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", dst],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  compress failed, copying original: {result.stderr[-200:]}")
        shutil.copy2(src, dst)


def main():
    parser = argparse.ArgumentParser(description="Export gold reels as a seed bundle")
    parser.add_argument("--out", default="seed_reels", help="Output directory")
    args = parser.parse_args()

    videos_dir = os.path.join(args.out, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    conn = get_db()
    rows = conn.execute(
        f"SELECT r.id, r.video_path, {', '.join('r.' + f for f in FIELDS)} FROM reels r "
        "JOIN uploads u ON u.id = r.upload_id "
        "WHERE u.filename = '__gold_standard__' ORDER BY r.id"
    ).fetchall()
    conn.close()

    manifest = []
    for n, row in enumerate(rows, start=1):
        if not row["video_path"] or not os.path.exists(row["video_path"]):
            print(f"  skip (no video): {row['title']}")
            continue
        video_name = f"{n:03d}.mp4"
        _compress(row["video_path"], os.path.join(videos_dir, video_name))
        manifest.append({**{f: row[f] for f in FIELDS}, "video": video_name})

    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"Exported {len(manifest)} reels to {args.out}")


if __name__ == "__main__":
    main()
