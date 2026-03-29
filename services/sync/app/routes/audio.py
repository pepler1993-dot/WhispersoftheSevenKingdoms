"""Audio generator routes."""
from __future__ import annotations

import uuid
from datetime import datetime
import mimetypes
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _load_house_templates
from app.audio_jobs import (
    CANCELLABLE_AUDIO_JOB_STATUSES,
    FINAL_AUDIO_JOB_STATUSES,
    create_audio_job,
    get_audio_generator_health,
    get_audio_generator,
)

router = APIRouter()


@router.get('/admin/audio', response_class=HTMLResponse)
def admin_audio(request: Request):
    jobs = shared.db.list_audio_jobs(limit=100)
    return shared.templates.TemplateResponse(request, 'audio_generator.html', {
        'request': request,
        'page': 'audio',
        'audio_tab': 'new',
        'audio_job_count': len(jobs),
        'house_templates': _load_house_templates(),
    })


@router.get('/admin/audio/jobs', response_class=HTMLResponse)
def admin_audio_jobs_list(request: Request):
    from app.routes.dashboard import _humanize_error
    jobs = shared.db.list_audio_jobs(limit=100)
    for j in jobs:
        if j.get('error_message'):
            j['error_display'] = _humanize_error(j['error_message'])
    return shared.templates.TemplateResponse(request, 'audio_jobs.html', {
        'request': request,
        'page': 'audio',
        'audio_tab': 'jobs',
        'audio_job_count': len(jobs),
        'jobs': jobs,
    })


@router.get('/admin/audio/health')
def admin_audio_health():
    return get_audio_generator_health()


@router.post('/admin/audio/generate')
def admin_audio_generate(
    slug: str = Form(...),
    title: str = Form(''),
    prompt_text: str = Form(''),
    minutes: int = Form(42),
    model: str = Form('medium'),
    clip_seconds: int = Form(47),
    steps: int = Form(50),
):
    slug = slug.strip().lower()
    title = title.strip() or slug.replace('-', ' ').title()
    prompt_text = prompt_text.strip()

    if not slug:
        raise HTTPException(status_code=400, detail='Slug is required')
    if not prompt_text:
        raise HTTPException(status_code=400, detail='Provide prompt text')

    job_id = create_audio_job(
        slug=slug,
        title=title,
        prompt_text=prompt_text,
        preset_name=None,
        minutes=minutes,
        model=model,
        clip_seconds=clip_seconds,
        db=shared.db,
        steps=steps,
    )

    # Create Audio Lab workflow
    workflow_id = uuid.uuid4().hex[:12]
    now = datetime.now(shared.CET).isoformat()
    shared.db.create_workflow({
        'workflow_id': workflow_id,
        'slug': slug,
        'title': title,
        'type': 'audio_lab',
        'phase': 'audio',
        'status': 'waiting_for_audio',
        'audio_job_id': job_id,
        'config': {
            'prompt_text': prompt_text,
            'minutes': minutes,
            'model': model,
            'clip_seconds': clip_seconds,
            'steps': steps,
        },
        'created_at': now,
    })
    shared.db.append_workflow_log(workflow_id, 'system', f'Audio Lab Workflow gestartet. Audio-Job: {job_id}', now)

    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)


@router.get('/admin/audio/jobs/{job_id}', response_class=HTMLResponse)
def admin_audio_job_detail(request: Request, job_id: str):
    job = shared.db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    logs = shared.db.get_audio_job_logs(job_id, limit=1000)
    return shared.templates.TemplateResponse(request, 'audio_job_detail.html', {
        'request': request,
        'page': 'audio',
        'job': job,
        'logs': logs,
    })


@router.get('/admin/audio/stream/{job_id}')
def admin_audio_stream(job_id: str):
    """Stream audio file for in-browser playback."""
    job = shared.db.get_audio_job(job_id)
    if not job or not job.get('output_path'):
        raise HTTPException(status_code=404, detail='Audio file not found')
    audio_path = Path(job['output_path'])
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail='Audio file missing from disk')
    media_type, _ = mimetypes.guess_type(str(audio_path))
    return FileResponse(audio_path, media_type=media_type or 'application/octet-stream', filename=audio_path.name)


@router.get('/admin/audio/jobs/{job_id}/logs')
def admin_audio_job_logs(job_id: str, after_id: int = Query(default=0, ge=0)):
    job = shared.db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    logs = shared.db.get_audio_job_logs(job_id, after_id=after_id)
    return {'logs': logs, 'status': job['status'], 'error_message': job.get('error_message')}


@router.post('/admin/audio/jobs/{job_id}/retry')
def admin_audio_job_retry(job_id: str):
    job = shared.db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')

    status = job.get('status', '')
    if status not in ('error', 'cancelled'):
        raise HTTPException(status_code=409, detail=f'Can only retry failed/cancelled jobs (current: {status})')

    new_job_id = create_audio_job(
        slug=job['slug'],
        title=job.get('title', job['slug']),
        prompt_text=job.get('prompt_text', ''),
        preset_name=None,
        minutes=job.get('minutes') or 60,
        model=job.get('model', 'medium'),
        clip_seconds=job.get('clip_seconds') or 47,
        db=shared.db,
        house=job.get('house', ''),
        base_dna=job.get('base_dna', ''),
        negative_prompt=job.get('negative_prompt', ''),
    )
    return RedirectResponse(url=f'/admin/audio/jobs/{new_job_id}', status_code=303)


@router.post('/admin/audio/jobs/{job_id}/cancel')
def admin_audio_job_cancel(job_id: str):
    job = shared.db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')

    status = job.get('status')
    now = datetime.now(shared.CET).isoformat()

    if status in FINAL_AUDIO_JOB_STATUSES:
        shared.db.append_audio_job_log(job_id, 'system', f'Cancel ignored: job is already in final state ({status}).', now)
        return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)

    if status not in CANCELLABLE_AUDIO_JOB_STATUSES:
        shared.db.append_audio_job_log(job_id, 'system', f'Cancel ignored: status {status} cannot be cancelled.', now)
        return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)

    generator = get_audio_generator()
    cancelled = generator.cancel(job, shared.db)
    if not cancelled:
        shared.db.append_audio_job_log(job_id, 'system', 'Cancellation request failed or is not supported for this provider/state.', now)

    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)
