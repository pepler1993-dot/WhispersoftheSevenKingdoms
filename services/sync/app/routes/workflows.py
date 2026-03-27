"""One-Click Workflow routes – Audio → Pipeline → Upload."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _load_house_templates, _build_song_metadata, slugify
from app.audio_jobs import create_audio_job
from app.stores.workflows import (
    create_workflow,
    get_workflow,
    list_workflows,
)
from app.pipeline_workflow import start_workflow

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Views ────────────────────────────────────────────────────────────────

@router.get('/admin/workflow', response_class=HTMLResponse)
def admin_workflow_list(request: Request):
    wfs = list_workflows(shared.db, limit=50)
    return shared.templates.TemplateResponse(request, 'workflows.html', {
        'page': 'pipeline',
        'workflows': wfs,
    })


@router.get('/admin/workflow/new', response_class=HTMLResponse)
def admin_workflow_new(request: Request):
    houses = _load_house_templates()
    return shared.templates.TemplateResponse(request, 'workflow_new.html', {
        'page': 'pipeline',
        'houses': houses,
    })


@router.get('/admin/workflow/{workflow_id}', response_class=HTMLResponse)
def admin_workflow_detail(request: Request, workflow_id: str):
    wf = get_workflow(shared.db, workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail='Workflow not found')

    audio_job = None
    pipeline_run = None
    if wf.get('audio_job_id'):
        audio_job = shared.db.get_audio_job(wf['audio_job_id'])
    if wf.get('pipeline_run_id'):
        pipeline_run = shared.db.get_run(wf['pipeline_run_id'])

    return shared.templates.TemplateResponse(request, 'workflow_detail.html', {
        'page': 'pipeline',
        'wf': wf,
        'audio_job': audio_job,
        'pipeline_run': pipeline_run,
    })


# ── Create ───────────────────────────────────────────────────────────────

@router.post('/admin/workflow/start')
def admin_workflow_start(
    title: str = Form(...),
    theme: str = Form(...),
    prompt_text: str = Form(''),
    minutes: int = Form(42),
    model: str = Form('stable-audio'),
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

    # 1. Create audio job
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

    # 2. Build pipeline config for later
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

    # 3. Create workflow
    now = _now_iso()
    workflow_id = uuid.uuid4().hex[:12]

    create_workflow(shared.db, {
        'workflow_id': workflow_id,
        'title': title,
        'slug': slug,
        'phase': 'audio',
        'status': 'running',
        'audio_job_id': audio_job_id,
        'config': pipeline_config,
        'auto_upload': auto_upload,
        'created_at': now,
        'updated_at': now,
    })

    # 4. Start orchestrator polling
    start_workflow(workflow_id, audio_job_id, slug, title, pipeline_config, auto_upload, shared.db)

    return RedirectResponse(url=f'/admin/workflow/{workflow_id}', status_code=303)


# ── API ──────────────────────────────────────────────────────────────────

@router.get('/api/workflow/{workflow_id}')
def api_workflow_detail(workflow_id: str):
    wf = get_workflow(shared.db, workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail='Workflow not found')
    return wf
