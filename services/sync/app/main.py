from __future__ import annotations

import hashlib
import hmac
import json
import shutil
import uuid
from datetime import datetime, timezone
from typing import Any

import psutil
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from app.config import get_settings
from app.github_sync import (
    DEFAULT_LEASE_SECONDS,
    apply_stale_state,
    build_event_record,
    build_internal_task_event,
    create_task_state,
    is_stale,
    lease_until_iso,
    normalize_task_event,
    update_snapshot_from_event,
    utc_now_iso,
)
from app.pipeline_runner import (
    PIPELINE_DIR,
    cancel_run,
    get_output_path,
    list_available_assets,
    list_available_themes,
    list_library_tracks_for_pipeline,
    start_run_async,
    trigger_upload,
)
from app.store import AgentSyncDB
from app.kaggle_gen import (
    create_audio_job,
    find_prompt_preset,
    get_audio_generator_health,
    list_prompt_presets,
    recover_interrupted_jobs,
)


HOUSE_TEMPLATES_PATH = Path(__file__).resolve().parent.parent / 'data' / 'house_templates.json'


def _load_house_templates() -> dict[str, Any]:
    if not HOUSE_TEMPLATES_PATH.exists():
        return {}
    try:
        return json.loads(HOUSE_TEMPLATES_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _get_house_template(name: str) -> dict[str, Any] | None:
    tpl = _load_house_templates()
    key = name.strip().lower().replace("'", "'").replace(' ', '_')
    if key in tpl:
        return tpl[key]
    for k, v in tpl.items():
        if v.get('display_name', '').lower() == name.strip().lower():
            return v
    return None


class ClaimRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    lease_seconds: int = Field(default=DEFAULT_LEASE_SECONDS, ge=30, le=3600)
    phase: str = Field(default='working', min_length=1, max_length=64)
    blocked_reason: str | None = Field(default=None, max_length=500)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value not in {'working', 'blocked'}:
            raise ValueError('claim phase must be working or blocked')
        return value


class HeartbeatRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    lease_seconds: int = Field(default=DEFAULT_LEASE_SECONDS, ge=30, le=3600)
    phase: str | None = Field(default=None, min_length=1, max_length=64)
    blocked_reason: str | None = Field(default=None, max_length=500)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in {'working', 'blocked'}:
            raise ValueError('heartbeat phase must be working or blocked')
        return value


class ReleaseRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(default='released', min_length=1, max_length=64)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value != 'released':
            raise ValueError('release phase must be released')
        return value


class CompleteRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(default='done', min_length=1, max_length=64)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value != 'done':
            raise ValueError('complete phase must be done')
        return value


settings = get_settings()
db = AgentSyncDB(settings.data_dir)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

app = FastAPI(title='agent-sync-service')
app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')



def verify_signature(raw_body: bytes, signature_header: str | None) -> None:
    secret = settings.github_webhook_secret
    if not secret:
        raise HTTPException(status_code=500, detail='GITHUB_WEBHOOK_SECRET is not configured')
    if not signature_header:
        raise HTTPException(status_code=401, detail='Missing X-Hub-Signature-256 header')

    expected = 'sha256=' + hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail='Invalid webhook signature')



def _normalize_task_state_for_response(task_state: dict[str, Any]) -> dict[str, Any]:
    if is_stale(task_state):
        return apply_stale_state(task_state)
    return task_state



def _append_task_event(task_event: dict[str, Any] | None) -> tuple[bool, int]:
    return db.append_task_event(task_event)



def _write_task_state(task_id: str, task_state: dict[str, Any]) -> None:
    db.upsert_task_state(task_id, task_state)



def _mark_task_stale_if_needed(task_id: str) -> dict[str, Any] | None:
    current = db.get_task_state(task_id)
    if not current or not is_stale(current) or current.get('phase') == 'stale':
        return current

    updated = apply_stale_state(current)
    _write_task_state(task_id, updated)
    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.stale',
        action='detected',
        agent_id=current.get('owner_agent'),
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={'reason': 'lease_expired'},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
        _write_task_state(task_id, updated)
    return updated


