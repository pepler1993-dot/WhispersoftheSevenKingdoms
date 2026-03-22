#!/usr/bin/env python3
"""
Upload Automation Example — Whispers of the Seven Kingdoms

This script demonstrates how to:
- Read song metadata from `song.json`
- Apply GoT-style templates for title/description/tags
- Validate presence of audio/thumbnail files
- Simulate upload (replace with real YouTube API)
- Move processed files to done/

Usage:
  1. Place song/thumbnail in upload/songs/ and upload/thumbnails/ with matching slugs
  2. Create upload/metadata/<slug>.song.json (see example schema)
  3. Run: python3 upload_automation_example.py
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# Optional: Jinja2 for template rendering (pip install jinja2)
try:
    from jinja2 import Template, Environment, FileSystemLoader
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False
    print("Warning: jinja2 not installed. Templates will use basic substitution.")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_SONGS = BASE_DIR / "data" / "upload" / "songs"
UPLOAD_THUMBNAILS = BASE_DIR / "data" / "upload" / "thumbnails"
UPLOAD_METADATA = BASE_DIR / "data" / "upload" / "metadata"
UPLOAD_DONE = BASE_DIR / "data" / "upload" / "done"
TEMPLATES_DIR = BASE_DIR / "docs" / "templates"

# Ensure dirs exist
for p in [UPLOAD_SONGS, UPLOAD_THUMBNAILS, UPLOAD_METADATA, UPLOAD_DONE]:
    p.mkdir(parents=True, exist_ok=True)

def load_metadata(slug: str) -> dict:
    meta_path = UPLOAD_METADATA / f"{slug}.song.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata missing: {meta_path}")
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_template(template_path: Path, context: dict) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template missing: {template_path}")
    text = template_path.read_text(encoding='utf-8')
    if HAS_JINJA:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        tmpl = env.get_template(template_path.name)
        return tmpl.render(**context)
    else:
        # Very basic fallback
        return text.format(**context)

def find_thumbnail(slug: str) -> Path | None:
    for ext in ('.jpg', '.jpeg', '.png', '.webp'):
        p = UPLOAD_THUMBNAILS / f"{slug}{ext}"
        if p.exists():
            return p
    return None

def validate_files(slug: str, audio_path: Path, thumb_path: Path | None, meta: dict) -> bool:
    issues = []
    if not audio_path.exists():
        issues.append(f"Audio missing: {audio_path}")
    if thumb_path and not thumb_path.exists():
        issues.append(f"Thumbnail missing: {thumb_path}")
    # Basic metadata check
    required = ['slug', 'title', 'theme', 'mood', 'duration_target', 'platforms', 'generator', 'prompt_summary', 'source_audio', 'source_artwork']
    missing = [k for k in required if k not in meta]
    if missing:
        issues.append(f"Metadata missing fields: {missing}")
    if meta.get('slug') != slug:
        issues.append("Slug mismatch between filename and metadata")
    if issues:
        print(f"[VALIDATION FAIL] {slug}:")
        for i in issues:
            print(f"  - {i}")
        return False
    return True

def generate_content(slug: str, meta: dict) -> tuple[str, str, list[str]]:
    # Prepare context for templates
    ctx = {
        'slug': slug,
        'title': meta['title'],
        'theme': meta['theme'],
        'mood': meta['mood'],
        'mood_list': ", ".join(meta['mood']) if isinstance(meta['mood'], list) else str(meta['mood']),
        'duration': meta['duration_target'],
        'generator': meta['generator'],
        'prompt_summary': meta['prompt_summary'],
        'description_paragraph_1': f"In the realm of {meta['theme']}, whispers drift through the air like a cool evening breeze. This track captures the essence of that place.",
        'description_paragraph_2': "Let the sounds carry you to distant lands where dragons soar and kings rule. Designed to ease you into dreams of faraway horizons.",
        'hashtags': f"#WhispersOfTheSevenKingdoms #GameOfThrones #{meta['theme'].replace(' ', '')} #SleepMusic #Fantasy"
    }

    # Title: use Template A
    title_tmpl = "{{title}} | Whispers of the Seven Kingdoms"
    title = Template(title_tmpl).render(**ctx) if not HAS_JINJA else title_tmpl

    # Description
    desc = render_template(TEMPLATES_DIR / "description.template.md", ctx)

    # Tags (simple version; could parse tags.template)
    tags = [
        "whispers of the seven kingdoms",
        "game of thrones",
        "got",
        "ambient sleep music",
        "fantasy music",
        "relaxing music",
        "sleep music",
        "study music",
        "meditation music",
        "background music",
        "dark ambient",
        "cinematic ambient",
        slug,
        slug.replace('-', ' ')
    ]
    # Add theme-specific
    theme_lower = meta['theme'].lower()
    if 'winterfell' in theme_lower:
        tags += ['winterfell', 'north', 'stark', 'castle', 'snow']
    if 'king' in theme_lower and 'landing' in theme_lower:
        tags += ['kings landing', 'lannister', 'red keep']
    if 'wall' in theme_lower:
        tags += ['the wall', "night's watch", 'jon snow', 'castle black']
    # Mood-based
    if isinstance(meta['mood'], list):
        if 'calm' in meta['mood']:
            tags += ['calm', 'peaceful', 'tranquil']
        if 'dark' in meta['mood']:
            tags += ['dark ambient', 'gothic', 'mysterious']
        if 'melancholic' in meta['mood']:
            tags += ['melancholic', 'sad', 'emotional']
        if 'epic' in meta['mood']:
            tags += ['epic', 'cinematic', 'dramatic']

    return title, desc, list(dict.fromkeys(tags))  # dedup

def upload_to_youtube(video_path: Path, thumbnail_path: Path, title: str, description: str, tags: list[str]) -> bool:
    """
    Replace this stub with real YouTube Data API v3 upload.
    See: https://developers.google.com/youtube/v3/guides/uploading
    """
    print(f"\n[UPLOAD SIMULATION]\nVideo: {video_path}\nThumbnail: {thumbnail_path}\nTitle: {title}\nDescription: {description}\nTags: {tags}\n")
    # success = ... API call ...
    return True  # simulate success

def log_upload(slug: str, video_path: Path, success: bool):
    log_file = BASE_DIR / "upload" / "upload.log"
    timestamp = datetime.utcnow().isoformat() + "Z"
    status = "SUCCESS" if success else "FAILED"
    entry = f"{timestamp},{slug},{video_path},{status}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)

def process_slug(slug: str):
    try:
        meta = load_metadata(slug)
    except Exception as e:
        print(f"[ERROR] Could not load metadata for {slug}: {e}")
        return False

    # Find audio file in upload/songs
    audio_path = None
    for ext in ('.mp3', '.wav', '.ogg', '.flac'):
        p = UPLOAD_SONGS / f"{slug}{ext}"
        if p.exists():
            audio_path = p
            break
    if not audio_path:
        print(f"[ERROR] No audio file for slug: {slug}")
        return False

    thumb_path = find_thumbnail(slug)

    if not validate_files(slug, audio_path, thumb_path, meta):
        return False

    title, description, tags = generate_content(slug, meta)

    # Output directory for this video
    out_dir = BASE_DIR / "data" / "output" / "youtube" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # In a real pipeline, you'd generate video.mp4 here using ffmpeg
    video_path = out_dir / "video.mp4"
    if not video_path.exists():
        print(f"[WARN] Video not pre-generated at {video_path}. Skipping upload step.")
        # In a real run, you'd call render_video(meta, audio_path, thumb_path, video_path)
        return False

    # Upload
    success = upload_to_youtube(video_path, thumb_path, title, description, tags)
    if success:
        # Move source files to done
        shutil.move(str(audio_path), UPLOAD_DONE / audio_path.name)
        if thumb_path:
            shutil.move(str(thumb_path), UPLOAD_DONE / thumb_path.name)
        print(f"[DONE] {slug} → uploaded and archived")
    else:
        print(f"[FAIL] {slug} upload did not succeed")

    log_upload(slug, video_path, success)
    return success

def main():
    # Process all metadata files in upload/metadata
    slugs = [p.stem.replace('.song', '') for p in UPLOAD_METADATA.glob('*.song.json')]
    if not slugs:
        print("No song metadata found in upload/metadata/. Add a <slug>.song.json and corresponding audio/thumbnail.")
        return
    for slug in slugs:
        process_slug(slug)

if __name__ == "__main__":
    main()
