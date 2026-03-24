"""Stable Audio Open generator – local GPU worker implementation.

Uses diffusers (not stable_audio_tools) for Python 3.13 compatibility.
Connects to GPU VM via SSH, runs worker.py, copies WAV back.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any

from app.kaggle_gen import AudioGenerator, get_pipeline_upload_dir, now_iso
from app.store import AgentSyncDB

# ── Configuration ─────────────────────────────────────────────────────────

GPU_WORKER_HOST = os.environ.get('GPU_WORKER_HOST', '192.168.178.152')
GPU_WORKER_USER = os.environ.get('GPU_WORKER_USER', 'root')
GPU_WORKER_SSH_KEY = os.environ.get('GPU_WORKER_SSH_KEY', '')
GPU_WORKER_VENV = os.environ.get('GPU_WORKER_VENV', '/opt/musicgen-worker/.venv')
GPU_WORKER_SCRIPT = os.environ.get('GPU_WORKER_SCRIPT', '/opt/musicgen-worker/worker.py')
GPU_WORKER_OUTPUT_DIR = os.environ.get('GPU_WORKER_OUTPUT_DIR', '/mnt/data/output')
GPU_WORKER_STATUS_FILE = '/mnt/data/worker_status.json'

MODEL_NAME = 'stabilityai/stable-audio-open-1.0'
MAX_CLIP_DURATION = 30  # Stable Audio Open max output length in seconds
SAMPLE_RATE = 44100

CET = timezone(timedelta(hours=1))


class StableAudioGenerator(AudioGenerator):
    """Audio generator using Stable Audio Open on a local GPU worker via SSH."""

    def __init__(self) -> None:
        self._ssh_base = self._build_ssh_cmd()

    def _build_ssh_cmd(self) -> list[str]:
        cmd = [
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'ConnectTimeout=10',
            '-o', 'BatchMode=yes',
        ]
        if GPU_WORKER_SSH_KEY:
            cmd.extend(['-i', GPU_WORKER_SSH_KEY])
        cmd.append(f'{GPU_WORKER_USER}@{GPU_WORKER_HOST}')
        return cmd

    def _ssh_run(self, command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            self._ssh_base + [command],
            capture_output=True, text=True, timeout=timeout,
        )

    def _scp_from(self, remote: str, local: str, timeout: int = 300) -> subprocess.CompletedProcess:
        cmd = ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'BatchMode=yes']
        if GPU_WORKER_SSH_KEY:
            cmd.extend(['-i', GPU_WORKER_SSH_KEY])
        cmd.extend([f'{GPU_WORKER_USER}@{GPU_WORKER_HOST}:{remote}', local])
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    def health(self) -> dict[str, Any]:
        try:
            result = self._ssh_run('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader', timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                return {
                    'provider': 'stable-audio-local',
                    'available': True,
                    'gpu': result.stdout.strip(),
                    'host': GPU_WORKER_HOST,
                    'model': MODEL_NAME,
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return {
            'provider': 'stable-audio-local',
            'available': False,
            'gpu': None,
            'host': GPU_WORKER_HOST,
            'model': MODEL_NAME,
            'error': 'GPU worker unreachable or nvidia-smi failed',
        }

    def start(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        thread = threading.Thread(target=self._run_job, args=(job, db), daemon=True)
        thread.start()

    def cancel(self, job: dict[str, Any], db: AgentSyncDB) -> bool:
        job_id = job['job_id']
        db.update_audio_job(job_id, status='cancelled', finished_at=now_iso(),
                            error_message='Cancelled by user')
        db.append_audio_job_log(job_id, 'system', 'Job cancelled.', now_iso())
        try:
            self._ssh_run(f'pkill -f "worker.py.*{job_id}"', timeout=5)
        except Exception:
            pass
        return True

    def _run_job(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        job_id = job['job_id']
        slug = job['slug']
        prompts = job.get('prompts', []) or []
        minutes = int(job.get('minutes') or 3)
        clip_seconds = min(int(job.get('clip_seconds') or MAX_CLIP_DURATION), MAX_CLIP_DURATION)
        steps = int(job.get('steps') or 30)
        crossfade = 4

        if not prompts:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message='No prompts provided')
            return

        db.update_audio_job(job_id, status='running')
        db.append_audio_job_log(job_id, 'system', 'Checking GPU worker health...', now_iso())

        health = self.health()
        if not health['available']:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f"GPU worker not available: {health.get('error', 'unknown')}")
            return

        db.append_audio_job_log(job_id, 'system', f"GPU: {health['gpu']}", now_iso())

        # Calculate clips needed
        effective_clip = clip_seconds - crossfade
        num_clips = max(1, int((minutes * 60) / effective_clip) + 1)
        total_duration = (num_clips * effective_clip + crossfade) / 60

        db.append_audio_job_log(
            job_id, 'system',
            f"Plan: {num_clips} clips × {clip_seconds}s ({steps} steps) ≈ {total_duration:.1f} min",
            now_iso(),
        )

        # Generate each clip using worker.py (diffusers-based)
        remote_clips = []
        for i in range(num_clips):
            prompt = prompts[i % len(prompts)]
            clip_slug = f'{job_id}_clip_{i:03d}'
            remote_path = f'{GPU_WORKER_OUTPUT_DIR}/{clip_slug}.wav'

            db.append_audio_job_log(
                job_id, 'system',
                f"Generating clip {i + 1}/{num_clips}: \"{prompt[:60]}\"",
                now_iso(),
            )

            try:
                cmd = (
                    f'{GPU_WORKER_VENV}/bin/python3 {GPU_WORKER_SCRIPT} '
                    f'--prompt {json.dumps(prompt)} '
                    f'--duration {clip_seconds} '
                    f'--slug {clip_slug} '
                    f'--steps {steps}'
                )
                result = self._ssh_run(cmd, timeout=900)  # 15 min per clip max

                if result.returncode != 0:
                    error_msg = result.stderr[:300] if result.stderr else result.stdout[-300:]
                    db.append_audio_job_log(job_id, 'error', f"Clip {i+1} failed: {error_msg}", now_iso())
                    db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                        error_message=f'Clip generation failed: {error_msg}')
                    return

                # Parse worker status
                try:
                    status = json.loads(
                        self._ssh_run(f'cat {GPU_WORKER_STATUS_FILE}', timeout=5).stdout
                    )
                    db.append_audio_job_log(
                        job_id, 'worker',
                        f"Clip {i+1} done in {status.get('elapsed_seconds', '?')}s",
                        now_iso(),
                    )
                except Exception:
                    db.append_audio_job_log(job_id, 'worker', f"Clip {i+1} generated", now_iso())

                remote_clips.append(remote_path)

            except subprocess.TimeoutExpired:
                db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                    error_message=f'Clip {i+1} timed out (>15 min)')
                return
            except Exception as e:
                db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                    error_message=f'Clip {i+1} error: {e}')
                return

        # Stitch clips with crossfade
        if len(remote_clips) > 1:
            db.append_audio_job_log(job_id, 'system',
                                    f'Stitching {len(remote_clips)} clips with {crossfade}s crossfade...', now_iso())
            final_remote = f'{GPU_WORKER_OUTPUT_DIR}/{slug}.wav'
            try:
                self._stitch_clips(remote_clips, final_remote, crossfade)
            except Exception as e:
                db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                    error_message=f'Stitching failed: {e}')
                return
        else:
            final_remote = remote_clips[0]

        # Download result via SCP
        db.append_audio_job_log(job_id, 'system', 'Downloading final track...', now_iso())
        upload_dir = get_pipeline_upload_dir()
        upload_dir.mkdir(parents=True, exist_ok=True)
        local_path = upload_dir / f'{slug}.wav'

        try:
            result = self._scp_from(final_remote, str(local_path))
            if result.returncode != 0:
                raise RuntimeError(f'SCP failed: {result.stderr}')
        except Exception as e:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f'Download failed: {e}')
            return

        # Cleanup remote files
        try:
            self._ssh_run(
                f'rm -f {GPU_WORKER_OUTPUT_DIR}/{job_id}_clip_*.wav {final_remote}',
                timeout=10,
            )
        except Exception:
            pass

        # Done!
        file_size_mb = local_path.stat().st_size / 1024 / 1024
        db.update_audio_job(job_id, status='complete', finished_at=now_iso(),
                            output_path=str(local_path))
        db.append_audio_job_log(
            job_id, 'system',
            f'✅ Track complete: {local_path.name} ({file_size_mb:.1f} MB)',
            now_iso(),
        )

    def _stitch_clips(self, clips: list[str], output: str, crossfade: int) -> None:
        """Stitch clips with crossfade using ffmpeg on the worker."""
        if len(clips) == 1:
            self._ssh_run(f'cp {clips[0]} {output}', timeout=30)
            return

        inputs = ' '.join(f'-i {c}' for c in clips)

        if len(clips) == 2:
            filter_str = f'[0][1]acrossfade=d={crossfade}:c1=tri:c2=tri'
        else:
            parts = []
            for i in range(1, len(clips)):
                if i == 1:
                    parts.append(f'[0][1]acrossfade=d={crossfade}:c1=tri:c2=tri[a{i:02d}]')
                elif i == len(clips) - 1:
                    parts.append(f'[a{i-1:02d}][{i}]acrossfade=d={crossfade}:c1=tri:c2=tri')
                else:
                    parts.append(f'[a{i-1:02d}][{i}]acrossfade=d={crossfade}:c1=tri:c2=tri[a{i:02d}]')
            filter_str = '; '.join(parts)

        cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_str}" {output}'
        result = self._ssh_run(cmd, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f'ffmpeg stitch failed: {result.stderr[:300]}')
