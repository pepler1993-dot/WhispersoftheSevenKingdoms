from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.store import AgentSyncDB

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PIPELINE_DIR = REPO_ROOT
MUSICGEN_DIR = PIPELINE_DIR / 'musicgen'
PROMPTS_PATH = MUSICGEN_DIR / 'prompts.json'
PIPELINE_UPLOAD_DIR = PIPELINE_DIR / 'data' / 'upload' / 'songs'
KAGGLE_WORK_DIR = PIPELINE_DIR / 'services' / 'sync' / 'data' / 'kaggle'
KAGGLE_JOB_DIR = KAGGLE_WORK_DIR / 'jobs'
KAGGLE_TEMPLATE_NOTEBOOK = MUSICGEN_DIR / 'MusicGen_Colab.ipynb'

KAGGLE_TOKEN_PATH = Path.home() / '.kaggle' / 'kaggle.json'

POLL_INTERVAL = 30   # seconds between status polls
MAX_POLL_ATTEMPTS = 240  # 2 hours max (240 * 30s)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_pipeline_upload_dir() -> Path:
    return PIPELINE_UPLOAD_DIR


def recover_interrupted_jobs(db: AgentSyncDB) -> int:
    recoverable = db.list_audio_jobs_by_status(['queued', 'pushing', 'running', 'downloading'])
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


def _load_prompt_presets() -> list[dict[str, Any]]:
    if not PROMPTS_PATH.exists():
        return []
    try:
        payload = json.loads(PROMPTS_PATH.read_text(encoding='utf-8'))
    except Exception:
        return []
    presets = payload.get('tracks', [])
    return [p for p in presets if isinstance(p, dict)]


def list_prompt_presets() -> list[dict[str, Any]]:
    items = []
    for preset in _load_prompt_presets():
        items.append({
            'name': preset.get('name', ''),
            'category': preset.get('category', ''),
            'house': preset.get('house', ''),
            'prompt_count': len(preset.get('prompts', []) or []),
            'prompts': preset.get('prompts', []) or [],
        })
    return items


def find_prompt_preset(name: str) -> dict[str, Any] | None:
    wanted = (name or '').strip().lower()
    if not wanted:
        return None
    for preset in _load_prompt_presets():
        if str(preset.get('name', '')).strip().lower() == wanted:
            return preset
    return None


def _get_kaggle_username() -> str:
    """Read Kaggle username from ~/.kaggle/kaggle.json."""
    try:
        data = json.loads(KAGGLE_TOKEN_PATH.read_text(encoding='utf-8'))
        return data.get('username', 'unknown')
    except Exception:
        return 'unknown'


def _safe_kernel_slug(raw: str) -> str:
    """Turn arbitrary string into a valid Kaggle kernel slug (max 50 chars)."""
    slug = raw.lower()
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    # Must start with a letter
    if slug and not slug[0].isalpha():
        slug = 'k-' + slug
    return slug[:50]


def _patch_notebook(template_path: Path, dest_path: Path, track_name: str, prompts: list[str], minutes: int, clip_seconds: int) -> None:
    """Copy template notebook and patch the KONFIGURATION cell in place."""
    nb = json.loads(template_path.read_text(encoding='utf-8'))

    prompts_repr = json.dumps(prompts, ensure_ascii=False, indent=4)
    # Build the new config cell source
    new_config_source = f'''\
# 3. KONFIGURATION

# === ZIEL-LÄNGE ===
TARGET_MINUTES = {minutes}  # Ziel-Länge in Minuten
CLIP_SECONDS = {clip_seconds}    # Länge pro Clip (max 30 empfohlen)
CROSSFADE_SEC = 4    # Crossfade zwischen Clips

# === TRACK-NAME (= Slug für Pipeline) ===
TRACK_NAME = {json.dumps(track_name)}

# === PROMPTS ===
PROMPTS = {prompts_repr}

# === UPLOAD-ZIEL ===
UPLOAD_TARGET = "none"

# === BERECHNUNG ===
effective_clip = CLIP_SECONDS - CROSSFADE_SEC
num_clips = int(np.ceil((TARGET_MINUTES * 60) / effective_clip))
estimated_minutes = (num_clips * effective_clip + CROSSFADE_SEC) / 60

print(f"🎵 Track: {{TRACK_NAME}}")
print(f"⏱️ Ziel: {{TARGET_MINUTES}} Min → {{num_clips}} Clips à {{CLIP_SECONDS}}s")
print(f"📊 Geschätzte Gesamtlänge: {{estimated_minutes:.1f}} Min")
print(f"🔁 {{len(PROMPTS)}} Prompt-Variationen")
print(f"📤 Upload: {{UPLOAD_TARGET}}")
'''

    for cell in nb['cells']:
        if cell.get('cell_type') == 'code':
            src = ''.join(cell['source'])
            if 'TARGET_MINUTES' in src and 'TRACK_NAME' in src and 'PROMPTS' in src:
                cell['source'] = [new_config_source]
                break

    dest_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding='utf-8')


