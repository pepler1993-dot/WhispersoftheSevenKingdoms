"""Pipeline control panel routes."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
import shutil
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
from app.pipeline_queue import enqueue_workflow, get_queue_status
from app.audio_jobs import create_audio_job
from app.workflow_orchestrator import start_workflow

router = APIRouter()

ALLOWED_AUDIO_EXT = {'.mp3', '.wav', '.ogg'}
ALLOWED_THUMB_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB


def _detect_thumbnail_source(slug: str, selected_thumbnail: str | None, metadata: dict[str, Any]) -> dict[str, Any]:
    selected_thumbnail = (selected_thumbnail or '').strip()
    upload_dir = PIPELINE_DIR / 'data' / 'upload' / 'thumbnails'
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'thumbnails'

    if selected_thumbnail:
        # Handle slug-prefixed YouTube output thumbnails (e.g. "my-slug--thumbnail.jpg")
        if '--' in selected_thumbnail:
            yt_slug, yt_filename = selected_thumbnail.split('--', 1)
            yt_path = PIPELINE_DIR / 'data' / 'output' / 'youtube' / yt_slug / yt_filename
            return {
                'type': 'library',
                'label': f'Pipeline-Thumbnail ({yt_slug})',
                'path': str(yt_path.relative_to(PIPELINE_DIR)) if yt_path.exists() else f'data/output/youtube/{yt_slug}/{yt_filename}',
                'filename': selected_thumbnail,
                'fallback_reason': None,
            }
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


def _place_selected_thumbnail(slug: str, thumbnail_source: dict[str, Any]) -> None:
    """Copy a library-selected thumbnail to data/upload/thumbnails/{slug}.ext so pipeline.py finds it."""
    if thumbnail_source.get('type') != 'library':
        return
    src_path_str = thumbnail_source.get('path')
    if not src_path_str:
        return
    src = PIPELINE_DIR / src_path_str
    if not src.exists():
        return
    dest_dir = PIPELINE_DIR / 'data' / 'upload' / 'thumbnails'
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f'{slug}{src.suffix.lower()}'
    if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
        shutil.copy2(src, dest)


def _detect_background_source(selected_background: str | None, theme: str) -> dict[str, Any]:
    selected_background = (selected_background or '').strip()
    bg_dir = PIPELINE_DIR / 'data' / 'assets' / 'backgrounds'

    if selected_background:
        bg_path = bg_dir / selected_background
        return {
            'type': 'library',
            'label': 'Explizit als Video-Hintergrund gewählt',
            'path': str(bg_path.relative_to(PIPELINE_DIR)) if bg_path.exists() else f'data/assets/backgrounds/{selected_background}',
            'filename': selected_background,
            'fallback_reason': None,
        }

    theme_path = bg_dir / f'{theme}.jpg'
    if theme_path.exists():
        return {
            'type': 'theme-default',
            'label': 'Theme-Standardhintergrund fürs Video',
            'path': str(theme_path.relative_to(PIPELINE_DIR)),
            'filename': theme_path.name,
            'fallback_reason': None,
        }

    return {
        'type': 'fallback',
        'label': 'Fallback / kein Video-Hintergrund gefunden',
        'path': None,
        'filename': None,
        'fallback_reason': f'Kein expliziter Hintergrund gewählt und kein Theme-Background für {theme} gefunden.',
    }


def _resolve_background_from_house_variant(house_key: str, variant_key: str) -> str | None:
    """Match library filename (any common image ext) from preset bg_key."""
    if not (house_key and variant_key):
        return None
    houses = _load_house_templates()
    h = houses.get(house_key.strip(), {})
    bp = (h.get('background_prompts') or {}).get(variant_key.strip(), {})
    bg_key = (bp or {}).get('bg_key')
    if not bg_key or not isinstance(bg_key, str):
        return None
    bg_dir = PIPELINE_DIR / 'data' / 'assets' / 'backgrounds'
    for ext in ('.jpg', '.jpeg', '.png', '.webp'):
        fn = f'{bg_key}{ext}'
        if (bg_dir / fn).is_file():
            return fn
    return f'{bg_key}.jpg'


def _prompts_from_house_variant(house_key: str, variant_key: str) -> str:
    """Audio prompts exist only per variant (no house-level prompts)."""
    houses = _load_house_templates()
    h = houses.get((house_key or '').strip(), {})
    variant_key = (variant_key or '').strip()
    vp = h.get('variant_prompts') or {}
    if not variant_key or variant_key not in vp:
        raise HTTPException(
            status_code=400,
            detail='Bitte eine Haus-Variante wählen — Audio-Prompts sind nur pro Variante definiert.',
        )
    raw = vp[variant_key]
    if not isinstance(raw, list):
        raise HTTPException(status_code=400, detail=f'Ungültige Prompt-Liste für Variante „{variant_key}".')
    lines = [x for x in raw if isinstance(x, str) and x.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail=f'Keine Prompts für Variante „{variant_key}" hinterlegt.')
    return '\n'.join(lines)


def _get_house_sleep_fields(house_key: str) -> dict:
    """Return base_dna and negative_prompt from house templates for sleep-first prompts."""
    houses = _load_house_templates()
    h = houses.get((house_key or '').strip(), {})
    return {
        'base_dna': h.get('base_dna', ''),
        'negative_prompt': h.get('negative_prompt', ''),
    }


@router.get('/admin/pipeline/logs', response_class=HTMLResponse)
def admin_pipeline_logs(request: Request):
    from app.routes.dashboard import _humanize_error
    workflows = shared.db.list_workflows(type='video', limit=100)
    for w in workflows:
        try:
            if w.get('error_message'):
                w['error_display'] = _humanize_error(w['error_message'])
        except Exception:
            w['error_display'] = str(w.get('error_message', ''))[:60]
    houses = _load_house_templates()
    queue = get_queue_status(shared.db)
    return shared.templates.TemplateResponse(request, 'pipeline_runs.html', {
        'request': request,
        'page': 'pipeline',
        'pipeline_tab': 'overview',
        'pipeline_run_count': len(workflows),
        'runs': workflows,
        'houses': houses,
        'queue': queue,
    })


@router.get('/admin/pipeline', response_class=HTMLResponse)
@router.get('/admin/pipeline/new', response_class=HTMLResponse)
def admin_pipeline_new(request: Request, slug: str | None = Query(default=None), error: str | None = Query(default=None)):
    assets = list_available_assets()
    themes = list_available_themes()
    houses = _load_house_templates()
    workflows = shared.db.list_workflows(type='video', limit=100)
    library_tracks = list_library_tracks_for_pipeline(shared.db)
    # Collect thumbnails from both manual output dir and pipeline-generated YouTube outputs
    thumb_dir = PIPELINE_DIR / 'data' / 'output' / 'thumbnails'
    yt_output_dir = PIPELINE_DIR / 'data' / 'output' / 'youtube'
    _thumb_exts = {'.jpg', '.jpeg', '.png', '.webp'}
    _thumbs = set()
    if thumb_dir.exists():
        _thumbs.update(f.name for f in thumb_dir.iterdir() if f.is_file() and f.suffix.lower() in _thumb_exts)
    if yt_output_dir.exists():
        for slug_dir in yt_output_dir.iterdir():
            if slug_dir.is_dir():
                for f in slug_dir.iterdir():
                    if f.name.startswith('thumbnail') and f.suffix.lower() in _thumb_exts:
                        # Use slug-prefixed name to avoid collisions
                        _thumbs.add(f'{slug_dir.name}--{f.name}')
    library_thumbnails = sorted(_thumbs)
    bg_dir = PIPELINE_DIR / 'data' / 'assets' / 'backgrounds'
    library_backgrounds = sorted(f.name for f in bg_dir.iterdir() if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}) if bg_dir.exists() else []
    prefill_slug = (slug or '').strip().lower()
    prefill_thumbnail_source = _detect_thumbnail_source(prefill_slug, None, {}) if prefill_slug else None
    return shared.templates.TemplateResponse(request, 'pipeline_new.html', {
        'request': request,
        'page': 'pipeline',
        'pipeline_tab': 'new',
        'pipeline_run_count': len(workflows),
        'assets': assets,
        'themes': themes,
        'houses': houses,
        'library_tracks': library_tracks,
        'library_thumbnails': library_thumbnails,
        'library_backgrounds': library_backgrounds,
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

    # Stream to disk in chunks to avoid loading entire file into RAM
    total_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    tmp_target = target.with_suffix(target.suffix + '.tmp')
    try:
        with open(tmp_target, 'wb') as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_UPLOAD_SIZE:
                    tmp_target.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail='File too large (max 500MB)')
                f.write(chunk)
        tmp_target.rename(target)
    except HTTPException:
        raise
    except Exception as e:
        tmp_target.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f'Upload failed: {e}')

    return {'ok': True, 'path': str(target.relative_to(PIPELINE_DIR)), 'size': total_size}


@router.get('/admin/pipeline/assets')
def admin_pipeline_assets():
    return list_available_assets()


@router.post('/admin/pipeline/start')
def admin_pipeline_start(
    title: str = Form(...),
    theme: str = Form(...),
    minutes: int = Form(60),
    loop_hours: float = Form(0),
    crossfade: int = Form(8),
    audio_preset: str = Form('ambient'),
    animated: bool = Form(False),
    auto_upload: bool = Form(False),
    public: bool = Form(False),
    skip_post_process: bool = Form(False),
    mood: str = Form(''),
    notes: str = Form(''),
    variant_key: str = Form(''),
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
    background_file: str = Form(''),
    audio_source: str = Form('library'),
    selected_audio_track: str = Form(''),
    audio_job_id: str = Form(''),
    gen_minutes: int = Form(60),
    gen_steps: int = Form(50),
    gen_model: str = Form('medium'),
    gen_prompt: str = Form(''),
):
    title = title.strip()
    theme = theme.strip()
    variant_key = (variant_key or notes or '').strip()
    slug = slugify(title)
    if not slug:
        raise HTTPException(status_code=400, detail='Title must produce a valid slug')
    if not title:
        raise HTTPException(status_code=400, detail='Title is required')
    if not theme:
        raise HTTPException(status_code=400, detail='Theme is required')
    if not house.strip():
        raise HTTPException(status_code=400, detail='Bitte ein Haus wählen.')
    if not variant_key:
        raise HTTPException(status_code=400, detail='Bitte eine Haus-Variante wählen.')

    selected_audio_track = (selected_audio_track or '').strip()
    audio_job_id = (audio_job_id or '').strip()
    audio_path = None

    if audio_source == 'library':
        if not selected_audio_track:
            return RedirectResponse(
                url=f'/admin/pipeline/new?slug={slug}&error=Bitte+einen+Audio-Track+aus+der+Bibliothek+wählen.',
                status_code=303,
            )
        for ext in ALLOWED_AUDIO_EXT:
            candidate = PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{selected_audio_track}{ext}'
            if candidate.exists():
                audio_path = candidate
                break
        if not audio_path:
            return RedirectResponse(
                url=f'/admin/pipeline/new?slug={slug}&error=Der+gewählte+Library-Track+wurde+nicht+gefunden.',
                status_code=303,
            )

    audio_found = bool(audio_path) or any(
        (PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{slug}{ext}').exists()
        for ext in ALLOWED_AUDIO_EXT
    )

    existing_audio_job = shared.db.get_audio_job(audio_job_id) if audio_job_id else None

    # -- Generate mode: start full workflow (Audio -> Pipeline -> Upload) --
    if not audio_found and audio_source == 'generate':
        if existing_audio_job and existing_audio_job.get('status') in {'queued', 'pushing', 'running', 'downloading', 'complete'}:
            resolved_audio_job_id = audio_job_id
        else:
            prompt_text = gen_prompt.strip()
            if not prompt_text:
                prompt_text = _prompts_from_house_variant(house, variant_key)

            sleep_fields = _get_house_sleep_fields(house)
            resolved_audio_job_id = create_audio_job(
                slug=slug,
                title=title,
                prompt_text=prompt_text,
                preset_name=None,
                minutes=gen_minutes,
                model=gen_model,
                clip_seconds=47,
                db=shared.db,
                steps=gen_steps,
                house=house,
                base_dna=sleep_fields['base_dna'],
                negative_prompt=sleep_fields['negative_prompt'],
            )

        metadata = _build_song_metadata(
            slug=slug, title=title, theme=theme, mood=mood,
            notes=notes, duration_hint=duration_hint, tags=tags,
            music_style=music_style, music_influences=music_influences,
            music_tempo=music_tempo, music_energy=music_energy,
            music_avoid=music_avoid, thumbnail_scene=thumbnail_scene,
            thumbnail_elements=thumbnail_elements, thumbnail_text=thumbnail_text,
            thumbnail_style=thumbnail_style, thumbnail_avoid=thumbnail_avoid,
        )

        metadata_path = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{slug}.json'
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

        thumbnail_source = _detect_thumbnail_source(slug, thumbnail_file, metadata)
        _place_selected_thumbnail(slug, thumbnail_source)
        bg_selected = (background_file or '').strip()
        if not bg_selected:
            bg_selected = (_resolve_background_from_house_variant(house, variant_key) or '').strip()
        background_source = _detect_background_source(bg_selected or None, theme)

        pipeline_config = {
            'minutes': minutes,
            'loop_hours': loop_hours,
            'crossfade': crossfade,
            'audio_preset': audio_preset,
            'animated': animated,
            'auto_upload': auto_upload,
            'public': public,
            'skip_post_process': skip_post_process,
            'mood': mood or None,
            'house': house or theme or None,
            'variant_key': variant_key or None,
            'metadata': metadata,
            'thumbnail_source': thumbnail_source,
            'background_source': background_source,
        }

        now = datetime.now(shared.CET).isoformat()
        workflow_id = uuid.uuid4().hex[:12]

        shared.db.create_workflow({
            'workflow_id': workflow_id,
            'slug': slug,
            'title': title,
            'type': 'video',
            'status': 'waiting_for_audio',
            'phase': 'audio',
            'audio_job_id': resolved_audio_job_id,
            'auto_upload': auto_upload,
            'config': pipeline_config,
            'created_at': now,
        })
        shared.db.append_workflow_log(workflow_id, 'system', 'Generate-Workflow gestartet. Warte auf Audio-Job.', now)

        start_workflow(workflow_id, resolved_audio_job_id, slug, title, pipeline_config, auto_upload, shared.db)
        return RedirectResponse(url=f'/admin/pipeline/run/{workflow_id}', status_code=303)

    if not audio_found:
        return RedirectResponse(
            url=f'/admin/pipeline/new?slug={slug}&error=Kein+Audio-Track+f\u00fcr+"{slug}"+gefunden.+W\u00e4hle+"Neu+generieren"+als+Audio-Quelle.',
            status_code=303,
        )

    if audio_path and audio_path.stem != slug:
        target_audio = PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{slug}{audio_path.suffix.lower()}'
        target_audio.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(audio_path, target_audio)
        audio_found = True

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
    _place_selected_thumbnail(slug, thumbnail_source)
    bg_selected = (background_file or '').strip()
    if not bg_selected:
        bg_selected = (_resolve_background_from_house_variant(house, variant_key) or '').strip()
    background_source = _detect_background_source(bg_selected or None, theme)

    config = {
        'minutes': minutes,
        'loop_hours': loop_hours,
        'crossfade': crossfade,
        'audio_preset': audio_preset,
        'animated': animated,
        'auto_upload': auto_upload,
        'public': public,
        'skip_post_process': skip_post_process,
        'mood': mood or None,
        'house': house or theme or None,
        'variant_key': variant_key or None,
        'metadata': metadata,
        'thumbnail_source': thumbnail_source,
        'background_source': background_source,
    }

    workflow_id = uuid.uuid4().hex[:12]
    now = datetime.now(shared.CET).isoformat()

    shared.db.create_workflow({
        'workflow_id': workflow_id,
        'slug': slug,
        'title': title,
        'type': 'video',
        'status': 'created',
        'config': config,
        'created_at': now,
    })

    enqueue_workflow(workflow_id, slug, config, shared.db)
    return RedirectResponse(url=f'/admin/pipeline/run/{workflow_id}', status_code=303)


@router.get('/admin/pipeline/run/{workflow_id}', response_class=HTMLResponse)
def admin_pipeline_run_detail(request: Request, workflow_id: str):
    run = shared.db.get_workflow(workflow_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = shared.db.get_workflow_logs(workflow_id, limit=1000)

    audio_job = None
    if run.get('audio_job_id'):
        audio_job = shared.db.get_audio_job(run['audio_job_id'])

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
        'audio_job': audio_job,
        'logs': logs,
        'output_files': output_files,
    })


@router.get('/admin/pipeline/run/{workflow_id}/logs')
def admin_pipeline_run_logs(workflow_id: str, after_id: int = Query(default=0, ge=0)):
    run = shared.db.get_workflow(workflow_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = shared.db.get_workflow_logs(workflow_id, after_id=after_id)
    return {'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')}


@router.post('/admin/pipeline/run/{workflow_id}/upload')
def admin_pipeline_run_upload(workflow_id: str):
    run = shared.db.get_workflow(workflow_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] != 'rendered':
        raise HTTPException(status_code=409, detail=f'Cannot upload from status {run["status"]}')

    trigger_upload(workflow_id, run['slug'], run.get('config', {}), shared.db)
    return RedirectResponse(url=f'/admin/pipeline/run/{workflow_id}', status_code=303)


@router.post('/admin/pipeline/run/{workflow_id}/cancel')
def admin_pipeline_run_cancel(workflow_id: str):
    run = shared.db.get_workflow(workflow_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')

    now = datetime.now(shared.CET).isoformat()
    status = run['status']
    cancellable = {'queued', 'waiting_for_audio', 'running', 'uploading', 'created'}

    if status not in cancellable:
        raise HTTPException(status_code=409, detail=f'Cannot cancel workflow in status "{status}"')

    if status == 'running':
        # Running pipeline has a subprocess – kill it
        cancel_run(workflow_id, shared.db)
    elif status == 'waiting_for_audio':
        # Cancel the linked audio job too
        audio_job_id = run.get('audio_job_id')
        if audio_job_id:
            from app.audio_jobs import get_audio_generator
            audio_job = shared.db.get_audio_job(audio_job_id)
            if audio_job and audio_job.get('status') in ('queued', 'running'):
                get_audio_generator().cancel(audio_job, shared.db)
        shared.db.update_workflow(workflow_id, status='cancelled', finished_at=now)
        shared.db.append_workflow_log(workflow_id, 'system', 'Workflow + Audio-Job abgebrochen.', now)
    else:
        # queued, uploading, created – just mark as cancelled
        shared.db.update_workflow(workflow_id, status='cancelled', finished_at=now)
        shared.db.append_workflow_log(workflow_id, 'system', f'Workflow abgebrochen (war: {status}).', now)

    return RedirectResponse(url=f'/admin/pipeline/run/{workflow_id}', status_code=303)




@router.get('/admin/pipeline/run/{workflow_id}/progress')
def admin_pipeline_run_progress(workflow_id: str):
    """Live progress for a running workflow."""
    import re
    wf = shared.db.get_workflow(workflow_id)
    if not wf:
        return {'error': 'not found'}
    
    phase = wf.get('phase', 'render')
    status = wf.get('status', 'created')
    
    # Parse progress from latest logs
    logs = shared.db.get_workflow_logs(workflow_id, limit=500)
    progress_pct = 0
    progress_text = ''
    
    if status in ('running', 'waiting_for_audio', 'uploading'):
        for log in reversed(logs):
            msg = log.get('message', '')
            
            # Audio clip progress: "Generating clip 3/7"
            m = re.search(r'clip\s+(\d+)/(\d+)', msg, re.IGNORECASE)
            if m:
                current, total = int(m.group(1)), int(m.group(2))
                progress_pct = int(current / total * 100) if total > 0 else 0
                progress_text = f'Clip {current}/{total}'
                break
            
            # Stitching
            if 'stitch' in msg.lower() or 'crossfade' in msg.lower():
                progress_pct = 85
                progress_text = 'Stitching...'
                break
            
            # Downloading
            if 'download' in msg.lower():
                progress_pct = 90
                progress_text = 'Downloading...'
                break
            
            # Pipeline steps
            if 'post-process' in msg.lower() or 'post_process' in msg.lower():
                progress_pct = 60
                progress_text = 'Post-Processing...'
                break
            if 'loop' in msg.lower() and 'audio' in msg.lower():
                progress_pct = 40
                progress_text = 'Audio looping...'
                break
            if 'render' in msg.lower() and 'video' in msg.lower():
                progress_pct = 70
                progress_text = 'Video rendern...'
                break
            if 'thumbnail' in msg.lower():
                progress_pct = 80
                progress_text = 'Thumbnail...'
                break
            if 'upload' in msg.lower() and 'youtube' in msg.lower():
                progress_pct = 95
                progress_text = 'YouTube Upload...'
                break
    
    return {
        'workflow_id': workflow_id,
        'status': status,
        'phase': phase,
        'progress_pct': progress_pct,
        'progress_text': progress_text,
    }

@router.get('/admin/pipeline/preview/{slug}/{filename}')
def admin_pipeline_preview_file(slug: str, filename: str):
    path = get_output_path(slug, filename)
    if not path and 'thumbnail' in filename.lower():
        # Fallback: check data/output/thumbnails/ and data/upload/thumbnails/
        for fallback_dir in [
            PIPELINE_DIR / 'data' / 'output' / 'thumbnails',
            PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        ]:
            for ext in ('.jpg', '.jpeg', '.png', '.webp'):
                candidate = fallback_dir / f'{slug}{ext}'
                if candidate.exists():
                    path = candidate
                    break
            if path:
                break
    if not path:
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@router.get('/api/pipeline/queue')
def api_pipeline_queue():
    return get_queue_status(shared.db)


@router.get('/api/pipeline/preview-metadata')
def api_preview_metadata(slug: str = '', house: str = '', duration: str = '3 Hours'):
    """Preview auto-generated YouTube metadata (description, tags, playlists) before pipeline run."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'metadata_gen',
        str(PIPELINE_DIR / 'pipeline' / 'scripts' / 'metadata' / 'metadata_gen.py'),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Build minimal song meta from slug + house
    song_meta = {'slug': slug, 'theme': house or slug.replace('-', ' ').title(), 'mood': ['calm']}

    # Try loading actual metadata file
    meta_path = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{slug}.json'
    if meta_path.exists():
        import json
        song_meta = json.loads(meta_path.read_text(encoding='utf-8'))

    metadata = mod.generate_metadata(song_meta, duration)
    return metadata