@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/github/events')
def list_github_events(
    limit: int = Query(default=20, ge=1, le=200),
    task_id: str | None = Query(default=None),
) -> dict[str, Any]:
    events = db.list_github_events(limit=limit, task_id=task_id)
    return {'events': events, 'count': len(events)}


@app.get('/debug/events')
def debug_events(
    limit: int = Query(default=20, ge=1, le=200),
    task_id: str | None = Query(default=None),
) -> dict[str, Any]:
    return list_github_events(limit=limit, task_id=task_id)


@app.get('/github/events/{delivery_id}')
def get_github_event(delivery_id: str) -> dict[str, Any]:
    event = db.get_github_event(delivery_id)
    if event:
        return event
    raise HTTPException(status_code=404, detail='Delivery not found')


@app.get('/github/tasks')
def list_github_task_snapshots(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    ordered = db.list_snapshots(task_id=task_id)
    return {'tasks': ordered, 'count': len(ordered)}


@app.get('/debug/tasks')
def debug_tasks(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    return list_github_task_snapshots(task_id=task_id)


@app.get('/github/task')
def get_github_task_snapshot(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    snapshot = db.get_snapshot(task_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail='Task snapshot not found')
    return snapshot


@app.get('/tasks')
def list_tasks(include_done: bool = Query(default=False)) -> dict[str, Any]:
    tasks = db.list_task_states(include_done=include_done)
    normalized = [_normalize_task_state_for_response(task) for task in tasks]
    return {'tasks': normalized, 'count': len(normalized)}


@app.get('/tasks/{task_id:path}/events')
def get_task_events(task_id: str, after_seq: int = Query(default=0, ge=0)) -> dict[str, Any]:
    _mark_task_stale_if_needed(task_id)
    events, latest_seq = db.get_task_events(task_id, after_seq=after_seq)
    return {
        'task_id': task_id,
        'events': events,
        'count': len(events),
        'latest_seq': latest_seq,
    }


@app.post('/tasks/{task_id:path}/claim')
def claim_task(task_id: str, body: ClaimRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')

    current = _normalize_task_state_for_response(current)
    if current.get('phase') in {'done', 'archived'}:
        raise HTTPException(status_code=409, detail='Completed or archived tasks cannot be claimed')
    if current.get('owner_agent') and current.get('owner_agent') != body.agent_id and not is_stale(current):
        raise HTTPException(status_code=409, detail='Task has an active lease owned by another agent')

    updated = current.copy()
    updated['owner_agent'] = body.agent_id
    updated['lease_until'] = lease_until_iso(body.lease_seconds)
    updated['heartbeat_at'] = utc_now_iso()
    updated['phase'] = body.phase
    updated['blocked_reason'] = body.blocked_reason
    updated['updated_at'] = utc_now_iso()

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.claimed',
        action='claimed',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={'lease_seconds': body.lease_seconds},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@app.post('/tasks/{task_id:path}/heartbeat')
def heartbeat_task(task_id: str, body: HeartbeatRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')
    current = _normalize_task_state_for_response(current)

    if current.get('owner_agent') != body.agent_id:
        raise HTTPException(status_code=409, detail='Only the owning agent can heartbeat this task')
    if current.get('phase') in {'stale', 'done', 'archived', 'released'}:
        raise HTTPException(status_code=409, detail='Task is not in a heartbeat-eligible phase')

    updated = current.copy()
    updated['lease_until'] = lease_until_iso(body.lease_seconds)
    updated['heartbeat_at'] = utc_now_iso()
    if body.phase is not None:
        updated['phase'] = body.phase
    updated['blocked_reason'] = body.blocked_reason
    updated['updated_at'] = utc_now_iso()

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.heartbeat',
        action='heartbeat',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={'lease_seconds': body.lease_seconds},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@app.post('/tasks/{task_id:path}/release')
def release_task(task_id: str, body: ReleaseRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')
    current = _normalize_task_state_for_response(current)

    if current.get('owner_agent') != body.agent_id:
        raise HTTPException(status_code=409, detail='Only the owning agent can release this task')

    updated = current.copy()
    updated['owner_agent'] = None
    updated['lease_until'] = None
    updated['heartbeat_at'] = None
    updated['phase'] = 'released'
    updated['blocked_reason'] = None
    updated['updated_at'] = utc_now_iso()

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.released',
        action='released',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@app.post('/tasks/{task_id:path}/complete')
def complete_task(task_id: str, body: CompleteRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')
    current = _normalize_task_state_for_response(current)

    if current.get('owner_agent') != body.agent_id:
        raise HTTPException(status_code=409, detail='Only the owning agent can complete this task')

    updated = current.copy()
    updated['owner_agent'] = None
    updated['lease_until'] = None
    updated['heartbeat_at'] = None
    updated['phase'] = 'done'
    updated['blocked_reason'] = None
    updated['updated_at'] = utc_now_iso()

    snapshot = updated.get('snapshot', {}).copy()
    snapshot['status'] = 'done'
    snapshot['updated_at'] = updated['updated_at']
    updated['snapshot'] = snapshot

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.completed',
        action='completed',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@app.get('/tasks/{task_id:path}')
def get_task(task_id: str) -> dict[str, Any]:
    task = _mark_task_stale_if_needed(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task state not found')
    return _normalize_task_state_for_response(task)


@app.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request):
    summary = db.get_dashboard_summary()
    return templates.TemplateResponse('dashboard.html', {
        'request': request,
        'page': 'dashboard',
        'summary': summary,
    })


@app.get('/admin/tasks', response_class=HTMLResponse)
def admin_tasks(
    request: Request,
    phase: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    q: str | None = Query(default=None),
    include_done: bool = Query(default=False),
):
    tasks = db.list_tasks_for_admin(phase=phase, owner=owner, query=q, include_done=include_done)
    return templates.TemplateResponse('tasks.html', {
        'request': request,
        'page': 'tasks',
        'tasks': tasks,
        'filters': {'phase': phase, 'owner': owner, 'q': q, 'include_done': include_done},
    })


@app.get('/admin/tasks/{task_id:path}', response_class=HTMLResponse)
def admin_task_detail(request: Request, task_id: str):
    detail = db.get_task_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail='Task not found')
    return templates.TemplateResponse('task_detail.html', {
        'request': request,
        'page': 'tasks',
        'task_id': task_id,
        'detail': detail,
    })


@app.get('/admin/events', response_class=HTMLResponse)
def admin_events(request: Request, limit: int = Query(default=100, ge=1, le=500)):
    events = db.list_github_events(limit=limit)
    return templates.TemplateResponse('events.html', {
        'request': request,
        'page': 'events',
        'events': events,
        'limit': limit,
    })


@app.get('/admin/system', response_class=HTMLResponse)
def admin_system(request: Request):
    system = db.get_system_summary()
    return templates.TemplateResponse('system.html', {
        'request': request,
        'page': 'system',
        'system': system,
    })


@app.get('/admin/api/server-stats')
def admin_server_stats():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage('/')
    load1, load5, load15 = psutil.getloadavg()
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc).isoformat()
    return {
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count(),
            'load_1m': round(load1, 2),
            'load_5m': round(load5, 2),
            'load_15m': round(load15, 2),
        },
        'memory': {
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent,
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': round(disk.used / disk.total * 100, 1),
        },
        'boot_time': boot_time,
    }


# ── audio generator ──

@app.get('/admin/audio', response_class=HTMLResponse)
def admin_audio(request: Request):
    health = get_audio_generator_health()
    presets = list_prompt_presets()
    jobs = db.list_audio_jobs(limit=100)
    return templates.TemplateResponse('audio_generator.html', {
        'request': request,
        'page': 'audio',
        'health': health,
        'presets': presets,
        'jobs': jobs,
    })


@app.post('/admin/audio/generate')
def admin_audio_generate(
    slug: str = Form(...),
    title: str = Form(''),
    prompt_text: str = Form(''),
    preset_name: str = Form(''),
    minutes: int = Form(42),
    model: str = Form('medium'),
    clip_seconds: int = Form(30),
):
    slug = slug.strip().lower()
    title = title.strip() or slug.replace('-', ' ').title()
    preset_name = preset_name.strip()
    prompt_text = prompt_text.strip()

    if not slug:
        raise HTTPException(status_code=400, detail='Slug is required')
    if not prompt_text and not preset_name:
        raise HTTPException(status_code=400, detail='Provide prompt text or choose a preset')
    if preset_name and not find_prompt_preset(preset_name):
        raise HTTPException(status_code=400, detail='Unknown preset selected')

    job_id = create_audio_job(
        slug=slug,
        title=title,
        prompt_text=prompt_text,
        preset_name=preset_name or None,
        minutes=minutes,
        model=model,
        clip_seconds=clip_seconds,
        db=db,
    )
    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)


@app.get('/admin/audio/jobs/{job_id}', response_class=HTMLResponse)
def admin_audio_job_detail(request: Request, job_id: str):
    job = db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    logs = db.get_audio_job_logs(job_id, limit=1000)
    return templates.TemplateResponse('audio_job_detail.html', {
        'request': request,
        'page': 'audio',
        'job': job,
        'logs': logs,
    })


@app.get('/admin/audio/jobs/{job_id}/logs')
def admin_audio_job_logs(job_id: str, after_id: int = Query(default=0, ge=0)):
    job = db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    logs = db.get_audio_job_logs(job_id, after_id=after_id)
    return {'logs': logs, 'status': job['status'], 'error_message': job.get('error_message')}


@app.post('/admin/audio/jobs/{job_id}/cancel')
def admin_audio_job_cancel(job_id: str):
    job = db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    db.update_audio_job(job_id, status='cancelled', finished_at=datetime.now(timezone.utc).isoformat(), error_message='Cancelled by user')
    db.append_audio_job_log(job_id, 'system', 'Cancellation requested by user', datetime.now(timezone.utc).isoformat())
    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)


# ── pipeline control panel ──

ALLOWED_AUDIO_EXT = {'.mp3', '.wav', '.ogg'}
ALLOWED_THUMB_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB


def _split_text_list(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace('\r', '\n').replace(',', '\n')
    return [item.strip() for item in normalized.split('\n') if item.strip()]


def _build_song_metadata(
    slug: str,
    title: str,
    theme: str,
    mood: str | None,
    notes: str | None,
    duration_hint: str | None,
    tags: str | None,
    music_style: str | None,
    music_influences: str | None,
    music_tempo: str | None,
    music_energy: str | None,
    music_avoid: str | None,
    thumbnail_scene: str | None,
    thumbnail_elements: str | None,
    thumbnail_text: str | None,
    thumbnail_style: str | None,
    thumbnail_avoid: str | None,
) -> dict[str, Any]:
    return {
        'slug': slug,
        'title': title,
        'platform': 'youtube',
        'theme': theme,
        'mood': _split_text_list(mood) or ['calm'],
        'notes': (notes or '').strip(),
        'duration_hint': (duration_hint or '').strip() or 'long-form sleep track',
        'tags': _split_text_list(tags),
        'music_brief': {
            'style': (music_style or '').strip(),
            'influences': _split_text_list(music_influences),
            'tempo': (music_tempo or '').strip(),
            'energy': (music_energy or '').strip(),
            'avoid': _split_text_list(music_avoid),
        },
        'thumbnail_brief': {
            'scene': (thumbnail_scene or '').strip(),
            'elements': _split_text_list(thumbnail_elements),
            'text': (thumbnail_text or '').strip() or title,
            'style': (thumbnail_style or '').strip(),
            'avoid': _split_text_list(thumbnail_avoid),
        },
    }


@app.get('/admin/pipeline', response_class=HTMLResponse)
def admin_pipeline(request: Request):
    runs = db.list_runs(limit=100)
    houses = _load_house_templates()
    return templates.TemplateResponse('pipeline_runs.html', {
        'request': request,
        'page': 'pipeline',
        'runs': runs,
        'houses': houses,
    })


@app.get('/admin/pipeline/new', response_class=HTMLResponse)
def admin_pipeline_new(request: Request, slug: str | None = Query(default=None)):
    assets = list_available_assets()
    themes = list_available_themes()
    houses = _load_house_templates()
    library_tracks = list_library_tracks_for_pipeline(db)
    return templates.TemplateResponse('pipeline_new.html', {
        'request': request,
        'page': 'pipeline',
        'assets': assets,
        'themes': themes,
        'houses': houses,
        'library_tracks': library_tracks,
        'prefill_slug': (slug or '').strip().lower(),
    })


@app.get('/admin/api/house/{name}')
def api_house_template(name: str):
    tpl = _get_house_template(name)
    if not tpl:
        raise HTTPException(status_code=404, detail='House template not found')
    return tpl


@app.post('/admin/pipeline/upload-asset')
async def admin_pipeline_upload_asset(
    asset_type: str = Form(...),
    slug: str = Form(...),
    file: UploadFile = File(...),
):
    slug = slug.strip().lower()
    if not slug:
        raise HTTPException(status_code=400, detail='Slug is required')

    upload_dir = PIPELINE_DIR / 'data' / 'upload'

    if asset_type == 'audio':
        ext = Path(file.filename or '').suffix.lower()
        if ext not in ALLOWED_AUDIO_EXT:
            raise HTTPException(status_code=400, detail=f'Audio must be {", ".join(ALLOWED_AUDIO_EXT)}')
        target = upload_dir / 'songs' / f'{slug}{ext}'
    elif asset_type == 'thumbnail':
        ext = Path(file.filename or '').suffix.lower()
        if ext not in ALLOWED_THUMB_EXT:
            raise HTTPException(status_code=400, detail=f'Thumbnail must be {", ".join(ALLOWED_THUMB_EXT)}')
        target = upload_dir / 'thumbnails' / f'{slug}{ext}'
    else:
        raise HTTPException(status_code=400, detail='asset_type must be audio or thumbnail')

    target.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail='File too large (max 500MB)')

    target.write_bytes(content)
    return {'ok': True, 'path': str(target.relative_to(PIPELINE_DIR)), 'size': len(content)}


@app.get('/admin/pipeline/assets')
def admin_pipeline_assets():
    return list_available_assets()


@app.post('/admin/pipeline/start')
def admin_pipeline_start(
    slug: str = Form(...),
    title: str = Form(...),
    theme: str = Form(...),
    minutes: int = Form(42),
    loop_hours: float = Form(0),
    crossfade: int = Form(8),
    audio_preset: str = Form('ambient'),
    animated: bool = Form(False),
    public: bool = Form(False),
    skip_post_process: bool = Form(False),
    mood: str = Form(''),
    notes: str = Form(''),
    duration_hint: str = Form('long-form sleep track'),
    tags: str = Form(''),
    music_style: str = Form(''),
    music_influences: str = Form(''),
    music_tempo: str = Form(''),
    music_energy: str = Form(''),
    music_avoid: str = Form(''),
    thumbnail_scene: str = Form(''),
    thumbnail_elements: str = Form(''),
    thumbnail_text: str = Form(''),
    thumbnail_style: str = Form(''),
    thumbnail_avoid: str = Form(''),
    house: str = Form(''),
):
    slug = slug.strip().lower()
    title = title.strip()
    theme = theme.strip()
    if not slug:
        raise HTTPException(status_code=400, detail='Slug is required')
    if not title:
        raise HTTPException(status_code=400, detail='Title is required')
    if not theme:
        raise HTTPException(status_code=400, detail='Theme is required')

    audio_found = any(
        (PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{slug}{ext}').exists()
        for ext in ALLOWED_AUDIO_EXT
    )
    if not audio_found:
        raise HTTPException(status_code=400, detail=f'Audio file missing: upload/songs/{slug}.*')

    metadata = _build_song_metadata(
        slug=slug,
        title=title,
        theme=theme,
        mood=mood,
        notes=notes,
        duration_hint=duration_hint,
        tags=tags,
        music_style=music_style,
        music_influences=music_influences,
        music_tempo=music_tempo,
        music_energy=music_energy,
        music_avoid=music_avoid,
        thumbnail_scene=thumbnail_scene,
        thumbnail_elements=thumbnail_elements,
        thumbnail_text=thumbnail_text,
        thumbnail_style=thumbnail_style,
        thumbnail_avoid=thumbnail_avoid,
    )

    metadata_path = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{slug}.json'
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    config = {
        'minutes': minutes,
        'loop_hours': loop_hours,
        'crossfade': crossfade,
        'audio_preset': audio_preset,
        'animated': animated,
        'public': public,
        'skip_post_process': skip_post_process,
        'mood': mood or None,
        'house': house or theme or None,
        'metadata': metadata,
    }

    run_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()

    db.create_run({
        'run_id': run_id,
        'slug': slug,
        'title': title,
        'status': 'created',
        'config': config,
        'created_at': now,
    })

    start_run_async(run_id, slug, config, db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.get('/admin/pipeline/run/{run_id}', response_class=HTMLResponse)
def admin_pipeline_run_detail(request: Request, run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = db.get_run_logs(run_id, limit=1000)

    output_files: list[dict[str, str]] = []
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'youtube' / run['slug']
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({'name': f.name, 'size': f'{f.stat().st_size / 1024 / 1024:.1f} MB'})

    return templates.TemplateResponse('pipeline_run_detail.html', {
        'request': request,
        'page': 'pipeline',
        'run': run,
        'logs': logs,
        'output_files': output_files,
    })


@app.get('/admin/pipeline/run/{run_id}/logs')
def admin_pipeline_run_logs(run_id: str, after_id: int = Query(default=0, ge=0)):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = db.get_run_logs(run_id, after_id=after_id)
    return {'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')}


@app.post('/admin/pipeline/run/{run_id}/upload')
def admin_pipeline_run_upload(run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] not in {'rendered', 'failed'}:
        raise HTTPException(status_code=409, detail=f'Cannot upload from status {run["status"]}')

    trigger_upload(run_id, run['slug'], run.get('config', {}), db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.post('/admin/pipeline/run/{run_id}/cancel')
def admin_pipeline_run_cancel(run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] != 'running':
        raise HTTPException(status_code=409, detail='Can only cancel running pipelines')
    cancel_run(run_id, db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.get('/admin/pipeline/preview/{slug}/{filename}')
def admin_pipeline_preview_file(slug: str, filename: str):
    path = get_output_path(slug, filename)
    if not path:
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@app.post('/github/webhook')
async def github_webhook(
    request: Request,
    x_github_delivery: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, Any]:
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail='Missing X-GitHub-Delivery header')
    if not x_github_event:
        raise HTTPException(status_code=400, detail='Missing X-GitHub-Event header')

    raw_body = await request.body()
    verify_signature(raw_body, x_hub_signature_256)

    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail='Invalid JSON payload') from exc

    event_record = build_event_record(x_github_delivery, x_github_event, payload)
    was_inserted = db.insert_github_event(event_record)

    snapshot_updated = False
    updated_snapshot: dict[str, Any] | None = None
    task_id = event_record.get('task_id')
    if task_id:
        existing_snapshot = db.get_snapshot(task_id)
        updated_snapshot = update_snapshot_from_event(existing_snapshot, event_record)
        if updated_snapshot:
            db.upsert_snapshot(updated_snapshot)
            snapshot_updated = True

    normalized_event = normalize_task_event(event_record, updated_snapshot)
    task_event_inserted, assigned_seq = _append_task_event(normalized_event)

    task_state_updated = False
    if normalized_event and updated_snapshot and assigned_seq:
        existing = db.get_task_state(normalized_event['task_id'])
        if existing:
            task_state = existing.copy()
            task_state['snapshot'] = updated_snapshot
            task_state['latest_seq'] = assigned_seq
            task_state['updated_at'] = updated_snapshot.get('updated_at', utc_now_iso())
        else:
            task_state = create_task_state(normalized_event['task_id'], updated_snapshot, assigned_seq)
        db.upsert_task_state(normalized_event['task_id'], task_state)
        task_state_updated = True

    return {
        'ok': True,
        'delivery_id': x_github_delivery,
        'event_type': x_github_event,
        'action': event_record.get('action'),
        'task_id': event_record.get('task_id'),
        'event_inserted': was_inserted,
        'snapshot_updated': snapshot_updated,
        'task_event_inserted': task_event_inserted,
        'task_state_updated': task_state_updated,
        'seq': assigned_seq or None,
    }
