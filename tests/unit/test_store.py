"""
Unit tests for services/sync/app/store.py (AgentSyncDB)

Tests CRUD for workflows and audio jobs.
Uses fixtures from tests/fixtures/conftest.py (tmp_path, isolated DB).
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Make services/sync importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SYNC_PATH = _REPO_ROOT / "services" / "sync"
if str(_SYNC_PATH) not in sys.path:
    sys.path.insert(0, str(_SYNC_PATH))

# Import fixtures from shared conftest
sys.path.insert(0, str(_REPO_ROOT / "tests" / "fixtures"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id() -> str:
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Workflow CRUD
# ---------------------------------------------------------------------------

class TestWorkflowCRUD:
    def test_create_and_get(self, db):
        wf_id = _id()
        db.create_workflow({
            "workflow_id": wf_id,
            "type": "video",
            "slug": "test-slug",
            "title": "Test Workflow",
            "status": "created",
            "phase": "render",
            "config": {"house_key": "stark"},
            "created_at": _now(),
        })
        wf = db.get_workflow(wf_id)
        assert wf is not None
        assert wf["workflow_id"] == wf_id
        assert wf["slug"] == "test-slug"
        assert wf["status"] == "created"
        assert wf["config"]["house_key"] == "stark"

    def test_get_nonexistent_returns_none(self, db):
        assert db.get_workflow("does-not-exist") is None

    def test_update_status(self, db):
        wf_id = _id()
        db.create_workflow({
            "workflow_id": wf_id,
            "type": "video",
            "slug": "update-test",
            "title": "Update Test",
            "status": "created",
            "phase": "render",
            "created_at": _now(),
        })
        db.update_workflow(wf_id, status="rendered")
        wf = db.get_workflow(wf_id)
        assert wf["status"] == "rendered"

    def test_list_workflows(self, db):
        for i in range(3):
            db.create_workflow({
                "workflow_id": _id(),
                "type": "video",
                "slug": f"slug-{i}",
                "title": f"WF {i}",
                "status": "created",
                "phase": "render",
                "created_at": _now(),
            })
        result = db.list_workflows(limit=10)
        assert len(result) >= 3

    def test_list_workflows_by_type(self, db):
        video_id = _id()
        short_id = _id()
        db.create_workflow({
            "workflow_id": video_id, "type": "video", "slug": "v1",
            "title": "Video", "status": "created", "phase": "render", "created_at": _now(),
        })
        db.create_workflow({
            "workflow_id": short_id, "type": "short", "slug": "s1",
            "title": "Short", "status": "created", "phase": "render", "created_at": _now(),
        })
        videos = db.list_workflows(type="video")
        shorts = db.list_workflows(type="short")
        assert all(w["type"] == "video" for w in videos)
        assert all(w["type"] == "short" for w in shorts)

    def test_config_preserved_roundtrip(self, db):
        wf_id = _id()
        config = {
            "house_key": "targaryen",
            "variant_key": "epic",
            "duration_minutes": 180,
            "visual_mode": "cinematic-gradient",
        }
        db.create_workflow({
            "workflow_id": wf_id, "type": "video", "slug": "config-test",
            "title": "Config Test", "status": "created", "phase": "render",
            "config": config, "created_at": _now(),
        })
        wf = db.get_workflow(wf_id)
        assert wf["config"] == config

    def test_fixture_workflow_video_uploaded(self, workflow_video_uploaded):
        """Fixture scenario 1: uploaded video workflow."""
        wf = workflow_video_uploaded
        assert wf["status"] == "uploaded"
        assert wf["type"] == "video"
        assert wf["config"]["house_key"] == "stark"

    def test_fixture_workflow_short_rendering(self, workflow_short_rendering):
        """Fixture scenario 2: short in rendering."""
        wf = workflow_short_rendering
        assert wf["status"] == "running"
        assert wf["type"] == "short"

    def test_fixture_workflow_video_created(self, workflow_video_created):
        """Fixture scenario 4: fresh draft."""
        wf = workflow_video_created
        assert wf["status"] == "created"
        assert wf["config"]["house_key"] == "targaryen"


# ---------------------------------------------------------------------------
# Workflow Logs
# ---------------------------------------------------------------------------

class TestWorkflowLogs:
    def test_append_and_get_logs(self, db):
        wf_id = _id()
        db.create_workflow({
            "workflow_id": wf_id, "type": "video", "slug": "log-test",
            "title": "Log Test", "status": "running", "phase": "render",
            "created_at": _now(),
        })
        db.append_workflow_log(wf_id, "stdout", "Starting render...", _now())
        db.append_workflow_log(wf_id, "stdout", "Render done.", _now())
        logs = db.get_workflow_logs(wf_id)
        assert len(logs) == 2
        assert logs[0]["message"] == "Starting render..."
        assert logs[1]["stream"] == "stdout"

    def test_logs_empty_for_new_workflow(self, db):
        wf_id = _id()
        db.create_workflow({
            "workflow_id": wf_id, "type": "video", "slug": "no-logs",
            "title": "No Logs", "status": "created", "phase": "render",
            "created_at": _now(),
        })
        assert db.get_workflow_logs(wf_id) == []

    def test_logs_after_id(self, db):
        wf_id = _id()
        db.create_workflow({
            "workflow_id": wf_id, "type": "video", "slug": "paginated",
            "title": "Paginated", "status": "running", "phase": "render",
            "created_at": _now(),
        })
        db.append_workflow_log(wf_id, "stdout", "line 1", _now())
        db.append_workflow_log(wf_id, "stdout", "line 2", _now())
        all_logs = db.get_workflow_logs(wf_id)
        first_id = all_logs[0]["id"]
        paginated = db.get_workflow_logs(wf_id, after_id=first_id)
        assert len(paginated) == 1
        assert paginated[0]["message"] == "line 2"


# ---------------------------------------------------------------------------
# Audio Job CRUD
# ---------------------------------------------------------------------------

class TestAudioJobCRUD:
    def test_create_and_get(self, db):
        job_id = _id()
        db.create_audio_job({
            "job_id": job_id,
            "slug": "stark-sleep",
            "title": "Stark Sleep",
            "provider": "stable-audio-local",
            "preset_name": "sleep",
            "prompts": ["cold winds, wolves"],
            "minutes": 60,
            "model": "stable-audio-open-1.0",
            "clip_seconds": 44,
            "status": "queued",
            "created_at": _now(),
        })
        job = db.get_audio_job(job_id)
        assert job is not None
        assert job["job_id"] == job_id
        assert job["slug"] == "stark-sleep"
        assert job["status"] == "queued"

    def test_get_nonexistent_returns_none(self, db):
        assert db.get_audio_job("nonexistent") is None

    def test_update_status_to_complete(self, db):
        job_id = _id()
        db.create_audio_job({
            "job_id": job_id, "slug": "test-job", "title": "Test",
            "provider": "stable-audio-local", "prompts": [],
            "minutes": 30, "model": "stable-audio-open-1.0",
            "clip_seconds": 30, "status": "queued", "created_at": _now(),
        })
        db.update_audio_job(job_id, status="complete", output_path="/mnt/data/output/test.wav")
        job = db.get_audio_job(job_id)
        assert job["status"] == "complete"
        assert job["output_path"] == "/mnt/data/output/test.wav"

    def test_update_status_to_error(self, db):
        job_id = _id()
        db.create_audio_job({
            "job_id": job_id, "slug": "fail-job", "title": "Fail",
            "provider": "stable-audio-local", "prompts": [],
            "minutes": 30, "model": "stable-audio-open-1.0",
            "clip_seconds": 30, "status": "queued", "created_at": _now(),
        })
        db.update_audio_job(job_id, status="error", error_message="GPU OOM")
        job = db.get_audio_job(job_id)
        assert job["status"] == "error"
        assert job["error_message"] == "GPU OOM"

    def test_list_audio_jobs(self, db):
        for i in range(3):
            db.create_audio_job({
                "job_id": _id(), "slug": f"job-{i}", "title": f"Job {i}",
                "provider": "stable-audio-local", "prompts": [],
                "minutes": 30, "model": "stable-audio-open-1.0",
                "clip_seconds": 30, "status": "queued", "created_at": _now(),
            })
        result = db.list_audio_jobs(limit=10)
        assert len(result) >= 3

    def test_list_jobs_by_status(self, db):
        queued_id = _id()
        running_id = _id()
        db.create_audio_job({
            "job_id": queued_id, "slug": "q", "title": "Q",
            "provider": "stable-audio-local", "prompts": [],
            "minutes": 30, "model": "stable-audio-open-1.0",
            "clip_seconds": 30, "status": "queued", "created_at": _now(),
        })
        db.create_audio_job({
            "job_id": running_id, "slug": "r", "title": "R",
            "provider": "stable-audio-local", "prompts": [],
            "minutes": 30, "model": "stable-audio-open-1.0",
            "clip_seconds": 30, "status": "running", "created_at": _now(),
        })
        queued = db.list_audio_jobs_by_status(["queued"])
        assert all(j["status"] == "queued" for j in queued)
        running = db.list_audio_jobs_by_status(["running"])
        assert all(j["status"] == "running" for j in running)

    def test_fixture_audio_job_failed(self, audio_job_failed):
        """Fixture scenario 3: failed audio job."""
        job = audio_job_failed
        assert job["status"] == "error"
        assert job["error_message"] == "GPU out of memory"
        assert job["slug"] == "lannister-epic-fail"


# ---------------------------------------------------------------------------
# Audio Job Logs
# ---------------------------------------------------------------------------

class TestAudioJobLogs:
    def test_append_and_get(self, db):
        job_id = _id()
        db.create_audio_job({
            "job_id": job_id, "slug": "log-job", "title": "Log Job",
            "provider": "stable-audio-local", "prompts": [],
            "minutes": 30, "model": "stable-audio-open-1.0",
            "clip_seconds": 30, "status": "running", "created_at": _now(),
        })
        db.append_audio_job_log(job_id, "system", "Worker started", _now())
        db.append_audio_job_log(job_id, "stdout", "Generating clip 1/5...", _now())
        logs = db.get_audio_job_logs(job_id)
        assert len(logs) == 2
        assert logs[0]["message"] == "Worker started"

    def test_logs_empty_for_new_job(self, db):
        job_id = _id()
        db.create_audio_job({
            "job_id": job_id, "slug": "empty-logs", "title": "Empty",
            "provider": "stable-audio-local", "prompts": [],
            "minutes": 30, "model": "stable-audio-open-1.0",
            "clip_seconds": 30, "status": "queued", "created_at": _now(),
        })
        assert db.get_audio_job_logs(job_id) == []
