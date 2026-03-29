#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = REPO_ROOT / 'data' / 'upload'
SONGS_DIR = UPLOAD_DIR / 'songs'
THUMBS_DIR = UPLOAD_DIR / 'thumbnails'
METADATA_DIR = UPLOAD_DIR / 'metadata'
DONE_DIR = UPLOAD_DIR / 'done'
OUTPUT_YT_DIR = REPO_ROOT / 'data' / 'output' / 'youtube'
WORK_JOBS_DIR = REPO_ROOT / 'data' / 'work' / 'jobs'

_step_count = 0
_step_total = 0
_pipeline_start = 0.0


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _utf8_env():
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    return env


def _set_total_steps(n):
    global _step_total, _pipeline_start
    _step_total = n
    _pipeline_start = time.time()


def _fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f'{m}m {s:02d}s'


def _fmt_size(path):
    try:
        mb = Path(path).stat().st_size / (1024 * 1024)
        return f'{mb:.1f} MB'
    except OSError:
        return '?'


def _step(label):
    global _step_count
    _step_count += 1
    elapsed = _fmt_time(time.time() - _pipeline_start)
    print(f'\n{"=" * 60}', flush=True)
    print(f'[{_step_count}/{_step_total}] {label} ({elapsed} elapsed)', flush=True)
    print(f'{"=" * 60}', flush=True)


def _info(msg):
    print(f'>> {msg}', flush=True)


def _ok(msg):
    print(f'>> {msg}', flush=True)


def _warn(msg):
    print(f'!! {msg}', flush=True)


