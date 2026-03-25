"""Audio generator routes."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _load_house_templates
from app.kaggle_gen import (
    CANCELLABLE_AUDIO_JOB_STATUSES,
    FINAL_AUDIO_JOB_STATUSES,
    create_audio_job,
    find_prompt_preset,
    get_audio_generator,
    get_audio_generator_health,
    list_prompt_presets,
)

router = APIRouter()


@router.get('/admin/audio', response_class=HTMLResponse)
def admin_audio(request: Request):
    presets = list_prompt_presets()
    jobs = shared.db.list_audio_jobs(limit=100)
    health_placeholder = {
        'provider': 'checking',
        'available': None,
        'gpu': None,
        'host': None,
        'model': None,
        'error': None,
    }
    return shared.templates.TemplateResponse(request, 'audio_generator.html', {
        'request': request,
        'page': 'audio',
        'health': health_placeholder,
        'presets': presets,
        'jobs': jobs,
        'house_templates': _load_house_templates(),
    })


@router.get('/admin/audio/health')
def admin_audio_health():
    return get_audio_generator_health()


@router.post('/admin/audio/generate')
def admin_audio_generate(
    slug: str = Form(...),
    title: str = Form(''),
    prompt_text: str = Form(''),
    preset_name: str = Form(''),
    minutes: int = Form(42),
    model: str = Form('medium'),
    clip_seconds: int = Form(30),
    steps: int = Form(50),
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
        db=shared.db,
        steps=steps,
    )
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
    return FileResponse(audio_path, media_type='audio/wav', filename=audio_path.name)


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
        preset_name=job.get('preset_name'),
        minutes=job.get('minutes') or 42,
        model=job.get('model', 'medium'),
        clip_seconds=job.get('clip_seconds') or 30,
        db=shared.db,
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

    generator = get_audio_generator(job.get('provider'))
    cancelled = generator.cancel(job, shared.db)
    if not cancelled:
        shared.db.append_audio_job_log(job_id, 'system', 'Cancellation request failed or is not supported for this provider/state.', now)

    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)
