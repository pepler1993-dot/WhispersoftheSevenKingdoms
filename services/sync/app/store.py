from __future__ import annotations

import json
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
        self._init_db()
        self._integrity_check()

    def _integrity_check(self) -> None:
        try:
            with self._connect() as conn:
                result = conn.execute('PRAGMA integrity_check').fetchone()
                if result[0] != 'ok':
                    import logging
                    logging.warning('DB integrity check failed: %s', result[0])
        except Exception as e:
            import logging
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

                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_id TEXT PRIMARY KEY,
                    slug TEXT NOT NULL,
                    title TEXT,
                    status TEXT NOT NULL DEFAULT 'created',
                    config_json TEXT,
                    pid INTEGER,
                    started_at TEXT,
                    finished_at TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
                CREATE INDEX IF NOT EXISTS idx_pipeline_runs_created_at ON pipeline_runs(created_at);

                CREATE TABLE IF NOT EXISTS pipeline_run_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    stream TEXT NOT NULL DEFAULT 'stdout',
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_pipeline_run_logs_run_id ON pipeline_run_logs(run_id);

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

    def get_system_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            counts: dict[str, int] = {}
            for table in ('pipeline_runs', 'audio_jobs', 'tickets'):
                row = conn.execute(f'SELECT COUNT(*) AS count FROM {table}').fetchone()
                counts[table] = int(row['count'] or 0)
        return {
            'db_path': str(self.db_path),
            'counts': counts,
        }

    # ── pipeline runs ──

    def create_run(self, run: dict[str, Any]) -> None:
        config_val = run.get('config')
        config_json = json.dumps(config_val, ensure_ascii=False) if config_val is not None else None
        params = (
            str(run['run_id']),
            str(run['slug']),
            str(run['title']) if run.get('title') else None,
            str(run.get('status', 'created')),
            config_json,
            run.get('pid'),
            run.get('started_at'),
            run.get('finished_at'),
            run.get('error_message'),
            str(run['created_at']),
        )
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''
                    INSERT INTO pipeline_runs (
                        run_id, slug, title, status, config_json,
                        pid, started_at, finished_at, error_message, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    params,
                )
                conn.commit()

    def update_run(self, run_id: str, **fields: Any) -> None:
        if not fields:
            return
        allowed_columns = {
            'slug', 'title', 'status', 'config', 'pid',
            'started_at', 'finished_at', 'error_message',
        }
        set_clauses = []
        params: list[Any] = []
        for key, value in fields.items():
            if key == 'config':
                set_clauses.append('config_json = ?')
                params.append(json.dumps(value, ensure_ascii=False))
            elif key in allowed_columns:
                set_clauses.append(f'{key} = ?')
                params.append(value)
        if not set_clauses:
            return
        params.append(run_id)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    f"UPDATE pipeline_runs SET {', '.join(set_clauses)} WHERE run_id = ?",
                    params,
                )
                conn.commit()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM pipeline_runs WHERE run_id = ?', (run_id,)).fetchone()
        return self._row_to_run(row) if row else None

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ?', (limit,)
            ).fetchall()
        return [self._row_to_run(row) for row in rows]

    def append_run_log(self, run_id: str, stream: str, message: str, created_at: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    'INSERT INTO pipeline_run_logs (run_id, stream, message, created_at) VALUES (?, ?, ?, ?)',
                    (run_id, stream, message, created_at),
                )
                conn.commit()

    def get_run_logs(self, run_id: str, after_id: int = 0, limit: int = 500) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM pipeline_run_logs WHERE run_id = ? AND id > ? ORDER BY id ASC LIMIT ?',
                (run_id, after_id, limit),
            ).fetchall()
        return [{'id': r['id'], 'stream': r['stream'], 'message': r['message'], 'created_at': r['created_at']} for r in rows]

    def _row_to_run(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'run_id': row['run_id'],
            'slug': row['slug'],
            'title': row['title'],
            'status': row['status'],
            'config': json.loads(row['config_json']) if row['config_json'] else {},
            'pid': row['pid'],
            'started_at': row['started_at'],
            'finished_at': row['finished_at'],
            'error_message': row['error_message'],
            'created_at': row['created_at'],
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
