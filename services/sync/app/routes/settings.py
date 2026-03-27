"""Settings routes – General, Providers, Presets CRUD."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _load_house_templates


def _load_presets() -> dict[str, Any]:
    """Load presets: DB-stored override > JSON file fallback."""
    db_presets = shared.db.get_setting('presets')
    if db_presets and isinstance(db_presets, dict) and len(db_presets) > 0:
        return db_presets
    return _load_house_templates()


def _save_presets(presets: dict[str, Any]) -> None:
    shared.db.set_setting('presets', presets)

router = APIRouter()

# ── Default settings ──────────────────────────────────────────────────────

DEFAULTS: dict[str, Any] = {
    'general.space_name': 'Whisper Studio',
    'general.tagline': 'Seven Kingdoms · Content Production',
    'general.timezone': 'Europe/Berlin',
    'general.language': 'de',
    'providers.gpu_host': '',
    'providers.gpu_api_key': '',
    'providers.youtube_enabled': True,
    'providers.stable_audio_model': 'stable-audio-open-1.0',
}


def _get(key: str) -> Any:
    val = shared.db.get_setting(key)
    return val if val is not None else DEFAULTS.get(key)


def _get_all_grouped() -> dict[str, dict[str, Any]]:
    """Return settings grouped by section prefix."""
    all_settings = shared.db.get_all_settings()
    merged = {**DEFAULTS, **all_settings}
    grouped: dict[str, dict[str, Any]] = {}
    for key, value in merged.items():
        section, _, field = key.partition('.')
        grouped.setdefault(section, {})[field] = value
    return grouped


# ── Pages ─────────────────────────────────────────────────────────────────

@router.get('/admin/settings', response_class=HTMLResponse)
def admin_settings(request: Request, tab: str = 'general'):
    grouped = _get_all_grouped()
    presets = _load_presets()
    edit_key = request.query_params.get('edit', '')
    return shared.templates.TemplateResponse(request, 'settings.html', {
        'request': request,
        'page': 'settings',
        'settings_tab': tab,
        'settings': grouped,
        'presets': presets,
        'preset_count': len(presets),
        'edit_key': edit_key,
        'edit_preset': presets.get(edit_key) if edit_key else None,
    })


# ── Save General ──────────────────────────────────────────────────────────

@router.post('/admin/settings/general')
def save_general(
    space_name: str = Form(''),
    tagline: str = Form(''),
    timezone_val: str = Form('Europe/Berlin'),
    language: str = Form('de'),
):
    shared.db.set_setting('general.space_name', space_name.strip() or 'Whisper Studio')
    shared.db.set_setting('general.tagline', tagline.strip())
    shared.db.set_setting('general.timezone', timezone_val.strip())
    shared.db.set_setting('general.language', language.strip())
    return RedirectResponse(url='/admin/settings?tab=general&saved=1', status_code=303)


# ── Save Providers ────────────────────────────────────────────────────────

@router.post('/admin/settings/providers')
def save_providers(
    gpu_host: str = Form(''),
    gpu_api_key: str = Form(''),
    youtube_enabled: bool = Form(False),
    stable_audio_model: str = Form('stable-audio-open-1.0'),
):
    shared.db.set_setting('providers.gpu_host', gpu_host.strip())
    shared.db.set_setting('providers.gpu_api_key', gpu_api_key.strip())
    shared.db.set_setting('providers.youtube_enabled', youtube_enabled)
    shared.db.set_setting('providers.stable_audio_model', stable_audio_model.strip())
    return RedirectResponse(url='/admin/settings?tab=providers&saved=1', status_code=303)


# ── Preset CRUD ───────────────────────────────────────────────────────────

@router.post('/admin/settings/presets/save')
def save_preset(
    preset_key: str = Form(''),
    original_key: str = Form(''),
    display_name: str = Form(''),
    house: str = Form(''),
    sigil: str = Form(''),
    color: str = Form('#c9a53a'),
    bg_color: str = Form('#1a1a2e'),
    mood: str = Form('calm'),
    motto: str = Form(''),
    seat: str = Form(''),
    minutes: int = Form(20),
    loop_hours: int = Form(3),
    crossfade: int = Form(8),
    audio_preset: str = Form('ambient'),
    music_tempo: str = Form('slow'),
    music_energy: str = Form('low'),
    music_style: str = Form(''),
    music_influences: str = Form(''),
    music_avoid: str = Form(''),
    title_template: str = Form(''),
):
    key = preset_key.strip().lower().replace(' ', '_').replace('-', '_')
    if not key or not display_name.strip():
        raise HTTPException(status_code=400, detail='Key and display_name required')

    presets = _load_presets()

    # If renaming, remove old key
    if original_key and original_key != key and original_key in presets:
        del presets[original_key]

    preset = presets.get(key, {})
    preset.update({
        'display_name': display_name.strip(),
        'house': house.strip() or f'House {display_name.strip()}',
        'sigil': sigil.strip() or '🏰',
        'color': color.strip(),
        'bg_color': bg_color.strip(),
        'mood': mood.strip(),
        'motto': motto.strip(),
        'seat': seat.strip(),
        'defaults': {
            'minutes': minutes,
            'loop_hours': loop_hours,
            'crossfade': crossfade,
            'audio_preset': audio_preset,
            'music_tempo': music_tempo,
            'music_energy': music_energy,
        },
        'music_brief': {
            'style': music_style.strip(),
            'influences': [i.strip() for i in music_influences.split(',') if i.strip()],
            'avoid': [a.strip() for a in music_avoid.split(',') if a.strip()],
        },
        'title_template': title_template.strip(),
    })

    # Preserve existing variants/prompts/backgrounds if not in this form
    for keep_key in ('variants', 'variant_prompts', 'background_prompts', 'thumbnail_brief'):
        if keep_key not in preset:
            preset[keep_key] = {}

    presets[key] = preset
    _save_presets(presets)
    return RedirectResponse(url='/admin/settings?tab=presets&saved=1', status_code=303)


@router.post('/admin/settings/presets/delete')
def delete_preset(preset_key: str = Form('')):
    key = preset_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail='Key required')
    presets = _load_presets()
    if key in presets:
        del presets[key]
        _save_presets(presets)
    return RedirectResponse(url='/admin/settings?tab=presets&saved=1', status_code=303)


@router.post('/admin/settings/presets/import-json')
def import_presets_from_json():
    """One-time import: copy house_templates.json into DB."""
    json_presets = _load_house_templates()
    if not json_presets:
        raise HTTPException(status_code=404, detail='No house_templates.json found')
    _save_presets(json_presets)
    return RedirectResponse(url='/admin/settings?tab=presets&saved=1', status_code=303)
