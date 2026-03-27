from __future__ import annotations

import os
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.store import AgentSyncDB

PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def _utf8_env():
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    return env


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_command(slug: str, config: dict[str, Any]) -> list[str]:
    cmd = [
        sys.executable, str(PIPELINE_DIR / 'pipeline' / 'pipeline.py'),
        '--slug', slug,
        '--skip-upload',
        '--skip-done-move',
    ]
    if config.get('minutes'):
        cmd += ['--minutes', str(config['minutes'])]
    if config.get('loop_hours') and float(config['loop_hours']) > 0:
        cmd += ['--loop-hours', str(config['loop_hours'])]
    if config.get('crossfade'):
        cmd += ['--crossfade', str(config['crossfade'])]
    if config.get('audio_preset') and config['audio_preset'] != 'ambient':
        cmd += ['--audio-preset', config['audio_preset']]
    if config.get('animated'):
        cmd.append('--animated')
    if config.get('skip_post_process'):
        cmd.append('--skip-post-process')
    if config.get('mood'):
        cmd += ['--mood', config['mood']]
    if config.get('house'):
        cmd += ['--house', config['house']]
    background = (config.get('background_source') or {}).get('path') if isinstance(config.get('background_source'), dict) else None
    if background:
        cmd += ['--bg-image', str(PIPELINE_DIR / background)]
    return cmd


def _stream_reader(pipe, run_id: str, stream_name: str, db: AgentSyncDB) -> None:
    try:
        for raw_line in pipe:
            line = raw_line.decode('utf-8', errors='replace').rstrip('\n\r')
            if line:
                db.append_run_log(run_id, stream_name, line, _now_iso())
    except Exception as exc:
        import logging
        logging.warning('Stream reader error for run %s (%s): %s', run_id, stream_name, exc)
    finally:
        pipe.close()


def start_run(run_id: str, slug: str, config: dict[str, Any], db: AgentSyncDB) -> None:
    cmd = _build_command(slug, config)

    db.append_run_log(run_id, 'system', f'Starting pipeline: {" ".join(cmd)}', _now_iso())
    db.update_run(run_id, status='running', started_at=_now_iso())

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(PIPELINE_DIR),
            env=_utf8_env(),
        )
    except Exception as exc:
        db.update_run(run_id, status='failed', error_message=str(exc), finished_at=_now_iso())
        db.append_run_log(run_id, 'system', f'Failed to start process: {exc}', _now_iso())
        return

    db.update_run(run_id, pid=proc.pid)

    stdout_thread = threading.Thread(
        target=_stream_reader, args=(proc.stdout, run_id, 'stdout', db), daemon=True
    )
    stderr_thread = threading.Thread(
        target=_stream_reader, args=(proc.stderr, run_id, 'stderr', db), daemon=True
    )
    stdout_thread.start()
    stderr_thread.start()

    exit_code = proc.wait()
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)

    if exit_code == 0:
        db.update_run(run_id, status='rendered', finished_at=_now_iso(), pid=None)
        db.append_run_log(run_id, 'system', 'Pipeline finished successfully', _now_iso())
    else:
        db.update_run(
            run_id, status='failed', finished_at=_now_iso(), pid=None,
            error_message=f'Process exited with code {exit_code}',
        )
        db.append_run_log(run_id, 'system', f'Pipeline failed with exit code {exit_code}', _now_iso())


def start_run_async(run_id: str, slug: str, config: dict[str, Any], db: AgentSyncDB) -> None:
    thread = threading.Thread(
        target=start_run, args=(run_id, slug, config, db), daemon=True
    )
    thread.start()


