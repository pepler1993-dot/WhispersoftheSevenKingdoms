"""Library routes: upload, preview, listing."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _build_song_metadata, _list_library_dir, slugify
from app.pipeline_runner import PIPELINE_DIR

router = APIRouter()


def _enrich_metadata_items(items: list[dict[str, str]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    meta_dir = PIPELINE_DIR / 'data' / 'upload' / 'metadata'
    for item in items:
        extra = {'title': '—', 'slug': Path(item['name']).stem}
        if item['name'].endswith('.json'):
            path = meta_dir / item['name']
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                extra['title'] = (data.get('title') or '—').strip() or '—'
                extra['slug'] = (data.get('slug') or extra['slug']).strip() or extra['slug']
            except (json.JSONDecodeError, OSError) as exc:
                import logging
                logging.warning('Failed to read metadata %s: %s', path.name, exc)
        enriched.append({**item, **extra})
    return enriched


@router.get('/admin/library', response_class=HTMLResponse)
def admin_library(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    songs = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'})
    thumbnails = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'thumbnails', {'.jpg', '.jpeg', '.png', '.webp'})
    backgrounds = _list_library_dir(PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', {'.jpg', '.jpeg', '.png', '.webp'})
    metadata = _enrich_metadata_items(_list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'metadata', {'.json', '.md'}))
    return shared.templates.TemplateResponse(request, 'library.html', {
        'request': request,
        'page': 'library',
        'songs': songs,
        'thumbnails': thumbnails,
        'backgrounds': backgrounds,
        'metadata': metadata,
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/library/create-metadata')
def admin_library_create_metadata(
    title: str = Form(...),
    slug: str = Form(''),
    theme: str = Form(...),
    mood: str = Form(''),
    notes: str = Form(''),
    duration_hint: str = Form('long-form sleep track'),
    tags: str = Form(''),
    music_style: str = Form(''),
    music_influences: str = Form(''),
    music_tempo: str = Form('slow'),
    music_energy: str = Form('low'),
    music_avoid: str = Form(''),
    thumbnail_scene: str = Form(''),
    thumbnail_elements: str = Form(''),
    thumbnail_text: str = Form(''),
    thumbnail_style: str = Form(''),
    thumbnail_avoid: str = Form(''),
    overwrite: str = Form(''),
):
    clean_title = title.strip()
    clean_slug = slugify(slug or clean_title)
    clean_theme = theme.strip()

    if not clean_title:
        return RedirectResponse('/admin/library?error=Titel+ist+erforderlich', status_code=303)
    if not clean_slug:
        return RedirectResponse('/admin/library?error=Slug+konnte+nicht+gebildet+werden', status_code=303)
    if not clean_theme:
        return RedirectResponse('/admin/library?error=Theme+ist+erforderlich', status_code=303)

    metadata = _build_song_metadata(
        slug=clean_slug,
        title=clean_title,
        theme=clean_theme,
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

    target = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{clean_slug}.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    existed_before = target.exists()
    if existed_before and overwrite != 'true':
        return RedirectResponse(f'/admin/library?error=Metadata+{clean_slug}.json+existiert+bereits.+Aktiviere+Overwrite+wenn+du+sie+ersetzen+willst', status_code=303)
    target.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    action = 'aktualisiert' if existed_before and overwrite == 'true' else 'erstellt'
    return RedirectResponse(f'/admin/library?success=Metadata+{clean_slug}.json+{action}', status_code=303)


@router.post('/admin/library/delete')
def admin_library_delete(asset_type: str = Form(...), filename: str = Form(...)):
    mapping = {
        'thumbnails': PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Löschen+ist+für+diesen+Asset-Typ+nicht+erlaubt', status_code=303)

    safe_name = Path(filename).name
    if not safe_name:
        return RedirectResponse('/admin/library?error=Ungültiger+Dateiname', status_code=303)

    path = mapping[asset_type] / safe_name
    if not path.exists() or not path.is_file():
        return RedirectResponse('/admin/library?error=Datei+nicht+gefunden', status_code=303)

    path.unlink()
    return RedirectResponse(f'/admin/library?success={asset_type}+Datei+{safe_name}+gelöscht', status_code=303)


@router.post('/admin/library/delete-multi')
def admin_library_delete_multi(asset_type: str = Form(...), filenames: list[str] = Form(default=[])):
    mapping = {
        'thumbnails': PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Mehrfach-Löschen+ist+für+diesen+Asset-Typ+nicht+erlaubt', status_code=303)
    if not filenames:
        return RedirectResponse('/admin/library?error=Keine+Dateien+ausgewählt', status_code=303)

    base = mapping[asset_type]
    deleted = 0
    for filename in filenames:
        safe_name = Path(filename).name
        if not safe_name:
            continue
        path = base / safe_name
        if path.exists() and path.is_file():
            path.unlink()
            deleted += 1

    return RedirectResponse(f'/admin/library?success={deleted}+{asset_type}+Datei(en)+gelöscht', status_code=303)


@router.post('/admin/library/rename')
def admin_library_rename(asset_type: str = Form(...), old_name: str = Form(...), new_name: str = Form(...)):
    mapping = {
        'thumbnails': PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Umbenennen+ist+für+diesen+Asset-Typ+nicht+erlaubt', status_code=303)

    safe_old = Path(old_name).name
    safe_new = Path(new_name).name
    if not safe_old or not safe_new:
        return RedirectResponse('/admin/library?error=Ungültiger+Dateiname', status_code=303)

    # Preserve original extension if new name has none
    old_ext = Path(safe_old).suffix.lower()
    new_ext = Path(safe_new).suffix.lower()
    if not new_ext and old_ext:
        safe_new = safe_new + old_ext
    elif new_ext != old_ext and old_ext:
        safe_new = Path(safe_new).stem + old_ext

    base = mapping[asset_type]
    src = base / safe_old
    dst = base / safe_new

    if not src.exists() or not src.is_file():
        return RedirectResponse('/admin/library?error=Quelldatei+nicht+gefunden', status_code=303)
    if dst.exists():
        return RedirectResponse(f'/admin/library?error=Datei+{safe_new}+existiert+bereits', status_code=303)

    src.rename(dst)
    return RedirectResponse(f'/admin/library?success={safe_old}+umbenannt+zu+{safe_new}', status_code=303)


@router.post('/admin/library/upload')
async def admin_library_upload(asset_type: str = Form(...), file: list[UploadFile] = File(...)):
    mapping = {
        'songs': (PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'}),
        'thumbnails': (PIPELINE_DIR / 'data' / 'upload' / 'thumbnails', {'.jpg', '.jpeg', '.png', '.webp'}),
        'backgrounds': (PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', {'.jpg', '.jpeg', '.png', '.webp'}),
        'metadata': (PIPELINE_DIR / 'data' / 'upload' / 'metadata', {'.json', '.md'}),
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Ung%C3%BCltiger+Asset-Typ', status_code=303)
    target_dir, allowed = mapping[asset_type]
    target_dir.mkdir(parents=True, exist_ok=True)
    uploaded = 0
    for uploaded_file in file:
        filename = Path(uploaded_file.filename or '').name
        if not filename:
            continue
        if Path(filename).suffix.lower() not in allowed:
            return RedirectResponse(f'/admin/library?error=Dateityp+für+{filename}+nicht+erlaubt', status_code=303)
        target_path = target_dir / filename
        with target_path.open('wb') as out:
            while True:
                chunk = await uploaded_file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        await uploaded_file.close()
        uploaded += 1
    if uploaded == 0:
        return RedirectResponse('/admin/library?error=Keine+gültigen+Dateien+hochgeladen', status_code=303)
    return RedirectResponse(f'/admin/library?success={uploaded}+{asset_type}+Datei(en)+hochgeladen', status_code=303)


@router.get('/admin/library/preview/{asset_type}/{filename}')
def admin_library_preview(asset_type: str, filename: str):
    mapping = {
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
        'thumbnails': PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'metadata': PIPELINE_DIR / 'data' / 'upload' / 'metadata',
    }
    if asset_type not in mapping:
        raise HTTPException(status_code=404, detail='Asset type not found')
    path = mapping[asset_type] / Path(filename).name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)
