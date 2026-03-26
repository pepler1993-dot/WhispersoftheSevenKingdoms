"""Ops routes: tasks admin, events, system, protocol health, filters."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from app import shared
from app.helpers import (
    _build_protocol_health,
    _event_manager_summary,
    _format_berlin,
    _humanize_task_detail_for_manager,
    _humanize_task_for_manager,
)

router = APIRouter()


@router.get('/admin/ops', response_class=HTMLResponse)
def admin_ops(
    request: Request,
    tab: str = Query(default='tasks'),
    phase: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    q: str | None = Query(default=None),
    include_done: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
):
    allowed_tabs = {'tasks', 'events', 'system'}
    current_tab = tab if tab in allowed_tabs else 'tasks'
    protocol_health = _build_protocol_health()
    raw_tasks = shared.db.list_tasks_for_admin(phase=phase, owner=owner, query=q, include_done=include_done)
    tasks = [_humanize_task_for_manager(task, shared.db.get_task_detail(task['task_id'])) for task in raw_tasks]
    events = [{**event, 'received_at_display': _format_berlin(event.get('received_at'), with_seconds=True), 'summary': _event_manager_summary(event)} for event in shared.db.list_github_events(limit=limit)]
    system = shared.db.get_system_summary()
    system['latest_github_event_at_display'] = _format_berlin(system.get('latest_github_event_at'), with_seconds=True)
    system['latest_task_update_at_display'] = _format_berlin(system.get('latest_task_update_at'), with_seconds=True)
    summary = shared.db.get_dashboard_summary()
    from app.stores.tickets import list_tickets, ticket_counts
    recent_tickets = list_tickets(shared.db, limit=8)
    tcounts = ticket_counts(shared.db)
    return shared.templates.TemplateResponse(request, 'ops.html', {
        'request': request,
        'page': 'ops',
        'current_tab': current_tab,
        'tasks': tasks,
        'events': events,
        'system': system,
        'summary': summary,
        'protocol_health': protocol_health,
        'limit': limit,
        'filters': {'phase': phase, 'owner': owner, 'q': q, 'include_done': include_done},
        'recent_tickets': recent_tickets,
        'ticket_counts': tcounts,
    })


@router.get('/admin/tasks', response_class=HTMLResponse)
def admin_tasks(
    request: Request,
    phase: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    q: str | None = Query(default=None),
    include_done: bool = Query(default=False),
):
    tasks = [_humanize_task_for_manager(task, shared.db.get_task_detail(task['task_id'])) for task in shared.db.list_tasks_for_admin(phase=phase, owner=owner, query=q, include_done=include_done)]
    return shared.templates.TemplateResponse(request, 'tasks.html', {
        'request': request,
        'page': 'ops',
        'tasks': tasks,
        'filters': {'phase': phase, 'owner': owner, 'q': q, 'include_done': include_done},
    })


@router.get('/admin/tasks/{task_id:path}', response_class=HTMLResponse)
def admin_task_detail(request: Request, task_id: str):
    detail = shared.db.get_task_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail='Task not found')
    detail = _humanize_task_detail_for_manager(task_id, detail)
    return shared.templates.TemplateResponse(request, 'task_detail.html', {
        'request': request,
        'page': 'ops',
        'task_id': task_id,
        'detail': detail,
    })


@router.get('/admin/events', response_class=HTMLResponse)
def admin_events(request: Request, limit: int = Query(default=100, ge=1, le=500)):
    events = shared.db.list_github_events(limit=limit)
    return shared.templates.TemplateResponse(request, 'events.html', {
        'request': request,
        'page': 'ops',
        'events': events,
        'limit': limit,
    })


@router.get('/admin/system', response_class=HTMLResponse)
def admin_system(request: Request):
    system = shared.db.get_system_summary()
    protocol_health = _build_protocol_health()
    system['latest_github_event_at_display'] = _format_berlin(system.get('latest_github_event_at'), with_seconds=True)
    system['latest_task_update_at_display'] = _format_berlin(system.get('latest_task_update_at'), with_seconds=True)
    return shared.templates.TemplateResponse(request, 'system.html', {
        'request': request,
        'page': 'ops',
        'system': system,
        'protocol_health': protocol_health,
    })


@router.get('/api/protocol-health')
def api_protocol_health() -> dict[str, Any]:
    return _build_protocol_health()


@router.get('/api/filters')
def get_filter_options():
    """Bereitstellung aller verfügbaren Filterwerte."""
    agents = shared.db.get_unique_agents()
    phases = shared.db.get_unique_phases()
    return {'agents': agents, 'phases': phases}
