"""
Shared test fixtures for Whispers of the Seven Kingdoms.

Rules:
- Never access prod DB or prod file paths.
- All DB fixtures use tmp_path with a fresh AgentSyncDB instance.
- Fixtures are deterministic and minimal.
"""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Make sure services/sync is importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SYNC_PATH = _REPO_ROOT / "services" / "sync"
if str(_SYNC_PATH) not in sys.path:
    sys.path.insert(0, str(_SYNC_PATH))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _wf_id() -> str:
    return uuid.uuid4().hex[:12]


def _job_id() -> str:
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# DB Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def db(tmp_path):
    """Fresh AgentSyncDB instance for each test (isolated tmp_path)."""
    from app.store import AgentSyncDB
    return AgentSyncDB(data_dir=tmp_path / "db")


# ---------------------------------------------------------------------------
# House Templates Fixture
# ---------------------------------------------------------------------------

HOUSE_TEMPLATES_FIXTURE: dict = {
    "stark": {
        "display_name": "House Stark",
        "house": "stark",
        "prompt_base": "cold northern winds, wolves howling, grey stone castle",
        "theme": "north",
        "variants": {
            "sleep": "gentle snowfall, ambient northern lights",
            "epic": "battle drums, howling blizzard",
        },
    },
    "lannister": {
        "display_name": "House Lannister",
        "house": "lannister",
        "prompt_base": "golden halls, lion roars distant, royal fanfare",
        "theme": "gold",
        "variants": {
            "sleep": "soft harp in stone corridors, distant fire crackling",
            "epic": "war horns, marching armies, orchestral swells",
        },
    },
    "targaryen": {
        "display_name": "House Targaryen",
        "house": "targaryen",
        "prompt_base": "dragon wings, volcanic heat, ancient power",
        "theme": "fire",
        "variants": {
            "sleep": "warm embers, soft dragon breathing, mystic ambient",
            "epic": "dragon roars, fire and chaos, epic orchestral",
        },
    },
}


@pytest.fixture()
def house_templates_file(tmp_path) -> Path:
    """Write minimal house_templates.json to tmp_path, return Path."""
    p = tmp_path / "house_templates.json"
    p.write_text(json.dumps(HOUSE_TEMPLATES_FIXTURE), encoding="utf-8")
    return p


@pytest.fixture()
def house_templates() -> dict:
    """Return house templates dict directly (no file I/O)."""
    return HOUSE_TEMPLATES_FIXTURE.copy()


# ---------------------------------------------------------------------------
# Scenario 1: Video workflow – created → uploaded (happy path)
# ---------------------------------------------------------------------------

@pytest.fixture()
def workflow_video_uploaded(db):
    """
    A complete video workflow: House Stark, sleep variant, uploaded to YouTube.
    Status: uploaded
    """
    wf_id = _wf_id()
    now = _now_iso()
    db.create_workflow({
        "workflow_id": wf_id,
        "type": "video",
        "slug": "stark-sleep-test-3-hours",
        "title": "House Stark Sleep Music – 3 Hours",
        "status": "uploaded",
        "phase": "done",
        "config": {
            "house_key": "stark",
            "variant_key": "sleep",
            "duration_minutes": 180,
            "visual_mode": "static-artwork",
            "auto_upload": False,
            "visibility": "public",
        },
        "created_at": now,
    })
    return db.get_workflow(wf_id)


# ---------------------------------------------------------------------------
# Scenario 2: Short workflow – currently rendering (in-progress)
# ---------------------------------------------------------------------------

@pytest.fixture()
def workflow_short_rendering(db):
    """
    A short workflow currently rendering.
    Status: running
    """
    wf_id = _wf_id()
    now = _now_iso()
    db.create_workflow({
        "workflow_id": wf_id,
        "type": "short",
        "slug": "stark-short-hook",
        "title": "House Stark – Short Hook",
        "status": "running",
        "phase": "render",
        "config": {
            "source_audio": "stark-sleep-test.mp3",
            "clip_start_seconds": 30,
            "clip_duration_seconds": 45,
            "visual_mode": "blurred-background",
            "visibility": "private",
            "content_type": "short",
        },
        "created_at": now,
    })
    return db.get_workflow(wf_id)


# ---------------------------------------------------------------------------
# Scenario 3: Audio job – failed (error state)
# ---------------------------------------------------------------------------

@pytest.fixture()
def audio_job_failed(db):
    """
    An audio job that has failed with an error message.
    Status: error
    """
    job_id = _job_id()
    now = _now_iso()
    db.create_audio_job({
        "job_id": job_id,
        "slug": "lannister-epic-fail",
        "title": "House Lannister Epic (failed)",
        "provider": "stable-audio-local",
        "preset_name": "epic",
        "prompts": ["golden halls, lion roars, war horns"],
        "minutes": 60,
        "model": "stable-audio-open-1.0",
        "clip_seconds": 44,
        "status": "error",
        "error_message": "GPU out of memory",
        "created_at": now,
    })
    return db.get_audio_job(job_id)


# ---------------------------------------------------------------------------
# Scenario 4: Freshly created workflow (draft, no action yet)
# ---------------------------------------------------------------------------

@pytest.fixture()
def workflow_video_created(db):
    """
    A brand new video workflow, just created, not yet rendered.
    Status: created
    """
    wf_id = _wf_id()
    now = _now_iso()
    db.create_workflow({
        "workflow_id": wf_id,
        "type": "video",
        "slug": "targaryen-ambient-new",
        "title": "House Targaryen Ambient – New",
        "status": "created",
        "phase": "render",
        "config": {
            "house_key": "targaryen",
            "variant_key": "sleep",
            "duration_minutes": 120,
            "visual_mode": "cinematic-gradient",
            "auto_upload": False,
            "visibility": "private",
        },
        "created_at": now,
    })
    return db.get_workflow(wf_id)
