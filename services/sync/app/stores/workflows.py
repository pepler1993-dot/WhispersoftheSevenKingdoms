"""Workflow store – tracks Audio→Pipeline→Upload workflows."""
from __future__ import annotations

import json
import sqlite3
from typing import Any


def ensure_table(db) -> None:
    """Create workflows table if it doesn't exist."""
    with db._lock:
        with db._connect() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    slug TEXT NOT NULL,
                    phase TEXT NOT NULL DEFAULT 'audio',
                    status TEXT NOT NULL DEFAULT 'running',
                    audio_job_id TEXT,
                    pipeline_run_id TEXT,
                    config_json TEXT,
                    auto_upload INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
            ''')
            conn.commit()


def create_workflow(db, wf: dict[str, Any]) -> None:
    with db._lock:
        with db._connect() as conn:
            conn.execute(
                '''INSERT INTO workflows
                   (workflow_id, title, slug, phase, status, audio_job_id,
                    pipeline_run_id, config_json, auto_upload, error_message,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    wf['workflow_id'], wf['title'], wf['slug'],
                    wf.get('phase', 'audio'), wf.get('status', 'running'),
                    wf.get('audio_job_id'), wf.get('pipeline_run_id'),
                    json.dumps(wf.get('config', {}), ensure_ascii=False),
                    1 if wf.get('auto_upload') else 0,
                    wf.get('error_message'),
                    wf['created_at'], wf['updated_at'],
                ),
            )
            conn.commit()


def get_workflow(db, workflow_id: str) -> dict[str, Any] | None:
    with db._connect() as conn:
        conn.row_factory = _wf_row_factory
        row = conn.execute('SELECT * FROM workflows WHERE workflow_id = ?', (workflow_id,)).fetchone()
        return row


def update_workflow(db, workflow_id: str, **fields: Any) -> None:
    allowed = {'phase', 'status', 'audio_job_id', 'pipeline_run_id',
               'error_message', 'updated_at', 'auto_upload'}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    if 'auto_upload' in updates:
        updates['auto_upload'] = 1 if updates['auto_upload'] else 0
    with db._lock:
        with db._connect() as conn:
            sets = ', '.join(f'{k} = ?' for k in updates)
            vals = list(updates.values()) + [workflow_id]
            conn.execute(f'UPDATE workflows SET {sets} WHERE workflow_id = ?', vals)
            conn.commit()


def list_workflows(db, limit: int = 50) -> list[dict[str, Any]]:
    with db._connect() as conn:
        conn.row_factory = _wf_row_factory
        return conn.execute(
            'SELECT * FROM workflows ORDER BY created_at DESC LIMIT ?', (limit,)
        ).fetchall()


def list_active_workflows(db) -> list[dict[str, Any]]:
    """Get workflows that are still running (need polling)."""
    with db._connect() as conn:
        conn.row_factory = _wf_row_factory
        return conn.execute(
            "SELECT * FROM workflows WHERE status = 'running' ORDER BY created_at ASC"
        ).fetchall()


def _wf_row_factory(cursor, row):
    cols = [d[0] for d in cursor.description]
    d = dict(zip(cols, row))
    d['config'] = json.loads(d.pop('config_json', '{}') or '{}')
    d['auto_upload'] = bool(d.get('auto_upload'))
    return d
