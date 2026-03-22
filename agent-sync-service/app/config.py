from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    github_webhook_secret: str
    data_dir: Path
    db_file: Path
    events_file: Path
    snapshots_file: Path
    task_events_file: Path
    task_states_file: Path



def get_settings() -> Settings:
    data_dir = Path(os.getenv('DATA_DIR', 'data'))
    secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    return Settings(
        github_webhook_secret=secret,
        data_dir=data_dir,
        db_file=data_dir / 'agent_sync.db',
        events_file=data_dir / 'github_events.json',
        snapshots_file=data_dir / 'task_snapshots.json',
        task_events_file=data_dir / 'task_events.json',
        task_states_file=data_dir / 'task_states.json',
    )
