from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    db_file: Path


def get_settings() -> Settings:
    data_dir = Path(os.getenv('DATA_DIR', 'data'))
    return Settings(
        data_dir=data_dir,
        db_file=data_dir / 'agent_sync.db',
    )
