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
    tab = request.query_params.get('tab', 'all')

    # All content workflows (exclude audio_lab)
    all_workflows = shared.db.list_workflows(limit=100)
    content_workflows = [w for w in all_workflows if w.get('type') != 'audio_lab']

    # Counts per type (always across ALL content workflows, not filtered by tab)
    count_videos = sum(1 for w in content_workflows if w.get('type') == 'video')
    count_shorts = sum(1 for w in content_workflows if w.get('type') == 'short')
    count_songs = sum(1 for w in content_workflows if w.get('type') == 'song')

    # Stats across all content workflows
    status_counts: dict[str, int] = {}
    for w in content_workflows:
        status_counts[w['status']] = status_counts.get(w['status'], 0) + 1

    count_running = sum(status_counts.get(s, 0) for s in ('running', 'uploading', 'waiting_for_audio'))
    count_queued = status_counts.get('queued', 0)
    count_rendered = status_counts.get('rendered', 0)
    count_uploaded = status_counts.get('uploaded', 0)

    # Active workflows (running/queued/uploading/waiting)
    active_workflows = [w for w in content_workflows if w['status'] in ('running', 'queued', 'uploading', 'waiting_for_audio')]

    # Filter by tab for the list
    if tab == 'videos':
        filtered = [w for w in content_workflows if w.get('type') == 'video']
    elif tab == 'shorts':
        filtered = [w for w in content_workflows if w.get('type') == 'short']
    elif tab == 'songs':
        filtered = [w for w in content_workflows if w.get('type') == 'song']
    else:
        filtered = content_workflows

    return shared.templates.TemplateResponse(request, 'dashboard.html', {
        'request': request,
        'page': 'dashboard',
        'tab': tab,
        'workflows': filtered[:20],
        'active_workflows': active_workflows,
        'count_running': count_running,
        'count_queued': count_queued,
        'count_rendered': count_rendered,
        'count_uploaded': count_uploaded,
        'count_videos': count_videos,
        'count_shorts': count_shorts,
        'count_songs': count_songs,
        'count_all': len(content_workflows),
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
