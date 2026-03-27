"""One-Click Workflow: Audio → Pipeline → (optional) Upload.

Phases: audio → render → (qa) → upload → done
The orchestrator polls the audio job. Once complete, it enqueues a pipeline run.
"""
from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from app.store import AgentSyncDB
from app.stores.workflows import (
    get_workflow,
    list_active_workflows,
    update_workflow,
)
from app.pipeline_queue import enqueue_run

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
        active = list_active_workflows(db)
        if not active:
            # Check once more after a pause
            time.sleep(10)
            active = list_active_workflows(db)
            if not active:
                return  # No more active workflows, thread exits

        for wf in active:
            try:
                _advance_workflow(wf, db)
            except Exception as e:
                update_workflow(db, wf['workflow_id'],
                               status='error', error_message=str(e),
                               updated_at=_now_iso())

        time.sleep(15)  # Poll every 15 seconds


def _advance_workflow(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Check current phase and advance if ready."""
    wf_id = wf['workflow_id']
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
    if not audio_job_id:
        update_workflow(db, wf['workflow_id'],
                        status='error', error_message='No audio job ID',
                        updated_at=_now_iso())
        return

    job = db.get_audio_job(audio_job_id)
    if not job:
        update_workflow(db, wf['workflow_id'],
                        status='error', error_message='Audio job not found',
                        updated_at=_now_iso())
        return

    status = job.get('status', '')

    if status == 'complete':
        # Audio done → enqueue existing pipeline run
        run_id = wf.get('pipeline_run_id')
        now = _now_iso()
        config = wf.get('config', {})

        if not run_id:
            update_workflow(db, wf['workflow_id'],
                            status='error', error_message='No pipeline run ID',
                            updated_at=now)
            return

        run = db.get_run(run_id)
        if not run:
            update_workflow(db, wf['workflow_id'],
                            status='error', error_message='Pipeline run not found',
                            updated_at=now)
            return

        db.update_run(run_id, status='created')
        db.append_run_log(run_id, 'system', 'Audio abgeschlossen – Render wird in die Warteschlange gestellt.', now)
        enqueue_run(run_id, wf['slug'], config, db)

        update_workflow(db, wf['workflow_id'],
                        phase='render', updated_at=now)

    elif status in ('error', 'cancelled'):
        update_workflow(db, wf['workflow_id'],
                        status='error',
                        error_message=f'Audio job {status}: {job.get("error_message", "")}',
                        updated_at=_now_iso())


def _handle_render_phase(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Wait for pipeline run to complete."""
    run_id = wf.get('pipeline_run_id')
    if not run_id:
        update_workflow(db, wf['workflow_id'],
                        status='error', error_message='No pipeline run ID',
                        updated_at=_now_iso())
        return

    run = db.get_run(run_id)
    if not run:
        return

    status = run.get('status', '')

    if status == 'rendered':
        if wf.get('auto_upload'):
            # Auto-upload → trigger upload
            from app.pipeline_runner import trigger_upload
            trigger_upload(run_id, wf['slug'], wf.get('config', {}), db)
            update_workflow(db, wf['workflow_id'],
                            phase='upload', updated_at=_now_iso())
        else:
            # No auto-upload → done (QA phase, user triggers manually)
            update_workflow(db, wf['workflow_id'],
                            phase='done', status='completed',
                            updated_at=_now_iso())

    elif status == 'uploaded':
        update_workflow(db, wf['workflow_id'],
                        phase='done', status='completed',
                        updated_at=_now_iso())

    elif status in ('failed', 'cancelled'):
        update_workflow(db, wf['workflow_id'],
                        status='error',
                        error_message=f'Pipeline {status}: {run.get("error_message", "")}',
                        updated_at=_now_iso())


def _handle_upload_phase(wf: dict[str, Any], db: AgentSyncDB) -> None:
    """Wait for upload to complete."""
    run_id = wf.get('pipeline_run_id')
    if not run_id:
        return

    run = db.get_run(run_id)
    if not run:
        return

    status = run.get('status', '')

    if status == 'uploaded':
        update_workflow(db, wf['workflow_id'],
                        phase='done', status='completed',
                        updated_at=_now_iso())
    elif status in ('failed', 'cancelled'):
        update_workflow(db, wf['workflow_id'],
                        status='error',
                        error_message=f'Upload {status}: {run.get("error_message", "")}',
                        updated_at=_now_iso())
