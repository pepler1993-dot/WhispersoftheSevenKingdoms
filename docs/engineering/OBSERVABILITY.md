# B07 – Observability Minimum

> Ticket: #143
> Status: Draft
> Scope: Structured logging, health checks, error tracking, basic metrics

---

## 1. Structured Logging

All log output MUST use JSON format for machine parseability.

### Log Schema

```json
{
  "timestamp": "2026-03-29T11:00:00.000Z",
  "level": "info",
  "module": "workflow_runner",
  "message": "Workflow started",
  "context": {
    "workflow_id": "abc-123",
    "slug": "episode-42",
    "phase": "render"
  }
}
```

### Fields

| Field       | Type   | Required | Description                              |
|-------------|--------|----------|------------------------------------------|
| `timestamp` | string | ✅       | ISO 8601 UTC                             |
| `level`     | string | ✅       | `debug`, `info`, `warning`, `error`, `critical` |
| `module`    | string | ✅       | Python module or logical component name  |
| `message`   | string | ✅       | Human-readable description               |
| `context`   | object | ❌       | Arbitrary key-value pairs for correlation |

### Implementation

Use Python's `logging` with a JSON formatter. Recommended: `python-json-logger`.

```python
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(timestamp)s %(level)s %(module)s %(message)s",
    rename_fields={"levelname": "level", "created": "timestamp"},
    datefmt="%Y-%m-%dT%H:%M:%S.%fZ",
)
handler.setFormatter(formatter)
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)
```

### Rules

- **No** `print()` statements in production code — use `logging.*`.
- Always include `workflow_id` or `job_id` in context when available.
- Log at `error` level only for actionable failures; use `warning` for degraded states.

---

## 2. Health Checks

### Current State

The existing `health.py` provides two endpoints:

| Endpoint               | Purpose                                    |
|------------------------|--------------------------------------------|
| `GET /healthz`         | Simple liveness probe — returns `{"status": "ok"}` unconditionally |
| `GET /api/health/overview` | Dashboard-oriented overview: GPU worker status, queue depths, upload success rate, pipeline health, last publish info |

**What works well:**
- GPU worker health is checked via `get_audio_generator_health()` (availability, GPU name, daemon status).
- Queue health is derived from workflow statuses (running/queued/failed counts).
- Upload health tracks recent success rate.

**What's missing:**
- No actual liveness/readiness distinction — `/healthz` always returns ok even if DB is dead.
- No disk space check (critical for a video/audio pipeline).
- No structured response codes (always 200).

### Expanded Health Checks

Extend `/healthz` into a proper readiness probe and add component checks:

#### 2.1 DB Connectivity

```python
def check_db() -> dict:
    try:
        shared.db._connect().execute("SELECT 1").fetchone()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### 2.2 GPU Worker Reachability

Already partially implemented via `get_audio_generator_health()`. Wrap in standard format:

```python
def check_gpu() -> dict:
    try:
        gpu = get_audio_generator_health()
        if gpu.get("available"):
            return {"status": "healthy", "gpu": gpu.get("gpu")}
        return {"status": "offline", "daemon": gpu.get("daemon", False)}
    except Exception:
        return {"status": "unreachable"}
```

#### 2.3 Disk Space

```python
import shutil

def check_disk(threshold_gb: float = 5.0) -> dict:
    usage = shutil.disk_usage("/")
    free_gb = usage.free / (1024 ** 3)
    return {
        "status": "healthy" if free_gb > threshold_gb else "critical",
        "free_gb": round(free_gb, 1),
        "total_gb": round(usage.total / (1024 ** 3), 1),
    }
```

#### 2.4 Active Jobs Count

```python
def check_jobs() -> dict:
    workflows = shared.db.list_workflows(limit=100)
    running = sum(1 for w in workflows if w["status"] in ("running", "uploading", "waiting_for_audio"))
    queued = sum(1 for w in workflows if w["status"] == "queued")
    return {"status": "healthy", "running": running, "queued": queued}
```

#### 2.5 Combined Readiness Endpoint

```python
@router.get("/readyz")
def readyz() -> dict:
    checks = {
        "db": check_db(),
        "gpu": check_gpu(),
        "disk": check_disk(),
        "jobs": check_jobs(),
    }
    all_healthy = all(c["status"] in ("healthy", "offline") for c in checks.values())
    # Disk critical = not ready
    if checks["disk"]["status"] == "critical":
        all_healthy = False
    status_code = 200 if all_healthy else 503
    return JSONResponse(
        content={"status": "ready" if all_healthy else "not_ready", "checks": checks},
        status_code=status_code,
    )
