"""Shared state – initialized by main.py at startup."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.store import AgentSyncDB
    from fastapi.templating import Jinja2Templates

db: AgentSyncDB = None  # type: ignore
templates: Jinja2Templates = None  # type: ignore
settings = None  # type: ignore
BASE_DIR: Path = None  # type: ignore
PIPELINE_DIR: Path = None  # type: ignore
BERLIN_TZ = None  # type: ignore
CET = None  # type: ignore
APP_VERSION: str = 'dev'
DOCS_ROOT: Path = None  # type: ignore
HOUSE_TEMPLATES_PATH: Path = None  # type: ignore
