"""Stable Audio Open generator – local GPU worker implementation.

This module implements the AudioGenerator ABC using Stable Audio Open
running on a local GPU (e.g. GTX 1070 via Proxmox passthrough).

The worker connects to the GPU VM via SSH, runs generation there,
and copies the result back to the pipeline upload directory.
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

GPU_WORKER_HOST = os.environ.get('GPU_WORKER_HOST', '192.168.178.131')
GPU_WORKER_USER = os.environ.get('GPU_WORKER_USER', 'root')
GPU_WORKER_SSH_KEY = os.environ.get('GPU_WORKER_SSH_KEY', '')
GPU_WORKER_VENV = os.environ.get('GPU_WORKER_VENV', '/opt/musicgen-worker/.venv')
GPU_WORKER_OUTPUT_DIR = os.environ.get('GPU_WORKER_OUTPUT_DIR', '/opt/musicgen-worker/output')

MODEL_NAME = 'stabilityai/stable-audio-open-1.0'
MAX_CLIP_DURATION = 47  # Stable Audio Open max output length in seconds
SAMPLE_RATE = 44100

CET = timezone(timedelta(hours=1))

# ── Generation script that runs ON the GPU worker ─────────────────────────

GENERATE_SCRIPT = r'''#!/usr/bin/env python3
"""Generate audio clip using Stable Audio Open. Runs on GPU worker."""

import argparse
import json
import sys
import torch
import torchaudio
from stable_audio_tools import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--duration', type=float, default=47.0)
    parser.add_argument('--output', required=True)
    parser.add_argument('--seed', type=int, default=-1)
    args = parser.parse_args()

    print(json.dumps({"phase": "loading", "message": "Loading Stable Audio Open model..."}), flush=True)

    model, model_config = get_pretrained_model(
        "stabilityai/stable-audio-open-1.0"
    )
    sample_rate = model_config["sample_rate"]
    sample_size = model_config["sample_size"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    print(json.dumps({"phase": "generating", "message": f"Generating {args.duration}s on {device}..."}), flush=True)

    seed = args.seed if args.seed >= 0 else torch.randint(0, 2**32 - 1, (1,)).item()

    conditioning = [{
        "prompt": args.prompt,
        "seconds_start": 0,
        "seconds_total": args.duration,
    }]

    with torch.no_grad():
        output = generate_diffusion_cond(
            model,
            steps=100,
            cfg_scale=7,
            conditioning=conditioning,
            sample_size=sample_size,
            sigma_min=0.3,
            sigma_max=500,
            sampler_type="dpmpp-3m-sde",
            device=device,
            seed=seed,
        )

    output = output.squeeze(0).cpu()

    # Trim to requested duration
    max_samples = int(args.duration * sample_rate)
    output = output[:, :max_samples]

    torchaudio.save(args.output, output, sample_rate)

    print(json.dumps({"phase": "done", "message": f"Saved to {args.output}", "seed": seed}), flush=True)

if __name__ == "__main__":
    main()
'''


class StableAudioGenerator(AudioGenerator):
    """Audio generator using Stable Audio Open on a local GPU worker via SSH."""

    def __init__(self) -> None:
        self._ssh_base = self._build_ssh_cmd()

    def _build_ssh_cmd(self) -> list[str]:
        """Build base SSH command with options."""
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
        """Run a command on the GPU worker via SSH."""
        return subprocess.run(
            self._ssh_base + [command],
            capture_output=True, text=True, timeout=timeout,
        )

    def health(self) -> dict[str, Any]:
        """Check if the GPU worker is reachable and has NVIDIA GPU."""
        try:
            result = self._ssh_run('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader', timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                gpu_info = result.stdout.strip()
                return {
                    'provider': 'stable-audio-local',
                    'available': True,
                    'gpu': gpu_info,
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
        """Start audio generation in a background thread."""
        thread = threading.Thread(target=self._run_job, args=(job, db), daemon=True)
        thread.start()

    def cancel(self, job: dict[str, Any], db: AgentSyncDB) -> bool:
        """Cancel a running job."""
        job_id = job['job_id']
        db.update_audio_job(job_id, status='cancelled', finished_at=now_iso(),
                            error_message='Cancelled by user')
        db.append_audio_job_log(job_id, 'system', 'Job cancelled.', now_iso())
        # Try to kill remote process
        try:
            self._ssh_run(f'pkill -f "generate_clip.*{job_id}"', timeout=5)
        except Exception:
            pass
        return True

    def _run_job(self, job: dict[str, Any], db: AgentSyncDB) -> None:
        """Main job execution: generate clips, stitch, download."""
        job_id = job['job_id']
        slug = job['slug']
        prompts = job.get('prompts', []) or []
        minutes = int(job.get('minutes') or 3)
        clip_seconds = min(int(job.get('clip_seconds') or MAX_CLIP_DURATION), MAX_CLIP_DURATION)
        crossfade = 4

        if not prompts:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message='No prompts provided')
            return

        # Check worker health
        db.update_audio_job(job_id, status='running')
        db.append_audio_job_log(job_id, 'system', 'Checking GPU worker health...', now_iso())

        health = self.health()
        if not health['available']:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f"GPU worker not available: {health.get('error', 'unknown')}")
            db.append_audio_job_log(job_id, 'system', f"GPU worker check failed: {health}", now_iso())
            return

        db.append_audio_job_log(job_id, 'system', f"GPU: {health['gpu']}", now_iso())

        # Calculate clips needed
        effective_clip = clip_seconds - crossfade
        num_clips = max(1, int((minutes * 60) / effective_clip) + 1)
        total_duration = (num_clips * effective_clip + crossfade) / 60

        db.append_audio_job_log(
            job_id, 'system',
            f"Plan: {num_clips} clips × {clip_seconds}s = ~{total_duration:.1f} min",
            now_iso(),
        )

        # Upload generate script to worker
        try:
            self._setup_worker(job_id, db)
        except Exception as e:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f'Worker setup failed: {e}')
            return

        # Generate each clip
        remote_clips = []
        for i in range(num_clips):
            prompt = prompts[i % len(prompts)]
            clip_name = f'{job_id}_clip_{i:03d}.wav'
            remote_path = f'{GPU_WORKER_OUTPUT_DIR}/{clip_name}'

            db.append_audio_job_log(
                job_id, 'system',
                f"Generating clip {i + 1}/{num_clips}: \"{prompt[:60]}...\"",
                now_iso(),
            )

            try:
                result = self._ssh_run(
                    f'{GPU_WORKER_VENV}/bin/python /opt/musicgen-worker/generate_clip.py '
                    f'--prompt {json.dumps(prompt)} '
                    f'--duration {clip_seconds} '
                    f'--output {remote_path}',
                    timeout=600,  # 10 min per clip max
                )

                if result.returncode != 0:
                    db.append_audio_job_log(job_id, 'error', f"Clip {i + 1} failed: {result.stderr[:200]}", now_iso())
                    db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                        error_message=f'Clip generation failed: {result.stderr[:200]}')
                    return

                # Parse progress from stdout
                for line in result.stdout.strip().split('\n'):
                    try:
                        msg = json.loads(line)
                        db.append_audio_job_log(job_id, 'worker', msg.get('message', line), now_iso())
                    except json.JSONDecodeError:
                        if line.strip():
                            db.append_audio_job_log(job_id, 'worker', line.strip(), now_iso())

                remote_clips.append(remote_path)

            except subprocess.TimeoutExpired:
                db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                    error_message=f'Clip {i + 1} timed out (>10 min)')
                return
            except Exception as e:
                db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                    error_message=f'Clip {i + 1} error: {e}')
                return

        # Stitch clips with crossfade on the worker
        db.append_audio_job_log(job_id, 'system', f'Stitching {len(remote_clips)} clips with {crossfade}s crossfade...', now_iso())
        final_remote = f'{GPU_WORKER_OUTPUT_DIR}/{slug}.wav'

        try:
            self._stitch_clips(job_id, remote_clips, final_remote, crossfade, db)
        except Exception as e:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f'Stitching failed: {e}')
            return

        # Download result
        db.append_audio_job_log(job_id, 'system', 'Downloading final track...', now_iso())
        upload_dir = get_pipeline_upload_dir()
        upload_dir.mkdir(parents=True, exist_ok=True)
        local_path = upload_dir / f'{slug}.wav'

        try:
            scp_cmd = ['scp', '-o', 'StrictHostKeyChecking=no']
            if GPU_WORKER_SSH_KEY:
                scp_cmd.extend(['-i', GPU_WORKER_SSH_KEY])
            scp_cmd.extend([
                f'{GPU_WORKER_USER}@{GPU_WORKER_HOST}:{final_remote}',
                str(local_path),
            ])
            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f'SCP failed: {result.stderr}')
        except Exception as e:
            db.update_audio_job(job_id, status='error', finished_at=now_iso(),
                                error_message=f'Download failed: {e}')
            return

        # Cleanup remote files
        try:
            cleanup_cmd = f'rm -f {GPU_WORKER_OUTPUT_DIR}/{job_id}_clip_*.wav {final_remote}'
            self._ssh_run(cleanup_cmd, timeout=10)
        except Exception:
            pass  # non-critical

        # Done!
        db.update_audio_job(job_id, status='complete', finished_at=now_iso(),
                            output_path=str(local_path))
        db.append_audio_job_log(
            job_id, 'system',
            f'✅ Track complete: {local_path.name} ({local_path.stat().st_size / 1024 / 1024:.1f} MB)',
            now_iso(),
        )

    def _setup_worker(self, job_id: str, db: AgentSyncDB) -> None:
        """Ensure the generate script and output dir exist on the worker."""
        # Create directories
        self._ssh_run(f'mkdir -p /opt/musicgen-worker {GPU_WORKER_OUTPUT_DIR}', timeout=10)

        # Upload generate script via stdin
        subprocess.run(
            self._ssh_base + ['cat > /opt/musicgen-worker/generate_clip.py'],
            input=GENERATE_SCRIPT,
            capture_output=True, text=True, timeout=15,
        )

        db.append_audio_job_log(job_id, 'system', 'Generate script uploaded to worker.', now_iso())

    def _stitch_clips(self, job_id: str, clips: list[str], output: str, crossfade: int, db: AgentSyncDB) -> None:
        """Stitch multiple clips with crossfade using ffmpeg on the worker."""
        if len(clips) == 1:
            self._ssh_run(f'cp {clips[0]} {output}', timeout=30)
            return

        # Build ffmpeg filter for crossfade stitching
        filter_parts = []
        inputs = ' '.join(f'-i {c}' for c in clips)

        # Chain crossfades: [0][1]acrossfade=d=4:c1=tri:c2=tri[a01]; [a01][2]acrossfade=...
        if len(clips) == 2:
            filter_str = f'[0][1]acrossfade=d={crossfade}:c1=tri:c2=tri'
        else:
            parts = []
            for i in range(1, len(clips)):
                if i == 1:
                    parts.append(f'[0][1]acrossfade=d={crossfade}:c1=tri:c2=tri[a{i:02d}]')
                elif i == len(clips) - 1:
                    parts.append(f'[a{i - 1:02d}][{i}]acrossfade=d={crossfade}:c1=tri:c2=tri')
                else:
                    parts.append(f'[a{i - 1:02d}][{i}]acrossfade=d={crossfade}:c1=tri:c2=tri[a{i:02d}]')
            filter_str = '; '.join(parts)

        cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_str}" {output}'
        result = self._ssh_run(cmd, timeout=120)

        if result.returncode != 0:
            raise RuntimeError(f'ffmpeg stitch failed: {result.stderr[:300]}')

        db.append_audio_job_log(job_id, 'system', f'Stitched {len(clips)} clips → {output}', now_iso())
