from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.store import AgentSyncDB

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PIPELINE_UPLOAD_DIR = REPO_ROOT / 'data' / 'upload' / 'songs'

CET = timezone(timedelta(hours=1))

FINAL_AUDIO_JOB_STATUSES = {'complete', 'cancelled', 'error'}
CANCELLABLE_AUDIO_JOB_STATUSES = {'queued', 'running'}


def now_iso() -> str:
    return datetime.now(CET).isoformat()


def get_pipeline_upload_dir() -> Path:
    return PIPELINE_UPLOAD_DIR


def recover_interrupted_jobs(db: AgentSyncDB) -> int:
    recoverable = db.list_audio_jobs_by_status(['queued', 'running'])
    recovered = 0
    for job in recoverable:
        db.update_audio_job(
            job['job_id'],
            status='error',
            finished_at=now_iso(),
            error_message='Service restarted while job was in progress; marked as interrupted.',
        )
        db.append_audio_job_log(job['job_id'], 'system', 'Recovered after service restart: job marked as interrupted.', now_iso())
        recovered += 1
    return recovered


class AudioGenerator(ABC):
    @abstractmethod
    def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def start(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        raise NotImplementedError

    @abstractmethod
    def cancel(self, job: dict[str, Any], db: AgentSyncDB) -> bool:
        raise NotImplementedError


def get_audio_generator() -> AudioGenerator:
    from app.stable_audio_gen import StableAudioGenerator

    return StableAudioGenerator()


def get_audio_generator_health() -> dict[str, Any]:
    return get_audio_generator().health()


def is_audio_job_cancelled(job_id: str, db: AgentSyncDB) -> bool:
    job = db.get_audio_job(job_id)
    return bool(job and job.get('status') == 'cancelled')


def mark_audio_job_cancelled(job_id: str, db: AgentSyncDB, message: str = 'Cancelled by user') -> None:
    job = db.get_audio_job(job_id)
    if not job or job.get('status') == 'cancelled':
        return
    db.update_audio_job(job_id, status='cancelled', finished_at=now_iso(), error_message=message)
    db.append_audio_job_log(job_id, 'system', message, now_iso())


def create_audio_job(
    slug: str,
    title: str,
    prompt_text: str,
    preset_name: str | None,
    minutes: int,
    model: str,
    clip_seconds: int,
    db: AgentSyncDB,
    steps: int = 50,
    house: str = '',
    base_dna: str = '',
    negative_prompt: str = '',
) -> str:
    prompts = [line.strip() for line in (prompt_text or '').splitlines() if line.strip()]
    if not prompts:
        raise ValueError('At least one prompt line is required.')

    job_id = uuid.uuid4().hex[:12]
    job = {
        'job_id': job_id,
        'slug': slug,
        'title': title,
        'provider': 'stable-audio-local',
        'preset_name': None,
        'prompt_text': prompt_text,
        'prompts': prompts,
        'minutes': minutes,
        'model': model,
        'clip_seconds': clip_seconds,
        'steps': steps,
        'house': house,
        'base_dna': base_dna,
        'negative_prompt': negative_prompt,
        'status': 'queued',
        'created_at': now_iso(),
    }
    db.create_audio_job(job)
    db.append_audio_job_log(job_id, 'system', 'Audio generation job created', now_iso())
    get_audio_generator().start(job, db)
    return job_id
