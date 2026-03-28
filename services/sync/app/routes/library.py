"""Library routes: upload, preview, listing, house presets (UI, no raw JSON)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from urllib.parse import urlencode

from app import shared
from app.helpers import _list_library_dir, _load_house_templates
from app.pipeline_runner import PIPELINE_DIR

router = APIRouter()

@router.get('/admin/library/house/{house_key}')
def admin_library_house_redirect(house_key: str):
    return RedirectResponse(url=f'/admin/library/houses/{house_key}', status_code=301)


_LIBRARY_TABS = frozenset({'houses', 'songs', 'backgrounds'})

_SONG_EXT = frozenset({'.mp3', '.wav', '.ogg'})
_BG_EXT = frozenset({'.jpg', '.jpeg', '.png', '.webp'})


def _sanitize_css_class_suffix(key: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9_-]', '_', (key or '').strip())
    return s or 'house'


def _safe_hex_color(val: Any, fallback: str) -> str:
    s = str(val or '').strip()
    if re.fullmatch(r'#[0-9A-Fa-f]{6}', s):
        return s
    return fallback


def _house_banner_gradient(class_suffix: str, c_raw: Any, bgc_raw: Any) -> tuple[str, str]:
    """CSS class + complete <style>…</style> for hero gradient (no Jinja inside CSS for linters)."""
    c = _safe_hex_color(c_raw, '#475569')
    bgc = _safe_hex_color(bgc_raw, '#0f172a')
    suf = _sanitize_css_class_suffix(class_suffix)
    cls = f'house-hero-banner-bg--{suf}'
    inner = f'.{cls}{{background:linear-gradient(135deg,{c} 0%,{bgc} 100%);}}'
    return cls, f'<style>{inner}</style>'


def _library_tab_counts() -> dict[str, int]:
    """Counts for tab badges on Library and subpages (avoids duplicating full lists on presets views)."""
    songs = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'songs', _SONG_EXT)
    backgrounds = _list_library_dir(PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', _BG_EXT)
    houses = _load_house_templates()
    n_houses = sum(1 for h in houses.values() if isinstance(h, dict))
    return {
        'library_house_count': n_houses,
        'library_song_count': len(songs),
        'library_background_count': len(backgrounds),
    }


def _normalize_library_tab(raw: str | None) -> str:
    if raw in _LIBRARY_TABS:
        return raw  # type: ignore[return-value]
    return 'houses'


def _tab_for_asset_type(asset_type: str) -> str:
    if asset_type == 'songs':
        return 'songs'
    if asset_type == 'backgrounds':
        return 'backgrounds'
    return 'houses'


def _library_list_url(*, tab: str | None = None, success: str | None = None, error: str | None = None) -> str:
    q: dict[str, str] = {}
    t = _normalize_library_tab(tab)
    if t != 'houses':
        q['tab'] = t
    if success:
        q['success'] = success
    if error:
        q['error'] = error
    return f'/admin/library?{urlencode(q)}' if q else '/admin/library'


def _as_list(val: Any) -> list[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


_DEFAULT_LABELS_DE: dict[str, str] = {
    'minutes': 'Dauer (Minuten)',
    'loop_hours': 'Loop (Stunden)',
    'crossfade': 'Crossfade (Sekunden)',
    'audio_preset': 'Audio-Preset',
    'music_tempo': 'Musik-Tempo',
    'music_energy': 'Musik-Energie',
}


def _format_default_value(v: Any) -> str:
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _build_variant_page_context(house_key: str, variant_key: str, house: dict[str, Any]) -> dict[str, Any]:
    variants = house.get('variants')
    if not isinstance(variants, dict) or variant_key not in variants:
        raise HTTPException(status_code=404, detail='Variante nicht gefunden')

    variant_description = variants.get(variant_key)
    if not isinstance(variant_description, str):
        variant_description = str(variant_description)

    defaults = house.get('defaults')
    default_rows: list[dict[str, str]] = []
    if isinstance(defaults, dict):
        for k, v in sorted(defaults.items(), key=lambda x: str(x[0])):
            ks = str(k)
            default_rows.append({
                'key': ks,
                'label': _DEFAULT_LABELS_DE.get(ks, ks.replace('_', ' ').title()),
                'value': _format_default_value(v),
            })

    mb = house.get('music_brief') if isinstance(house.get('music_brief'), dict) else {}
    tb = house.get('thumbnail_brief') if isinstance(house.get('thumbnail_brief'), dict) else {}

    vp = house.get('variant_prompts')
    audio_prompts: list[str] = []
    if isinstance(vp, dict) and variant_key in vp:
        audio_prompts = [str(p) for p in _as_list(vp.get(variant_key))]

    bg_block: dict[str, str] | None = None
    bp = house.get('background_prompts')
    if isinstance(bp, dict) and variant_key in bp:
        raw = bp.get(variant_key)
        if isinstance(raw, dict):
            bg_block = {
                'prompt': str(raw.get('prompt', '') or ''),
                'bg_key': str(raw.get('bg_key', '') or ''),
            }
            if not bg_block['prompt'] and not bg_block['bg_key']:
                bg_block = None

    title_template = house.get('title_template')
    if title_template is not None:
        title_template = str(title_template)

    return {
        'house_key': house_key,
        'variant_key': variant_key,
        'variant_title': str(variant_key).replace('_', ' ').strip().title(),
        'house_display': str(house.get('display_name') or house_key),
        'house_line': str(house.get('house') or ''),
        'variant_description': variant_description,
        'motto': str(house.get('motto') or ''),
        'seat': str(house.get('seat') or ''),
        'mood': str(house.get('mood') or ''),
        'sigil': str(house.get('sigil') or ''),
        'color': str(house.get('color') or '#334155'),
        'bg_color': str(house.get('bg_color') or '#0f172a'),
        'default_rows': default_rows,
        'music_style': str(mb.get('style') or '') if mb else '',
        'music_influences': [str(x) for x in _as_list(mb.get('influences'))] if mb else [],
        'music_avoid': [str(x) for x in _as_list(mb.get('avoid'))] if mb else [],
        'thumb_scene': str(tb.get('scene') or '') if tb else '',
        'thumb_elements': [str(x) for x in _as_list(tb.get('elements'))] if tb else [],
        'thumb_style': str(tb.get('style') or '') if tb else '',
        'title_template': title_template,
        'audio_prompts': audio_prompts,
        'background_block': bg_block,
    }


@router.get('/admin/library', response_class=HTMLResponse)
def admin_library(
    request: Request,
    tab: str | None = Query(default=None),
    success: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    songs = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'songs', _SONG_EXT)
    backgrounds = _list_library_dir(PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', _BG_EXT)
    houses = _load_house_templates()
    house_cards: list[dict[str, Any]] = []
    for key, h in sorted(houses.items(), key=lambda x: x[0]):
        if not isinstance(h, dict):
            continue
        n_var = 0
        v = h.get('variants')
        if isinstance(v, dict):
            n_var = len(v)
        # Get first variant bg_key for house preview image
        first_bg_key = ''
        bg_prompts = h.get('background_prompts', {})
        if isinstance(bg_prompts, dict):
            for vdata in bg_prompts.values():
                if isinstance(vdata, dict) and vdata.get('bg_key'):
                    first_bg_key = vdata['bg_key']
                    break
        house_cards.append({
            'key': key,
            'display_name': str(h.get('display_name') or key),
            'house': str(h.get('house') or ''),
            'sigil': str(h.get('sigil') or '·'),
            'color': str(h.get('color') or '#475569'),
            'bg_color': str(h.get('bg_color') or '#0f172a'),
            'variant_count': n_var,
            'first_bg_key': first_bg_key,
        })
    library_tab = _normalize_library_tab(tab)
    return shared.templates.TemplateResponse(request, 'library.html', {
        'request': request,
        'page': 'library',
        'library_tab': library_tab,
        'songs': songs,
        'backgrounds': backgrounds,
        'house_cards': house_cards,
        'library_house_count': len(house_cards),
        'library_song_count': len(songs),
        'library_background_count': len(backgrounds),
        'success_message': success or '',
        'error_message': error or '',
    })


@router.get('/admin/library/houses/{house_key}', response_class=HTMLResponse)
def admin_library_house(request: Request, house_key: str):
    houses = _load_house_templates()
    house = houses.get(house_key)
    if not house or not isinstance(house, dict):
        raise HTTPException(status_code=404, detail='Haus nicht gefunden')

    variant_rows: list[dict[str, str]] = []
    vmap = house.get('variants')
    bg_prompts = house.get('background_prompts', {})
    if isinstance(vmap, dict):
        for vk, desc in sorted(vmap.items(), key=lambda x: x[0]):
            title = str(vk).replace('_', ' ').strip().title()
            bg_key = ''
            if isinstance(bg_prompts, dict) and vk in bg_prompts:
                vdata = bg_prompts[vk]
                if isinstance(vdata, dict):
                    bg_key = str(vdata.get('bg_key', ''))
            variant_rows.append({
                'key': vk,
                'title': title,
                'description': str(desc) if desc is not None else vk,
                'href': f'/admin/library/houses/{house_key}/variants/{vk}',
                'bg_key': bg_key,
            })

    banner_class, banner_style = _house_banner_gradient(house_key, house.get('color'), house.get('bg_color'))
    return shared.templates.TemplateResponse(request, 'library_house.html', {
        'request': request,
        'page': 'library',
        'library_tab': 'houses',
        'house_key': house_key,
        'house': house,
        'variants': variant_rows,
        'house_banner_class': banner_class,
        'house_banner_style_tag': banner_style,
        **_library_tab_counts(),
    })


@router.get('/admin/library/houses/{house_key}/variants/{variant_key}', response_class=HTMLResponse)
def admin_library_variant(request: Request, house_key: str, variant_key: str):
    houses = _load_house_templates()
    house = houses.get(house_key)
    if not house or not isinstance(house, dict):
        raise HTTPException(status_code=404, detail='Haus nicht gefunden')

    ctx = _build_variant_page_context(house_key, variant_key, house)
    return shared.templates.TemplateResponse(request, 'library_variant.html', {
        'request': request,
        'page': 'library',
        'library_tab': 'houses',
        'preset': ctx,
        **_library_tab_counts(),
    })


@router.post('/admin/library/delete')
def admin_library_delete(asset_type: str = Form(...), filename: str = Form(...)):
    mapping = {
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
    }
    if asset_type not in mapping:
        return RedirectResponse(
            _library_list_url(error='Löschen ist für diesen Asset-Typ nicht erlaubt'),
            status_code=303,
        )

    safe_name = Path(filename).name
    if not safe_name:
        return RedirectResponse(_library_list_url(tab=_tab_for_asset_type(asset_type), error='Ungültiger Dateiname'), status_code=303)

    path = mapping[asset_type] / safe_name
    if not path.exists() or not path.is_file():
        return RedirectResponse(_library_list_url(tab=_tab_for_asset_type(asset_type), error='Datei nicht gefunden'), status_code=303)

    path.unlink()
    return RedirectResponse(
        _library_list_url(
            tab=_tab_for_asset_type(asset_type),
            success=f'{asset_type} Datei {safe_name} gelöscht',
        ),
        status_code=303,
    )


@router.post('/admin/library/delete-multi')
def admin_library_delete_multi(asset_type: str = Form(...), filenames: list[str] = Form(default=[])):
    mapping = {
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
    }
    if asset_type not in mapping:
        return RedirectResponse(
            _library_list_url(error='Mehrfach-Löschen ist für diesen Asset-Typ nicht erlaubt'),
            status_code=303,
        )
    if not filenames:
        return RedirectResponse(
            _library_list_url(tab=_tab_for_asset_type(asset_type), error='Keine Dateien ausgewählt'),
            status_code=303,
        )

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

    return RedirectResponse(
        _library_list_url(
            tab=_tab_for_asset_type(asset_type),
            success=f'{deleted} {asset_type} Datei(en) gelöscht',
        ),
        status_code=303,
    )


@router.post('/admin/library/rename')
def admin_library_rename(asset_type: str = Form(...), old_name: str = Form(...), new_name: str = Form(...)):
    mapping = {
        'backgrounds': PIPELINE_DIR / 'data' / 'assets' / 'backgrounds',
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
    }
    if asset_type not in mapping:
        return RedirectResponse(
            _library_list_url(error='Umbenennen ist für diesen Asset-Typ nicht erlaubt'),
            status_code=303,
        )

    safe_old = Path(old_name).name
    safe_new = Path(new_name).name
    if not safe_old or not safe_new:
        return RedirectResponse(
            _library_list_url(tab=_tab_for_asset_type(asset_type), error='Ungültiger Dateiname'),
            status_code=303,
        )

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
        return RedirectResponse(
            _library_list_url(tab=_tab_for_asset_type(asset_type), error='Quelldatei nicht gefunden'),
            status_code=303,
        )
    if dst.exists():
        return RedirectResponse(
            _library_list_url(tab=_tab_for_asset_type(asset_type), error=f'Datei {safe_new} existiert bereits'),
            status_code=303,
        )

    src.rename(dst)
    return RedirectResponse(
        _library_list_url(
            tab=_tab_for_asset_type(asset_type),
            success=f'{safe_old} umbenannt zu {safe_new}',
        ),
        status_code=303,
    )


@router.post('/admin/library/upload')
async def admin_library_upload(asset_type: str = Form(...), file: list[UploadFile] = File(...)):
    mapping = {
        'songs': (PIPELINE_DIR / 'data' / 'upload' / 'songs', _SONG_EXT),
        'backgrounds': (PIPELINE_DIR / 'data' / 'assets' / 'backgrounds', _BG_EXT),
    }
    if asset_type not in mapping:
        return RedirectResponse(_library_list_url(error='Ungültiger Asset-Typ'), status_code=303)
    target_dir, allowed = mapping[asset_type]
    target_dir.mkdir(parents=True, exist_ok=True)
    uploaded = 0
    for uploaded_file in file:
        filename = Path(uploaded_file.filename or '').name
        if not filename:
            continue
        if Path(filename).suffix.lower() not in allowed:
            return RedirectResponse(
                _library_list_url(tab=_tab_for_asset_type(asset_type), error=f'Dateityp für {filename} nicht erlaubt'),
                status_code=303,
            )
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
        return RedirectResponse(
            _library_list_url(tab=_tab_for_asset_type(asset_type), error='Keine gültigen Dateien hochgeladen'),
            status_code=303,
        )
    return RedirectResponse(
        _library_list_url(
            tab=_tab_for_asset_type(asset_type),
            success=f'{uploaded} {asset_type} Datei(en) hochgeladen',
        ),
        status_code=303,
    )


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
