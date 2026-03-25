"""Dashboard, server stats, backup, and releases routes."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from typing import Any

import psutil
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app import shared
from app.helpers import _build_protocol_health, _get_release_notes

router = APIRouter()


@router.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request):
    protocol_health = _build_protocol_health()
    summary = shared.db.get_dashboard_summary()
    recent_runs = shared.db.list_runs(limit=5)
    recent_audio = shared.db.list_audio_jobs(limit=5)
    return shared.templates.TemplateResponse('dashboard.html', {
        'request': request,
        'page': 'dashboard',
        'summary': summary,
        'protocol_health': protocol_health,
        'recent_runs': recent_runs,
        'recent_audio': recent_audio,
    })


@router.post('/admin/api/backup')
def admin_api_backup():
    """Create a hot backup of the database. Returns backup path."""
    try:
        backup_path = shared.db.backup()
        return {'status': 'ok', 'backup_path': str(backup_path), 'size_mb': round(backup_path.stat().st_size / 1024 / 1024, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Backup failed: {e}')


@router.get('/admin/api/server-stats')
def admin_server_stats():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage('/')
    load1, load5, load15 = psutil.getloadavg()
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc).isoformat()
    return {
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count(),
            'load_1m': round(load1, 2),
            'load_5m': round(load5, 2),
            'load_15m': round(load15, 2),
        },
        'memory': {
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent,
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': round(disk.used / disk.total * 100, 1),
        },
        'boot_time': boot_time,
    }


@router.get('/admin/releases', response_class=HTMLResponse)
def admin_releases(request: Request):
    releases = _get_release_notes()
    return shared.templates.TemplateResponse('releases.html', {
        'request': request, 'page': 'releases', 'releases': releases,
    })
