"""Dashboard, server stats, backup, and releases routes."""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from typing import Any

import psutil
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import shared
from app.helpers import _get_release_notes

router = APIRouter()


@router.get('/')
def root_redirect(request: Request):
    return RedirectResponse(url='/admin', status_code=302)


@router.get('/admin/songs', response_class=HTMLResponse)
def admin_songs(request: Request):
    return shared.templates.TemplateResponse(request, 'songs.html', {
        'request': request,
        'page': 'songs',
    })


@router.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request):
    all_workflows = shared.db.list_workflows(limit=100)
    recent_audio = shared.db.list_audio_jobs(limit=10)

    # Count by status
    status_counts: dict[str, int] = {}
    for r in all_workflows:
        status_counts[r['status']] = status_counts.get(r['status'], 0) + 1

    # Active workflows (running + queued)
    active_workflows = [r for r in all_workflows if r['status'] in ('running', 'queued')]
    active_audio = [j for j in recent_audio if j['status'] in ('queued', 'pushing', 'running', 'downloading')]

    # Shorts
    recent_shorts = [r for r in all_workflows if r.get('type') == 'short'][:5]

    return shared.templates.TemplateResponse(request, 'dashboard.html', {
        'request': request,
        'page': 'dashboard',
        'recent_runs': all_workflows[:5],
        'recent_audio': recent_audio[:5],
        'recent_shorts': recent_shorts,
        'active_runs': active_workflows,
        'active_audio': active_audio,
        'count_running': status_counts.get('running', 0),
        'count_queued': status_counts.get('queued', 0),
        'count_rendered': status_counts.get('rendered', 0),
        'count_uploaded': status_counts.get('uploaded', 0),
        'count_audio_active': len(active_audio),
        'count_shorts': len(recent_shorts),
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
    return shared.templates.TemplateResponse(request, 'releases.html', {
        'request': request, 'page': 'releases', 'releases': releases,
    })
