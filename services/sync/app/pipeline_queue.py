"""Pipeline job queue – sequential execution with concurrency limit."""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

from app.pipeline_runner import start_run
from app.store import AgentSyncDB

_lock = threading.Lock()
_worker_thread: threading.Thread | None = None
_running = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def enqueue_run(run_id: str, slug: str, config: dict[str, Any], db: AgentSyncDB) -> None:
    """Add a run to the queue and ensure the worker is running."""
    db.update_run(run_id, status='queued')
    db.append_run_log(run_id, 'system', 'Job in Warteschlange eingereiht.', _now_iso())
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
    """Process queued pipeline runs one at a time."""
    global _running
    while _running:
        next_run = _get_next_queued(db)
        if not next_run:
            # Nothing left – sleep briefly, then check once more before exiting
            time.sleep(2)
            next_run = _get_next_queued(db)
            if not next_run:
                with _lock:
                    _running = False
                return

        run_id = next_run['run_id']
        slug = next_run['slug']
        config = next_run.get('config', {})

        db.append_run_log(run_id, 'system', 'Warteschlange: Job wird jetzt gestartet.', _now_iso())

        try:
            # start_run is blocking – it waits for the subprocess to finish
            start_run(run_id, slug, config, db)
        except Exception as exc:
            db.update_run(run_id, status='failed', error_message=f'Queue worker error: {exc}', finished_at=_now_iso())
            db.append_run_log(run_id, 'system', f'Queue worker error: {exc}', _now_iso())

        # Small pause between jobs
        time.sleep(1)


def _get_next_queued(db: AgentSyncDB) -> dict[str, Any] | None:
    """Get the oldest queued run."""
    runs = db.list_runs(limit=200)
    queued = [r for r in runs if r['status'] == 'queued']
    if not queued:
        return None
    # Oldest first (list_runs is DESC, so last = oldest)
    return queued[-1]


def get_queue_status(db: AgentSyncDB) -> dict[str, Any]:
    """Get current queue state for UI."""
    runs = db.list_runs(limit=200)
    queued = [r for r in runs if r['status'] == 'queued']
    running = [r for r in runs if r['status'] == 'running']
    return {
        'queued_count': len(queued),
        'running_count': len(running),
        'queued_runs': queued,
        'running_runs': running,
        'worker_alive': _worker_thread is not None and _worker_thread.is_alive(),
    }
