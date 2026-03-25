"""Pipeline control panel routes."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import shared
from app.helpers import (
    _build_song_metadata,
    _get_house_template,
    _load_house_templates,
    slugify,
)
from app.pipeline_runner import (
    PIPELINE_DIR,
    cancel_run,
    get_output_path,
    list_available_assets,
    list_available_themes,
    list_library_tracks_for_pipeline,
    trigger_upload,
)
from app.pipeline_queue import enqueue_run, get_queue_status

router = APIRouter()

ALLOWED_AUDIO_EXT = {'.mp3', '.wav', '.ogg'}
ALLOWED_THUMB_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB


def _detect_thumbnail_source(slug: str, selected_thumbnail: str | None, metadata: dict[str, Any]) -> dict[str, Any]:
    selected_thumbnail = (selected_thumbnail or '').strip()
    upload_dir = PIPELINE_DIR / 'data' / 'upload' / 'thumbnails'
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'thumbnails'

    if selected_thumbnail:
        selected_path = output_dir / selected_thumbnail
        return {
            'type': 'library',
            'label': 'Aus Thumbnail-Library gewählt',
            'path': str(selected_path.relative_to(PIPELINE_DIR)) if selected_path.exists() else f'data/output/thumbnails/{selected_thumbnail}',
            'filename': selected_thumbnail,
            'fallback_reason': None,
        }

    upload_match = next((upload_dir / f'{slug}{ext}' for ext in ALLOWED_THUMB_EXT if (upload_dir / f'{slug}{ext}').exists()), None)
    if upload_match:
        return {
            'type': 'upload',
            'label': 'Manuell hochgeladenes Thumbnail',
            'path': str(upload_match.relative_to(PIPELINE_DIR)),
            'filename': upload_match.name,
            'fallback_reason': None,
        }

    thumb_brief = (metadata or {}).get('thumbnail_brief') or {}
    if any((thumb_brief.get('scene'), thumb_brief.get('elements'), thumb_brief.get('style'), thumb_brief.get('text'))):
        return {
            'type': 'briefing',
            'label': 'Wird aus dem Thumbnail-Briefing generiert',
            'path': None,
            'filename': None,
            'fallback_reason': None,
        }

    return {
        'type': 'fallback',
        'label': 'Fallback / unbekannte Quelle',
        'path': None,
        'filename': None,
        'fallback_reason': 'Kein Library-Thumbnail, kein Upload und kein verwertbares Thumbnail-Briefing gefunden.',
    }


@router.get('/admin/pipeline', response_class=HTMLResponse)
def admin_pipeline(request: Request):
    runs = shared.db.list_runs(limit=100)
    houses = _load_house_templates()
    queue = get_queue_status(shared.db)
    return shared.templates.TemplateResponse(request, 'pipeline_runs.html', {
        'request': request,
        'page': 'pipeline',
        'runs': runs,
        'houses': houses,
        'queue': queue,
    })


@router.get('/admin/pipeline/new', response_class=HTMLResponse)
def admin_pipeline_new(request: Request, slug: str | None = Query(default=None), error: str | None = Query(default=None)):
    assets = list_available_assets()
    themes = list_available_themes()
    houses = _load_house_templates()
    library_tracks = list_library_tracks_for_pipeline(shared.db)
    thumb_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'output' / 'thumbnails'
    library_thumbnails = sorted(f.name for f in thumb_dir.iterdir() if f.is_file() and f.suffix in {'.jpg', '.jpeg', '.png', '.webp'}) if thumb_dir.exists() else []
    prefill_slug = (slug or '').strip().lower()
    prefill_thumbnail_source = _detect_thumbnail_source(prefill_slug, None, {}) if prefill_slug else None
    return shared.templates.TemplateResponse(request, 'pipeline_new.html', {
        'request': request,
        'page': 'pipeline',
        'assets': assets,
        'themes': themes,
        'houses': houses,
        'library_tracks': library_tracks,
        'library_thumbnails': library_thumbnails,
        'prefill_slug': prefill_slug,
        'prefill_thumbnail_source': prefill_thumbnail_source,
        'error_message': error or '',
    })


@router.get('/admin/api/house/{name}')
def api_house_template(name: str):
    tpl = _get_house_template(name)
    if not tpl:
        raise HTTPException(status_code=404, detail='House template not found')
    return tpl


@router.post('/admin/pipeline/upload-asset')
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


@router.get('/admin/pipeline/assets')
def admin_pipeline_assets():
    return list_available_assets()


@router.post('/admin/pipeline/start')
def admin_pipeline_start(
    slug: str = Form(''),
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
    thumbnail_file: str = Form(''),
):
    title = title.strip()
    slug = slugify(title)
    theme = theme.strip()
    if not slug:
        raise HTTPException(status_code=400, detail='Title must produce a valid slug')
    if not title:
        raise HTTPException(status_code=400, detail='Title is required')
    if not theme:
        raise HTTPException(status_code=400, detail='Theme is required')

    audio_found = any(
        (PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{slug}{ext}').exists()
        for ext in ALLOWED_AUDIO_EXT
    )
    if not audio_found:
        return RedirectResponse(
            url=f'/admin/pipeline/new?slug={slug}&error=Kein+Audio-Track+f\u00fcr+"{slug}"+gefunden.+Generiere+zuerst+einen+Track+im+Audio+Lab.',
            status_code=303,
        )

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

    thumbnail_source = _detect_thumbnail_source(slug, thumbnail_file, metadata)

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
        'thumbnail_source': thumbnail_source,
    }

    run_id = uuid.uuid4().hex[:12]
    now = datetime.now(shared.CET).isoformat()

    shared.db.create_run({
        'run_id': run_id,
        'slug': slug,
        'title': title,
        'status': 'created',
        'config': config,
        'created_at': now,
    })

    enqueue_run(run_id, slug, config, shared.db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@router.get('/admin/pipeline/run/{run_id}', response_class=HTMLResponse)
def admin_pipeline_run_detail(request: Request, run_id: str):
    run = shared.db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = shared.db.get_run_logs(run_id, limit=1000)

    output_files: list[dict[str, str]] = []
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'youtube' / run['slug']
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({'name': f.name, 'size': f'{f.stat().st_size / 1024 / 1024:.1f} MB'})

    return shared.templates.TemplateResponse(request, 'pipeline_run_detail.html', {
        'request': request,
        'page': 'pipeline',
        'run': run,
        'logs': logs,
        'output_files': output_files,
    })


@router.get('/admin/pipeline/run/{run_id}/logs')
def admin_pipeline_run_logs(run_id: str, after_id: int = Query(default=0, ge=0)):
    run = shared.db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = shared.db.get_run_logs(run_id, after_id=after_id)
    return {'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')}


@router.post('/admin/pipeline/run/{run_id}/upload')
def admin_pipeline_run_upload(run_id: str):
    run = shared.db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] not in {'rendered', 'failed'}:
        raise HTTPException(status_code=409, detail=f'Cannot upload from status {run["status"]}')

    trigger_upload(run_id, run['slug'], run.get('config', {}), shared.db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@router.post('/admin/pipeline/run/{run_id}/cancel')
def admin_pipeline_run_cancel(run_id: str):
    run = shared.db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] == 'queued':
        shared.db.update_run(run_id, status='cancelled', finished_at=datetime.now(shared.CET).isoformat())
        shared.db.append_run_log(run_id, 'system', 'Job aus Warteschlange entfernt.', datetime.now(shared.CET).isoformat())
        return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)
    if run['status'] != 'running':
        raise HTTPException(status_code=409, detail='Can only cancel running or queued pipelines')
    cancel_run(run_id, shared.db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@router.get('/admin/pipeline/preview/{slug}/{filename}')
def admin_pipeline_preview_file(slug: str, filename: str):
    path = get_output_path(slug, filename)
    if not path:
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@router.get('/api/pipeline/queue')
def api_pipeline_queue():
    return get_queue_status(shared.db)
