"""Shorts routes."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse

from app import shared
from app.helpers import slugify, _load_house_templates
from app.pipeline_runner import PIPELINE_DIR, list_library_tracks_for_pipeline, _stream_reader, _upload_env

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(shared.CET).isoformat()


def _pick_short_image(source_audio: str) -> Path | None:
    stem = Path(source_audio).stem
    candidates: list[Path] = []

    upload_thumb_dir = PIPELINE_DIR / 'data' / 'upload' / 'thumbnails'
    output_thumb_dir = PIPELINE_DIR / 'data' / 'output' / 'thumbnails'
    bg_dir = PIPELINE_DIR / 'data' / 'assets' / 'backgrounds'
    meta_path = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{stem}.json'

    for ext in ('.jpg', '.jpeg', '.png', '.webp'):
        candidates.append(upload_thumb_dir / f'{stem}{ext}')
        candidates.append(output_thumb_dir / f'{stem}{ext}')

    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            theme = slugify(str(meta.get('theme') or ''))
            if theme:
                for ext in ('.jpg', '.jpeg', '.png', '.webp'):
                    candidates.append(bg_dir / f'{theme}{ext}')
        except Exception:
            pass

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    if bg_dir.exists():
        for f in sorted(bg_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
                return f

    return None


def _list_uploaded_longform_videos() -> list[dict[str, Any]]:
    houses = _load_house_templates()
    out: list[dict[str, Any]] = []
    for wf in shared.db.list_workflows(type='video', limit=300):
        if wf.get('status') != 'uploaded':
            continue
        slug = wf.get('slug') or ''
        meta_path = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{slug}.json'
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding='utf-8'))
            except Exception:
                meta = {}
        title = wf.get('title') or meta.get('title') or slug
        tags = [str(x).lower() for x in (meta.get('tags') or []) if isinstance(x, str)]
        text = ' '.join([str(title).lower(), str(meta.get('description') or '').lower(), ' '.join(tags)])
        house_key = ''
        variant_key = ''
        for hk, house in houses.items():
            if not isinstance(house, dict):
                continue
            house_terms = [hk.lower(), str(house.get('display_name') or '').lower(), str(house.get('house') or '').lower()]
            if any(term and term in text for term in house_terms):
                house_key = hk
                variants = house.get('variants') or {}
                if isinstance(variants, dict):
                    for vk, desc in variants.items():
                        terms = [vk.replace('_', ' ').lower(), str(desc).lower()]
                        if any(term and term in text for term in terms):
                            variant_key = vk
                            break
                break
        cfg = wf.get('config') or {}
        out.append({
            'workflow_id': wf['workflow_id'],
            'slug': slug,
            'title': title,
            'created_at': wf.get('created_at'),
            'house_key': house_key,
            'variant_key': variant_key,
            'audio_filename': next((f'{slug}{ext}' for ext in ('.mp3','.wav','.ogg') if (PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{slug}{ext}').exists()), ''),
            'video_path': str(PIPELINE_DIR / 'data' / 'output' / 'youtube' / slug / 'video.mp4'),
            'config': cfg,
        })
    return out


def _build_short_output_metadata(run: dict[str, Any]) -> dict[str, Any]:
    cfg = run.get('config') or {}
    title = run.get('title') or run.get('slug') or 'Untitled Short'
    source_audio = cfg.get('source_audio', '')
    visual_mode = cfg.get('visual_mode', 'static-artwork')
    clip_start = cfg.get('clip_start_seconds', 0)
    clip_duration = cfg.get('clip_duration_seconds', 30)
    stem = Path(source_audio).stem

    return {
        'title': title,
        'titles': {'primary': title},
        'description': f'{title}\n\nSource track: {stem}\nClip: {clip_start}s\u2013{clip_start + clip_duration}s\nVisual: {visual_mode}\n#shorts',
        'tags': ['shorts', 'youtube shorts', 'ambient', 'sleep music', stem.replace('-', ' ')],
        'category': '10',
        'language': 'en',
        'content_type': 'short',
        'source_audio': source_audio,
        'clip_start_seconds': clip_start,
        'clip_duration_seconds': clip_duration,
        'visual_mode': visual_mode,
    }


@router.get('/admin/shorts', response_class=HTMLResponse)
def admin_shorts(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None), tab: str | None = Query(default='new')):
    library_tracks = list_library_tracks_for_pipeline(shared.db)
    houses = _load_house_templates()
    uploaded_videos = _list_uploaded_longform_videos()
    short_runs = shared.db.list_workflows(type='short', limit=100)
    presets = [
        {'key': 'hook-teaser', 'name': 'Hook Teaser', 'duration': 20, 'visual_mode': 'blurred-background', 'start': 0, 'title_suffix': ' | Short'},
        {'key': 'ambient-loop', 'name': 'Ambient Loop', 'duration': 30, 'visual_mode': 'cinematic-gradient', 'start': 15, 'title_suffix': ' | Ambient Short'},
        {'key': 'highlight-cut', 'name': 'Highlight Cut', 'duration': 45, 'visual_mode': 'static-artwork', 'start': 30, 'title_suffix': ' | Highlight'},
    ]
    active_tab = tab if tab in {'new', 'drafts'} else 'new'
    return shared.templates.TemplateResponse(request, 'shorts.html', {
        'request': request,
        'page': 'shorts',
        'shorts_tab': active_tab,
        'library_tracks': library_tracks,
        'houses': houses,
        'uploaded_videos': uploaded_videos,
        'short_runs': short_runs[:20],
        'short_presets': presets,
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/shorts/create')
def admin_shorts_create(
    source_audio: str = Form(''),
    source_run_id: str = Form(''),
    house_key: str = Form(''),
    variant_key: str = Form(''),
    title: str = Form(...),
    slug: str = Form(''),
    clip_start_seconds: int = Form(0),
    clip_duration_seconds: int = Form(30),
    visual_mode: str = Form('static-artwork'),
    visibility: str = Form('private'),
):
    source_audio = source_audio.strip()
    source_run_id = source_run_id.strip()
    title = title.strip()
    slug = slugify(slug.strip() or title)

    if source_run_id and not source_audio:
        selected = next((v for v in _list_uploaded_longform_videos() if v.get('workflow_id') == source_run_id), None)
        if selected:
            source_audio = str(selected.get('audio_filename') or '')
            if not title.strip():
                title = str(selected.get('title') or '').strip()
    if not source_audio:
        raise HTTPException(status_code=400, detail='Quelle für Audio ist erforderlich')
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

    selected = next((v for v in _list_uploaded_longform_videos() if v.get('workflow_id') == source_run_id), None) if source_run_id else None
    source_path = PIPELINE_DIR / 'data' / 'upload' / 'songs' / source_audio
    source_video_path = Path(selected.get('video_path')) if selected and selected.get('video_path') else Path()
    if not source_path.exists():
        raise HTTPException(status_code=400, detail='Gewählte Audio-Datei existiert nicht')
    if not source_video_path.is_file():
        raise HTTPException(status_code=400, detail='Gewähltes Video existiert nicht')

    now = datetime.now(shared.CET).isoformat()
    workflow_id = uuid.uuid4().hex[:12]
    metadata = {
        'slug': slug,
        'title': title,
        'platform': 'youtube',
        'content_type': 'short',
        'source_audio': source_audio,
        'source_run_id': source_run_id,
        'house_key': house_key,
        'variant_key': variant_key,
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
        'source_run_id': source_run_id,
        'house_key': house_key,
        'variant_key': variant_key,
        'source_audio_path': str(source_path),
        'source_video_path': str(source_video_path),
        'clip_start_seconds': clip_start_seconds,
        'clip_duration_seconds': clip_duration_seconds,
        'visual_mode': visual_mode,
        'visibility': visibility,
        'metadata_path': str(metadata_path),
    }

    shared.db.create_workflow({
        'workflow_id': workflow_id,
        'slug': slug,
        'title': title,
        'type': 'short',
        'status': 'created',
        'config': config,
        'created_at': now,
    })
    shared.db.append_workflow_log(workflow_id, 'system', f'Short draft created from {source_audio}', now)
    shared.db.append_workflow_log(workflow_id, 'system', f'Clip window: start={clip_start_seconds}s duration={clip_duration_seconds}s', now)
    shared.db.append_workflow_log(workflow_id, 'system', f'Visual mode: {visual_mode} \u00b7 visibility: {visibility}', now)

    return RedirectResponse(url=f'/admin/shorts/{workflow_id}?success=Short-Entwurf+{slug}+wurde+angelegt', status_code=303)


@router.get('/admin/shorts/{workflow_id}', response_class=HTMLResponse)
def admin_shorts_detail(request: Request, workflow_id: str, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    run = shared.db.get_workflow(workflow_id)
    if not run or run.get('type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    logs = shared.db.get_workflow_logs(workflow_id, limit=1000)
    output_files: list[dict[str, str]] = []
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / run['slug']
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({'name': f.name, 'size': f'{f.stat().st_size / 1024 / 1024:.1f} MB'})

    cfg = run.get('config') or {}
    source_run = None
    source_run_id = cfg.get('source_run_id')
    if source_run_id:
        source_run = shared.db.get_workflow(source_run_id)

    preview_image = next((f for f in output_files if f['name'].lower().startswith('thumbnail.') or f['name'].lower() in {'thumbnail.jpg', 'thumbnail.png', 'thumbnail.webp'}), None)
    return shared.templates.TemplateResponse(request, 'short_detail.html', {
        'request': request,
        'page': 'shorts',
        'run': run,
        'logs': logs,
        'output_files': output_files,
        'source_run': source_run,
        'preview_image': preview_image,
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/shorts/{workflow_id}/render')
def admin_shorts_render(workflow_id: str):
    run = shared.db.get_workflow(workflow_id)
    if not run or run.get('type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    if run.get('status') in {'running', 'uploading'}:
        raise HTTPException(status_code=409, detail='Short is already processing')

    cfg = run.get('config') or {}
    source_audio_path = Path(cfg.get('source_audio_path') or '')
    source_video_path = Path(cfg.get('source_video_path') or '')
    if not source_audio_path.is_file():
        raise HTTPException(status_code=400, detail='Source audio path is invalid')
    if not source_video_path.is_file():
        raise HTTPException(status_code=400, detail='Source video path is invalid')

    image_path = _pick_short_image(cfg.get('source_audio', ''))

    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / run['slug']
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / 'video.mp4'
    output_metadata = output_dir / 'metadata.json'
    output_metadata.write_text(json.dumps(_build_short_output_metadata(run), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    cmd = [
        sys.executable,
        str(PIPELINE_DIR / 'pipeline' / 'scripts' / 'video' / 'render_short.py'),
        '--video', str(source_video_path),
        '--audio', str(source_audio_path),
        '--output', str(output_video),
        '--clip-start', str(cfg.get('clip_start_seconds', 0)),
        '--clip-duration', str(cfg.get('clip_duration_seconds', 30)),
        '--visual-mode', str(cfg.get('visual_mode', 'static-artwork')),
    ]
    if image_path:
        cmd += ['--image', str(image_path)]

    now = _now_iso()
    cmd_str = ' '.join(cmd)
    shared.db.update_workflow(workflow_id, status='running', started_at=now, error_message=None)
    shared.db.append_workflow_log(workflow_id, 'system', f'Starting Shorts render: {cmd_str}', now)
    shared.db.append_workflow_log(workflow_id, 'system', f'Using source video: {source_video_path.name}', now)
    if image_path:
        shared.db.append_workflow_log(workflow_id, 'system', f'Fallback image available: {image_path.name}', now)

    def worker():
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(PIPELINE_DIR))
        except Exception as exc:
            shared.db.update_workflow(workflow_id, status='failed', error_message=f'Render start failed: {exc}')
            shared.db.append_workflow_log(workflow_id, 'system', f'Render start failed: {exc}', _now_iso())
            return

        t_out = threading.Thread(target=_stream_reader, args=(proc.stdout, workflow_id, 'stdout', shared.db), daemon=True)
        t_err = threading.Thread(target=_stream_reader, args=(proc.stderr, workflow_id, 'stderr', shared.db), daemon=True)
        t_out.start()
        t_err.start()
        code = proc.wait()
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        finished = _now_iso()
        if code == 0 and output_video.exists():
            shared.db.update_workflow(workflow_id, status='rendered', finished_at=finished, error_message=None)
            shared.db.append_workflow_log(workflow_id, 'system', 'Short rendered successfully', finished)
        else:
            shared.db.update_workflow(workflow_id, status='failed', finished_at=finished, error_message=f'Shorts render failed (exit {code})')
            shared.db.append_workflow_log(workflow_id, 'system', f'Shorts render failed with exit code {code}', finished)

    threading.Thread(target=worker, daemon=True).start()
    return RedirectResponse(url=f'/admin/shorts/{workflow_id}?success=Short-Rendering+wurde+gestartet', status_code=303)


@router.get('/admin/shorts/{workflow_id}/logs')
def admin_shorts_logs(workflow_id: str, after_id: int = Query(default=0, ge=0)):
    run = shared.db.get_workflow(workflow_id)
    if not run or run.get('type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    logs = shared.db.get_workflow_logs(workflow_id, after_id=after_id)
    return JSONResponse({'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')})


@router.post('/admin/shorts/{workflow_id}/upload')
def admin_shorts_upload(workflow_id: str):
    run = shared.db.get_workflow(workflow_id)
    if not run or run.get('type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    if run.get('status') in {'created', 'failed', 'queued', 'running'}:
        raise HTTPException(status_code=409, detail='Short must be rendered before upload')
    if run['status'] != 'rendered':
        raise HTTPException(status_code=409, detail=f'Cannot upload short from status {run["status"]}')

    slug = run['slug']
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / slug
    video_path = output_dir / 'video.mp4'
    metadata_path = output_dir / 'metadata.json'
    if not video_path.exists() or not metadata_path.exists():
        raise HTTPException(status_code=400, detail='Rendered short output is incomplete')

    run_cfg = run.get('config', {})
    thumb_candidates = [output_dir / 'thumbnail.jpg', output_dir / 'thumbnail.png', output_dir / 'thumbnail.webp']

    cmd = [
        sys.executable,
        str(PIPELINE_DIR / 'pipeline' / 'scripts' / 'publish' / 'youtube_upload.py'),
        '--video', str(video_path),
        '--metadata', str(metadata_path),
    ]
    thumbnail_path = next((p for p in thumb_candidates if p.exists()), None)
    if thumbnail_path:
        cmd += ['--thumbnail', str(thumbnail_path)]
    if run_cfg.get('visibility') == 'public':
        cmd.append('--public')

    upload_env = _upload_env()
    shared.db.update_workflow(workflow_id, status='uploading', error_message=None)
    cmd_str = ' '.join(cmd)
    now = datetime.now(shared.CET).isoformat()
    shared.db.append_workflow_log(workflow_id, 'system', f'Starting Shorts upload: {cmd_str}', now)
    shared.db.append_workflow_log(workflow_id, 'system', f'YouTube credentials source: {upload_env.get("GOOGLE_CLIENT_SECRET", "client_secret.json")}', now)

    def worker():
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(PIPELINE_DIR), env=upload_env)
        except Exception as exc:
            shared.db.update_workflow(workflow_id, status='rendered', error_message=f'Upload start failed: {exc}')
            shared.db.append_workflow_log(workflow_id, 'system', f'Upload start failed: {exc}', datetime.now(shared.CET).isoformat())
            return
        from app.pipeline_runner import _stream_reader
        t_out = threading.Thread(target=_stream_reader, args=(proc.stdout, workflow_id, 'stdout', shared.db), daemon=True)
        t_err = threading.Thread(target=_stream_reader, args=(proc.stderr, workflow_id, 'stderr', shared.db), daemon=True)
        t_out.start()
        t_err.start()
        code = proc.wait()
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        now = datetime.now(shared.CET).isoformat()
        if code == 0:
            shared.db.update_workflow(workflow_id, status='uploaded', finished_at=now, error_message=None)
            shared.db.append_workflow_log(workflow_id, 'system', 'Short uploaded successfully', now)
        else:
            shared.db.update_workflow(workflow_id, status='rendered', error_message=f'Shorts upload failed (exit {code})')
            shared.db.append_workflow_log(workflow_id, 'system', f'Shorts upload failed with exit code {code}', now)

    threading.Thread(target=worker, daemon=True).start()
    return RedirectResponse(url=f'/admin/shorts/{workflow_id}?success=Short-Upload+wurde+gestartet', status_code=303)


@router.get('/admin/shorts/preview/{slug}/{filename}')
def admin_shorts_preview_file(slug: str, filename: str):
    base = PIPELINE_DIR / 'data' / 'output' / 'shorts'
    path = (base / slug / filename).resolve()
    if not path.is_relative_to(base.resolve()):
        raise HTTPException(status_code=400, detail='Invalid path')
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)