def trigger_upload(run_id: str, slug: str, config: dict[str, Any], db: AgentSyncDB) -> None:
    video_path = PIPELINE_DIR / 'data' / 'output' / 'youtube' / slug / 'video.mp4'
    metadata_path = PIPELINE_DIR / 'data' / 'output' / 'youtube' / slug / 'metadata.json'

    if not video_path.exists():
        db.update_run(run_id, status='failed', error_message='Video file not found for upload')
        return
    if not metadata_path.exists():
        db.update_run(run_id, status='failed', error_message='Metadata file not found for upload')
        return

    cmd = [
        sys.executable, str(PIPELINE_DIR / 'pipeline' / 'scripts' / 'publish' / 'youtube_upload.py'),
        '--video', str(video_path),
        '--metadata', str(metadata_path),
    ]
    if config.get('public'):
        cmd.append('--public')

    db.update_run(run_id, status='uploading')
    db.append_run_log(run_id, 'system', f'Starting YouTube upload: {" ".join(cmd)}', _now_iso())

    def _upload():
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(PIPELINE_DIR),
                env=_utf8_env(),
            )
            stdout_t = threading.Thread(
                target=_stream_reader, args=(proc.stdout, run_id, 'stdout', db), daemon=True
            )
            stderr_t = threading.Thread(
                target=_stream_reader, args=(proc.stderr, run_id, 'stderr', db), daemon=True
            )
            stdout_t.start()
            stderr_t.start()
            exit_code = proc.wait()
            stdout_t.join(timeout=5)
            stderr_t.join(timeout=5)

            if exit_code == 0:
                db.update_run(run_id, status='uploaded', finished_at=_now_iso())
                db.append_run_log(run_id, 'system', 'YouTube upload completed', _now_iso())
            else:
                db.update_run(run_id, status='rendered', error_message=f'Upload failed (exit {exit_code})')
                db.append_run_log(run_id, 'system', f'Upload failed with exit code {exit_code}', _now_iso())
        except Exception as exc:
            db.update_run(run_id, status='rendered', error_message=f'Upload error: {exc}')
            db.append_run_log(run_id, 'system', f'Upload error: {exc}', _now_iso())

    threading.Thread(target=_upload, daemon=True).start()


def cancel_run(run_id: str, db: AgentSyncDB) -> bool:
    import signal
    run = db.get_run(run_id)
    if not run or not run.get('pid'):
        return False
    try:
        import os
        os.kill(run['pid'], signal.SIGTERM)
        db.update_run(run_id, status='cancelled', finished_at=_now_iso(), pid=None)
        db.append_run_log(run_id, 'system', 'Pipeline cancelled by user', _now_iso())
        return True
    except ProcessLookupError:
        db.update_run(run_id, status='cancelled', finished_at=_now_iso(), pid=None)
        return True
    except Exception as exc:
        import logging
        logging.warning('Failed to cancel run %s: %s', run_id, exc)
        return False


def get_output_path(slug: str, filename: str) -> Path | None:
    base = PIPELINE_DIR / 'data' / 'output' / 'youtube'
    path = (base / slug / filename).resolve()
    if not path.is_relative_to(base.resolve()):
        return None
    if path.exists() and path.is_file():
        return path
    return None


def list_available_assets() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {'songs': [], 'thumbnails': [], 'metadata': []}
    upload_dir = PIPELINE_DIR / 'data' / 'upload'

    songs_dir = upload_dir / 'songs'
    if songs_dir.exists():
        result['songs'] = [f.name for f in songs_dir.iterdir() if f.is_file() and f.suffix in {'.mp3', '.wav', '.ogg'}]

    thumbs_dir = upload_dir / 'thumbnails'
    if thumbs_dir.exists():
        result['thumbnails'] = [f.name for f in thumbs_dir.iterdir() if f.is_file() and f.suffix in {'.jpg', '.jpeg', '.png', '.webp'}]

    meta_dir = upload_dir / 'metadata'
    if meta_dir.exists():
        result['metadata'] = [f.name for f in meta_dir.iterdir() if f.is_file() and f.suffix == '.json']

    return result


def list_library_tracks_for_pipeline(db: AgentSyncDB) -> list[dict[str, Any]]:
    """Tracks under data/upload/songs for the pipeline picker."""
    song_names = sorted(list_available_assets()['songs'])
    jobs = db.list_audio_jobs(limit=400)
    title_by_slug: dict[str, str] = {}
    for j in jobs:
        if j.get('status') != 'complete' or not j.get('slug'):
            continue
        s = j['slug']
        if s not in title_by_slug:
            t = (j.get('title') or '').strip()
            title_by_slug[s] = t if t else s

    out: list[dict[str, Any]] = []
    for name in song_names:
        stem = Path(name).stem
        title = title_by_slug.get(stem)
        if title and title != stem:
            label = f'{title} · {name}'
        else:
            label = name
        out.append({'stem': stem, 'filename': name, 'label': label})
    return out


def list_available_themes() -> list[str]:
    bg_dir = PIPELINE_DIR / 'data' / 'assets' / 'backgrounds'
    if not bg_dir.exists():
        return []
    return sorted(f.stem for f in bg_dir.iterdir() if f.is_file() and f.suffix in {'.jpg', '.jpeg', '.png'})
