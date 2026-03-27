"""Ticket management routes – /admin/tickets/*."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import shared
from app.stores.tickets import (
    list_tickets,
    get_ticket,
    create_ticket,
    update_ticket,
    ticket_counts,
)

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Views ────────────────────────────────────────────────────────────────

@router.get('/admin/tickets', response_class=HTMLResponse)
def admin_tickets(
    request: Request,
    status: str | None = Query(default=None),
    ticket_type: str | None = Query(default=None),
):
    tickets = list_tickets(shared.db, status=status, ticket_type=ticket_type)
    counts = ticket_counts(shared.db)
    return shared.templates.TemplateResponse(request, 'tickets.html', {
        'page': 'tickets',
        'tickets': tickets,
        'counts': counts,
        'filter_status': status or 'all',
        'filter_type': ticket_type or 'all',
    })


@router.get('/admin/tickets/new', response_class=HTMLResponse)
def admin_ticket_new(request: Request):
    return shared.templates.TemplateResponse(request, 'ticket_new.html', {
        'page': 'tickets',
    })


@router.get('/admin/tickets/{ticket_id}', response_class=HTMLResponse)
def admin_ticket_detail(request: Request, ticket_id: str):
    ticket = get_ticket(shared.db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    return shared.templates.TemplateResponse(request, 'ticket_detail.html', {
        'page': 'tickets',
        'ticket': ticket,
    })


# ── API ──────────────────────────────────────────────────────────────────

@router.post('/admin/tickets/create')
async def admin_ticket_create(request: Request):
    form = await request.form()

    title = form.get('title', '').strip()
    if not title:
        raise HTTPException(status_code=400, detail='Title is required')

    now = _now_iso()
    ticket_id = str(uuid.uuid4())[:8]
    ticket = {
        'ticket_id': ticket_id,
        'title': title,
        'type': form.get('type', 'bug'),
        'priority': form.get('priority', 'medium'),
        'description': form.get('description', '').strip(),
        'status': 'open',
        'created_by': form.get('created_by', 'dashboard'),
        'created_at': now,
        'updated_at': now,
    }
    create_ticket(shared.db, ticket)
    return RedirectResponse(url='/admin/tickets', status_code=303)


@router.post('/admin/tickets/{ticket_id}/update')
async def admin_ticket_update(request: Request, ticket_id: str):
    form = await request.form()

    existing = get_ticket(shared.db, ticket_id)
    if not existing:
        raise HTTPException(status_code=404, detail='Ticket not found')

    updates = {'updated_at': _now_iso()}
    for field in ('title', 'type', 'priority', 'description', 'status'):
        val = form.get(field)
        if val is not None:
            updates[field] = val.strip() if isinstance(val, str) else val

    update_ticket(shared.db, ticket_id, updates)
    return RedirectResponse(url=f'/admin/tickets/{ticket_id}', status_code=303)


# ── JSON API ─────────────────────────────────────────────────────────────

@router.get('/api/tickets')
def api_tickets(
    status: str | None = Query(default=None),
    ticket_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    return {'tickets': list_tickets(shared.db, status=status, ticket_type=ticket_type, limit=limit)}


@router.get('/api/tickets/{ticket_id}')
def api_ticket_detail(ticket_id: str):
    ticket = get_ticket(shared.db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    return ticket
