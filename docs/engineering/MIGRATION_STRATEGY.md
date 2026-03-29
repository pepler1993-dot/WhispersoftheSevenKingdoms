# B08 – Migrationsstrategie

> Ticket: #144
> Status: Draft
> Scope: Database schema migration approach for SQLite

---

## 1. Current State

### Storage Layer

The application uses **SQLite** via `AgentSyncDB` in `services/sync/app/store.py`.

### Schema Management Today

- **`_init_db()`** — Creates all tables with `CREATE TABLE IF NOT EXISTS`. The full schema is defined inline as a single `executescript()` call. Tables: `workflows`, `workflow_logs`, `audio_jobs`, `audio_job_logs`, plus indexes.
- **`_rename_legacy_tables()`** — Renames old table names to current ones (one-time migration from earlier naming).
- **`_migrate_legacy_tables()`** — Adds missing columns to existing tables with `ALTER TABLE ... ADD COLUMN` wrapped in try/except (ignores "duplicate column" errors).
- **`_fix_workflow_types()`** — Data migration: sets `type='video'` where NULL.
- **`_integrity_check()`** — Runs `PRAGMA integrity_check` on startup.

### Problems

1. **No version tracking** — impossible to know which migrations have run.
2. **Silent failures** — `ALTER TABLE` errors are caught and ignored; no distinction between "already applied" and "actual error".
3. **No rollback** — if a migration breaks, manual intervention required.
4. **Monolithic schema** — entire schema in one function; hard to review changes over time.
5. **No migration history** — git blame on `store.py` is the only audit trail.

---

## 2. Migration Approach

### Numbered Migration Files

```
migrations/
├── 001_initial_schema.sql
├── 002_add_workflow_type.sql
├── 003_add_audio_model_field.sql
└── ...
```

### File Format

Each migration file contains two sections separated by a marker:

```sql
-- Migration: 001_initial_schema
-- Description: Create initial tables
-- Date: 2026-03-29

-- === UP ===

CREATE TABLE IF NOT EXISTS workflows (
    workflow_id TEXT PRIMARY KEY,
    slug TEXT NOT NULL,
    title TEXT,
    status TEXT NOT NULL DEFAULT 'created',
    created_at TEXT NOT NULL
);

-- === DOWN ===

DROP TABLE IF EXISTS workflows;
```

### Naming Convention

```
{NNN}_{snake_case_description}.sql
```

- `NNN` — zero-padded sequence number (001, 002, ...)
- Description — short, descriptive, no spaces

---

## 3. Version Tracking

### Schema Migrations Table

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,   -- migration number (1, 2, 3...)
    name        TEXT NOT NULL,          -- filename without extension
    applied_at  TEXT NOT NULL,          -- ISO 8601 timestamp
    checksum    TEXT NOT NULL           -- SHA-256 of the UP section
);
```

### How It Works

1. On startup, read all files from `migrations/` directory.
2. Query `schema_migrations` for already-applied versions.
3. Run unapplied migrations in order, within a transaction per migration.
4. Insert row into `schema_migrations` after each successful migration.
5. If a migration fails, the transaction rolls back and startup aborts with a clear error.

---

## 4. Rollback Strategy

### Per-Migration Rollback

Each migration file contains a `DOWN` section. Rollback executes the DOWN section and removes the row from `schema_migrations`.

### Rollback Rules

| Scenario                  | Strategy                                      |
|---------------------------|-----------------------------------------------|
| Migration failed mid-apply | Automatic — transaction rollback              |
| Need to undo last migration | `python -m app.migrate rollback`             |
| Need to undo N migrations  | `python -m app.migrate rollback --steps N`   |
| Corrupted DB               | Restore from backup (existing backup system)  |

### SQLite Limitations

SQLite does NOT support:
- `DROP COLUMN` (before 3.35.0)
- `ALTER COLUMN` / `RENAME COLUMN` (limited support)

For destructive column changes, the DOWN section must use the **recreate pattern**:
```sql
-- === DOWN ===
-- Remove 'new_column' from workflows
CREATE TABLE workflows_backup AS SELECT workflow_id, slug, title, status, created_at FROM workflows;
DROP TABLE workflows;
ALTER TABLE workflows_backup RENAME TO workflows;
```

---

## 5. Tool Decision

### Recommendation: Lightweight Custom Runner

**Why not Alembic/other ORMs:**
- SQLite is the only backend — no multi-DB abstraction needed.
- Schema is simple (~4 tables) — full ORM tooling is overkill.
- No SQLAlchemy dependency in the project — adding it just for migrations adds complexity.
- The team needs to understand exactly what runs — plain SQL is transparent.

**The custom runner** is ~80 lines of Python:

```python
# app/migrate.py (sketch)
import hashlib
import re
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"

def _parse_migration(path: Path) -> tuple[str, str]:
    """Split a migration file into UP and DOWN sections."""
    content = path.read_text()
    parts = re.split(r"--\s*===\s*DOWN\s*===", content, maxsplit=1)
    up = re.split(r"--\s*===\s*UP\s*===", parts[0], maxsplit=1)[-1].strip()
    down = parts[1].strip() if len(parts) > 1 else ""
    return up, down

