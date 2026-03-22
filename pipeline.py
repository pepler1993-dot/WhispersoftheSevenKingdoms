#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = REPO_ROOT / 'upload'
SONGS_DIR = UPLOAD_DIR / 'songs'
THUMBS_DIR = UPLOAD_DIR / 'thumbnails'
METADATA_DIR = UPLOAD_DIR / 'metadata'
DONE_DIR = UPLOAD_DIR / 'done'
OUTPUT_YT_DIR = REPO_ROOT / 'output' / 'youtube'
WORK_JOBS_DIR = REPO_ROOT / 'work' / 'jobs'
COLAB_JOBS_DIR = REPO_ROOT / 'publishing' / 'musicgen' / 'jobs'


def now_iso():
    return datetime.now(timezone.utc).isoformat()


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


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write('\n')


def detect_theme(meta: dict, house: str | None):
    if house:
        return house
    theme = str(meta.get('theme', 'default')).strip().lower()
    return theme or 'default'


def ensure_dirs():
    for p in [DONE_DIR, OUTPUT_YT_DIR, WORK_JOBS_DIR, COLAB_JOBS_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser(description='End-to-end pipeline for Whispers of the Seven Kingdoms')
    p.add_argument('--slug', help='Existing slug in upload/{songs,thumbnails,metadata}')
    p.add_argument('--song', help='Song title / request text for pipeline job creation')
    p.add_argument('--mood', help='Mood hint for generation mode')
    p.add_argument('--house', help='Theme/house hint for thumbnails + metadata')
    p.add_argument('--minutes', type=int, default=42, help='Target duration hint')
    p.add_argument('--public', action='store_true', help='Upload publicly instead of private')
    p.add_argument('--skip-upload', action='store_true', help='Run pipeline but do not upload to YouTube')
    p.add_argument('--skip-done-move', action='store_true', help='Do not move processed source files to upload/done')
    p.add_argument('--animated', action='store_true', help='Use animated renderer (particle effects + camera pan). Default: static image.')
    p.add_argument('--dry-run', action='store_true', help='Print steps without executing external scripts')
    p.add_argument('--loop-hours', type=float, default=0, help='Loop audio to target hours (e.g. 3 for 3h from 20min source)')
    p.add_argument('--crossfade', type=int, default=8, help='Crossfade seconds for loop (default: 8)')
    p.add_argument('--audio-preset', default='ambient', choices=['ambient', 'dark', 'gentle', 'raw'],
                   help='Audio post-processing preset (default: ambient)')
    p.add_argument('--skip-post-process', action='store_true', help='Skip audio post-processing (EQ/Reverb/Normalize)')
    p.add_argument('--prepare-colab', action='store_true', help='Prepare job + status files for manual Colab run')
    p.add_argument('--resume', action='store_true', help='Resume pipeline after Colab has produced audio')
    return p.parse_args()


def infer_slug_from_title(title: str):
    slug = ''.join(c.lower() if c.isalnum() else '-' for c in title)
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-')


def job_paths(slug: str):
    work_dir = WORK_JOBS_DIR / slug
    return {
        'dir': work_dir,
        'status': work_dir / 'status.json',
        'colab_job': COLAB_JOBS_DIR / f'{slug}.job.json',
    }


def prepare_colab_job(slug: str, meta: dict, theme: str, args):
    paths = job_paths(slug)
    title = args.song or meta.get('title', slug.replace('-', ' ').title())
    payload = {
        'slug': slug,
        'title': title,
        'theme': meta.get('theme', theme),
        'house': args.house or theme,
        'mood': args.mood or meta.get('mood', []),
        'minutes': args.minutes,
        'target_audio_path': f'upload/songs/{slug}.mp3',
        'created_at': now_iso(),
        'generator': 'google-colab-musicgen',
        'status': 'waiting_for_colab',
    }
    status = {
        'slug': slug,
        'phase': 'waiting_for_colab',
        'updated_at': now_iso(),
        'notes': 'Run the matching Colab job and place generated audio into upload/songs/',
        'job_file': str(paths['colab_job'].relative_to(REPO_ROOT)),
    }
    write_json(paths['colab_job'], payload)
    write_json(paths['status'], status)
    print(f'OK: prepared Colab job for {slug}')
    print(f'JOB: {paths["colab_job"]}')
    print(f'STATUS: {paths["status"]}')


def update_status(slug: str, phase: str, **extra):
    paths = job_paths(slug)
    payload = {'slug': slug, 'phase': phase, 'updated_at': now_iso(), **extra}
    write_json(paths['status'], payload)


def main():
    args = parse_args()
    ensure_dirs()

    slug = args.slug or (infer_slug_from_title(args.song) if args.song else None)
    if not slug:
        print('ERROR: provide --slug or --song', file=sys.stderr)
        raise SystemExit(1)

    metadata_path = METADATA_DIR / f'{slug}.json'
    if not metadata_path.exists():
        print(f'ERROR: metadata missing for slug {slug}: {metadata_path}', file=sys.stderr)
        raise SystemExit(1)

    meta = load_json(metadata_path)
    theme = detect_theme(meta, args.house)

    if args.prepare_colab:
        prepare_colab_job(slug, meta, theme, args)
        return

    audio_path = find_first(slug, SONGS_DIR, ('.mp3', '.wav', '.ogg'))
    if audio_path is None:
        print(f'ERROR: audio missing for slug {slug} in {SONGS_DIR}', file=sys.stderr)
        if args.resume:
            update_status(slug, 'waiting_for_colab', error='audio_missing_on_resume')
        raise SystemExit(1)

    # Loop short audio to target duration (e.g. 20 min → 3h)
    if args.loop_hours and args.loop_hours > 0:
        looped_path = SONGS_DIR / f'{slug}-looped.mp3'
        loop_cmd = [
            sys.executable, 'scripts/audio/loop_audio.py',
            '--input', str(audio_path),
            '--output', str(looped_path),
            '--target-hours', str(args.loop_hours),
            '--crossfade', str(args.crossfade),
        ]
        if args.dry_run:
            print('DRY:', ' '.join(loop_cmd))
        else:
            run(loop_cmd)
            audio_path = looped_path
        update_status(slug, 'audio_looped', looped=str(looped_path.relative_to(REPO_ROOT)))

    # Post-processing: EQ, Reverb, Normalisierung
    if not args.skip_post_process:
        processed_path = audio_path.parent / f'{audio_path.stem}-processed{audio_path.suffix}'
        post_cmd = [
            sys.executable, 'scripts/audio/post_process.py',
            '--input', str(audio_path),
            '--output', str(processed_path),
            '--preset', args.audio_preset,
        ]
        if args.dry_run:
            print('DRY:', ' '.join(post_cmd))
        else:
            run(post_cmd)
            audio_path = processed_path
        update_status(slug, 'audio_processed', processed=str(processed_path.relative_to(REPO_ROOT)))

    update_status(slug, 'audio_ready', audio=str(audio_path.relative_to(REPO_ROOT)))

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
    update_status(slug, 'thumbnail_ready', thumbnail=str(thumb_path.relative_to(REPO_ROOT)))

    video_path = yt_dir / 'video.mp4'
    metadata_out = yt_dir / 'metadata.json'

    metadata_cmd = [
        sys.executable, 'scripts/metadata/metadata_gen.py',
        '--song', slug,
        '--duration', f'{args.minutes} Minutes',
        '--output', str(metadata_out),
    ]
    # Animated renderer only with explicit --animated flag
    bg_image = REPO_ROOT / 'assets' / 'backgrounds' / f'{theme}.jpg'
    if args.animated and bg_image.exists():
        render_cmd = [
            sys.executable, 'scripts/video/render_animated.py',
            '--bg-image', str(bg_image),
            '--theme', theme,
            '--audio', str(audio_path),
            '--output', str(video_path),
        ]
    else:
        # Default: static thumbnail + audio (fast, small output)
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
        update_status(slug, 'metadata_ready', metadata=str(metadata_out.relative_to(REPO_ROOT)))
        run(render_cmd)
        update_status(slug, 'rendered', video=str(video_path.relative_to(REPO_ROOT)))
        run(preflight_cmd)
        update_status(slug, 'qa_passed')

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
            update_status(slug, 'uploaded')

    if not args.skip_done_move and not args.dry_run:
        done_slug_dir = DONE_DIR / slug
        done_slug_dir.mkdir(parents=True, exist_ok=True)
        for source in [audio_path, metadata_path, thumb_path if thumb_path.parent == THUMBS_DIR else None]:
            if source and source.exists():
                target = done_slug_dir / source.name
                if source.resolve() != target.resolve():
                    shutil.move(str(source), str(target))
        update_status(slug, 'done', output=str(yt_dir.relative_to(REPO_ROOT)))

    print(f'OK: pipeline completed for {slug}')
    print(f'OUTPUT: {yt_dir}')


if __name__ == '__main__':
    main()