```

> **Note:** GPU being `offline` does NOT make the service unready — the sync API itself still functions. Only DB and disk are hard dependencies.

---

## 3. Error Tracking

### Error Categories

| Category        | Examples                                 | Severity |
|-----------------|------------------------------------------|----------|
| `db_error`      | SQLite lock timeout, corruption          | critical |
| `gpu_error`     | Worker unreachable, OOM on GPU           | high     |
| `render_error`  | FFmpeg crash, missing assets             | high     |
| `upload_error`  | YouTube API failure, auth expired        | medium   |
| `audio_error`   | Generation timeout, model load failure   | medium   |
| `validation`    | Bad request payload, missing slug        | low      |

### Log Aggregation Strategy

**Phase 1 (now):** Structured JSON logs → file rotation → `grep`/`jq` for investigation.

**Phase 2 (later):** Ship logs to a lightweight aggregator:
- Option A: Loki + Grafana (self-hosted, works well with JSON logs)
- Option B: SQLite-based local log DB (ultra-lightweight, query with SQL)

### Error Context

Every error log MUST include:
```json
{
  "level": "error",
  "module": "workflow_runner",
  "message": "Render failed",
  "context": {
    "workflow_id": "abc-123",
    "error_category": "render_error",
    "error_type": "FFmpegCrash",
    "attempt": 2,
    "max_retries": 3
  }
}
```

---

## 4. Basic Metrics

### Key Metrics

| Metric              | Type      | Source                          |
|----------------------|-----------|---------------------------------|
| `request_count`      | counter   | FastAPI middleware               |
| `job_duration_seconds` | histogram | Workflow start→finish delta   |
| `error_rate`         | gauge     | Errors / total requests (1min)  |
| `gpu_utilization`    | gauge     | GPU health endpoint polling     |

### Implementation Approach

**Phase 1:** Expose a `/metrics` endpoint with simple JSON counters (no Prometheus dependency yet).

```python
from collections import defaultdict
from time import time

_metrics = {
    "requests_total": defaultdict(int),  # keyed by path
    "errors_total": 0,
    "jobs_completed": 0,
    "job_duration_sum": 0.0,
    "job_duration_count": 0,
}

@router.get("/metrics")
def metrics():
    return {
        "requests_total": dict(_metrics["requests_total"]),
        "errors_total": _metrics["errors_total"],
        "jobs_completed": _metrics["jobs_completed"],
        "avg_job_duration_s": (
            round(_metrics["job_duration_sum"] / max(_metrics["job_duration_count"], 1), 1)
        ),
    }
```

**Phase 2:** Prometheus client library (`prometheus_client`) with proper histogram buckets.

### Middleware for Request Counting

```python
@app.middleware("http")
async def metrics_middleware(request, call_next):
    _metrics["requests_total"][request.url.path] += 1
    response = await call_next(request)
    if response.status_code >= 500:
        _metrics["errors_total"] += 1
    return response
```

---

## 5. Implementation Priority

| Priority | Task                              | Effort | Impact |
|----------|-----------------------------------|--------|--------|
| **P0**   | Structured JSON logging           | 2h     | High — enables everything else |
| **P0**   | `/readyz` with DB + disk checks   | 2h     | High — catch outages early     |
| **P1**   | Error categories in log context   | 1h     | Medium — faster debugging      |
| **P1**   | Request count middleware           | 1h     | Medium — baseline visibility   |
| **P2**   | `/metrics` endpoint               | 2h     | Medium — operational insight   |
| **P2**   | Job duration tracking             | 1h     | Medium — performance baseline  |
| **P3**   | Log aggregation (Loki or SQLite)  | 4h+    | Low initially — grows with scale |
| **P3**   | Prometheus integration            | 3h     | Low initially — overkill for now |

### Recommended Order

1. **JSON logging** — switch all modules to structured output
2. **`/readyz` endpoint** — replace blind `/healthz` with real checks
3. **Error categories** — tag errors for filtering
4. **Request middleware** — count and time requests
5. **`/metrics`** — expose counters for dashboards
6. **Log aggregation** — once volume justifies it
