"""Task API routes: /tasks and /tasks/{id}/*."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app import shared
from app.models import ClaimRequest, HeartbeatRequest, ReleaseRequest, CompleteRequest
from app.helpers import (
    _normalize_task_state_for_response,
    _mark_task_stale_if_needed,
    _append_task_event,
    _write_task_state,
)
from app.github_sync import (
    build_internal_task_event,
    is_stale,
    lease_until_iso,
    utc_now_iso,
)

router = APIRouter()


@router.get('/tasks')
def list_tasks(include_done: bool = Query(default=False)) -> dict[str, Any]:
    tasks = shared.db.list_task_states(include_done=include_done)
    normalized = [_normalize_task_state_for_response(task) for task in tasks]
    return {'tasks': normalized, 'count': len(normalized)}


@router.get('/tasks/{task_id:path}/events')
def get_task_events(task_id: str, after_seq: int = Query(default=0, ge=0)) -> dict[str, Any]:
    _mark_task_stale_if_needed(task_id)
    events, latest_seq = shared.db.get_task_events(task_id, after_seq=after_seq)
    return {
        'task_id': task_id,
        'events': events,
        'count': len(events),
        'latest_seq': latest_seq,
    }


@router.post('/tasks/{task_id:path}/claim')
def claim_task(task_id: str, body: ClaimRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')

    current = _normalize_task_state_for_response(current)
    if current.get('phase') in {'done', 'archived'}:
        raise HTTPException(status_code=409, detail='Completed or archived tasks cannot be claimed')
    if current.get('owner_agent') and current.get('owner_agent') != body.agent_id and not is_stale(current):
        raise HTTPException(status_code=409, detail='Task has an active lease owned by another agent')

    updated = current.copy()
    updated['owner_agent'] = body.agent_id
    updated['lease_until'] = lease_until_iso(body.lease_seconds)
    updated['heartbeat_at'] = utc_now_iso()
    updated['phase'] = body.phase
    updated['blocked_reason'] = body.blocked_reason
    updated['updated_at'] = utc_now_iso()

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.claimed',
        action='claimed',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={'lease_seconds': body.lease_seconds},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@router.post('/tasks/{task_id:path}/heartbeat')
def heartbeat_task(task_id: str, body: HeartbeatRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')
    current = _normalize_task_state_for_response(current)

    if current.get('owner_agent') != body.agent_id:
        raise HTTPException(status_code=409, detail='Only the owning agent can heartbeat this task')
    if current.get('phase') in {'stale', 'done', 'archived', 'released'}:
        raise HTTPException(status_code=409, detail='Task is not in a heartbeat-eligible phase')

    updated = current.copy()
    updated['lease_until'] = lease_until_iso(body.lease_seconds)
    updated['heartbeat_at'] = utc_now_iso()
    if body.phase is not None:
        updated['phase'] = body.phase
    updated['blocked_reason'] = body.blocked_reason
    updated['updated_at'] = utc_now_iso()

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.heartbeat',
        action='heartbeat',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={'lease_seconds': body.lease_seconds},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@router.post('/tasks/{task_id:path}/release')
def release_task(task_id: str, body: ReleaseRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')
    current = _normalize_task_state_for_response(current)

    if current.get('owner_agent') != body.agent_id:
        raise HTTPException(status_code=409, detail='Only the owning agent can release this task')

    updated = current.copy()
    updated['owner_agent'] = None
    updated['lease_until'] = None
    updated['heartbeat_at'] = None
    updated['phase'] = 'released'
    updated['blocked_reason'] = None
    updated['updated_at'] = utc_now_iso()

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.released',
        action='released',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@router.post('/tasks/{task_id:path}/complete')
def complete_task(task_id: str, body: CompleteRequest) -> dict[str, Any]:
    current = _mark_task_stale_if_needed(task_id)
    if not current:
        raise HTTPException(status_code=404, detail='Task state not found')
    current = _normalize_task_state_for_response(current)

    if current.get('owner_agent') != body.agent_id:
        raise HTTPException(status_code=409, detail='Only the owning agent can complete this task')

    updated = current.copy()
    updated['owner_agent'] = None
    updated['lease_until'] = None
    updated['heartbeat_at'] = None
    updated['phase'] = 'done'
    updated['blocked_reason'] = None
    updated['updated_at'] = utc_now_iso()

    snapshot = updated.get('snapshot', {}).copy()
    snapshot['status'] = 'done'
    snapshot['updated_at'] = updated['updated_at']
    updated['snapshot'] = snapshot

    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.completed',
        action='completed',
        agent_id=body.agent_id,
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
    _write_task_state(task_id, updated)
    return _normalize_task_state_for_response(updated)


@router.get('/tasks/{task_id:path}')
def get_task(task_id: str) -> dict[str, Any]:
    task = _mark_task_stale_if_needed(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task state not found')
    return _normalize_task_state_for_response(task)
