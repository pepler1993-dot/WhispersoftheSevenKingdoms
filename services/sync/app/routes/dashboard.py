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
    tab = request.query_params.get('tab', 'videos')

    # All content workflows (exclude audio_lab)
    all_content = [w for w in shared.db.list_workflows(limit=200) if w.get('type') != 'audio_lab']

    # Tab filtering
    if tab == 'videos':
        filtered = [w for w in all_content if w['type'] == 'video']
    elif tab == 'shorts':
        filtered = [w for w in all_content if w['type'] == 'short']
    elif tab == 'songs':
        filtered = [w for w in all_content if w['type'] == 'song']
    else:
        filtered = all_content

    # Stats (scoped to current tab)
    running_statuses = {'running', 'uploading', 'waiting_for_audio'}
    count_running = sum(1 for w in filtered if w['status'] in running_statuses)
    count_queued = sum(1 for w in filtered if w['status'] == 'queued')
    count_rendered = sum(1 for w in filtered if w['status'] == 'rendered')
    count_uploaded = sum(1 for w in filtered if w['status'] == 'uploaded')

    # Sections (scoped to current tab)
    active = [w for w in filtered if w['status'] in running_statuses | {'queued'}]
    published = [w for w in filtered if w['status'] == 'uploaded'][:8]

    # Type counts for tabs
    count_all = len(all_content)
    count_videos = sum(1 for w in all_content if w['type'] == 'video')
    count_shorts = sum(1 for w in all_content if w['type'] == 'short')
    count_songs = sum(1 for w in all_content if w['type'] == 'song')

    return shared.templates.TemplateResponse(request, 'dashboard.html', {
        'request': request,
        'page': 'dashboard',
        'tab': tab,
        'workflows': filtered[:20],
        'active': active,
        'published': published,
        'count_running': count_running,
        'count_queued': count_queued,
        'count_rendered': count_rendered,
        'count_uploaded': count_uploaded,
        'count_all': count_all,
        'count_videos': count_videos,
        'count_shorts': count_shorts,
        'count_songs': count_songs,
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
