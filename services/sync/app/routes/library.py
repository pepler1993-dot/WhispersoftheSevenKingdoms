"""Library routes: upload, preview, listing, house presets."""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _list_library_dir, _load_house_templates
from app.pipeline_runner import PIPELINE_DIR

router = APIRouter()


def _redirect_library(msg: str, *, error: bool = False) -> RedirectResponse:
    q = 'error' if error else 'success'
    from urllib.parse import quote

    return RedirectResponse(f'/admin/library?{q}={quote(msg)}', status_code=303)


@router.get('/admin/library', response_class=HTMLResponse)
def admin_library(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    songs = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'})
    backgrounds = _list_library_dir(PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', {'.jpg', '.jpeg', '.png', '.webp'})
    houses = _load_house_templates()
    house_pretty = {
        k: json.dumps(v, indent=2, ensure_ascii=False) + '\n'
        for k, v in sorted(houses.items(), key=lambda x: x[0])
    }
    return shared.templates.TemplateResponse(request, 'library.html', {
        'request': request,
        'page': 'library',
        'songs': songs,
        'backgrounds': backgrounds,
        'houses': houses,
        'house_pretty': house_pretty,
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/library/save-house-template')
def admin_library_save_house_template(
    house_key: str = Form(...),
    template_json: str = Form(...),
):
    key = (house_key or '').strip()
    if not key:
        return _redirect_library('Haus-Schlüssel fehlt', error=True)

    all_houses = _load_house_templates()
    if key not in all_houses:
        return _redirect_library(f'Unbekannter Haus-Schlüssel: {key}', error=True)

    raw = (template_json or '').strip()
    if not raw:
        return _redirect_library('JSON darf nicht leer sein', error=True)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        return _redirect_library(f'Ungültiges JSON: {e}', error=True)

    if not isinstance(parsed, dict):
        return _redirect_library('Preset muss ein JSON-Objekt sein', error=True)

    path = shared.HOUSE_TEMPLATES_PATH
    if not path.exists():
        return _redirect_library('house_templates.json nicht gefunden', error=True)

    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError) as e:
        return _redirect_library(f'Datei konnte nicht gelesen werden: {e}', error=True)

    if not isinstance(data, dict):
        return _redirect_library('Ungültige Struktur in house_templates.json', error=True)

    data[key] = parsed

    try:
        text = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
        fd, tmp = tempfile.mkstemp(suffix='.json', dir=str(path.parent))
        try:
            Path(fd).write_text(text, encoding='utf-8')
        except TypeError:
            # Windows: fd is int
            Path(tmp).write_text(text, encoding='utf-8')
        else:
            import os

            os.close(fd)
            Path(tmp).write_text(text, encoding='utf-8')
        Path(tmp).replace(path)
    except OSError as e:
        try:
            Path(tmp).unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass
        return _redirect_library(f'Speichern fehlgeschlagen: {e}', error=True)

    return _redirect_library(f'Haus-Preset „{key}“ gespeichert')


@router.post('/admin/library/delete')
def admin_library_delete(asset_type: str = Form(...), filename: str = Form(...)):
    mapping = {
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
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
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
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
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Umbenennen+ist+für+diesen+Asset-Typ+nicht+erlaubt', status_code=303)

    safe_old = Path(old_name).name
    safe_new = Path(new_name).name
    if not safe_old or not safe_new:
        return RedirectResponse('/admin/library?error=Ungültiger+Dateiname', status_code=303)

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
        'backgrounds': (PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', {'.jpg', '.jpeg', '.png', '.webp'}),
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
