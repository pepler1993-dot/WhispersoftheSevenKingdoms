"""Settings routes – Phase 1: General, Providers, Presets."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _load_house_templates

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
    presets = _load_house_templates()
    return shared.templates.TemplateResponse(request, 'settings.html', {
        'request': request,
        'page': 'settings',
        'settings_tab': tab,
        'settings': grouped,
        'presets': presets,
        'preset_count': len(presets),
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
