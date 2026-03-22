from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

DEFAULT_LEASE_SECONDS = 300
VALID_PHASES = {'working', 'blocked', 'released', 'done', 'archived', 'stale'}
VISIBLE_ACTIVE_PHASES = {'working', 'blocked', 'released', 'stale'}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)



def utc_now_iso() -> str:
    return utc_now().isoformat()



def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None



def extract_numbers(payload: dict[str, Any]) -> tuple[int | None, int | None]:
    issue_number = payload.get('issue', {}).get('number')
    pull_request_number = payload.get('pull_request', {}).get('number')

    if issue_number is None and payload.get('number') and payload.get('pull_request'):
        issue_number = payload.get('number')
        pull_request_number = payload.get('number')

    if issue_number is None and payload.get('issue', {}).get('pull_request'):
        issue_number = payload['issue'].get('number')
        pull_request_number = payload['issue'].get('number')

    return issue_number, pull_request_number



def build_task_id(repo: str | None, issue_number: int | None) -> str | None:
    if not repo or not issue_number:
        return None
    return f'{repo}#{issue_number}'



def build_event_record(delivery_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    action = payload.get('action')
    repo_full_name = payload.get('repository', {}).get('full_name')
    issue_number, pull_request_number = extract_numbers(payload)
    sender = payload.get('sender', {}).get('login')
    task_id = build_task_id(repo_full_name, issue_number)

    return {
        'id': delivery_id,
        'delivery_id': delivery_id,
        'event_type': event_type,
        'action': action,
        'repo': repo_full_name,
        'issue_number': issue_number,
        'pr_number': pull_request_number,
        'task_id': task_id,
        'sender': sender,
        'received_at': utc_now_iso(),
        'payload_json': payload,
    }



def create_base_snapshot(task_id: str, issue_number: int, pr_number: int | None) -> dict[str, Any]:
    now = utc_now_iso()
    return {
        'task_id': task_id,
        'issue_number': issue_number,
        'status': 'open',
        'branch': None,
        'pr_number': pr_number,
        'last_commit_sha': None,
        'review_state': None,
        'last_summary': None,
        'updated_at': now,
    }



def update_snapshot_from_event(existing: dict[str, Any] | None, event: dict[str, Any]) -> dict[str, Any] | None:
    repo = event.get('repo')
    issue_number = event.get('issue_number')
    task_id = build_task_id(repo, issue_number)
    if not task_id or not issue_number:
        return None

    snapshot = existing.copy() if existing else create_base_snapshot(task_id, issue_number, event.get('pr_number'))

    payload = event['payload_json']
    event_type = event['event_type']
    action = event.get('action')

    snapshot['updated_at'] = utc_now_iso()
    if event.get('pr_number') is not None:
        snapshot['pr_number'] = event['pr_number']

    if event_type == 'issues':
        snapshot['status'] = payload.get('issue', {}).get('state', snapshot['status'])

    elif event_type == 'issue_comment':
        snapshot['status'] = payload.get('issue', {}).get('state', snapshot['status'])
        if payload.get('issue', {}).get('pull_request'):
            snapshot['pr_number'] = payload['issue'].get('number')

    elif event_type == 'pull_request':
        pr = payload.get('pull_request', {})
        snapshot['status'] = pr.get('state', snapshot['status'])
        snapshot['pr_number'] = pr.get('number', snapshot['pr_number'])
        snapshot['branch'] = pr.get('head', {}).get('ref', snapshot['branch'])
        snapshot['last_commit_sha'] = pr.get('head', {}).get('sha', snapshot['last_commit_sha'])
        if action == 'closed' and pr.get('merged'):
            snapshot['status'] = 'merged'

    elif event_type == 'pull_request_review':
        review_state = payload.get('review', {}).get('state')
        if review_state:
            snapshot['review_state'] = review_state.lower()
        pr = payload.get('pull_request', {})
        snapshot['pr_number'] = pr.get('number', snapshot['pr_number'])
        snapshot['branch'] = pr.get('head', {}).get('ref', snapshot['branch'])
        snapshot['last_commit_sha'] = pr.get('head', {}).get('sha', snapshot['last_commit_sha'])

    elif event_type == 'pull_request_review_comment':
        pr = payload.get('pull_request', {})
        snapshot['pr_number'] = pr.get('number', snapshot['pr_number'])
        snapshot['branch'] = pr.get('head', {}).get('ref', snapshot['branch'])
        snapshot['last_commit_sha'] = pr.get('head', {}).get('sha', snapshot['last_commit_sha'])

    elif event_type == 'push':
        snapshot['branch'] = payload.get('ref', '').removeprefix('refs/heads/') or snapshot['branch']
        snapshot['last_commit_sha'] = payload.get('after', snapshot['last_commit_sha'])

    return snapshot



def normalize_task_event(event: dict[str, Any], snapshot: dict[str, Any] | None) -> dict[str, Any] | None:
    task_id = event.get('task_id')
    if not task_id:
        return None

    return {
        'task_id': task_id,
        'repo': event.get('repo'),
        'issue_number': event.get('issue_number'),
        'pr_number': event.get('pr_number'),
        'delivery_id': event.get('delivery_id'),
        'event_type': event.get('event_type'),
        'action': event.get('action'),
        'sender': event.get('sender'),
        'occurred_at': event.get('received_at'),
        'snapshot': snapshot,
    }



def create_task_state(task_id: str, snapshot: dict[str, Any], latest_seq: int) -> dict[str, Any]:
    return {
        'task_id': task_id,
        'snapshot': snapshot,
        'latest_seq': latest_seq,
        'updated_at': snapshot.get('updated_at', utc_now_iso()),
        'owner_agent': None,
        'lease_until': None,
        'heartbeat_at': None,
        'phase': 'released',
        'blocked_reason': None,
    }



def lease_until_iso(seconds: int = DEFAULT_LEASE_SECONDS) -> str:
    return (utc_now() + timedelta(seconds=seconds)).isoformat()



def is_stale(task_state: dict[str, Any]) -> bool:
    owner = task_state.get('owner_agent')
    lease_until = parse_iso_datetime(task_state.get('lease_until'))
    if not owner or not lease_until:
        return False
    return lease_until <= utc_now()



def apply_stale_state(task_state: dict[str, Any]) -> dict[str, Any]:
    updated = task_state.copy()
    updated['phase'] = 'stale'
    updated['updated_at'] = utc_now_iso()
    return updated



def build_internal_task_event(
    task_id: str,
    event_type: str,
    action: str,
    agent_id: str | None,
    snapshot: dict[str, Any],
    task_state: dict[str, Any],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        'task_id': task_id,
        'repo': snapshot.get('task_id', '').split('#')[0] if snapshot.get('task_id') else None,
        'issue_number': snapshot.get('issue_number'),
        'pr_number': snapshot.get('pr_number'),
        'delivery_id': None,
        'event_type': event_type,
        'action': action,
        'sender': agent_id,
        'occurred_at': utc_now_iso(),
        'snapshot': snapshot,
        'task_state': {
            'owner_agent': task_state.get('owner_agent'),
            'lease_until': task_state.get('lease_until'),
            'heartbeat_at': task_state.get('heartbeat_at'),
            'phase': task_state.get('phase'),
            'blocked_reason': task_state.get('blocked_reason'),
            'updated_at': task_state.get('updated_at'),
        },
        'details': details or {},
    }
