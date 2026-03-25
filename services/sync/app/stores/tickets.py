"""Ticket store methods – extends AgentSyncDB."""
from __future__ import annotations

from typing import Any


def list_tickets(db, status: str | None = None, ticket_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """List tickets with optional filters."""
    with db._lock:
        with db._connect() as conn:
            query = 'SELECT * FROM tickets'
            params: list[Any] = []
            conditions = []
            if status:
                conditions.append('status = ?')
                params.append(status)
            if ticket_type:
                conditions.append('type = ?')
                params.append(ticket_type)
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            conn.row_factory = _ticket_row_factory
            return conn.execute(query, params).fetchall()


def get_ticket(db, ticket_id: str) -> dict[str, Any] | None:
    """Get a single ticket by ID."""
    with db._lock:
        with db._connect() as conn:
            conn.row_factory = _ticket_row_factory
            row = conn.execute('SELECT * FROM tickets WHERE ticket_id = ?', (ticket_id,)).fetchone()
            return row


def create_ticket(db, ticket: dict[str, Any]) -> dict[str, Any]:
    """Insert a new ticket."""
    with db._lock:
        with db._connect() as conn:
            conn.execute(
                '''INSERT INTO tickets
                   (ticket_id, title, type, priority, description, status,
                    github_issue_number, github_issue_url, task_id, created_by,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    ticket['ticket_id'], ticket['title'], ticket['type'],
                    ticket['priority'], ticket.get('description', ''),
                    ticket.get('status', 'open'),
                    ticket.get('github_issue_number'),
                    ticket.get('github_issue_url'),
                    ticket.get('task_id'),
                    ticket.get('created_by', 'dashboard'),
                    ticket['created_at'], ticket['updated_at'],
                ),
            )
            conn.commit()
    return ticket


def update_ticket(db, ticket_id: str, updates: dict[str, Any]) -> bool:
    """Update ticket fields."""
    allowed = {'title', 'type', 'priority', 'description', 'status',
               'github_issue_number', 'github_issue_url', 'task_id', 'updated_at',
               'assigned_to'}
    fields = {k: v for k, v in updates.items() if k in allowed}
    if not fields:
        return False
    with db._lock:
        with db._connect() as conn:
            sets = ', '.join(f'{k} = ?' for k in fields)
            vals = list(fields.values()) + [ticket_id]
            conn.execute(f'UPDATE tickets SET {sets} WHERE ticket_id = ?', vals)
            conn.commit()
    return True


def ticket_counts(db) -> dict[str, int]:
    """Get ticket counts by status."""
    with db._lock:
        with db._connect() as conn:
            rows = conn.execute(
                'SELECT status, COUNT(*) as cnt FROM tickets GROUP BY status'
            ).fetchall()
            return {r[0]: r[1] for r in rows}


def _ticket_row_factory(cursor, row):
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))
