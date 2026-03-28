"""agent-sync-service – FastAPI application entry point."""
from __future__ import annotations

from datetime import timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import shared
from app.config import get_settings
from app.helpers import _detect_version
from app.audio_jobs import recover_interrupted_jobs
from app.pipeline_runner import PIPELINE_DIR
from app.store import AgentSyncDB

# ── Settings & DB ─────────────────────────────────────────────────────────

settings = get_settings()
db = AgentSyncDB(settings.data_dir)

# ── Paths ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_ROOT = Path(__file__).resolve().parents[3] / 'docs'
HOUSE_TEMPLATES_PATH = BASE_DIR / 'data' / 'house_templates.json'

CET = timezone(timedelta(hours=1))
BERLIN_TZ = ZoneInfo('Europe/Berlin')

# ── Templates ─────────────────────────────────────────────────────────────

templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

# ── Populate shared state ────────────────────────────────────────────────

shared.db = db
shared.templates = templates
shared.settings = settings
shared.BASE_DIR = BASE_DIR
shared.PIPELINE_DIR = PIPELINE_DIR
shared.BERLIN_TZ = BERLIN_TZ
shared.CET = CET
shared.DOCS_ROOT = DOCS_ROOT
shared.HOUSE_TEMPLATES_PATH = HOUSE_TEMPLATES_PATH

# ── Version ───────────────────────────────────────────────────────────────

APP_VERSION = _detect_version()
shared.APP_VERSION = APP_VERSION
templates.env.globals['app_version'] = APP_VERSION

# ── Template helpers ──────────────────────────────────────────────────────

_INTERNAL_STATUS_MAP = {
    'waiting_for_audio': 'running',
    'uploading': 'running',
    'error': 'failed',
}

def _display_status(status: str) -> str:
    return _INTERNAL_STATUS_MAP.get(status, status)

templates.env.globals['display_status'] = _display_status
templates.env.filters['display_status'] = _display_status

# ── App ───────────────────────────────────────────────────────────────────

app = FastAPI(title='Whisper Studio')

# ── Static files ──────────────────────────────────────────────────────────

app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

# Background images from data/assets/backgrounds
_bg_dir = BASE_DIR.parent.parent / 'data' / 'assets' / 'backgrounds'
if _bg_dir.exists():
    app.mount('/static/backgrounds', StaticFiles(directory=str(_bg_dir)), name='backgrounds')

# ── Router includes ──────────────────────────────────────────────────────

from app.routes.health import router as health_router          # noqa: E402
from app.routes.dashboard import router as dashboard_router    # noqa: E402
from app.routes.ops import router as ops_router                # noqa: E402
from app.routes.audio import router as audio_router            # noqa: E402
from app.routes.pipeline import router as pipeline_router      # noqa: E402
from app.routes.library import router as library_router        # noqa: E402
from app.routes.docs import router as docs_router              # noqa: E402
from app.routes.shorts import router as shorts_router          # noqa: E402
from app.routes.tickets import router as tickets_router        # noqa: E402
from app.routes.workflows import router as workflows_router    # noqa: E402
from app.routes.gpu import router as gpu_router                # noqa: E402
from app.routes.settings import router as settings_router      # noqa: E402
from app.routes.auth import router as auth_router              # noqa: E402

# ── Auth middleware (opt-in via AUTH_ENABLED=1 env var) ────────────────────
import os as _os_auth                                          # noqa: E402
AUTH_ENABLED = _os_auth.environ.get('AUTH_ENABLED', '1') == '1'

if AUTH_ENABLED:
    from starlette.middleware.base import BaseHTTPMiddleware        # noqa: E402
    from starlette.responses import RedirectResponse as StarletteRedirect  # noqa: E402
    from app.auth import get_current_user, ensure_admin_exists     # noqa: E402

    PUBLIC_PATHS = {'/login', '/static', '/health', '/api/gpu/metrics', '/api/'}

    class AuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            path = request.url.path
            # Allow public paths
            if any(path.startswith(p) for p in PUBLIC_PATHS):
                return await call_next(request)
            # Allow all API calls (JSON endpoints used by agents/scripts)
            if '/api/' in path:
                return await call_next(request)
            # Allow non-GET requests (form posts, API calls from agents)
            # Only browser GET requests to /admin need login
            if request.method != 'GET' and path.startswith('/admin'):
                # Try to set user if available, but don't block
                user = get_current_user(request)
                if user:
                    request.state.user = user
                return await call_next(request)
            if path.startswith('/admin'):
                user = get_current_user(request)
                if not user:
                    return StarletteRedirect(url='/login', status_code=302)
                request.state.user = user
            return await call_next(request)

    app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(dashboard_router)
app.include_router(ops_router)
app.include_router(audio_router)
app.include_router(pipeline_router)
app.include_router(library_router)
app.include_router(docs_router)
app.include_router(shorts_router)
app.include_router(tickets_router)
app.include_router(workflows_router)
app.include_router(gpu_router)
app.include_router(settings_router)

# ── Startup ──────────────────────────────────────────────────────────────

from app.pipeline_queue import _ensure_worker, recover_interrupted_workflows  # noqa: E402
from app.workflow_orchestrator import _ensure_poll_thread  # noqa: E402

if AUTH_ENABLED:
    ensure_admin_exists()

# ── Recover jobs/workflows interrupted by restarts ────────────────────────
import os as _os
if _os.environ.get('SKIP_RECOVERY') != '1':
    _recovered_audio = recover_interrupted_jobs(db)
    _recovered_workflows = recover_interrupted_workflows(db)
    if _recovered_audio or _recovered_workflows:
        print(f'[startup] Recovered {_recovered_audio} audio jobs, {_recovered_workflows} workflows after restart.')
else:
    print('[startup] Recovery skipped (SKIP_RECOVERY=1)')

_ensure_worker(db)
_ensure_poll_thread(db)
