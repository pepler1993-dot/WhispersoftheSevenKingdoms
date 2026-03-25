"""Library routes: upload, preview, listing."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _list_library_dir
from app.pipeline_runner import PIPELINE_DIR

router = APIRouter()


@router.get('/admin/library', response_class=HTMLResponse)
def admin_library(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    songs = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'})
    thumbnails = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'thumbnails', {'.jpg', '.jpeg', '.png', '.webp'})
    metadata = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'metadata', {'.json', '.md'})
    return shared.templates.TemplateResponse('library.html', {
        'request': request,
        'page': 'library',
        'songs': songs,
        'thumbnails': thumbnails,
        'metadata': metadata,
        'success_message': success or '',
        'error_message': error or '',
    })


@router.post('/admin/library/upload')
async def admin_library_upload(asset_type: str = Form(...), file: UploadFile = File(...)):
    mapping = {
        'songs': (PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'}),
        'thumbnails': (PIPELINE_DIR / 'data' / 'upload' / 'thumbnails', {'.jpg', '.jpeg', '.png', '.webp'}),
        'metadata': (PIPELINE_DIR / 'data' / 'upload' / 'metadata', {'.json', '.md'}),
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Ung%C3%BCltiger+Asset-Typ', status_code=303)
    target_dir, allowed = mapping[asset_type]
    filename = Path(file.filename or '').name
    if not filename:
        return RedirectResponse('/admin/library?error=Dateiname+fehlt', status_code=303)
    if Path(filename).suffix.lower() not in allowed:
        return RedirectResponse('/admin/library?error=Dateityp+nicht+erlaubt', status_code=303)
    target_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    (target_dir / filename).write_bytes(content)
    return RedirectResponse(f'/admin/library?success={asset_type}+Datei+{filename}+hochgeladen', status_code=303)


@router.get('/admin/library/preview/{asset_type}/{filename}')
def admin_library_preview(asset_type: str, filename: str):
    mapping = {
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
        'thumbnails': PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        'metadata': PIPELINE_DIR / 'data' / 'upload' / 'metadata',
    }
    if asset_type not in mapping:
        raise HTTPException(status_code=404, detail='Asset type not found')
    path = mapping[asset_type] / Path(filename).name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)
