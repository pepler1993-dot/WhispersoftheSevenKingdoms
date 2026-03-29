"""Pipeline job queue – sequential execution with concurrency limit."""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

from app.pipeline_runner import start_run, trigger_upload
from app.store import AgentSyncDB

_lock = threading.Lock()
_worker_thread: threading.Thread | None = None
_running = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def recover_interrupted_workflows(db: AgentSyncDB) -> int:
    """On startup, recover workflows that were interrupted by a restart.

    - 'running' workflows → mark as 'failed' (subprocess is gone)
    - 'queued' workflows → re-enqueue them so they actually run
    """
    workflows = db.list_workflows(limit=200)
    recovered = 0
    requeued = []

    for wf in workflows:
        if wf['status'] == 'running':
            db.update_workflow(
                wf['workflow_id'],
                status='failed',
                finished_at=_now_iso(),
                error_message='Service restarted while workflow was in progress.',
                pid=None,
            )
            db.append_workflow_log(wf['workflow_id'], 'system', 'Recovered after restart: marked as failed.', _now_iso())
            recovered += 1
        elif wf['status'] == 'queued':
            requeued.append(wf)

    # Re-enqueue queued workflows (they'll be picked up by the worker)
    for wf in requeued:
        db.append_workflow_log(wf['workflow_id'], 'system', 'Re-queued after service restart.', _now_iso())
        recovered += 1

    return recovered


def enqueue_workflow(workflow_id: str, slug: str, config: dict[str, Any], db: AgentSyncDB) -> None:
    """Add a workflow to the queue and ensure the worker is running."""
    db.update_workflow(workflow_id, status='queued')
    db.append_workflow_log(workflow_id, 'system', 'Job in Warteschlange eingereiht.', _now_iso())
    _ensure_worker(db)


def _ensure_worker(db: AgentSyncDB) -> None:
    """Start the queue worker thread if not already running."""
    global _worker_thread, _running
    with _lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            return
        _running = True
        _worker_thread = threading.Thread(target=_queue_worker, args=(db,), daemon=True)
        _worker_thread.start()


def _queue_worker(db: AgentSyncDB) -> None:
    """Process queued workflows one at a time."""
    global _running
    while _running:
        next_wf = _get_next_queued(db)
        if not next_wf:
            # Nothing left – sleep briefly, then check once more before exiting
            time.sleep(2)
            next_wf = _get_next_queued(db)
            if not next_wf:
                with _lock:
                    _running = False
                return

        workflow_id = next_wf['workflow_id']
        slug = next_wf['slug']
        config = next_wf.get('config', {})

        db.append_workflow_log(workflow_id, 'system', 'Warteschlange: Job wird jetzt gestartet.', _now_iso())

        try:
            # start_run is blocking – it waits for the subprocess to finish
            start_run(workflow_id, slug, config, db)

            # Auto-upload if configured
            wf_after = db.get_workflow(workflow_id)
            if wf_after and wf_after.get('status') == 'rendered' and config.get('auto_upload'):
                db.append_workflow_log(workflow_id, 'system', f'Auto-Upload gestartet (public={config.get("public", False)})', _now_iso())
                db.update_workflow(workflow_id, phase='upload')
                trigger_upload(workflow_id, slug, config, db)
                # Ensure orchestrator polls for upload→completed transition
                # Lazy import to avoid circular dependency
                from app.workflow_orchestrator import _ensure_poll_thread
                _ensure_poll_thread(db)
        except Exception as exc:
            db.update_workflow(workflow_id, status='failed', error_message=f'Queue worker error: {exc}', finished_at=_now_iso())
            db.append_workflow_log(workflow_id, 'system', f'Queue worker error: {exc}', _now_iso())

        # Small pause between jobs
        time.sleep(1)


def _get_next_queued(db: AgentSyncDB) -> dict[str, Any] | None:
    """Get the oldest queued workflow."""
    workflows = db.list_workflows(limit=200)
    queued = [w for w in workflows if w['status'] == 'queued']
    if not queued:
        return None
    # Oldest first (list_workflows is DESC, so last = oldest)
    return queued[-1]


def get_queue_status(db: AgentSyncDB) -> dict[str, Any]:
    """Get current queue state for UI."""
    workflows = db.list_workflows(limit=200)
    queued = [w for w in workflows if w['status'] == 'queued']
    running = [w for w in workflows if w['status'] == 'running']
    return {
        'queued_count': len(queued),
        'running_count': len(running),
        'queued_workflows': queued,
        'running_workflows': running,
        'worker_alive': _worker_thread is not None and _worker_thread.is_alive(),
    }
