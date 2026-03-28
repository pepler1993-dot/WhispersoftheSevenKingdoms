"""Health routes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

from app import shared
from app.audio_jobs import get_audio_generator_health

router = APIRouter()


@router.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/api/health/overview')
def health_overview() -> dict[str, Any]:
    """Global health status for the Overview dashboard."""

    # GPU/Audio Worker
    try:
        gpu = get_audio_generator_health()
        gpu_status = 'healthy' if gpu.get('available') else 'offline'
        gpu_detail = gpu.get('gpu', 'unknown')
        gpu_daemon = gpu.get('daemon', False)
    except Exception:
        gpu_status = 'error'
        gpu_detail = 'Health check failed'
        gpu_daemon = False

    # Queue health
    workflows = shared.db.list_workflows(limit=200)
    queued = [w for w in workflows if w['status'] == 'queued']
    running = [w for w in workflows if w['status'] in ('running', 'uploading', 'waiting_for_audio')]
    failed_recent = [w for w in workflows if w['status'] in ('failed', 'error')][:5]

    # Last successful publish
    uploaded = [w for w in workflows if w['status'] == 'uploaded']
    last_publish = uploaded[0] if uploaded else None
    last_publish_time = last_publish['finished_at'] if last_publish else None

    # YouTube/Upload health (based on recent upload success/failure)
    recent_uploads = [w for w in workflows if w['status'] in ('uploaded', 'failed') and w.get('phase') in ('upload', 'done')][:10]
    upload_success = sum(1 for w in recent_uploads if w['status'] == 'uploaded')
    upload_total = len(recent_uploads)
    upload_status = 'healthy' if upload_total == 0 or upload_success / max(upload_total, 1) > 0.7 else 'degraded'

    # Pipeline health
    pipeline_status = 'healthy'
    if len(failed_recent) > 3:
        pipeline_status = 'degraded'
    if running:
        pipeline_status = 'active'

    return {
        'gpu_worker': {
            'status': gpu_status,
            'detail': gpu_detail,
            'daemon': gpu_daemon,
        },
        'queue': {
            'status': 'active' if running else ('waiting' if queued else 'idle'),
            'running': len(running),
            'queued': len(queued),
        },
        'upload': {
            'status': upload_status,
            'success_rate': f'{upload_success}/{upload_total}' if upload_total else 'n/a',
        },
        'pipeline': {
            'status': pipeline_status,
            'recent_failures': len(failed_recent),
        },
        'last_publish': {
            'title': last_publish['title'] if last_publish else None,
            'time': last_publish_time,
        },
    }
