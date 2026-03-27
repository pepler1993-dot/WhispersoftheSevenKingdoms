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
from app.audio_jobs import create_audio_job
from app.stores.workflows import create_workflow, get_workflow, get_workflow_by_run_id
from app.pipeline_workflow import start_workflow

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
        raise HTTPException(status_code=400, detail=f'Ungültige Prompt-Liste für Variante „{variant_key}“.')
    lines = [x for x in raw if isinstance(x, str) and x.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail=f'Keine Prompts für Variante „{variant_key}“ hinterlegt.')
    return '\n'.join(lines)


@router.get('/admin/pipeline/logs', response_class=HTMLResponse)
def admin_pipeline_logs(request: Request):
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


@router.get('/admin/pipeline', response_class=HTMLResponse)
@router.get('/admin/pipeline/new', response_class=HTMLResponse)
def admin_pipeline_new(request: Request, slug: str | None = Query(default=None), error: str | None = Query(default=None)):
    assets = list_available_assets()
    themes = list_available_themes()
    houses = _load_house_templates()
    library_tracks = list_library_tracks_for_pipeline(shared.db)
    thumb_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'output' / 'thumbnails'
    library_thumbnails = sorted(f.name for f in thumb_dir.iterdir() if f.is_file() and f.suffix in {'.jpg', '.jpeg', '.png', '.webp'}) if thumb_dir.exists() else []
    bg_dir = PIPELINE_DIR / 'data' / 'assets' / 'backgrounds'
    library_backgrounds = sorted(f.name for f in bg_dir.iterdir() if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}) if bg_dir.exists() else []
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
    title: str = Form(...),
    theme: str = Form(...),
    minutes: int = Form(42),
    loop_hours: float = Form(0),
    crossfade: int = Form(8),
    audio_preset: str = Form('ambient'),
    animated: bool = Form(False),
    auto_upload: bool = Form(False),
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
    background_file: str = Form(''),
    audio_source: str = Form('library'),
    gen_minutes: int = Form(42),
    gen_steps: int = Form(50),
    gen_model: str = Form('medium'),
    gen_prompt: str = Form(''),
):
    title = title.strip()
    theme = theme.strip()
    slug = slugify(title)
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

    # ── Generate mode: start full workflow (Audio → Pipeline → Upload) ──
    if not audio_found and audio_source == 'generate':
        prompt_text = gen_prompt.strip()
        if not prompt_text:
            prompt_text = _prompts_from_house_variant(house, notes)

        audio_job_id = create_audio_job(
            slug=slug,
            title=title,
            prompt_text=prompt_text,
            preset_name=None,
            minutes=gen_minutes,
            model=gen_model,
            clip_seconds=30,
            db=shared.db,
            steps=gen_steps,
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
        bg_selected = (background_file or '').strip()
        if not bg_selected:
            bg_selected = (_resolve_background_from_house_variant(house, notes) or '').strip()
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
            'metadata': metadata,
            'thumbnail_source': thumbnail_source,
            'background_source': background_source,
        }

        now = datetime.now(shared.CET).isoformat()
        workflow_id = uuid.uuid4().hex[:12]
        run_id = uuid.uuid4().hex[:12]

        shared.db.create_run({
            'run_id': run_id,
            'slug': slug,
            'title': title,
            'status': 'waiting_for_audio',
            'config': pipeline_config,
            'created_at': now,
        })
        shared.db.append_run_log(run_id, 'system', 'Generate-Workflow gestartet. Warte auf Audio-Job.', now)

        create_workflow(shared.db, {
            'workflow_id': workflow_id,
            'title': title,
            'slug': slug,
            'phase': 'audio',
            'status': 'running',
            'audio_job_id': audio_job_id,
            'pipeline_run_id': run_id,
            'config': pipeline_config,
            'auto_upload': auto_upload,
            'created_at': now,
            'updated_at': now,
        })

        start_workflow(workflow_id, audio_job_id, slug, title, pipeline_config, auto_upload, shared.db)
        return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)

    if not audio_found:
        return RedirectResponse(
            url=f'/admin/pipeline/new?slug={slug}&error=Kein+Audio-Track+f\u00fcr+"{slug}"+gefunden.+W\u00e4hle+"Neu+generieren"+als+Audio-Quelle.',
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
    bg_selected = (background_file or '').strip()
    if not bg_selected:
        bg_selected = (_resolve_background_from_house_variant(house, notes) or '').strip()
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
        'metadata': metadata,
        'thumbnail_source': thumbnail_source,
        'background_source': background_source,
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

    workflow = get_workflow_by_run_id(shared.db, run_id)
    audio_job = None
    if workflow and workflow.get('audio_job_id'):
        audio_job = shared.db.get_audio_job(workflow['audio_job_id'])

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
        'workflow': workflow,
        'audio_job': audio_job,
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
    if run['status'] != 'rendered':
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
