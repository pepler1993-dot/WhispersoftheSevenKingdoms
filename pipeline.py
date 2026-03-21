#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = REPO_ROOT / 'upload'
SONGS_DIR = UPLOAD_DIR / 'songs'
THUMBS_DIR = UPLOAD_DIR / 'thumbnails'
METADATA_DIR = UPLOAD_DIR / 'metadata'
DONE_DIR = UPLOAD_DIR / 'done'
OUTPUT_YT_DIR = REPO_ROOT / 'output' / 'youtube'


def run(cmd, cwd=None):
    print('RUN:', ' '.join(str(x) for x in cmd))
    result = subprocess.run(cmd, cwd=cwd or REPO_ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def find_first(slug: str, folder: Path, exts: tuple[str, ...]):
    for ext in exts:
        p = folder / f'{slug}{ext}'
        if p.exists():
            return p
    return None


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def detect_theme(meta: dict, house: str | None):
    if house:
        return house
    theme = str(meta.get('theme', 'default')).strip().lower()
    return theme or 'default'


def ensure_dirs():
    for p in [DONE_DIR, OUTPUT_YT_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser(description='End-to-end pipeline for Whispers of the Seven Kingdoms')
    p.add_argument('--slug', help='Existing slug in upload/{songs,thumbnails,metadata}')
    p.add_argument('--song', help='Song title / request text for future full automation mode')
    p.add_argument('--mood', help='Mood hint for future generation mode')
    p.add_argument('--house', help='Theme/house hint for thumbnails + metadata')
    p.add_argument('--minutes', type=int, default=42, help='Target duration hint')
    p.add_argument('--public', action='store_true', help='Upload publicly instead of private')
    p.add_argument('--skip-upload', action='store_true', help='Run pipeline but do not upload to YouTube')
    p.add_argument('--skip-done-move', action='store_true', help='Do not move processed source files to upload/done')
    p.add_argument('--dry-run', action='store_true', help='Print steps without executing external scripts')
    return p.parse_args()


def infer_slug_from_title(title: str):
    slug = ''.join(c.lower() if c.isalnum() else '-' for c in title)
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-')


def main():
    args = parse_args()
    ensure_dirs()

    slug = args.slug or (infer_slug_from_title(args.song) if args.song else None)
    if not slug:
        print('ERROR: provide --slug for current repo flow', file=sys.stderr)
        raise SystemExit(1)

    metadata_path = METADATA_DIR / f'{slug}.json'
    if not metadata_path.exists():
        print(f'ERROR: metadata missing for slug {slug}: {metadata_path}', file=sys.stderr)
        raise SystemExit(1)

    meta = load_json(metadata_path)
    theme = detect_theme(meta, args.house)

    audio_path = find_first(slug, SONGS_DIR, ('.mp3', '.wav', '.ogg'))
    if audio_path is None:
        print(f'ERROR: audio missing for slug {slug} in {SONGS_DIR}', file=sys.stderr)
        raise SystemExit(1)

    thumb_path = find_first(slug, THUMBS_DIR, ('.jpg', '.jpeg', '.png', '.webp'))
    yt_dir = OUTPUT_YT_DIR / slug
    yt_dir.mkdir(parents=True, exist_ok=True)

    title = meta.get('title', slug.replace('-', ' ').title())

    if thumb_path is None:
        thumb_path = yt_dir / 'thumbnail.jpg'
        cmd = [
            sys.executable, 'scripts/thumbnails/generate_thumbnail.py',
            '--title', title,
            '--theme', theme,
            '--output', str(thumb_path),
        ]
        if args.dry_run:
            print('DRY:', ' '.join(cmd))
        else:
            run(cmd)

    video_path = yt_dir / 'video.mp4'
    metadata_out = yt_dir / 'metadata.json'

    metadata_cmd = [
        sys.executable, 'scripts/metadata/metadata_gen.py',
        '--song', slug,
        '--duration', f'{args.minutes} Minutes',
        '--output', str(metadata_out),
    ]
    render_cmd = [
        sys.executable, 'scripts/video/render.py',
        '--audio', str(audio_path),
        '--image', str(thumb_path),
        '--output', str(video_path),
    ]
    node_bin = shutil.which('node') or 'node'
    preflight_cmd = [node_bin, 'scripts/qa/preflight-metadata-report.js']

    if args.dry_run:
        print('DRY:', ' '.join(metadata_cmd))
        print('DRY:', ' '.join(render_cmd))
        print('DRY:', ' '.join(preflight_cmd))
    else:
        run(metadata_cmd)
        run(render_cmd)
        run(preflight_cmd)

    if not args.skip_upload:
        upload_cmd = [
            sys.executable, 'scripts/publish/youtube_upload.py',
            '--video', str(video_path),
            '--metadata', str(metadata_out),
        ]
        if args.public:
            upload_cmd.append('--public')
        if args.dry_run:
            print('DRY:', ' '.join(upload_cmd))
        else:
            run(upload_cmd)

    if not args.skip_done_move and not args.dry_run:
        done_slug_dir = DONE_DIR / slug
        done_slug_dir.mkdir(parents=True, exist_ok=True)
        for source in [audio_path, metadata_path, thumb_path if thumb_path.parent == THUMBS_DIR else None]:
            if source and source.exists():
                target = done_slug_dir / source.name
                if source.resolve() != target.resolve():
                    shutil.move(str(source), str(target))

    print(f'OK: pipeline completed for {slug}')
    print(f'OUTPUT: {yt_dir}')


if __name__ == '__main__':
    main()
