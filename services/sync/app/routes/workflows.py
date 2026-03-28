"""Workflow routes – compatibility redirects and API."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app import shared
from app.helpers import _build_song_metadata, slugify
from app.audio_jobs import create_audio_job
from app.workflow_orchestrator import start_workflow

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get('/admin/workflow')
def admin_workflow_list(request: Request):
    return RedirectResponse(url='/admin/pipeline/new', status_code=303)


@router.get('/admin/workflow/new')
def admin_workflow_new(request: Request):
    return RedirectResponse(url='/admin/pipeline/new', status_code=303)


@router.get('/admin/workflow/{workflow_id}')
def admin_workflow_detail(request: Request, workflow_id: str):
    wf = shared.db.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail='Workflow not found')
    return RedirectResponse(url=f'/admin/pipeline/run/{workflow_id}', status_code=303)


@router.post('/admin/workflow/start')
def admin_workflow_start(
    title: str = Form(...),
    theme: str = Form(...),
    prompt_text: str = Form(''),
    minutes: int = Form(20),
    model: str = Form('medium'),
    clip_seconds: int = Form(30),
    loop_hours: float = Form(0),
    crossfade: int = Form(8),
    auto_upload: bool = Form(False),
    house: str = Form(''),
    mood: str = Form(''),
    thumbnail_scene: str = Form(''),
    thumbnail_text: str = Form(''),
    thumbnail_style: str = Form(''),
):
    title = title.strip()
    slug = slugify(title)
    theme = theme.strip()
    prompt_text = prompt_text.strip()

    if not title:
        raise HTTPException(status_code=400, detail='Title is required')
    if not theme:
        raise HTTPException(status_code=400, detail='Theme is required')
    if not prompt_text:
        raise HTTPException(status_code=400, detail='Provide prompt text')

    audio_job_id = create_audio_job(
        slug=slug,
        title=title,
        prompt_text=prompt_text,
        preset_name=None,
        minutes=minutes,
        model=model,
        clip_seconds=clip_seconds,
        db=shared.db,
    )

    metadata = _build_song_metadata(
        slug=slug, title=title, theme=theme, mood=mood,
        notes='', duration_hint='long-form sleep track', tags='',
        music_style='', music_influences='', music_tempo='',
        music_energy='', music_avoid='',
        thumbnail_scene=thumbnail_scene, thumbnail_elements='',
        thumbnail_text=thumbnail_text, thumbnail_style=thumbnail_style,
        thumbnail_avoid='',
    )

    pipeline_config = {
        'minutes': minutes,
        'loop_hours': loop_hours,
        'crossfade': crossfade,
        'audio_preset': 'ambient',
        'animated': False,
        'public': False,
        'skip_post_process': False,
        'mood': mood or None,
        'house': house or theme or None,
        'metadata': metadata,
    }

    now = _now_iso()
    workflow_id = uuid.uuid4().hex[:12]

    shared.db.create_workflow({
        'workflow_id': workflow_id,
        'slug': slug,
        'title': title,
        'type': 'video',
        'status': 'waiting_for_audio',
        'phase': 'audio',
        'audio_job_id': audio_job_id,
        'auto_upload': auto_upload,
        'config': pipeline_config,
        'created_at': now,
    })
    shared.db.append_workflow_log(workflow_id, 'system', 'One-Click-Workflow gestartet. Warte auf Audio-Job.', now)

    start_workflow(workflow_id, audio_job_id, slug, title, pipeline_config, auto_upload, shared.db)
    return RedirectResponse(url=f'/admin/pipeline/run/{workflow_id}', status_code=303)


@router.get('/api/workflow/{workflow_id}')
def api_workflow_detail(workflow_id: str):
    wf = shared.db.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail='Workflow not found')
    return wf
