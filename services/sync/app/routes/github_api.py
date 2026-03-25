"""GitHub webhook and event API routes."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, Request

from app import shared
from app.helpers import (
    verify_signature,
    _append_task_event,
)
from app.github_sync import (
    build_event_record,
    create_task_state,
    normalize_task_event,
    update_snapshot_from_event,
    utc_now_iso,
)

router = APIRouter()


@router.get('/github/events')
def list_github_events(
    limit: int = Query(default=20, ge=1, le=200),
    task_id: str | None = Query(default=None),
) -> dict[str, Any]:
    events = shared.db.list_github_events(limit=limit, task_id=task_id)
    return {'events': events, 'count': len(events)}


@router.get('/github/events/{delivery_id}')
def get_github_event(delivery_id: str) -> dict[str, Any]:
    event = shared.db.get_github_event(delivery_id)
    if event:
        return event
    raise HTTPException(status_code=404, detail='Delivery not found')


@router.get('/github/tasks')
def list_github_task_snapshots(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    ordered = shared.db.list_snapshots(task_id=task_id)
    return {'tasks': ordered, 'count': len(ordered)}


@router.get('/github/task')
def get_github_task_snapshot(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    snapshot = shared.db.get_snapshot(task_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail='Task snapshot not found')
    return snapshot


@router.post('/github/webhook')
async def github_webhook(
    request: Request,
    x_github_delivery: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, Any]:
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail='Missing X-GitHub-Delivery header')
    if not x_github_event:
        raise HTTPException(status_code=400, detail='Missing X-GitHub-Event header')

    raw_body = await request.body()
    verify_signature(raw_body, x_hub_signature_256)

    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail='Invalid JSON payload') from exc

    event_record = build_event_record(x_github_delivery, x_github_event, payload)
    was_inserted = shared.db.insert_github_event(event_record)

    snapshot_updated = False
    updated_snapshot: dict[str, Any] | None = None
    task_id = event_record.get('task_id')
    if task_id:
        existing_snapshot = shared.db.get_snapshot(task_id)
        updated_snapshot = update_snapshot_from_event(existing_snapshot, event_record)
        if updated_snapshot:
            shared.db.upsert_snapshot(updated_snapshot)
            snapshot_updated = True

    normalized_event = normalize_task_event(event_record, updated_snapshot)
    task_event_inserted, assigned_seq = _append_task_event(normalized_event)

    task_state_updated = False
    if normalized_event and updated_snapshot and assigned_seq:
        existing = shared.db.get_task_state(normalized_event['task_id'])
        if existing:
            task_state = existing.copy()
            task_state['snapshot'] = updated_snapshot
            task_state['latest_seq'] = assigned_seq
            task_state['updated_at'] = updated_snapshot.get('updated_at', utc_now_iso())
        else:
            task_state = create_task_state(normalized_event['task_id'], updated_snapshot, assigned_seq)
        shared.db.upsert_task_state(normalized_event['task_id'], task_state)
        task_state_updated = True

    return {
        'ok': True,
        'delivery_id': x_github_delivery,
        'event_type': x_github_event,
        'action': event_record.get('action'),
        'task_id': event_record.get('task_id'),
        'event_inserted': was_inserted,
        'snapshot_updated': snapshot_updated,
        'task_event_inserted': task_event_inserted,
        'task_state_updated': task_state_updated,
        'seq': assigned_seq or None,
    }
