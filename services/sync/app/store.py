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
        self._migrate_if_needed()
        self._integrity_check()

    def _integrity_check(self) -> None:
        """Run integrity check on startup. Log warning if DB is corrupted."""
        try:
            with self._connect() as conn:
                result = conn.execute('PRAGMA integrity_check').fetchone()
                if result[0] != 'ok':
                    import logging
                    logging.warning(f'DB integrity check failed: {result[0]}')
        except Exception as e:
            import logging
            logging.error(f'DB integrity check error: {e}')

    def backup(self, backup_dir: Path | None = None) -> Path:
        """Create a hot backup of the database using SQLite backup API.

        Returns the path to the backup file.
        """
        import shutil
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

        # Keep only last 7 backups
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

                CREATE TABLE IF NOT EXISTS github_events (
                    delivery_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    action TEXT,
                    repo TEXT,
                    issue_number INTEGER,
                    pr_number INTEGER,
                    task_id TEXT,
                    sender TEXT,
                    received_at TEXT,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_github_events_task_id ON github_events(task_id);
                CREATE INDEX IF NOT EXISTS idx_github_events_received_at ON github_events(received_at);

                CREATE TABLE IF NOT EXISTS task_snapshots (
                    task_id TEXT PRIMARY KEY,
                    issue_number INTEGER,
                    status TEXT,
                    branch TEXT,
                    pr_number INTEGER,
                    last_commit_sha TEXT,
                    review_state TEXT,
                    last_summary TEXT,
                    updated_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_task_snapshots_updated_at ON task_snapshots(updated_at);

                CREATE TABLE IF NOT EXISTS task_events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    repo TEXT,
                    issue_number INTEGER,
                    pr_number INTEGER,
                    delivery_id TEXT,
                    event_type TEXT,
                    action TEXT,
                    sender TEXT,
                    occurred_at TEXT,
                    snapshot_json TEXT,
                    task_state_json TEXT,
                    details_json TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_task_events_task_seq ON task_events(task_id, seq);
                CREATE INDEX IF NOT EXISTS idx_task_events_delivery_id ON task_events(delivery_id);

                CREATE TABLE IF NOT EXISTS task_states (
                    task_id TEXT PRIMARY KEY,
                    latest_seq INTEGER,
                    updated_at TEXT,
                    owner_agent TEXT,
                    lease_until TEXT,
                    heartbeat_at TEXT,
                    phase TEXT,
                    blocked_reason TEXT,
                    snapshot_json TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_task_states_phase ON task_states(phase);
                CREATE INDEX IF NOT EXISTS idx_task_states_updated_at ON task_states(updated_at);

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
                    provider TEXT NOT NULL DEFAULT 'kaggle',
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
                '''
            )
            conn.commit()

    def _table_empty(self, conn: sqlite3.Connection, table: str) -> bool:
        row = conn.execute(f'SELECT COUNT(*) AS c FROM {table}').fetchone()
        return not row or row['c'] == 0

    def _load_legacy_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        with path.open('r', encoding='utf-8') as handle:
            return json.load(handle)

    def _migrate_blob_store(self, conn: sqlite3.Connection) -> bool:
        tables = {r['name'] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if 'store_documents' not in tables:
            return False

        rows = conn.execute('SELECT store_key, payload_json FROM store_documents').fetchall()
        if not rows:
            return False

        payloads = {row['store_key']: json.loads(row['payload_json']) for row in rows}
        self._import_payloads(conn, payloads)
        return True

    def _migrate_legacy_json_files(self, conn: sqlite3.Connection) -> None:
        payloads = {
            'github_events.json': self._load_legacy_json(self.data_dir / 'github_events.json', {'events': []}),
            'task_snapshots.json': self._load_legacy_json(self.data_dir / 'task_snapshots.json', {'snapshots': {}}),
            'task_events.json': self._load_legacy_json(self.data_dir / 'task_events.json', {'next_seq': 1, 'events_by_task': {}}),
            'task_states.json': self._load_legacy_json(self.data_dir / 'task_states.json', {'tasks': {}}),
        }
        self._import_payloads(conn, payloads)

    def _import_payloads(self, conn: sqlite3.Connection, payloads: dict[str, Any]) -> None:
        if self._table_empty(conn, 'github_events'):
            for event in payloads.get('github_events.json', {}).get('events', []):
                conn.execute(
                    '''
                    INSERT OR IGNORE INTO github_events (
                        delivery_id, event_type, action, repo, issue_number, pr_number,
                        task_id, sender, received_at, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        event.get('delivery_id'), event.get('event_type'), event.get('action'), event.get('repo'),
                        event.get('issue_number'), event.get('pr_number'), event.get('task_id'), event.get('sender'),
                        event.get('received_at'), json.dumps(event.get('payload_json'), ensure_ascii=False),
                    ),
                )

        if self._table_empty(conn, 'task_snapshots'):
            for snapshot in payloads.get('task_snapshots.json', {}).get('snapshots', {}).values():
                conn.execute(
                    '''
                    INSERT OR REPLACE INTO task_snapshots (
                        task_id, issue_number, status, branch, pr_number,
                        last_commit_sha, review_state, last_summary, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        snapshot.get('task_id'), snapshot.get('issue_number'), snapshot.get('status'), snapshot.get('branch'),
                        snapshot.get('pr_number'), snapshot.get('last_commit_sha'), snapshot.get('review_state'),
                        snapshot.get('last_summary'), snapshot.get('updated_at'),
                    ),
                )

        if self._table_empty(conn, 'task_events'):
            seq_max = 0
            for task_id, events in payloads.get('task_events.json', {}).get('events_by_task', {}).items():
                for event in events:
                    seq = int(event.get('seq', 0) or 0)
                    seq_max = max(seq_max, seq)
                    conn.execute(
                        '''
                        INSERT OR IGNORE INTO task_events (
                            seq, task_id, repo, issue_number, pr_number, delivery_id,
                            event_type, action, sender, occurred_at, snapshot_json, task_state_json, details_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        (
                            seq, task_id, event.get('repo'), event.get('issue_number'), event.get('pr_number'),
                            event.get('delivery_id'), event.get('event_type'), event.get('action'), event.get('sender'),
                            event.get('occurred_at'), json.dumps(event.get('snapshot'), ensure_ascii=False),
                            json.dumps(event.get('task_state'), ensure_ascii=False),
                            json.dumps(event.get('details'), ensure_ascii=False),
                        ),
                    )
            if seq_max:
                conn.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'task_events'", (seq_max,))
                if conn.execute("SELECT changes()").fetchone()[0] == 0:
                    conn.execute("INSERT OR REPLACE INTO sqlite_sequence(name, seq) VALUES ('task_events', ?)", (seq_max,))

        if self._table_empty(conn, 'task_states'):
            for state in payloads.get('task_states.json', {}).get('tasks', {}).values():
                conn.execute(
                    '''
                    INSERT OR REPLACE INTO task_states (
                        task_id, latest_seq, updated_at, owner_agent, lease_until,
                        heartbeat_at, phase, blocked_reason, snapshot_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        state.get('task_id'), state.get('latest_seq'), state.get('updated_at'), state.get('owner_agent'),
                        state.get('lease_until'), state.get('heartbeat_at'), state.get('phase'), state.get('blocked_reason'),
                        json.dumps(state.get('snapshot'), ensure_ascii=False),
                    ),
                )

    def _migrate_if_needed(self) -> None:
        with self._lock:
            with self._connect() as conn:
                if not all(self._table_empty(conn, name) for name in ('github_events', 'task_snapshots', 'task_events', 'task_states')):
                    return
                migrated = self._migrate_blob_store(conn)
                if not migrated:
                    self._migrate_legacy_json_files(conn)
                conn.commit()

    def list_github_events(self, limit: int, task_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if task_id:
                rows = conn.execute(
                    'SELECT * FROM github_events WHERE task_id = ? ORDER BY received_at DESC LIMIT ?',
                    (task_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT * FROM github_events ORDER BY received_at DESC LIMIT ?',
                    (limit,),
                ).fetchall()
        return [self._row_to_github_event(row) for row in rows]

    def get_github_event(self, delivery_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM github_events WHERE delivery_id = ?', (delivery_id,)).fetchone()
        return self._row_to_github_event(row) if row else None

    def insert_github_event(self, event: dict[str, Any]) -> bool:
        with self._lock:
            with self._connect() as conn:
                cur = conn.execute(
                    '''
                    INSERT OR IGNORE INTO github_events (
                        delivery_id, event_type, action, repo, issue_number, pr_number,
                        task_id, sender, received_at, payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        event.get('delivery_id'), event.get('event_type'), event.get('action'), event.get('repo'),
                        event.get('issue_number'), event.get('pr_number'), event.get('task_id'), event.get('sender'),
                        event.get('received_at'), json.dumps(event.get('payload_json'), ensure_ascii=False),
                    ),
                )
                conn.commit()
                return cur.rowcount > 0

    def list_snapshots(self, task_id: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if task_id:
                rows = conn.execute('SELECT * FROM task_snapshots WHERE task_id = ? ORDER BY updated_at DESC', (task_id,)).fetchall()
            else:
                rows = conn.execute('SELECT * FROM task_snapshots ORDER BY updated_at DESC').fetchall()
        return [dict(row) for row in rows]

    def get_snapshot(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM task_snapshots WHERE task_id = ?', (task_id,)).fetchone()
        return dict(row) if row else None

    def upsert_snapshot(self, snapshot: dict[str, Any]) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''
                    INSERT INTO task_snapshots (
                        task_id, issue_number, status, branch, pr_number,
                        last_commit_sha, review_state, last_summary, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(task_id) DO UPDATE SET
                        issue_number = excluded.issue_number,
                        status = excluded.status,
                        branch = excluded.branch,
                        pr_number = excluded.pr_number,
                        last_commit_sha = excluded.last_commit_sha,
                        review_state = excluded.review_state,
                        last_summary = excluded.last_summary,
                        updated_at = excluded.updated_at
                    ''',
                    (
                        snapshot.get('task_id'), snapshot.get('issue_number'), snapshot.get('status'), snapshot.get('branch'),
                        snapshot.get('pr_number'), snapshot.get('last_commit_sha'), snapshot.get('review_state'),
                        snapshot.get('last_summary'), snapshot.get('updated_at'),
                    ),
                )
                conn.commit()

    def append_task_event(self, task_event: dict[str, Any] | None) -> tuple[bool, int]:
        if not task_event:
            return False, 0
        with self._lock:
            with self._connect() as conn:
                delivery_id = task_event.get('delivery_id')
                if delivery_id:
                    existing = conn.execute(
                        'SELECT seq FROM task_events WHERE task_id = ? AND delivery_id = ?',
                        (task_event['task_id'], delivery_id),
                    ).fetchone()
                    if existing:
                        return False, int(existing['seq'])
                cur = conn.execute(
                    '''
                    INSERT INTO task_events (
                        task_id, repo, issue_number, pr_number, delivery_id,
                        event_type, action, sender, occurred_at, snapshot_json, task_state_json, details_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        task_event.get('task_id'), task_event.get('repo'), task_event.get('issue_number'),
                        task_event.get('pr_number'), delivery_id, task_event.get('event_type'), task_event.get('action'),
                        task_event.get('sender'), task_event.get('occurred_at'),
                        json.dumps(task_event.get('snapshot'), ensure_ascii=False),
                        json.dumps(task_event.get('task_state'), ensure_ascii=False),
                        json.dumps(task_event.get('details'), ensure_ascii=False),
                    ),
                )
                conn.commit()
                return True, int(cur.lastrowid)

    def get_task_events(self, task_id: str, after_seq: int = 0) -> tuple[list[dict[str, Any]], int]:
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM task_events WHERE task_id = ? AND seq > ? ORDER BY seq ASC',
                (task_id, after_seq),
            ).fetchall()
            latest_row = conn.execute(
                'SELECT MAX(seq) AS max_seq FROM task_events WHERE task_id = ?',
                (task_id,),
            ).fetchone()
        latest_seq = int(latest_row['max_seq'] or 0)
        return [self._row_to_task_event(row) for row in rows], latest_seq

    def get_task_state(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM task_states WHERE task_id = ?', (task_id,)).fetchone()
        return self._row_to_task_state(row) if row else None

    def list_task_states(self, include_done: bool = False) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if include_done:
                rows = conn.execute('SELECT * FROM task_states ORDER BY updated_at DESC').fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM task_states WHERE phase IN ('working', 'blocked', 'released', 'stale') ORDER BY updated_at DESC"
                ).fetchall()
        return [self._row_to_task_state(row) for row in rows]

    def upsert_task_state(self, task_id: str, task_state: dict[str, Any]) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    '''
                    INSERT INTO task_states (
                        task_id, latest_seq, updated_at, owner_agent, lease_until,
                        heartbeat_at, phase, blocked_reason, snapshot_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(task_id) DO UPDATE SET
                        latest_seq = excluded.latest_seq,
                        updated_at = excluded.updated_at,
                        owner_agent = excluded.owner_agent,
                        lease_until = excluded.lease_until,
                        heartbeat_at = excluded.heartbeat_at,
                        phase = excluded.phase,
                        blocked_reason = excluded.blocked_reason,
                        snapshot_json = excluded.snapshot_json
                    ''',
                    (
                        task_id, task_state.get('latest_seq'), task_state.get('updated_at'), task_state.get('owner_agent'),
                        task_state.get('lease_until'), task_state.get('heartbeat_at'), task_state.get('phase'),
                        task_state.get('blocked_reason'), json.dumps(task_state.get('snapshot'), ensure_ascii=False),
                    ),
                )
                conn.commit()

    def get_dashboard_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            phase_counts = {
                row['phase']: row['count']
                for row in conn.execute(
                    'SELECT phase, COUNT(*) AS count FROM task_states GROUP BY phase'
                ).fetchall()
            }
            active_leases = [
                self._row_to_task_state(row)
                for row in conn.execute(
                    "SELECT * FROM task_states WHERE owner_agent IS NOT NULL ORDER BY updated_at DESC LIMIT 10"
                ).fetchall()
            ]
            stale_tasks = [
                self._row_to_task_state(row)
                for row in conn.execute(
                    "SELECT * FROM task_states WHERE phase = 'stale' ORDER BY updated_at DESC LIMIT 10"
                ).fetchall()
            ]
            recent_task_events = [
                self._row_to_task_event(row)
                for row in conn.execute(
                    'SELECT * FROM task_events ORDER BY seq DESC LIMIT 20'
                ).fetchall()
            ]
            recent_github_events = [
                self._row_to_github_event(row)
                for row in conn.execute(
                    'SELECT * FROM github_events ORDER BY received_at DESC LIMIT 20'
                ).fetchall()
            ]
        return {
            'phase_counts': phase_counts,
            'active_leases': active_leases,
            'stale_tasks': stale_tasks,
            'recent_task_events': recent_task_events,
            'recent_github_events': recent_github_events,
        }

    def list_tasks_for_admin(
        self,
        phase: str | None = None,
        owner: str | None = None,
        query: str | None = None,
        include_done: bool = False,
    ) -> list[dict[str, Any]]:
        clauses = []
        params: list[Any] = []
        if not include_done:
            clauses.append("phase IN ('working', 'blocked', 'released', 'stale')")
        if phase:
            clauses.append('phase = ?')
            params.append(phase)
        if owner:
            clauses.append('owner_agent = ?')
            params.append(owner)
        if query:
            clauses.append('task_id LIKE ?')
            params.append(f'%{query}%')
        sql = 'SELECT * FROM task_states'
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        sql += ' ORDER BY updated_at DESC'
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row_to_task_state(row) for row in rows]

    def get_task_detail(self, task_id: str) -> dict[str, Any] | None:
        state = self.get_task_state(task_id)
        if not state:
            return None
        snapshot = self.get_snapshot(task_id)
        events, latest_seq = self.get_task_events(task_id, after_seq=0)
        github_events = self.list_github_events(limit=50, task_id=task_id)
        return {
            'state': state,
            'snapshot': snapshot,
            'task_events': events,
            'github_events': github_events,
            'latest_seq': latest_seq,
        }

    def get_system_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            counts = {}
            for table in ('github_events', 'task_snapshots', 'task_events', 'task_states'):
                row = conn.execute(f'SELECT COUNT(*) AS c FROM {table}').fetchone()
                counts[table] = row['c'] if row else 0
            latest_github = conn.execute(
                'SELECT received_at FROM github_events ORDER BY received_at DESC LIMIT 1'
            ).fetchone()
            latest_task = conn.execute(
                'SELECT updated_at FROM task_states ORDER BY updated_at DESC LIMIT 1'
            ).fetchone()
        return {
            'db_path': str(self.db_path),
            'counts': counts,
            'latest_github_event_at': latest_github['received_at'] if latest_github else None,
            'latest_task_update_at': latest_task['updated_at'] if latest_task else None,
        }

    def _row_to_github_event(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'id': row['delivery_id'],
            'delivery_id': row['delivery_id'],
            'event_type': row['event_type'],
            'action': row['action'],
            'repo': row['repo'],
            'issue_number': row['issue_number'],
            'pr_number': row['pr_number'],
            'task_id': row['task_id'],
            'sender': row['sender'],
            'received_at': row['received_at'],
            'payload_json': json.loads(row['payload_json']) if row['payload_json'] else None,
        }

    def _row_to_task_event(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'seq': row['seq'],
            'task_id': row['task_id'],
            'repo': row['repo'],
            'issue_number': row['issue_number'],
            'pr_number': row['pr_number'],
            'delivery_id': row['delivery_id'],
            'event_type': row['event_type'],
            'action': row['action'],
            'sender': row['sender'],
            'occurred_at': row['occurred_at'],
            'snapshot': json.loads(row['snapshot_json']) if row['snapshot_json'] else None,
            'task_state': json.loads(row['task_state_json']) if row['task_state_json'] else None,
            'details': json.loads(row['details_json']) if row['details_json'] else {},
        }

    def _row_to_task_state(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            'task_id': row['task_id'],
            'latest_seq': row['latest_seq'],
            'updated_at': row['updated_at'],
            'owner_agent': row['owner_agent'],
            'lease_until': row['lease_until'],
            'heartbeat_at': row['heartbeat_at'],
            'phase': row['phase'],
            'blocked_reason': row['blocked_reason'],
            'snapshot': json.loads(row['snapshot_json']) if row['snapshot_json'] else None,
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
        set_clauses = []
        params: list[Any] = []
        for key, value in fields.items():
            if key == 'config':
                set_clauses.append('config_json = ?')
                params.append(json.dumps(value, ensure_ascii=False))
            else:
                set_clauses.append(f'{key} = ?')
                params.append(value)
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
        set_clauses = []
        params: list[Any] = []
        for key, value in fields.items():
            set_clauses.append(f'{key} = ?')
            params.append(value)
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