def run(cmd, cwd=None, fatal=True):
    print('RUN:', ' '.join(str(x) for x in cmd), flush=True)
    result = subprocess.run(cmd, cwd=cwd or REPO_ROOT, env=_utf8_env())
    if result.returncode != 0:
        if fatal:
            raise SystemExit(result.returncode)
        print(f'WARNING: command exited with code {result.returncode} (non-fatal)', flush=True)
    return result.returncode


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
    for p in [DONE_DIR, OUTPUT_YT_DIR, WORK_JOBS_DIR]:
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
    p.add_argument('--animated', action='store_true', help='Use animated renderer (particle effects). Default: static image.')
    p.add_argument('--dry-run', action='store_true', help='Print steps without executing external scripts')
    p.add_argument('--loop-hours', type=float, default=0, help='Loop audio to target hours (e.g. 3 for 3h from 20min source)')
    p.add_argument('--crossfade', type=int, default=8, help='Crossfade seconds for loop (default: 8)')
    p.add_argument('--audio-preset', default='sleep', choices=['sleep', 'ambient', 'dark', 'gentle', 'raw'],
                   help='Audio post-processing preset (default: sleep)')
    p.add_argument('--skip-post-process', action='store_true', help='Skip audio post-processing (EQ/Reverb/Normalize)')
    p.add_argument('--bg-image', help='Explicit background image for video rendering')
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
    }


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

    audio_path = find_first(slug, SONGS_DIR, ('.mp3', '.wav', '.ogg'))
    if audio_path is None:
        print(f'ERROR: audio missing for slug {slug} in {SONGS_DIR}', file=sys.stderr)
        raise SystemExit(1)

    title = meta.get('title', slug.replace('-', ' ').title())
    if isinstance(title, dict):
        title = title.get('primary', slug.replace('-', ' ').title())

    # Calculate total steps
    total = 0
    if args.loop_hours and args.loop_hours > 0:
        total += 1
    if not args.skip_post_process:
        total += 1
    total += 1  # thumbnail
    total += 1  # metadata
    total += 1  # render
    total += 1  # QA
    if not args.skip_upload:
        total += 1
    if not args.skip_done_move:
        total += 1
    _set_total_steps(total)

    renderer_label = 'animated (particles)' if args.animated else 'static'
    upload_label = 'skip' if args.skip_upload else ('public' if args.public else 'private')
    audio_size = _fmt_size(audio_path)

    print(f'\n{"*" * 60}', flush=True)
    print(f'PIPELINE START: {slug}', flush=True)
    print(f'  Title:    {title}', flush=True)
    print(f'  Theme:    {theme}', flush=True)
    print(f'  Duration: {args.minutes} min', flush=True)
    print(f'  Audio:    {audio_path.name} ({audio_size})', flush=True)
    print(f'  Preset:   {args.audio_preset}', flush=True)
    print(f'  Renderer: {renderer_label}', flush=True)
    print(f'  Upload:   {upload_label}', flush=True)
    print(f'  Steps:    {total}', flush=True)
    print(f'{"*" * 60}', flush=True)

    # Loop short audio to target duration (e.g. 20 min → 3h)
    if args.loop_hours and args.loop_hours > 0:
        looped_path = SONGS_DIR / f'{slug}-looped.mp3'
        loop_cmd = [
            sys.executable, 'pipeline/scripts/audio/loop_audio.py',
            '--input', str(audio_path),
            '--output', str(looped_path),
            '--target-hours', str(args.loop_hours),
            '--crossfade', str(args.crossfade),
        ]
        _step(f'AUDIO LOOP -- target: {args.loop_hours}h, crossfade: {args.crossfade}s')
        if args.dry_run:
            print('DRY:', ' '.join(loop_cmd))
        else:
            run(loop_cmd)
            audio_path = looped_path
        _info(f'{_fmt_size(audio_path)}')
        update_status(slug, 'audio_looped', looped=str(looped_path.relative_to(REPO_ROOT)))

    # Post-processing: EQ, Reverb, Normalisierung
    if not args.skip_post_process:
        processed_path = audio_path.parent / f'{audio_path.stem}-processed{audio_path.suffix}'
        post_cmd = [
            sys.executable, 'pipeline/scripts/audio/post_process.py',
            '--input', str(audio_path),
            '--output', str(processed_path),
            '--preset', args.audio_preset,
        ]
        _step(f'AUDIO POST-PROCESS -- preset: {args.audio_preset}')
        in_size = _fmt_size(audio_path)
        if args.dry_run:
            print('DRY:', ' '.join(post_cmd))
        else:
            run(post_cmd)
            audio_path = processed_path
        out_size = _fmt_size(audio_path)
        _info(f'{in_size} -> {out_size}')
        update_status(slug, 'audio_processed', processed=str(processed_path.relative_to(REPO_ROOT)))

    update_status(slug, 'audio_ready', audio=str(audio_path.relative_to(REPO_ROOT)))

    # Thumbnail
    thumb_path = find_first(slug, THUMBS_DIR, ('.jpg', '.jpeg', '.png', '.webp'))
    yt_dir = OUTPUT_YT_DIR / slug
    yt_dir.mkdir(parents=True, exist_ok=True)

    _step('THUMBNAIL')
    if thumb_path is None:
        thumb_path = yt_dir / 'thumbnail.jpg'
        bg_for_thumb = Path(args.bg_image) if args.bg_image else (REPO_ROOT / 'data' / 'assets' / 'backgrounds' / f'{theme}.jpg')
        cmd = [
            sys.executable, 'pipeline/scripts/thumbnails/generate_thumbnail.py',
            '--title', title,
            '--theme', theme,
            '--output', str(thumb_path),
        ]
        if bg_for_thumb.exists():
            cmd += ['--bg-image', str(bg_for_thumb)]
        if args.dry_run:
            print('DRY:', ' '.join(cmd))
        else:
            run(cmd)
        _info(f'Generated: {thumb_path.name} ({_fmt_size(thumb_path)})')
    else:
        _info(f'Using existing: {thumb_path.name} ({_fmt_size(thumb_path)})')
    update_status(slug, 'thumbnail_ready', thumbnail=str(thumb_path.relative_to(REPO_ROOT)))

    # Metadata + Video
    video_path = yt_dir / 'video.mp4'
    metadata_out = yt_dir / 'metadata.json'

    metadata_cmd = [
        sys.executable, 'pipeline/scripts/metadata/metadata_gen.py',
        '--song', slug,
        '--duration', f'{args.loop_hours} Hours' if args.loop_hours and args.loop_hours > 0 else f'{args.minutes} Minutes',
        '--output', str(metadata_out),
    ]

    _step('METADATA GENERATION')
    if args.dry_run:
        print('DRY:', ' '.join(metadata_cmd))
    else:
        run(metadata_cmd)
    _info(f'Output: {metadata_out.relative_to(REPO_ROOT)}')
    update_status(slug, 'metadata_ready', metadata=str(metadata_out.relative_to(REPO_ROOT)))

    # Video render
    bg_image = Path(args.bg_image) if args.bg_image else (REPO_ROOT / 'data' / 'assets' / 'backgrounds' / f'{theme}.jpg')
    if args.animated and bg_image.exists():
        render_cmd = [
            sys.executable, 'pipeline/scripts/video/render_animated.py',
            '--bg-image', str(bg_image),
            '--theme', theme,
            '--audio', str(audio_path),
            '--output', str(video_path),
        ]
        _step('VIDEO RENDER (animated) -- this may take several minutes')
        _info(f'Theme: {theme} | Background: {bg_image.name}')
        _info(f'Audio: {audio_path.name} ({_fmt_size(audio_path)})')
    else:
        # Default: static thumbnail + audio (fast, small output)
        render_cmd = [
            sys.executable, 'pipeline/scripts/video/render.py',
            '--audio', str(audio_path),
            '--image', str(thumb_path),
            '--output', str(video_path),
        ]
        _step('VIDEO RENDER (static)')
        _info(f'Thumbnail: {thumb_path.name} | Audio: {audio_path.name}')

    if args.dry_run:
        print('DRY:', ' '.join(render_cmd))
    else:
        run(render_cmd)
    _info(f'Video: {video_path.name} ({_fmt_size(video_path)})')
    update_status(slug, 'rendered', video=str(video_path.relative_to(REPO_ROOT)))

    # QA
    preflight_cmd = [sys.executable, 'pipeline/scripts/qa/preflight_metadata_report.py']
    _step('QA PREFLIGHT CHECK')
    if args.dry_run:
        print('DRY:', ' '.join(preflight_cmd))
    else:
        qa_exit = run(preflight_cmd, fatal=False)
        if qa_exit == 0:
            update_status(slug, 'qa_passed')
        else:
            _warn(f'finished with warnings after {_fmt_time(time.time() - _pipeline_start)} (exit code {qa_exit})')
            _warn('Some metadata checks failed (non-fatal, see report above)')
            update_status(slug, 'qa_warning')

    # Upload
    if not args.skip_upload:
        _step('YOUTUBE UPLOAD')
        upload_cmd = [
            sys.executable, 'pipeline/scripts/publish/youtube_upload.py',
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

    # Move to done
    if not args.skip_done_move and not args.dry_run:
        _step('CLEANUP -- moving source files to done/')
        done_slug_dir = DONE_DIR / slug
        done_slug_dir.mkdir(parents=True, exist_ok=True)
        for source in [audio_path, metadata_path, thumb_path if thumb_path.parent == THUMBS_DIR else None]:
            if source and source.exists():
                target = done_slug_dir / source.name
                if source.resolve() != target.resolve():
                    shutil.move(str(source), str(target))
        update_status(slug, 'done', output=str(yt_dir.relative_to(REPO_ROOT)))

    total_time = _fmt_time(time.time() - _pipeline_start)
    print(f'\n{"*" * 60}', flush=True)
    print(f'PIPELINE COMPLETE: {slug}', flush=True)
    print(f'  Total time: {total_time}', flush=True)
    print(f'  Output:     {yt_dir.relative_to(REPO_ROOT)}/', flush=True)
    print(f'  Video:      {_fmt_size(video_path)}', flush=True)
    print(f'  Metadata:   {metadata_out.relative_to(REPO_ROOT)}', flush=True)
    print(f'{"*" * 60}', flush=True)
    print('Pipeline finished successfully', flush=True)


if __name__ == '__main__':
    main()
