"""Ops routes: system overview and ticket dashboard."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app import shared

router = APIRouter()


@router.get('/admin/ops', response_class=HTMLResponse)
def admin_ops(request: Request):
    system = shared.db.get_system_summary()
    from app.stores.tickets import list_tickets, ticket_counts
    recent_tickets = list_tickets(shared.db, limit=8)
    tcounts = ticket_counts(shared.db)
    alerts: list[dict[str, str]] = []
    if tcounts.get('open', 0) > 10:
        alerts.append({
            'level': 'warning',
            'title': 'Viele offene Tickets',
            'action': 'Priorisieren und Top-3 für diese Woche festlegen.',
        })
    if tcounts.get('critical', 0) > 0:
        alerts.append({
            'level': 'critical',
            'title': 'Kritische Tickets vorhanden',
            'action': 'Sofort triagieren und einen Owner zuweisen.',
        })
    if system.get('counts', {}).get('workflows', 0) == 0:
        alerts.append({
            'level': 'info',
            'title': 'Keine Pipeline-Runs gefunden',
            'action': 'Einen Test-Run starten, um die Produktionskette zu validieren.',
        })
    return shared.templates.TemplateResponse(request, 'ops.html', {
        'request': request,
        'page': 'ops',
        'system': system,
        'recent_tickets': recent_tickets,
        'ticket_counts': tcounts,
        'alerts': alerts,
    })


@router.get('/admin/system', response_class=HTMLResponse)
def admin_system(request: Request):
    system = shared.db.get_system_summary()
    return shared.templates.TemplateResponse(request, 'system.html', {
        'request': request,
        'page': 'ops',
        'system': system,
    })