def _run_subprocess(cmd: list[str], log_prefix: str, job_id: str, db: AgentSyncDB, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a subprocess and log stdout/stderr."""
    db.append_audio_job_log(job_id, 'system', f'{log_prefix}: {" ".join(cmd)}', now_iso())
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )
    if result.stdout.strip():
        db.append_audio_job_log(job_id, 'stdout', result.stdout.strip()[:2000], now_iso())
    if result.stderr.strip():
        db.append_audio_job_log(job_id, 'stderr', result.stderr.strip()[:2000], now_iso())
    return result


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


class KaggleGenerator(AudioGenerator):
    def __init__(self) -> None:
        self.kaggle_bin = shutil.which('kaggle')
        self.kaggle_token = KAGGLE_TOKEN_PATH

    def health(self) -> dict[str, Any]:
        upload_dir = get_pipeline_upload_dir()
        return {
            'provider': 'kaggle',
            'available': bool(self.kaggle_bin and self.kaggle_token.exists() and KAGGLE_TEMPLATE_NOTEBOOK.exists() and upload_dir.exists()),
            'kaggle_bin': self.kaggle_bin,
            'token_present': self.kaggle_token.exists(),
            'template_present': KAGGLE_TEMPLATE_NOTEBOOK.exists(),
            'upload_dir': str(upload_dir),
            'upload_dir_present': upload_dir.exists(),
        }

    def start(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        thread = threading.Thread(target=self._run_job, args=(job, db), daemon=True)
        thread.start()

    def cancel(self, job: dict[str, Any], db: AgentSyncDB) -> bool:
        db.update_audio_job(job['job_id'], status='cancelled', finished_at=now_iso(), error_message='Cancelled by user')
        db.append_audio_job_log(job['job_id'], 'system', 'Cancellation requested. Manual Kaggle stop may still be required.', now_iso())
        return True

    def _run_job(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        health = self.health()
        if not health['available']:
            reason = (
                f"Kaggle CLI/token/template missing – "
                f"bin={health['kaggle_bin']}, token={health['token_present']}, "
                f"template={health['template_present']}, upload_dir={health['upload_dir_present']}"
            )
            db.update_audio_job(job['job_id'], status='error', finished_at=now_iso(), error_message=reason)
            db.append_audio_job_log(job['job_id'], 'system', reason, now_iso())
            return

        job_id = job['job_id']
        slug = job['slug']
        prompts = job.get('prompts', []) or []
        model = job.get('model', 'medium')
        minutes = int(job.get('minutes') or 42)
        clip_seconds = int(job.get('clip_seconds') or 30)

        # ── 1. Prepare job directory ──────────────────────────────────────────
        job_dir = KAGGLE_JOB_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        notebook_dest = job_dir / 'MusicGen_Kaggle.ipynb'

        payload = {
            'job_id': job_id,
            'slug': slug,
            'prompts': prompts,
            'minutes': minutes,
            'model': model,
            'clip_seconds': clip_seconds,
            'created_at': now_iso(),
        }
        (job_dir / 'job.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

        # ── 2. Patch notebook template ────────────────────────────────────────
        try:
            _patch_notebook(
                template_path=KAGGLE_TEMPLATE_NOTEBOOK,
                dest_path=notebook_dest,
                track_name=slug,
                prompts=prompts,
                minutes=minutes,
                clip_seconds=clip_seconds,
            )
            db.append_audio_job_log(job_id, 'system', f'Notebook patched: track={slug}, minutes={minutes}, clips={clip_seconds}s, prompts={len(prompts)}', now_iso())
        except Exception as exc:
            reason = f'Failed to patch notebook: {exc}'
            db.update_audio_job(job_id, status='error', finished_at=now_iso(), error_message=reason)
            db.append_audio_job_log(job_id, 'system', reason, now_iso())
            return

        # ── 3. Build kernel-metadata.json ─────────────────────────────────────
        kaggle_username = _get_kaggle_username()
        raw_kernel_slug = f'wsk-{slug}-{job_id[:6]}'
        kernel_slug = _safe_kernel_slug(raw_kernel_slug)
        kernel_ref = f'{kaggle_username}/{kernel_slug}'

        metadata = {
            'id': kernel_ref,
            'title': kernel_slug,  # match title to slug to avoid Kaggle rename
            'code_file': 'MusicGen_Kaggle.ipynb',
            'language': 'python',
            'kernel_type': 'notebook',
            'is_private': 'true',
            'enable_gpu': 'true',
            'enable_internet': 'true',
            'dataset_sources': [],
            'competition_sources': [],
            'kernel_sources': [],
        }
        (job_dir / 'kernel-metadata.json').write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
        )
        db.append_audio_job_log(job_id, 'system', f'kernel-metadata.json written: {kernel_ref}', now_iso())

        db.update_audio_job(job_id, status='pushing', kernel_ref=kernel_ref, started_at=now_iso())

        # ── 4. kaggle kernels push ────────────────────────────────────────────
        push_result = _run_subprocess(
            [self.kaggle_bin, 'kernels', 'push', '-p', str(job_dir)],
            log_prefix='kaggle kernels push',
            job_id=job_id,
            db=db,
        )
        if push_result.returncode != 0:
            reason = f'kaggle kernels push failed (rc={push_result.returncode}): {push_result.stderr.strip()[:500]}'
            db.update_audio_job(job_id, status='error', finished_at=now_iso(), error_message=reason)
            db.append_audio_job_log(job_id, 'system', reason, now_iso())
            return

        # Parse real kernel URL from push output to get correct slug
        push_output = push_result.stdout + push_result.stderr
        real_kernel_ref = kernel_ref  # fallback
        # Look for URL like https://www.kaggle.com/code/username/kernel-slug
        import re as _re
        url_match = _re.search(r'kaggle\.com/code/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', push_output)
        if url_match:
            real_kernel_ref = url_match.group(1)
            if real_kernel_ref != kernel_ref:
                db.append_audio_job_log(job_id, 'system', f'Kaggle assigned slug: {real_kernel_ref} (was {kernel_ref})', now_iso())
                db.update_audio_job(job_id, kernel_ref=real_kernel_ref)

        db.update_audio_job(job_id, status='running')
        db.append_audio_job_log(job_id, 'system', f'Kernel pushed. Polling status for {real_kernel_ref} …', now_iso())

        # ── 5. Poll kaggle kernels status ─────────────────────────────────────
        final_status: str | None = None
        for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
            time.sleep(POLL_INTERVAL)

            status_result = _run_subprocess(
                [self.kaggle_bin, 'kernels', 'status', real_kernel_ref],
                log_prefix=f'poll #{attempt}',
                job_id=job_id,
                db=db,
            )
            output = (status_result.stdout + status_result.stderr).lower()

            if 'complete' in output:
                final_status = 'complete'
                db.append_audio_job_log(job_id, 'system', f'Kernel completed after {attempt} polls.', now_iso())
                break
            elif 'error' in output or 'fail' in output:
                final_status = 'error'
                db.append_audio_job_log(job_id, 'system', f'Kernel reported error after {attempt} polls.', now_iso())
                break
            elif 'cancel' in output:
                final_status = 'cancelled'
                db.append_audio_job_log(job_id, 'system', f'Kernel was cancelled after {attempt} polls.', now_iso())
                break
            else:
                db.append_audio_job_log(job_id, 'system', f'Poll #{attempt}: still running …', now_iso())

        if final_status != 'complete':
            reason = f'Kernel did not complete successfully: status={final_status}'
            db.update_audio_job(job_id, status='error', finished_at=now_iso(), error_message=reason)
            db.append_audio_job_log(job_id, 'system', reason, now_iso())
            return

        # ── 6. Download kernel output ──────────────────────────────────────────
        output_dir = job_dir / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        db.update_audio_job(job_id, status='downloading')

        dl_result = _run_subprocess(
            [self.kaggle_bin, 'kernels', 'output', real_kernel_ref, '-p', str(output_dir)],
            log_prefix='kaggle kernels output',
            job_id=job_id,
            db=db,
        )
        if dl_result.returncode != 0:
            reason = f'kaggle kernels output failed (rc={dl_result.returncode}): {dl_result.stderr.strip()[:500]}'
            db.update_audio_job(job_id, status='error', finished_at=now_iso(), error_message=reason)
            db.append_audio_job_log(job_id, 'system', reason, now_iso())
            return

        # ── 7. Find WAV or MP3 and copy to upload dir ─────────────────────────
        audio_file: Path | None = None
        for pattern in ('**/*.wav', '**/*.mp3'):
            found = sorted(output_dir.glob(pattern))
            if found:
                # Prefer the largest file (the merged track, not a clip)
                audio_file = max(found, key=lambda p: p.stat().st_size)
                break

        if audio_file is None:
            reason = f'No WAV/MP3 found in kernel output directory: {output_dir}'
            db.update_audio_job(job_id, status='error', finished_at=now_iso(), error_message=reason)
            db.append_audio_job_log(job_id, 'system', reason, now_iso())
            return

        PIPELINE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        dest = PIPELINE_UPLOAD_DIR / f'{slug}.wav'
        shutil.copy2(str(audio_file), str(dest))
        db.append_audio_job_log(job_id, 'system', f'Audio copied: {audio_file.name} → {dest}', now_iso())

        # ── 8. Mark complete ───────────────────────────────────────────────────
        db.update_audio_job(
            job_id,
            status='complete',
            finished_at=now_iso(),
            output_path=str(dest),
        )
        db.append_audio_job_log(job_id, 'system', f'Job complete. Output: {dest}', now_iso())


def get_audio_generator() -> AudioGenerator:
    return KaggleGenerator()


def get_audio_generator_health() -> dict[str, Any]:
    return get_audio_generator().health()


def create_audio_job(
    slug: str,
    title: str,
    prompt_text: str,
    preset_name: str | None,
    minutes: int,
    model: str,
    clip_seconds: int,
    db: AgentSyncDB,
) -> str:
    job_id = uuid.uuid4().hex[:12]
    prompts = [line.strip() for line in prompt_text.splitlines() if line.strip()]
    if not prompts and preset_name:
        preset = find_prompt_preset(preset_name)
        prompts = (preset or {}).get('prompts', [])

    job = {
        'job_id': job_id,
        'slug': slug,
        'title': title,
        'preset_name': preset_name,
        'prompt_text': prompt_text,
        'prompts': prompts,
        'minutes': minutes,
        'model': model,
        'clip_seconds': clip_seconds,
        'status': 'queued',
        'created_at': now_iso(),
    }
    db.create_audio_job(job)
    db.append_audio_job_log(job_id, 'system', 'Audio generation job created', now_iso())
    get_audio_generator().start(job, db)
    return job_id
