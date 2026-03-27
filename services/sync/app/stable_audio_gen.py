"""Stable Audio Open generator – daemon-based GPU worker.

Submits jobs as JSON files to the worker daemon on the GPU VM.
The daemon keeps the model loaded in VRAM, eliminating load time per clip.
Falls back to single-shot mode if daemon is not running.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import threading
import time
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any

from app.audio_jobs import (
    AudioGenerator,
    get_pipeline_upload_dir,
    is_audio_job_cancelled,
    mark_audio_job_cancelled,
    now_iso,
)
from app.store import AgentSyncDB

# ── Configuration ─────────────────────────────────────────────────────────

GPU_WORKER_HOST = os.environ.get('GPU_WORKER_HOST', '192.168.178.152')
GPU_WORKER_USER = os.environ.get('GPU_WORKER_USER', 'root')
GPU_WORKER_SSH_KEY = os.environ.get('GPU_WORKER_SSH_KEY', '')
GPU_WORKER_OUTPUT_DIR = os.environ.get('GPU_WORKER_OUTPUT_DIR', '/mnt/data/output')
GPU_WORKER_JOB_DIR = '/mnt/data/jobs'
GPU_WORKER_STATUS_FILE = '/mnt/data/worker_status.json'
GPU_WORKER_CODE_DIR = os.environ.get('GPU_WORKER_CODE_DIR', '/opt/stable-audio-worker')

MODEL_NAME = 'stabilityai/stable-audio-open-1.0'
MAX_CLIP_DURATION = 30  # reduced from 47 for 4GB RAM
SAMPLE_RATE = 44100

# Polling config for daemon job completion
JOB_POLL_INTERVAL = 5  # seconds between status checks
JOB_TIMEOUT = 600  # max seconds to wait for a single clip

CET = timezone(timedelta(hours=1))


class StableAudioGenerator(AudioGenerator):
    """Audio generator using Stable Audio Open via daemon on GPU VM."""

    def __init__(self) -> None:
        self._ssh_base = self._build_ssh_cmd()

    def _job_cancelled(self, job_id: str, db: AgentSyncDB, *, log: bool = False) -> bool:
        cancelled = is_audio_job_cancelled(job_id, db)
        if cancelled and log:
            db.append_audio_job_log(job_id, 'system', 'Job execution stopped because cancellation was requested.', now_iso())
        return cancelled

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

    def _is_daemon_ready(self) -> bool:
        """Check if the worker daemon is running and ready."""
        try:
            result = self._ssh_run(f'cat {GPU_WORKER_STATUS_FILE}', timeout=10)
            if result.returncode == 0:
                status = json.loads(result.stdout)
                return status.get('status') in ('ready', 'done')
        except Exception:
            pass
        return False

    def health(self) -> dict[str, Any]:
        try:
            result = self._ssh_run('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader', timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                daemon_ready = self._is_daemon_ready()
                return {
                    'provider': 'stable-audio-local',
                    'available': True,
                    'daemon': daemon_ready,
                    'gpu': result.stdout.strip(),
                    'host': GPU_WORKER_HOST,
                    'model': MODEL_NAME,
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return {
            'provider': 'stable-audio-local',
            'available': False,
            'daemon': False,
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
        mark_audio_job_cancelled(job_id, db, message='Job cancelled by user.')
        try:
            self._ssh_run(
                f'rm -f {GPU_WORKER_JOB_DIR}/{job_id}_*.json '
                f'{GPU_WORKER_JOB_DIR}/{job_id}_*.running '
                f'{GPU_WORKER_JOB_DIR}/{job_id}_*.tmp '
                f'{GPU_WORKER_JOB_DIR}/{job_id}_*.done '
                f'{GPU_WORKER_JOB_DIR}/{job_id}_*.error '
                f'{GPU_WORKER_JOB_DIR}/{job_id}_*.error.log',
                timeout=5,
            )
        except Exception:
            pass
        return True

    def _submit_daemon_job(self, clip_slug: str, prompt: str, duration: float, steps: int) -> bool:
        """Submit a job to the daemon via JSON file (shell-safe with base64)."""
        job_data = json.dumps({
            'prompt': prompt,
            'duration': duration,
            'steps': steps,
            'slug': clip_slug,
        })
        # Base64-encode to avoid any shell escaping issues with special chars
        b64 = base64.b64encode(job_data.encode()).decode()
        try:
            result = self._ssh_run(
                f"echo {b64} | base64 -d > {GPU_WORKER_JOB_DIR}/{clip_slug}.tmp && "
                f"mv {GPU_WORKER_JOB_DIR}/{clip_slug}.tmp {GPU_WORKER_JOB_DIR}/{clip_slug}.json",
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _wait_for_clip(self, clip_slug: str, timeout: int = JOB_TIMEOUT) -> dict | None:
        """Wait for daemon to complete a clip job."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                result = self._ssh_run(
                    f'if test -f {GPU_WORKER_JOB_DIR}/{clip_slug}.done; then echo DONE; '
                    f'elif test -f {GPU_WORKER_JOB_DIR}/{clip_slug}.error; then echo ERROR; '
                    f'else echo PENDING; fi',
                    timeout=10,
                )
                status = result.stdout.strip()
                if status == 'DONE':
                    try:
                        sr = self._ssh_run(f'cat {GPU_WORKER_STATUS_FILE}', timeout=5)
                        return json.loads(sr.stdout)
                    except Exception:
                        return {'status': 'done'}
                elif status == 'ERROR':
                    try:
                        er = self._ssh_run(f'cat {GPU_WORKER_JOB_DIR}/{clip_slug}.error.log', timeout=5)
                        return {'status': 'error', 'error': er.stdout[:300]}
                    except Exception:
                        return {'status': 'error', 'error': 'Unknown error'}
            except Exception:
                pass
            time.sleep(JOB_POLL_INTERVAL)
        return None  # timeout

    def _run_job(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        job_id = job['job_id']
        if self._job_cancelled(job_id, db):
            return
        slug = job['slug']
        prompts = job.get('prompts', []) or []
        minutes = int(job.get('minutes') or 3)
        clip_seconds = min(int(job.get('clip_seconds') or MAX_CLIP_DURATION), MAX_CLIP_DURATION)
        steps = int(job.get('steps') or 50)
        crossfade = 4

        if not prompts:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message='No prompts provided')
            return

        start_ts = now_iso()
        db.update_audio_job(job_id, status='running', started_at=start_ts, provider='stable-audio-local')
        db.append_audio_job_log(job_id, 'system', 'Checking GPU worker health...', start_ts)

        health = self.health()
        if self._job_cancelled(job_id, db, log=True):
            return
        if not health['available']:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f"GPU worker not available: {health.get('error', 'unknown')}")
            return

        use_daemon = health.get('daemon', False)
        mode_str = 'daemon (model pre-loaded)' if use_daemon else 'single-shot (cold start)'
        db.append_audio_job_log(job_id, 'system', f"GPU: {health['gpu']} | Mode: {mode_str}", now_iso())

        # Calculate clips needed
        effective_clip = clip_seconds - crossfade
        num_clips = max(1, int((minutes * 60) / effective_clip) + 1)
        total_duration = (num_clips * effective_clip + crossfade) / 60

        # Estimate render time: measured ~4s per step on GTX 1070 as initial guess
        est_seconds_per_clip = steps * 4
        est_total_minutes = (num_clips * est_seconds_per_clip) / 60
        actual_clip_duration = None  # will be set after first clip for accurate estimates

        db.append_audio_job_log(
            job_id, 'system',
            f"Plan: {num_clips} clips × {clip_seconds}s ({steps} steps) "
            f"≈ {est_seconds_per_clip}s/clip ≈ {est_total_minutes:.0f} min Renderzeit (Schätzung, wird nach Clip 1 korrigiert)",
            now_iso(),
        )

        if self._job_cancelled(job_id, db, log=True):
            return

        # Generate each clip
        remote_clips = []
        for i in range(num_clips):
            if self._job_cancelled(job_id, db, log=True):
                return
            prompt = prompts[i % len(prompts)]
            clip_slug = f'{job_id}_clip_{i:03d}'
            remote_path = f'{GPU_WORKER_OUTPUT_DIR}/{clip_slug}.wav'

            remaining_clips = num_clips - i
            spc = actual_clip_duration if actual_clip_duration else est_seconds_per_clip
            est_remaining = (remaining_clips * spc) / 60
            est_label = "" if actual_clip_duration else " (Schätzung)"
            db.append_audio_job_log(
                job_id, 'system',
                f"Generating clip {i + 1}/{num_clips} (~{spc:.0f}s/clip, ~{est_remaining:.0f} min übrig{est_label}): \"{prompt[:80]}\"",
                now_iso(),
            )

            clip_start = time.monotonic()
            try:
                if use_daemon:
                    if not self._submit_daemon_job(clip_slug, prompt, clip_seconds, steps):
                        raise RuntimeError('Failed to submit job to daemon')

                    result = self._wait_for_clip(clip_slug, timeout=JOB_TIMEOUT)
                    if self._job_cancelled(job_id, db, log=True):
                        return
                    if result is None:
                        db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                            error_message=f'Clip {i+1} timed out (>{JOB_TIMEOUT}s)')
                        return
                    if result.get('status') == 'error':
                        raise RuntimeError(result.get('error', 'Unknown daemon error'))

                    elapsed = result.get('elapsed_seconds', '?')
                    clip_wall = time.monotonic() - clip_start
                    if actual_clip_duration is None:
                        actual_clip_duration = clip_wall
                    db.append_audio_job_log(job_id, 'worker', f"Clip {i+1} done in {elapsed}s (wall: {clip_wall:.0f}s)", now_iso())

                    # Update estimate based on actual render time
                    if isinstance(elapsed, (int, float)) and elapsed > 0:
                        if actual_clip_duration is None:
                            actual_clip_duration = elapsed
                            est_seconds_per_clip = int(actual_clip_duration)
                            new_est_total = (num_clips - (i + 1)) * est_seconds_per_clip / 60
                            db.append_audio_job_log(job_id, 'system',
                                f"Schätzung korrigiert: {est_seconds_per_clip}s/clip (gemessen) → ≈{new_est_total:.0f} min verbleibend",
                                now_iso())
                        else:
                            # Running average
                            actual_clip_duration = (actual_clip_duration + elapsed) / 2
                            est_seconds_per_clip = int(actual_clip_duration)

                    # Cleanup job files
                    self._ssh_run(f'rm -f {GPU_WORKER_JOB_DIR}/{clip_slug}.*', timeout=5)

                else:
                    cmd = (
                        f'{GPU_WORKER_CODE_DIR}/.venv/bin/python3 '
                        f'{GPU_WORKER_CODE_DIR}/worker_daemon.py '
                        f'--prompt {json.dumps(prompt)} '
                        f'--duration {clip_seconds} '
                        f'--slug {clip_slug} '
                        f'--steps {steps}'
                    )
                    ssh_result = self._ssh_run(cmd, timeout=900)
                    if self._job_cancelled(job_id, db, log=True):
                        return

                    if ssh_result.returncode != 0:
                        error_msg = ssh_result.stderr[:300] if ssh_result.stderr else ssh_result.stdout[-300:]
                        raise RuntimeError(f'Generation failed: {error_msg}')

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

        if self._job_cancelled(job_id, db, log=True):
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
            if self._job_cancelled(job_id, db, log=True):
                return
            result = self._scp_from(final_remote, str(local_path))
            if result.returncode != 0:
                raise RuntimeError(f'SCP failed: {result.stderr}')
        except Exception as e:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f'Download failed: {e}')
            return

        db.append_audio_job_log(job_id, 'system', f'Final track downloaded: {local_path.name}', now_iso())

        # Cleanup remote files
        db.append_audio_job_log(job_id, 'system', 'Cleaning up remote worker files...', now_iso())
        try:
            self._ssh_run(
                f'rm -f {GPU_WORKER_OUTPUT_DIR}/{job_id}_clip_*.wav {final_remote}',
                timeout=10,
            )
        except Exception:
            pass

        if self._job_cancelled(job_id, db, log=True):
            return

        # Generate timestamps from clip boundaries
        timestamps = self._generate_timestamps(num_clips, effective_clip, crossfade, job.get('house') or slug)
        timestamp_str = '\n'.join(f'{ts["time"]} – {ts["label"]}' for ts in timestamps)
        db.append_audio_job_log(job_id, 'system', f'Timestamps:\n{timestamp_str}', now_iso())

        # Done!
        file_size_mb = local_path.stat().st_size / 1024 / 1024
        finish_ts = now_iso()
        db.update_audio_job(job_id, status='complete', finished_at=finish_ts,
                            output_path=str(local_path), provider='stable-audio-local')

        # Save timestamps to metadata JSON for YouTube description
        import json as _json
        ts_path = local_path.parent / f'{slug}_timestamps.json'
        ts_path.write_text(_json.dumps(timestamps, indent=2, ensure_ascii=False), encoding='utf-8')
        db.append_audio_job_log(
            job_id, 'system',
            f'✅ Track complete: {local_path.name} ({file_size_mb:.1f} MB)',
            finish_ts,
        )

    # Thematic timestamp labels per house
    TIMESTAMP_LABELS = {
        'winterfell': ['Arrival at Winterfell', 'The Godswood by Moonlight', 'Snow on the Battlements',
                        'The Crypts Below', 'Hearthfire', 'Northern Lights', 'The Long Rest',
                        'Bran\'s Lullaby', 'Dawn Over Winterfell', 'Winter Dreams'],
        'kings_landing': ['The Red Keep at Dusk', 'Candlelight in the Throne Room', 'Streets of Flea Bottom',
                          'The Sept of Baelor', 'Blackwater Bay', 'A Lannister\'s Rest',
                          'The Small Council', 'Night at the Harbour', 'King\'s Dream', 'Dawn of the Crown'],
        'targaryen': ['Shores of Dragonstone', 'The Painted Table', 'Dragon\'s Breath',
                      'Old Valyria', 'Fire and Blood', 'The Last Dragon', 'Throne of Scales',
                      'Embers in the Dark', 'Wings Over the Sea', 'Valyrian Dreams'],
        'the_wall': ['Castle Black', 'The Night\'s Watch', 'Beyond the Wall', 'Frozen Wastes',
                     'The Haunted Forest', 'White Walker\'s March', 'Craster\'s Keep',
                     'The Fist of the First Men', 'Hardhome', 'The Long Night'],
        'highgarden': ['Morning in the Gardens', 'The Rose Arbor', 'Sunlit Terraces',
                       'The Mander River', 'Butterflies and Bees', 'Tyrell\'s Feast',
                       'Twilight Blossoms', 'The Reach at Dawn', 'Golden Harvest', 'Petals in the Wind'],
        'dorne': ['Water Gardens by Night', 'Desert Starlight', 'The Shadow City',
                  'Sunspear at Dusk', 'Oasis Dreams', 'Sand and Silk',
                  'The Prince\'s Tower', 'Moonrise Over Dorne', 'Spice Market Lullaby', 'Dornish Dawn'],
        'godswood': ['The Heart Tree', 'Whispers of the Old Gods', 'Moss and Stone',
                     'The Stream of Memory', 'Roots of Time', 'Sacred Silence',
                     'Night in the Grove', 'Ancient Prayers', 'Leaves of Prophecy', 'The Weirwood Dreams'],
        'castamere': ['Rains of Castamere', 'The Empty Halls', 'Echoes of Gold',
                      'A Lion\'s Lament', 'Stone and Shadow', 'The Fallen House',
                      'Dripping Corridors', 'Ghosts of the Rock', 'Mourning Light', 'The Silence After'],
    }

    def _generate_timestamps(self, num_clips: int, effective_clip: int, crossfade: int, house: str) -> list[dict]:
        """Generate timestamps with thematic labels from clip boundaries."""
        house_lower = house.lower().replace('-', '_').replace(' ', '_')
        # Find matching house labels
        labels = None
        for key, vals in self.TIMESTAMP_LABELS.items():
            if key in house_lower or house_lower in key:
                labels = vals
                break
        if not labels:
            labels = [f'Chapter {i+1}' for i in range(num_clips)]

        timestamps = []
        for i in range(num_clips):
            offset_seconds = i * effective_clip
            hours = offset_seconds // 3600
            minutes = (offset_seconds % 3600) // 60
            seconds = offset_seconds % 60
            time_str = f'{hours}:{minutes:02d}:{seconds:02d}'
            label = labels[i % len(labels)]
            timestamps.append({'time': time_str, 'label': label, 'offset_seconds': offset_seconds})
        return timestamps

    def _stitch_clips(self, clips: list[str], output: str, crossfade: int) -> None:
        """Stitch clips with crossfade using ffmpeg on the worker."""
        if len(clips) == 1:
            self._ssh_run(f'cp {clips[0]} {output}', timeout=30)
            return

        inputs = ' '.join(f'-i {c}' for c in clips)

        if len(clips) == 2:
            filter_str = f'[0][1]acrossfade=d={crossfade}:c1=exp:c2=exp[out]; [out]loudnorm=I=-16:TP=-1.5:LRA=11'
        else:
            parts = []
            for i in range(1, len(clips)):
                if i == 1:
                    parts.append(f'[0][1]acrossfade=d={crossfade}:c1=exp:c2=exp[a{i:02d}]')
                elif i == len(clips) - 1:
                    parts.append(f'[a{i-1:02d}][{i}]acrossfade=d={crossfade}:c1=exp:c2=exp[out]; [out]loudnorm=I=-16:TP=-1.5:LRA=11')
                else:
                    parts.append(f'[a{i-1:02d}][{i}]acrossfade=d={crossfade}:c1=exp:c2=exp[a{i:02d}]')
            filter_str = '; '.join(parts)

        cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_str}" {output}'
        result = self._ssh_run(cmd, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f'ffmpeg stitch failed: {result.stderr[:300]}')
