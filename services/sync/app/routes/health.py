"""Health and debug routes."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app import shared
from app.routes.github_api import list_github_task_snapshots

router = APIRouter()


@router.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/debug/tasks')
def debug_tasks(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    return list_github_task_snapshots(task_id=task_id)
