"""One-Click Workflow Orchestrator: Audio → Pipeline → (optional) Upload.

Phases: audio → render → (qa) → upload → done
The orchestrator polls active workflows. Once audio completes, it enqueues the render phase.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

from app.store import AgentSyncDB
from app.pipeline_queue import enqueue_workflow

_poll_thread: threading.Thread | None = None
_poll_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def start_workflow(
    workflow_id: str,
    audio_job_id: str,
    slug: str,
    title: str,
    pipeline_config: dict[str, Any],
    auto_upload: bool,
    db: AgentSyncDB,
) -> None:
    """Called after audio job is created. Starts polling for completion."""
    _ensure_poll_thread(db)


def _ensure_poll_thread(db: AgentSyncDB) -> None:
    global _poll_thread
    with _poll_lock:
        if _poll_thread is not None and _poll_thread.is_alive():
            return
        _poll_thread = threading.Thread(target=_poll_worker, args=(db,), daemon=True)
        _poll_thread.start()


def _poll_worker(db: AgentSyncDB) -> None:
    """Polls active workflows and advances them through phases."""
    while True:
        active = db.list_active_workflows()
        if not active:
            # Check once more after a pause
            time.sleep(10)
            active = db.list_active_workflows()
            if not active:
                return  # No more active workflows, thread exits

        for wf in active:
            try:
                _advance_workflow(wf, db)
            except Exception as e:
                db.update_workflow(wf['workflow_id'],
                                  status='error', error_message=str(e),
                                  updated_at=_now_iso())

        time.sleep(15)  # Poll every 15 seconds


def _advance_workflow(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Check current phase and advance if ready."""
    phase = wf['phase']

    if phase == 'audio':
        _handle_audio_phase(wf, db)
    elif phase == 'render':
        _handle_render_phase(wf, db)
    elif phase == 'upload':
        _handle_upload_phase(wf, db)


def _handle_audio_phase(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Wait for audio job to complete, then start pipeline."""
    audio_job_id = wf.get('audio_job_id')
    wf_id = wf['workflow_id']
    if not audio_job_id:
        db.update_workflow(wf_id,
                           status='error', error_message='No audio job ID',
                           updated_at=_now_iso())
        return

    job = db.get_audio_job(audio_job_id)
    if not job:
        db.update_workflow(wf_id,
                           status='error', error_message='Audio job not found',
                           updated_at=_now_iso())
        return

    status = job.get('status', '')

    if status == 'complete':
        # Audio done → enqueue this workflow for render
        now = _now_iso()
        config = wf.get('config', {})

        db.update_workflow(wf_id, status='created', phase='render', updated_at=now)
        db.append_workflow_log(wf_id, 'system', 'Audio abgeschlossen – Render wird in die Warteschlange gestellt.', now)
        enqueue_workflow(wf_id, wf['slug'], config, db)

    elif status in ('error', 'cancelled'):
        db.update_workflow(wf_id,
                           status='error',
                           error_message=f'Audio job {status}: {job.get("error_message", "")}',
                           updated_at=_now_iso())


def _handle_render_phase(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Wait for pipeline render to complete."""
    wf_id = wf['workflow_id']
    # Re-read current state
    current = db.get_workflow(wf_id)
    if not current:
        return

    status = current.get('status', '')

    if status == 'rendered':
        if current.get('auto_upload'):
            from app.pipeline_runner import trigger_upload
            trigger_upload(wf_id, current['slug'], current.get('config', {}), db)
            db.update_workflow(wf_id,
                               phase='upload', updated_at=_now_iso())
        else:
            db.update_workflow(wf_id,
                               phase='done', status='completed',
                               updated_at=_now_iso())

    elif status == 'uploaded':
        db.update_workflow(wf_id,
                           phase='done', status='completed',
                           updated_at=_now_iso())

    elif status in ('failed', 'cancelled'):
        db.update_workflow(wf_id,
                           status='error',
                           error_message=f'Pipeline {status}: {current.get("error_message", "")}',
                           updated_at=_now_iso())


def _handle_upload_phase(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Wait for upload to complete."""
    wf_id = wf['workflow_id']
    current = db.get_workflow(wf_id)
    if not current:
        return

    status = current.get('status', '')

    if status == 'uploaded':
        db.update_workflow(wf_id,
                           phase='done', status='completed',
                           updated_at=_now_iso())
    elif status in ('failed', 'cancelled'):
        db.update_workflow(wf_id,
                           status='error',
                           error_message=f'Upload {status}: {current.get("error_message", "")}',
                           updated_at=_now_iso())
