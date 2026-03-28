from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any


class AgentSyncDB:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / 'agent_sync.db'
        self._lock = Lock()
        self._rename_legacy_tables()
        self._init_db()
        self._migrate_legacy_tables()
        self._integrity_check()

    def _integrity_check(self) -> None:
        try:
            with self._connect() as conn:
                result = conn.execute('PRAGMA integrity_check').fetchone()
                if result[0] != 'ok':
                    logging.warning('DB integrity check failed: %s', result[0])
        except Exception as e:
            logging.error('DB integrity check error: %s', e)

    def backup(self, backup_dir: Path | None = None) -> Path:
        """Create a hot backup using SQLite backup API."""
        from datetime import datetime
        backup_dir = backup_dir or self.data_dir / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'agent_sync_{timestamp}.db'

        with self._lock:
            src = sqlite3.connect(self.db_path)
            dst = sqlite3.connect(backup_path)
            src.backup(dst)
            dst.close()
            src.close()

        backups = sorted(backup_dir.glob('agent_sync_*.db'))
        for old in backups[:-7]:
            old.unlink(missing_ok=True)

        return backup_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                '''
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL DEFAULT 'video',
                    slug TEXT NOT NULL,
                    title TEXT,
                    phase TEXT NOT NULL DEFAULT 'render',
                    status TEXT NOT NULL DEFAULT 'created',
                    audio_job_id TEXT,
                    config_json TEXT,
                    auto_upload INTEGER NOT NULL DEFAULT 0,
                    pid INTEGER,
                    started_at TEXT,
                    finished_at TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
                CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at);
                CREATE INDEX IF NOT EXISTS idx_workflows_type ON workflows(type);

                CREATE TABLE IF NOT EXISTS workflow_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    stream TEXT NOT NULL DEFAULT 'stdout',
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_workflow_logs_workflow_id ON workflow_logs(workflow_id);

                CREATE TABLE IF NOT EXISTS audio_jobs (
                    job_id TEXT PRIMARY KEY,
                    slug TEXT NOT NULL,
                    title TEXT,
                    provider TEXT NOT NULL DEFAULT 'stable-audio-local',
                    preset_name TEXT,
                    prompt_text TEXT,
                    prompts_json TEXT,
                    minutes INTEGER,
                    model TEXT,
                    clip_seconds INTEGER,
                    status TEXT NOT NULL DEFAULT 'queued',
                    kernel_ref TEXT,
                    output_path TEXT,
                    started_at TEXT,
                    finished_at TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audio_jobs_status ON audio_jobs(status);
                CREATE INDEX IF NOT EXISTS idx_audio_jobs_created_at ON audio_jobs(created_at);

                CREATE TABLE IF NOT EXISTS audio_job_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    stream TEXT NOT NULL DEFAULT 'system',
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audio_job_logs_job_id ON audio_job_logs(job_id);

                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL DEFAULT 'bug',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'open',
                    github_issue_number INTEGER,
                    github_issue_url TEXT,
                    task_id TEXT,
                    created_by TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
                CREATE INDEX IF NOT EXISTS idx_tickets_type ON tickets(type);

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    email TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'editor',
                    space_id TEXT DEFAULT 'default',
                    created_at TEXT NOT NULL,
                    last_login TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_users_space ON users(space_id);

                CREATE TABLE IF NOT EXISTS spaces (
                    space_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tagline TEXT,
                    created_at TEXT NOT NULL
                );
                '''
            )
            try:
                conn.execute('ALTER TABLE tickets ADD COLUMN assigned_to TEXT')
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def _rename_legacy_tables(self) -> None:
        """Rename old tables before _init_db creates the new schema."""
        try:
            with self._connect() as conn:
                tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

                # Rename old workflows table (has pipeline_run_id column) if it exists
                if 'workflows' in tables:
                    cols = {r[1] for r in conn.execute('PRAGMA table_info(workflows)').fetchall()}
                    if 'pipeline_run_id' in cols:
                        conn.execute('ALTER TABLE workflows RENAME TO _old_workflows_backup')
                        conn.commit()
                        logging.info('Renamed old workflows table to _old_workflows_backup')

                # Rename old pipeline tables
                tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
                if 'pipeline_runs' in tables:
                    conn.execute('ALTER TABLE pipeline_runs RENAME TO _pipeline_runs_backup')
                    if 'pipeline_run_logs' in tables:
                        conn.execute('ALTER TABLE pipeline_run_logs RENAME TO _pipeline_run_logs_backup')
                    conn.commit()
                    logging.info('Renamed old pipeline_runs tables to _backup')
        except Exception as e:
            logging.warning('Legacy table rename (non-fatal): %s', e)

    def _migrate_legacy_tables(self) -> None:
        """Migrate data from backup tables into the new unified workflows table."""
        try:
            self._do_migrate_legacy()
        except Exception as e:
            logging.error('Legacy migration failed (non-fatal): %s', e)

    def _do_migrate_legacy(self) -> None:
        with self._lock:
            with self._connect() as conn:
                tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
                if '_pipeline_runs_backup' not in tables:
                    return  # Nothing to migrate

                # Load old workflow data for merging (audio_job_id, auto_upload)
                old_wf_by_run: dict[str, dict] = {}
                if '_old_workflows_backup' in tables:
                    for row in conn.execute('SELECT * FROM _old_workflows_backup').fetchall():
                        d = dict(row)
                        run_id = d.get('pipeline_run_id')
                        if run_id:
                            old_wf_by_run[run_id] = d

                # Skip if already migrated (workflows table has data)
                existing = conn.execute('SELECT COUNT(*) FROM workflows').fetchone()[0]
                if existing > 0:
                    return

                # Migrate pipeline_runs → workflows
                for row in conn.execute('SELECT * FROM _pipeline_runs_backup').fetchall():
                    d = dict(row)
                    run_id = d['run_id']
                    config_json = d.get('config_json') or '{}'
                    try:
                        config = json.loads(config_json)
                    except (json.JSONDecodeError, TypeError):
                        config = {}

                    wf_type = 'short' if config.get('content_type') == 'short' else 'video'

                    # Merge fields from old workflow if available
                    old_wf = old_wf_by_run.get(run_id, {})
                    audio_job_id = old_wf.get('audio_job_id')
                    auto_upload = 1 if old_wf.get('auto_upload') else (1 if config.get('auto_upload') else 0)

                    status = d.get('status', 'created')
                    phase = 'render'
                    if status == 'waiting_for_audio':
                        phase = 'audio'
                    elif status in ('uploaded',):
                        phase = 'done'
                    elif status in ('uploading',):
                        phase = 'upload'

                    if old_wf.get('phase'):
                        phase = old_wf['phase']

                    conn.execute(
                        '''INSERT OR IGNORE INTO workflows
                           (workflow_id, type, slug, title, phase, status, audio_job_id,
                            config_json, auto_upload, pid, started_at, finished_at,
                            error_message, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (
                            run_id, wf_type, d['slug'], d.get('title'),
                            phase, status, audio_job_id,
                            config_json, auto_upload,
                            d.get('pid'), d.get('started_at'), d.get('finished_at'),
                            d.get('error_message'), d['created_at'],
                            old_wf.get('updated_at'),
                        ),
                    )

                # Migrate pipeline_run_logs → workflow_logs
                backup_tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
                if '_pipeline_run_logs_backup' in backup_tables:
                    conn.execute(
                        '''INSERT INTO workflow_logs (workflow_id, stream, message, created_at)
                           SELECT run_id, stream, message, created_at FROM _pipeline_run_logs_backup'''
                    )

                conn.commit()
                logging.info('Migrated legacy pipeline_runs + workflows into unified workflows table.')

    def get_system_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            counts: dict[str, int] = {}
            for table in ('workflows', 'audio_jobs', 'tickets'):
                row = conn.execute(f'SELECT COUNT(*) AS count FROM {table}').fetchone()
                counts[table] = int(row['count'] or 0)
        return {
            'db_path': str(self.db_path),
            'counts': counts,
        }

    # ── workflows ──

    def create_workflow(self, wf: dict[str, Any]) -> None:
        config_val = wf.get('config')
        config_json = json.dumps(config_val, ensure_ascii=False) if config_val is not None else None
        params = (
            str(wf['workflow_id']),
            str(wf.get('type', 'video')),
            str(wf['slug']),
            str(wf['title']) if wf.get('title') else None,
            str(wf.get('phase', 'render')),
            str(wf.get('status', 'created')),
            wf.get('audio_job_id'),
            config_json,
            1 if wf.get('auto_upload') else 0,
            wf.get('pid'),
            wf.get('started_at'),
            wf.get('finished_at'),
            wf.get('error_message'),
            str(wf['created_at']),
            wf.get('updated_at'),
        )
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''
                    INSERT INTO workflows (
                        workflow_id, type, slug, title, phase, status, audio_job_id,
                        config_json, auto_upload, pid, started_at, finished_at,
                        error_message, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    params,
                )
                conn.commit()

    def update_workflow(self, workflow_id: str, **fields: Any) -> None:
        if not fields:
            return
        allowed_columns = {
            'type', 'slug', 'title', 'phase', 'status', 'audio_job_id',
            'config', 'auto_upload', 'pid', 'started_at', 'finished_at',
            'error_message', 'updated_at',
        }
        set_clauses = []
        params: list[Any] = []
        for key, value in fields.items():
            if key == 'config':
                set_clauses.append('config_json = ?')
                params.append(json.dumps(value, ensure_ascii=False))
            elif key == 'auto_upload':
                set_clauses.append('auto_upload = ?')
                params.append(1 if value else 0)
            elif key in allowed_columns:
                set_clauses.append(f'{key} = ?')
                params.append(value)
        if not set_clauses:
            return
        params.append(workflow_id)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE workflows SET {', '.join(set_clauses)} WHERE workflow_id = ?",
                    params,
                )
                conn.commit()

    def get_workflow(self, workflow_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM workflows WHERE workflow_id = ?', (workflow_id,)).fetchone()
        return self._row_to_workflow(row) if row else None

    def list_workflows(self, limit: int = 50, type: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if type:
                rows = conn.execute(
                    'SELECT * FROM workflows WHERE type = ? ORDER BY created_at DESC LIMIT ?', (type, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT * FROM workflows ORDER BY created_at DESC LIMIT ?', (limit,)
                ).fetchall()
        return [self._row_to_workflow(row) for row in rows]

    def list_active_workflows(self) -> list[dict[str, Any]]:
        """Get workflows that need polling (running or waiting for audio)."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM workflows WHERE status IN ('running', 'waiting_for_audio') "
                "OR (phase = 'audio' AND status NOT IN ('error', 'cancelled', 'completed')) "
                "ORDER BY created_at ASC"
            ).fetchall()
        return [self._row_to_workflow(row) for row in rows]

    def append_workflow_log(self, workflow_id: str, stream: str, message: str, created_at: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    'INSERT INTO workflow_logs (workflow_id, stream, message, created_at) VALUES (?, ?, ?, ?)',
                    (workflow_id, stream, message, created_at),
                )
                conn.commit()

    def get_workflow_logs(self, workflow_id: str, after_id: int = 0, limit: int = 500) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM workflow_logs WHERE workflow_id = ? AND id > ? ORDER BY id ASC LIMIT ?',
                (workflow_id, after_id, limit),
            ).fetchall()
        return [{'id': r['id'], 'stream': r['stream'], 'message': r['message'], 'created_at': r['created_at']} for r in rows]

    def _row_to_workflow(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'workflow_id': row['workflow_id'],
            'type': row['type'],
            'slug': row['slug'],
            'title': row['title'],
            'phase': row['phase'],
            'status': row['status'],
            'audio_job_id': row['audio_job_id'],
            'config': json.loads(row['config_json']) if row['config_json'] else {},
            'auto_upload': bool(row['auto_upload']),
            'pid': row['pid'],
            'started_at': row['started_at'],
            'finished_at': row['finished_at'],
            'error_message': row['error_message'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        }

    # ── audio jobs ──

    def create_audio_job(self, job: dict[str, Any]) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''
                    INSERT INTO audio_jobs (
                        job_id, slug, title, provider, preset_name, prompt_text, prompts_json,
                        minutes, model, clip_seconds, status, kernel_ref, output_path,
                        started_at, finished_at, error_message, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        job['job_id'], job['slug'], job.get('title'), job.get('provider', 'stable-audio-local'),
                        job.get('preset_name'), job.get('prompt_text'), json.dumps(job.get('prompts', []), ensure_ascii=False),
                        job.get('minutes'), job.get('model'), job.get('clip_seconds'), job.get('status', 'queued'),
                        job.get('kernel_ref'), job.get('output_path'), job.get('started_at'), job.get('finished_at'),
                        job.get('error_message'), job['created_at'],
                    ),
                )
                conn.commit()

    def update_audio_job(self, job_id: str, **fields: Any) -> None:
        if not fields:
            return
        allowed_columns = {
            'slug', 'title', 'provider', 'preset_name', 'prompt_text',
            'prompts_json', 'minutes', 'model', 'clip_seconds', 'status',
            'kernel_ref', 'output_path', 'started_at', 'finished_at', 'error_message',
        }
        set_clauses = []
        params: list[Any] = []
        for key, value in fields.items():
            if key in allowed_columns:
                set_clauses.append(f'{key} = ?')
                params.append(value)
        if not set_clauses:
            return
        params.append(job_id)
        with self._lock:
            with self._connect() as conn:
                conn.execute(f"UPDATE audio_jobs SET {', '.join(set_clauses)} WHERE job_id = ?", params)
                conn.commit()

    def get_audio_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM audio_jobs WHERE job_id = ?', (job_id,)).fetchone()
        return self._row_to_audio_job(row) if row else None

    def list_audio_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute('SELECT * FROM audio_jobs ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [self._row_to_audio_job(row) for row in rows]

    def list_audio_jobs_by_status(self, statuses: list[str]) -> list[dict[str, Any]]:
        if not statuses:
            return []
        placeholders = ', '.join('?' for _ in statuses)
        with self._connect() as conn:
            rows = conn.execute(
                f'SELECT * FROM audio_jobs WHERE status IN ({placeholders}) ORDER BY created_at DESC',
                tuple(statuses),
            ).fetchall()
        return [self._row_to_audio_job(row) for row in rows]

    def append_audio_job_log(self, job_id: str, stream: str, message: str, created_at: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    'INSERT INTO audio_job_logs (job_id, stream, message, created_at) VALUES (?, ?, ?, ?)',
                    (job_id, stream, message, created_at),
                )
                conn.commit()

    def get_audio_job_logs(self, job_id: str, after_id: int = 0, limit: int = 500) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM audio_job_logs WHERE job_id = ? AND id > ? ORDER BY id ASC LIMIT ?',
                (job_id, after_id, limit),
            ).fetchall()
        return [{'id': r['id'], 'stream': r['stream'], 'message': r['message'], 'created_at': r['created_at']} for r in rows]

    def _row_to_audio_job(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'job_id': row['job_id'],
            'slug': row['slug'],
            'title': row['title'],
            'provider': row['provider'],
            'preset_name': row['preset_name'],
            'prompt_text': row['prompt_text'],
            'prompts': json.loads(row['prompts_json']) if row['prompts_json'] else [],
            'minutes': row['minutes'],
            'model': row['model'],
            'clip_seconds': row['clip_seconds'],
            'status': row['status'],
            'kernel_ref': row['kernel_ref'],
            'output_path': row['output_path'],
            'started_at': row['started_at'],
            'finished_at': row['finished_at'],
            'error_message': row['error_message'],
            'created_at': row['created_at'],
        }

    # ── settings (key-value) ──

    def get_setting(self, key: str) -> Any | None:
        with self._connect() as conn:
            row = conn.execute('SELECT value_json FROM settings WHERE key = ?', (key,)).fetchone()
        if row is None:
            return None
        return json.loads(row['value_json'])

    def set_setting(self, key: str, value: Any) -> None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''INSERT INTO settings (key, value_json, updated_at) VALUES (?, ?, ?)
                       ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at''',
                    (key, json.dumps(value, ensure_ascii=False), now),
                )
                conn.commit()

    def get_all_settings(self) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute('SELECT key, value_json FROM settings ORDER BY key').fetchall()
        return {r['key']: json.loads(r['value_json']) for r in rows}

    def delete_setting(self, key: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute('DELETE FROM settings WHERE key = ?', (key,))
                conn.commit()

    # ── users ──

    def create_user(self, user: dict[str, Any]) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''INSERT INTO users (user_id, username, display_name, email, password_hash, role, space_id, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user['user_id'], user['username'], user.get('display_name'), user.get('email'),
                     user['password_hash'], user.get('role', 'editor'), user.get('space_id', 'default'), user['created_at']),
                )
                conn.commit()

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        return dict(row) if row else None

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        return dict(row) if row else None

    def list_users(self, space_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if space_id:
                rows = conn.execute('SELECT * FROM users WHERE space_id = ? ORDER BY created_at', (space_id,)).fetchall()
            else:
                rows = conn.execute('SELECT * FROM users ORDER BY created_at').fetchall()
        return [dict(r) for r in rows]

    def update_user(self, user_id: str, **fields: Any) -> None:
        allowed = {'display_name', 'email', 'password_hash', 'role', 'space_id', 'last_login'}
        set_clauses, params = [], []
        for k, v in fields.items():
            if k in allowed:
                set_clauses.append(f'{k} = ?')
                params.append(v)
        if not set_clauses:
            return
        params.append(user_id)
        with self._lock:
            with self._connect() as conn:
                conn.execute(f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = ?", params)
                conn.commit()

    def delete_user(self, user_id: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()

    def user_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute('SELECT COUNT(*) AS c FROM users').fetchone()
        return int(row['c'] or 0)

    # ── spaces ──

    def create_space(self, space: dict[str, Any]) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    'INSERT INTO spaces (space_id, name, tagline, created_at) VALUES (?, ?, ?, ?)',
                    (space['space_id'], space['name'], space.get('tagline', ''), space['created_at']),
                )
                conn.commit()

    def get_space(self, space_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM spaces WHERE space_id = ?', (space_id,)).fetchone()
        return dict(row) if row else None

    def list_spaces(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute('SELECT * FROM spaces ORDER BY created_at').fetchall()
        return [dict(r) for r in rows]
