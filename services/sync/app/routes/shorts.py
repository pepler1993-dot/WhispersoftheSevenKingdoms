"""Shorts routes."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse

from app import shared
from app.helpers import slugify
from app.pipeline_runner import PIPELINE_DIR, list_library_tracks_for_pipeline

router = APIRouter()


@router.get('/admin/shorts', response_class=HTMLResponse)
def admin_shorts(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    library_tracks = list_library_tracks_for_pipeline(shared.db)
    short_runs = [run for run in shared.db.list_runs(limit=100) if (run.get('config') or {}).get('content_type') == 'short']
    return shared.templates.TemplateResponse(request, 'shorts.html', {
        'request': request,
        'page': 'shorts',
        'library_tracks': library_tracks,
        'short_runs': short_runs[:20],
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/shorts/create')
def admin_shorts_create(
    source_audio: str = Form(...),
    title: str = Form(...),
    slug: str = Form(''),
    clip_start_seconds: int = Form(0),
    clip_duration_seconds: int = Form(30),
    visual_mode: str = Form('static-artwork'),
    visibility: str = Form('private'),
):
    source_audio = source_audio.strip()
    title = title.strip()
    slug = slugify(slug.strip() or title)

    if not source_audio:
        raise HTTPException(status_code=400, detail='Quelle f\u00fcr Audio ist erforderlich')
    if not title:
        raise HTTPException(status_code=400, detail='Titel ist erforderlich')
    if not slug:
        raise HTTPException(status_code=400, detail='Slug ist erforderlich')
    if clip_start_seconds < 0:
        raise HTTPException(status_code=400, detail='Clip-Start darf nicht negativ sein')
    if clip_duration_seconds < 15 or clip_duration_seconds > 60:
        raise HTTPException(status_code=400, detail='Clip-L\u00e4nge muss zwischen 15 und 60 Sekunden liegen')
    if visual_mode not in {'static-artwork', 'blurred-background', 'cinematic-gradient'}:
        raise HTTPException(status_code=400, detail='Ung\u00fcltiger Visual Mode')
    if visibility not in {'private', 'unlisted', 'public'}:
        raise HTTPException(status_code=400, detail='Ung\u00fcltige Sichtbarkeit')

    source_path = PIPELINE_DIR / 'data' / 'upload' / 'songs' / source_audio
    if not source_path.exists():
        raise HTTPException(status_code=400, detail='Gew\u00e4hlte Audio-Datei existiert nicht')

    now = datetime.now(shared.CET).isoformat()
    run_id = uuid.uuid4().hex[:12]
    metadata = {
        'slug': slug,
        'title': title,
        'platform': 'youtube',
        'content_type': 'short',
        'source_audio': source_audio,
        'clip_start_seconds': clip_start_seconds,
        'clip_duration_seconds': clip_duration_seconds,
        'visual_mode': visual_mode,
        'visibility': visibility,
        'hashtags': ['shorts'],
    }

    metadata_dir = PIPELINE_DIR / 'data' / 'upload' / 'shorts' / 'metadata'
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_dir / f'{slug}.json'
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    config = {
        'content_type': 'short',
        'format': 'youtube_short',
        'aspect_ratio': '9:16',
        'source_audio': source_audio,
        'source_audio_path': str(source_path),
        'clip_start_seconds': clip_start_seconds,
        'clip_duration_seconds': clip_duration_seconds,
        'visual_mode': visual_mode,
        'visibility': visibility,
        'metadata_path': str(metadata_path),
    }

    shared.db.create_run({
        'run_id': run_id,
        'slug': slug,
        'title': title,
        'status': 'created',
        'config': config,
        'created_at': now,
    })
    shared.db.append_run_log(run_id, 'system', f'Short draft created from {source_audio}', now)
    shared.db.append_run_log(run_id, 'system', f'Clip window: start={clip_start_seconds}s duration={clip_duration_seconds}s', now)
    shared.db.append_run_log(run_id, 'system', f'Visual mode: {visual_mode} \u00b7 visibility: {visibility}', now)

    return RedirectResponse(url=f'/admin/shorts/{run_id}?success=Short-Entwurf+{slug}+wurde+angelegt', status_code=303)


@router.get('/admin/shorts/{run_id}', response_class=HTMLResponse)
def admin_shorts_detail(request: Request, run_id: str, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    run = shared.db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    logs = shared.db.get_run_logs(run_id, limit=1000)
    output_files: list[dict[str, str]] = []
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / run['slug']
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({'name': f.name, 'size': f'{f.stat().st_size / 1024 / 1024:.1f} MB'})
    return shared.templates.TemplateResponse(request, 'short_detail.html', {
        'request': request,
        'page': 'shorts',
        'run': run,
        'logs': logs,
        'output_files': output_files,
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/shorts/{run_id}/render')
def admin_shorts_render(run_id: str):
    run = shared.db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    if run['status'] not in {'created', 'failed'}:
        raise HTTPException(status_code=409, detail=f'Cannot render short from status {run["status"]}')

    now = datetime.now(shared.CET).isoformat()
    config = run.get('config', {})
    shared.db.update_run(run_id, status='running', started_at=now, error_message=None)
    shared.db.append_run_log(run_id, 'system', 'Short render requested from dashboard', now)
    shared.db.append_run_log(run_id, 'system', f"Source audio: {config.get('source_audio')}", now)
    shared.db.append_run_log(run_id, 'system', f"Clip window: {config.get('clip_start_seconds', 0)}s \u2192 +{config.get('clip_duration_seconds', 30)}s", now)
    shared.db.append_run_log(run_id, 'system', f"Visual mode: {config.get('visual_mode', 'static-artwork')}", now)
    shared.db.append_run_log(run_id, 'system', 'Render backend for Shorts is not wired yet \u2014 this draft is now queued for implementation.', now)
    shared.db.update_run(run_id, status='queued')

    return RedirectResponse(url=f'/admin/shorts/{run_id}?success=Short-Render+wurde+angesto\u00dfen', status_code=303)


@router.get('/admin/shorts/{run_id}/logs')
def admin_shorts_logs(run_id: str, after_id: int = Query(default=0, ge=0)):
    run = shared.db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    logs = shared.db.get_run_logs(run_id, after_id=after_id)
    return JSONResponse({'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')})


@router.post('/admin/shorts/{run_id}/upload')
def admin_shorts_upload(run_id: str):
    run = shared.db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    if run['status'] != 'rendered':
        raise HTTPException(status_code=409, detail=f'Cannot upload short from status {run["status"]}')

    slug = run['slug']
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / slug
    video_path = output_dir / 'video.mp4'
    metadata_path = output_dir / 'metadata.json'
    if not video_path.exists() or not metadata_path.exists():
        raise HTTPException(status_code=400, detail='Rendered short output is incomplete')

    run_cfg = run.get('config', {})
    cmd = [
        sys.executable,
        str(PIPELINE_DIR / 'pipeline' / 'scripts' / 'publish' / 'youtube_upload.py'),
        '--video', str(video_path),
        '--metadata', str(metadata_path),
    ]
    if run_cfg.get('visibility') == 'public':
        cmd.append('--public')

    shared.db.update_run(run_id, status='uploading', error_message=None)
    cmd_str = ' '.join(cmd)
    shared.db.append_run_log(run_id, 'system', f'Starting Shorts upload: {cmd_str}', datetime.now(shared.CET).isoformat())

    def worker():
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(PIPELINE_DIR))
        except Exception as exc:
            shared.db.update_run(run_id, status='rendered', error_message=f'Upload start failed: {exc}')
            shared.db.append_run_log(run_id, 'system', f'Upload start failed: {exc}', datetime.now(shared.CET).isoformat())
            return
        t_out, t_err = _append_process_logs(run_id, proc)
        code = proc.wait()
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        now = datetime.now(shared.CET).isoformat()
        if code == 0:
            shared.db.update_run(run_id, status='uploaded', finished_at=now, error_message=None)
            shared.db.append_run_log(run_id, 'system', 'Short uploaded successfully', now)
        else:
            shared.db.update_run(run_id, status='rendered', error_message=f'Shorts upload failed (exit {code})')
            shared.db.append_run_log(run_id, 'system', f'Shorts upload failed with exit code {code}', now)

    threading.Thread(target=worker, daemon=True).start()
    return RedirectResponse(url=f'/admin/shorts/{run_id}?success=Short-Upload+wurde+gestartet', status_code=303)


@router.get('/admin/shorts/preview/{slug}/{filename}')
def admin_shorts_preview_file(slug: str, filename: str):
    path = PIPELINE_DIR / 'data' / 'output' / 'shorts' / slug / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)
