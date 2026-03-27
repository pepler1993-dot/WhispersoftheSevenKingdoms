"""GPU worker metrics routes."""
from __future__ import annotations

import subprocess
from typing import Any

from fastapi import APIRouter

from app.stable_audio_gen import GPU_WORKER_HOST, GPU_WORKER_SSH_KEY, GPU_WORKER_USER

router = APIRouter()


def _ssh_cmd() -> list[str]:
    cmd = ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no']
    if GPU_WORKER_SSH_KEY:
        cmd.extend(['-i', GPU_WORKER_SSH_KEY])
    cmd.append(f'{GPU_WORKER_USER}@{GPU_WORKER_HOST}')
    return cmd


def get_gpu_metrics() -> dict[str, Any]:
    """Fetch GPU metrics via SSH + nvidia-smi."""
    try:
        result = subprocess.run(
            _ssh_cmd() + [
                'nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,'
                'temperature.gpu,fan.speed,power.draw --format=csv,noheader,nounits'
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return {'available': False, 'error': result.stderr[:200]}

        parts = [p.strip() for p in result.stdout.strip().split(',')]
        if len(parts) < 7:
            return {'available': False, 'error': 'Unexpected nvidia-smi output'}

        mem_used = float(parts[2])
        mem_total = float(parts[3])
        gpu_util = float(parts[1])
        temp = float(parts[4])

        return {
            'available': True,
            'name': parts[0],
            'gpu_util': gpu_util,
            'mem_used_mb': mem_used,
            'mem_total_mb': mem_total,
            'mem_pct': round(mem_used / mem_total * 100, 1) if mem_total else 0,
            'temperature': temp,
            'fan_speed': float(parts[5]),
            'power_draw': float(parts[6]),
            'host': GPU_WORKER_HOST,
            'warnings': _check_warnings(gpu_util, temp, mem_used / mem_total * 100 if mem_total else 0),
        }
    except subprocess.TimeoutExpired:
        return {'available': False, 'error': 'SSH timeout'}
    except Exception as e:
        return {'available': False, 'error': str(e)}


def _check_warnings(gpu_util: float, temp: float, mem_pct: float) -> list[str]:
    warnings = []
    if temp > 85:
        warnings.append(f'🔥 GPU Temperatur kritisch: {temp}°C')
    elif temp > 75:
        warnings.append(f'⚠️ GPU Temperatur hoch: {temp}°C')
    if mem_pct > 95:
        warnings.append(f'⚠️ VRAM fast voll: {mem_pct:.0f}%')
    return warnings


@router.get('/api/gpu/metrics')
def api_gpu_metrics():
    return get_gpu_metrics()