def _checksum(sql: str) -> str:
    return hashlib.sha256(sql.encode()).hexdigest()[:16]

def migrate(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL,
            checksum TEXT NOT NULL
        )
    """)

    applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = int(path.name.split("_")[0])
        if version in applied:
            continue

        up, _down = _parse_migration(path)
        checksum = _checksum(up)

        try:
            conn.executescript(up)
            conn.execute(
                "INSERT INTO schema_migrations (version, name, applied_at, checksum) VALUES (?, ?, datetime('now'), ?)",
                (version, path.stem, checksum),
            )
            conn.commit()
            print(f"  ✅ Applied: {path.name}")
        except Exception as e:
            print(f"  ❌ Failed: {path.name} — {e}")
            raise

def rollback(db_path: str, steps: int = 1) -> None:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT version, name FROM schema_migrations ORDER BY version DESC LIMIT ?",
        (steps,),
    ).fetchall()

    for version, name in rows:
        path = MIGRATIONS_DIR / f"{name}.sql"
        _up, down = _parse_migration(path)
        if not down:
            raise RuntimeError(f"No DOWN section in {path.name} — cannot rollback")
        conn.executescript(down)
        conn.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
        conn.commit()
        print(f"  ↩️  Rolled back: {path.name}")
```

### Path to Alembic

If any of these become true, switch to Alembic:
- A second database backend is added (PostgreSQL, MySQL).
- SQLAlchemy models are introduced for the ORM layer.
- The team grows and needs auto-generated migrations from model diffs.
- Migration count exceeds ~50 and manual management becomes painful.

The migration file format is compatible — Alembic migration can read the `schema_migrations` table to understand current state.

---

## 6. Migration Testing

### Requirements

| Test                          | Description                                          |
|-------------------------------|------------------------------------------------------|
| **Fresh install**             | Run all migrations on empty DB — must succeed         |
| **Idempotency**              | Run `migrate()` twice — second run is a no-op         |
| **Rollback completeness**    | Every UP has a matching DOWN that actually works       |
| **Round-trip**               | Apply → rollback → re-apply must produce same schema  |
| **Data preservation**        | Migrations must not silently drop user data            |
| **Checksum integrity**       | Changing an already-applied migration raises an error  |

### Test Pattern

```python
# tests/test_migrations.py
import sqlite3, tempfile
from app.migrate import migrate, rollback

def test_fresh_install():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        migrate(f.name)
        conn = sqlite3.connect(f.name)
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        assert "workflows" in tables
        assert "schema_migrations" in tables

def test_idempotent():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        migrate(f.name)
        migrate(f.name)  # no error

def test_rollback_roundtrip():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        migrate(f.name)
        conn = sqlite3.connect(f.name)
        count = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        rollback(f.name, steps=count)
        remaining = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        assert remaining == 0
        migrate(f.name)  # re-apply all
```

---

## 7. Example Migration

### `001_initial_schema.sql`

```sql
-- Migration: 001_initial_schema
-- Description: Establish base tables (matches current _init_db output)
-- Date: 2026-03-29

-- === UP ===

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

-- === DOWN ===

DROP TABLE IF EXISTS audio_job_logs;
DROP TABLE IF EXISTS audio_jobs;
DROP TABLE IF EXISTS workflow_logs;
DROP TABLE IF EXISTS workflows;
```

### `002_add_workflow_priority.sql` (hypothetical future)

```sql
-- Migration: 002_add_workflow_priority
-- Description: Add priority field to workflows for queue ordering
-- Date: 2026-04-01

-- === UP ===

ALTER TABLE workflows ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_workflows_priority ON workflows(priority);

-- === DOWN ===

DROP INDEX IF EXISTS idx_workflows_priority;
-- SQLite <3.35 cannot DROP COLUMN; recreate table approach:
CREATE TABLE workflows_backup AS SELECT
    workflow_id, type, slug, title, phase, status, audio_job_id,
    config_json, auto_upload, pid, started_at, finished_at,
    error_message, created_at, updated_at
FROM workflows;
DROP TABLE workflows;
ALTER TABLE workflows_backup RENAME TO workflows;
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at);
CREATE INDEX IF NOT EXISTS idx_workflows_type ON workflows(type);
```

---

## 8. Transition Plan

1. **Create `migrations/` directory** and `001_initial_schema.sql`.
2. **Implement `app/migrate.py`** (~80 lines, as sketched above).
3. **Bootstrap existing DBs:** On first run, detect existing tables → insert `001` into `schema_migrations` without re-running it.
4. **Replace `_init_db()` / `_migrate_legacy_tables()`** with a single `migrate()` call in `AgentSyncDB.__init__()`.
5. **Add migration tests** to CI.
6. **All future schema changes** go through numbered migration files — no more inline DDL.
