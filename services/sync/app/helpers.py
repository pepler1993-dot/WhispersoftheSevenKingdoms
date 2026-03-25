"""Helper functions extracted from main.py."""
from __future__ import annotations

import hashlib
import html
import hmac
import json
import re
import subprocess as _sp
import markdown as _md_lib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app import shared
from app.github_sync import (
    apply_stale_state,
    build_internal_task_event,
    is_stale,
    utc_now_iso,
)


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def _human_size(size: int) -> str:
    units = ['B', 'KB', 'MB', 'GB']
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f'{value:.1f} {unit}' if unit != 'B' else f'{int(value)} B'
        value /= 1024
    return f'{value:.1f} GB'


def _format_local_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, shared.CET).strftime('%Y-%m-%d %H:%M')


def _list_library_dir(dir_path: Path, allowed_suffixes: set[str]) -> list[dict[str, str]]:
    if not dir_path.exists():
        return []
    items = []
    for f in sorted(dir_path.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not f.is_file() or f.name.startswith('.'):
            continue
        if allowed_suffixes and f.suffix.lower() not in allowed_suffixes:
            continue
        stat = f.stat()
        items.append({
            'name': f.name,
            'size': _human_size(stat.st_size),
            'modified': _format_local_ts(stat.st_mtime),
        })
    return items


def _load_house_templates() -> dict[str, Any]:
    if not shared.HOUSE_TEMPLATES_PATH.exists():
        return {}
    try:
        return json.loads(shared.HOUSE_TEMPLATES_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _build_docs_nav() -> dict[str, Any]:
    DOCS_ROOT = shared.DOCS_ROOT
    return {
        'getting-started': {
            'title': 'Getting Started',
            'subtitle': 'Schneller Einstieg für Eddi, Kevin und Iwan.',
            'items': [
                {'slug': 'quickstart', 'title': 'Quickstart', 'path': DOCS_ROOT / 'guides' / 'QUICKSTART.md', 'kind': 'Guide'},
                {'slug': 'first-local-pipeline-run', 'title': 'First Local Pipeline Run', 'path': DOCS_ROOT / 'tutorials' / 'first-local-pipeline-run.md', 'kind': 'Tutorial'},
                {'slug': 'dashboard-local-start', 'title': 'Dashboard lokal starten', 'path': DOCS_ROOT / 'tutorials' / 'dashboard-local-start.md', 'kind': 'Tutorial'},
            ],
        },
        'workflow': {
            'title': 'Workflow & Bedienung',
            'subtitle': 'Wie man mit Dashboard, Pipeline und Output arbeitet.',
            'items': [
                {'slug': 'pipeline', 'title': 'Pipeline Guide', 'path': DOCS_ROOT / 'guides' / 'PIPELINE.md', 'kind': 'Guide'},
                {'slug': 'automation', 'title': 'Automation', 'path': DOCS_ROOT / 'guides' / 'AUTOMATION.md', 'kind': 'Guide'},
                {'slug': 'song-to-output', 'title': 'Vom Song zum Output-Artefakt', 'path': DOCS_ROOT / 'tutorials' / 'song-to-output.md', 'kind': 'Tutorial'},
                {'slug': 'contributing', 'title': 'Contributing', 'path': DOCS_ROOT / 'guides' / 'CONTRIBUTING.md', 'kind': 'Guide'},
            ],
        },
        'reference': {
            'title': 'Reference',
            'subtitle': 'Technische Fakten, Struktur und Diagramme.',
            'items': [
                {'slug': 'repo-structure', 'title': 'Repo-Struktur', 'path': DOCS_ROOT / 'technical' / 'repo-structure.md', 'kind': 'Reference'},
                {'slug': 'metadata', 'title': 'Metadata', 'path': DOCS_ROOT / 'technical' / 'metadata.md', 'kind': 'Reference'},
                {'slug': 'validation', 'title': 'Validation', 'path': DOCS_ROOT / 'technical' / 'validation.md', 'kind': 'Reference'},
                {'slug': 'preflight', 'title': 'Preflight', 'path': DOCS_ROOT / 'technical' / 'preflight.md', 'kind': 'Reference'},
                {'slug': 'upload-completeness', 'title': 'Upload Completeness', 'path': DOCS_ROOT / 'technical' / 'upload-completeness.md', 'kind': 'Reference'},
                {'slug': 'architecture-diagram', 'title': 'Architecture Diagram', 'path': DOCS_ROOT / 'reference' / 'architecture-diagram.md', 'kind': 'Reference'},
                {'slug': 'architecture-overview-ref', 'title': 'Architecture Overview', 'path': DOCS_ROOT / 'explanation' / 'architecture-overview.md', 'kind': 'Overview'},
            ],
        },
        'explanation': {
            'title': 'Explanation',
            'subtitle': 'Warum das System so gebaut ist.',
            'items': [
                {'slug': 'architecture-overview', 'title': 'Architecture Overview', 'path': DOCS_ROOT / 'explanation' / 'architecture-overview.md', 'kind': 'Explanation'},
                {'slug': 'audio-strategy', 'title': 'Audio Strategy', 'path': DOCS_ROOT / 'explanation' / 'audio-strategy.md', 'kind': 'Explanation'},
            ],
        },
    }


def _docs_by_slug() -> dict[str, dict[str, Any]]:
    nav = _build_docs_nav()
    return {item['slug']: {**item, 'section': section_key, 'section_title': section['title']} for section_key, section in nav.items() for item in section['items']}


def _render_inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def _markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False
    in_code = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append('</ul>')
            in_ul = False
        if in_ol:
            out.append('</ol>')
            in_ol = False

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith('```'):
            close_lists()
            if not in_code:
                out.append('<pre class="doc-code"><code>')
                in_code = True
            else:
                out.append('</code></pre>')
                in_code = False
            continue
        if in_code:
            out.append(html.escape(raw))
            continue
        if not stripped:
            close_lists()
            continue
        if stripped.startswith('# '):
            close_lists()
            out.append(f'<h1>{_render_inline_md(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            close_lists()
            out.append(f'<h2>{_render_inline_md(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            close_lists()
            out.append(f'<h3>{_render_inline_md(stripped[4:])}</h3>')
        elif re.match(r'^[-*]\s+', stripped):
            if in_ol:
                out.append('</ol>')
                in_ol = False
            if not in_ul:
                out.append('<ul>')
                in_ul = True
            list_text = re.sub(r'^[-*]\s+', '', stripped)
            out.append(f'<li>{_render_inline_md(list_text)}</li>')
        elif re.match(r'^\d+\.\s+', stripped):
            if in_ul:
                out.append('</ul>')
                in_ul = False
            if not in_ol:
                out.append('<ol>')
                in_ol = True
            list_text = re.sub(r'^\d+\.\s+', '', stripped)
            out.append(f'<li>{_render_inline_md(list_text)}</li>')
        elif stripped.startswith('> '):
            close_lists()
            out.append(f'<blockquote>{_render_inline_md(stripped[2:])}</blockquote>')
        elif stripped.startswith('---'):
            close_lists()
            out.append('<hr />')
        else:
            close_lists()
            out.append(f'<p>{_render_inline_md(stripped)}</p>')
    close_lists()
    if in_code:
        out.append('</code></pre>')
    return '\n'.join(out)


def _get_house_template(name: str) -> dict[str, Any] | None:
    tpl = _load_house_templates()
    key = name.strip().lower().replace("'", "\u2019").replace(' ', '_')
    if key in tpl:
        return tpl[key]
    for k, v in tpl.items():
        if v.get('display_name', '').lower() == name.strip().lower():
            return v
    return None


def _detect_version() -> str:
    """Read current version from latest git tag."""
    try:
        result = _sp.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, timeout=5,
            cwd=str(shared.BASE_DIR),
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return 'dev'


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def _format_berlin(value: str | None, with_seconds: bool = False) -> str:
    dt = _parse_iso(value)
    if not dt:
        return '\u2014'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(shared.BERLIN_TZ)
    return dt.strftime('%d.%m.%Y %H:%M:%S' if with_seconds else '%d.%m.%Y %H:%M')


def _event_manager_summary(event: dict[str, Any]) -> str:
    et = event.get('event_type')
    action = event.get('action')
    sender = event.get('sender') or 'jemand'
    if et == 'issues' and action == 'opened':
        return f'Issue wurde von {sender} er\u00f6ffnet.'
    if et == 'task.claimed':
        return f'{sender} hat die Aufgabe \u00fcbernommen.'
    if et == 'task.heartbeat':
        return f'{sender} arbeitet weiter an der Aufgabe.'
    if et == 'task.released':
        return f'{sender} hat die Aufgabe wieder freigegeben.'
    if et == 'task.completed':
        return f'{sender} hat die Aufgabe als erledigt markiert.'
    if et == 'task.stale':
        return 'Ein Claim ist abgelaufen.'
    if et == 'pull_request' and action == 'opened':
        return f'{sender} hat einen Pull Request er\u00f6ffnet.'
    if et == 'pull_request' and action == 'closed':
        return 'Ein Pull Request wurde geschlossen.'
    if et == 'pull_request_review':
        return f'Ein Review von {sender} ist eingegangen.'
    return f'{et or "event"}{(" / " + action) if action else ""}'


def _phase_label(phase: str | None) -> str:
    return {
        'working': 'In Arbeit',
        'blocked': 'Blockiert',
        'released': 'Freigegeben (offen)',
        'done': 'Abgeschlossen',
        'stale': 'Abgelaufen',
        'archived': 'Archiviert',
    }.get(phase or '', phase or '\u2014')


def _extract_issue_title(detail: dict[str, Any] | None, snapshot: dict[str, Any], fallback_task_id: str) -> str | None:
    if detail:
        for event in detail.get('github_events') or []:
            payload = event.get('payload_json') or {}
            issue = payload.get('issue') or {}
            title = issue.get('title')
            if title:
                return title.strip()
    title = snapshot.get('last_summary')
    if isinstance(title, str) and title.strip():
        return title.strip()
    return None


def _extract_issue_body(detail: dict[str, Any] | None) -> str | None:
    """Extrahiere den Issue-Body f\u00fcr detailliertere Beschreibungen."""
    if not detail:
        return None
    for event in detail.get('github_events') or []:
        payload = event.get('payload_json') or {}
        issue = payload.get('issue') or {}
        body = issue.get('body')
        if body and isinstance(body, str) and body.strip():
            return body.strip()[:500] + "..." if len(body.strip()) > 500 else body.strip()
    return None


def _humanize_task_for_manager(task: dict[str, Any], detail: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = task.get('snapshot') or {}
    task_id = task.get('task_id', '')
    issue_number = snapshot.get('issue_number')
    assignment_title = _extract_issue_title(detail, snapshot, task_id)
    title = assignment_title or (f'Issue #{issue_number}' if issue_number else task_id)

    last_agent = task.get('owner_agent')
    last_action = None
    last_action_at = task.get('updated_at')
    summary = 'Noch keine verst\u00e4ndliche Zusammenfassung vorhanden.'

    if detail:
        events = detail.get('task_events') or []
        for event in reversed(events):
            agent = event.get('sender') or (event.get('task_state') or {}).get('owner_agent')
            if agent and not last_agent:
                last_agent = agent
            et = event.get('event_type')
            action = event.get('action')
            occurred_at = event.get('occurred_at') or last_action_at
            if et == 'task.claimed':
                last_action = f'Von {event.get("sender") or agent or "einem Agenten"} \u00fcbernommen'
                last_action_at = occurred_at
            elif et == 'task.released':
                who = event.get('sender') or agent or last_agent or 'ein Agent'
                last_action = f'Von {who} freigegeben'
                last_action_at = occurred_at
            elif et == 'task.completed':
                who = event.get('sender') or agent or last_agent or 'ein Agent'
                last_action = f'Von {who} als erledigt markiert'
                last_action_at = occurred_at
            elif et == 'task.heartbeat' and not last_action:
                who = event.get('sender') or agent or last_agent or 'ein Agent'
                last_action = f'{who} arbeitet daran'
                last_action_at = occurred_at
            elif et == 'issues' and action == 'opened' and not last_action:
                who = event.get('sender') or 'GitHub'
                last_action = f'Issue von {who} ge\u00f6ffnet'
                last_action_at = occurred_at
        if not last_agent:
            for event in reversed(detail.get('github_events') or []):
                if event.get('sender'):
                    last_agent = event['sender']
                    break

    phase = task.get('phase') or 'released'
    if phase == 'working':
        summary = f'{last_agent or "Ein Agent"} arbeitet aktuell daran.'
    elif phase == 'blocked':
        summary = f'Blockiert{": " + task.get("blocked_reason") if task.get("blocked_reason") else "."}'
    elif phase == 'released':
        summary = last_action or f'Zuletzt bearbeitet von {last_agent}.' if last_agent else 'Freigegeben und aktuell bei niemandem aktiv.'
    elif phase == 'done':
        summary = last_action or f'Erledigt{(" von " + last_agent) if last_agent else ""}.'
    elif phase == 'stale':
        agent_suffix = " \u2013 zuletzt bei " + last_agent if last_agent else ""
        summary = f'Claim abgelaufen{agent_suffix}.'

    # Verbesserte Fallback-Beschreibung
    if summary == 'Noch keine verst\u00e4ndliche Zusammenfassung vorhanden.':
        if detail:
            issue_body = _extract_issue_body(detail)
            if issue_body:
                summary = issue_body
            else:
                github_events = detail.get('github_events') or []
                for event in github_events:
                    payload = event.get('payload_json') or {}
                    issue = payload.get('issue') or {}
                    if issue.get('body'):
                        summary = f"Issue-Beschreibung: {issue['body'][:100]}..." if len(issue['body']) > 100 else issue['body']
                        break
                    elif event.get('event_type') == 'issues' and event.get('action') == 'opened':
                        summary = f"Neues Issue: {issue.get('title', 'Ohne Titel')}"
                        break
                    elif event.get('event_type') == 'pull_request' and event.get('action') == 'opened':
                        summary = f"Neuer Pull Request von {event.get('sender', 'einem Contributor')}"
                        break

    return {
        **task,
        'display_title': title,
        'assignment_title': assignment_title or title,
        'phase_label': _phase_label(task.get('phase')),
        'issue_url': f"https://github.com/{task_id.split('#')[0]}/issues/{issue_number}" if issue_number and '#' in task_id else None,
        'last_agent': last_agent or '\u2014',
        'summary': summary,
        'updated_at_display': _format_berlin(task.get('updated_at')),
        'lease_until_display': _format_berlin(task.get('lease_until')),
        'heartbeat_at_display': _format_berlin(task.get('heartbeat_at')),
        'last_action': last_action or '\u2014',
        'last_action_at_display': _format_berlin(last_action_at),
    }


def _humanize_task_detail_for_manager(task_id: str, detail: dict[str, Any]) -> dict[str, Any]:
    state = detail.get('state') or {}
    snapshot = detail.get('snapshot') or {}
    human = _humanize_task_for_manager(state, detail)
    task_events = []
    for event in detail.get('task_events') or []:
        actor = event.get('sender') or (event.get('task_state') or {}).get('owner_agent') or 'System'
        label = event.get('event_type') or 'event'
        action = event.get('action') or ''
        task_events.append({
            **event,
            'actor': actor,
            'display_time': _format_berlin(event.get('occurred_at'), with_seconds=True),
            'display_label': f'{label} / {action}'.strip(' /'),
            'summary': _event_manager_summary(event),
        })
    github_events = []
    for event in detail.get('github_events') or []:
        github_events.append({
            **event,
            'display_time': _format_berlin(event.get('received_at'), with_seconds=True),
            'summary': _event_manager_summary(event),
        })

    # Verbesserte detaillierte Beschreibung
    detailed_description = human.get('summary', '')
    if detail:
        issue_body = _extract_issue_body(detail)
        if issue_body and issue_body != detailed_description:
            detailed_description = issue_body

    protocol_flags: list[str] = []
    if state.get('phase') == 'stale':
        protocol_flags.append('Claim ist stale / Lease abgelaufen')
    if state.get('phase') in {'working', 'blocked'} and state.get('owner_agent') and not state.get('heartbeat_at'):
        protocol_flags.append('Aktive Aufgabe ohne Heartbeat-Zeitstempel')
    if state.get('phase') == 'released' and any(event.get('event_type') == 'task.completed' for event in detail.get('task_events') or []):
        protocol_flags.append('Task wurde completed, ist aber aktuell als released markiert')

    return {
        **detail,
        'human': human,
        'task_id': task_id,
        'state': state,
        'snapshot': snapshot,
        'task_events': task_events,
        'github_events': github_events,
        'updated_at_display': _format_berlin(state.get('updated_at'), with_seconds=True),
        'lease_until_display': _format_berlin(state.get('lease_until'), with_seconds=True),
        'heartbeat_at_display': _format_berlin(state.get('heartbeat_at'), with_seconds=True),
        'issue_number': snapshot.get('issue_number'),
        'detailed_description': detailed_description,
        'protocol_flags': protocol_flags,
    }


def verify_signature(raw_body: bytes, signature_header: str | None) -> None:
    secret = shared.settings.github_webhook_secret
    if not secret:
        raise HTTPException(status_code=500, detail='GITHUB_WEBHOOK_SECRET is not configured')
    if not signature_header:
        raise HTTPException(status_code=401, detail='Missing X-Hub-Signature-256 header')

    expected = 'sha256=' + hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail='Invalid webhook signature')


def _normalize_task_state_for_response(task_state: dict[str, Any]) -> dict[str, Any]:
    if is_stale(task_state):
        return apply_stale_state(task_state)
    return task_state


def _append_task_event(task_event: dict[str, Any] | None) -> tuple[bool, int]:
    return shared.db.append_task_event(task_event)


def _write_task_state(task_id: str, task_state: dict[str, Any]) -> None:
    shared.db.upsert_task_state(task_id, task_state)


def _mark_task_stale_if_needed(task_id: str) -> dict[str, Any] | None:
    current = shared.db.get_task_state(task_id)
    if not current or not is_stale(current) or current.get('phase') == 'stale':
        return current

    updated = apply_stale_state(current)
    _write_task_state(task_id, updated)
    task_event = build_internal_task_event(
        task_id=task_id,
        event_type='task.stale',
        action='detected',
        agent_id=current.get('owner_agent'),
        snapshot=updated.get('snapshot', {}),
        task_state=updated,
        details={'reason': 'lease_expired'},
    )
    inserted, seq = _append_task_event(task_event)
    if inserted:
        updated['latest_seq'] = seq
        _write_task_state(task_id, updated)
    return updated


def _sweep_stale_tasks() -> list[dict[str, Any]]:
    updated_tasks: list[dict[str, Any]] = []
    for task in shared.db.list_task_states(include_done=True):
        current = shared.db.get_task_state(task['task_id'])
        if not current:
            continue
        if is_stale(current) and current.get('phase') != 'stale':
            updated = _mark_task_stale_if_needed(task['task_id'])
            if updated:
                updated_tasks.append(updated)
    return updated_tasks


def _build_protocol_health() -> dict[str, Any]:
    _sweep_stale_tasks()
    tasks = shared.db.list_task_states(include_done=True)
    active_tasks = [task for task in tasks if task.get('phase') in {'working', 'blocked'}]
    stale_tasks = [task for task in tasks if task.get('phase') == 'stale']
    missing_heartbeat = [
        task for task in active_tasks
        if task.get('owner_agent') and not task.get('heartbeat_at')
    ]

    active_by_agent: dict[str, list[dict[str, Any]]] = {}
    for task in active_tasks:
        owner = task.get('owner_agent')
        if not owner:
            continue
        active_by_agent.setdefault(owner, []).append(task)

    multiple_active_assignments = [
        {
            'agent_id': agent_id,
            'count': len(agent_tasks),
            'task_ids': [task.get('task_id') for task in agent_tasks],
        }
        for agent_id, agent_tasks in active_by_agent.items()
        if len(agent_tasks) > 1
    ]

    released_after_completion = []
    for task in tasks:
        if task.get('phase') != 'released':
            continue
        events, _latest_seq = shared.db.get_task_events(task['task_id'], after_seq=0)
        if any(event.get('event_type') == 'task.completed' for event in events):
            released_after_completion.append(task)

    warnings = []
    if stale_tasks:
        warnings.append(f'{len(stale_tasks)} stale claim(s) detected')
    if missing_heartbeat:
        warnings.append(f'{len(missing_heartbeat)} active task(s) missing heartbeat timestamp')
    if multiple_active_assignments:
        warnings.append(f'{len(multiple_active_assignments)} agent(s) hold multiple active tasks')
    if released_after_completion:
        warnings.append(f'{len(released_after_completion)} task(s) were completed but are still marked released')

    status = 'ok' if not warnings else 'warn'
    return {
        'status': status,
        'warnings': warnings,
        'stale_tasks': stale_tasks,
        'missing_heartbeat': missing_heartbeat,
        'multiple_active_assignments': multiple_active_assignments,
        'released_after_completion': released_after_completion,
        'counts': {
            'stale_tasks': len(stale_tasks),
            'missing_heartbeat': len(missing_heartbeat),
            'multiple_active_assignments': len(multiple_active_assignments),
            'released_after_completion': len(released_after_completion),
        },
    }


def _get_release_notes() -> list[dict[str, str]]:
    """Parse git tags into release notes."""
    releases = []
    try:
        result = _sp.run(
            ['git', 'tag', '-l', 'v*', '--sort=-creatordate', '--format=%(refname:short)|%(creatordate:short)|%(contents)'],
            capture_output=True, text=True, timeout=10,
            cwd=str(shared.BASE_DIR),
        )
        if result.returncode != 0:
            return releases

        current: dict[str, str] | None = None
        for line in result.stdout.strip().split('\n'):
            if not line:
                if current:
                    current['body'] += '<br>'
                continue
            if '|' in line and line.startswith('v'):
                parts = line.split('|', 2)
                if len(parts) >= 2:
                    if current:
                        releases.append(current)
                    body_raw = parts[2] if len(parts) > 2 else ''
                    try:
                        body_html = _md_lib.markdown(body_raw)
                    except Exception:
                        body_html = body_raw.replace('\n', '<br>')
                    current = {
                        'tag': parts[0],
                        'date': parts[1],
                        'body': body_html,
                    }
            elif current:
                try:
                    current['body'] += _md_lib.markdown(line)
                except Exception:
                    current['body'] += '<br>' + line
        if current:
            releases.append(current)
    except Exception:
        pass
    return releases


def _split_text_list(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace('\r', '\n').replace(',', '\n')
    return [item.strip() for item in normalized.split('\n') if item.strip()]


def _build_song_metadata(
    slug: str,
    title: str,
    theme: str,
    mood: str | None,
    notes: str | None,
    duration_hint: str | None,
    tags: str | None,
    music_style: str | None,
    music_influences: str | None,
    music_tempo: str | None,
    music_energy: str | None,
    music_avoid: str | None,
    thumbnail_scene: str | None,
    thumbnail_elements: str | None,
    thumbnail_text: str | None,
    thumbnail_style: str | None,
    thumbnail_avoid: str | None,
) -> dict[str, Any]:
    return {
        'slug': slug,
        'title': title,
        'platform': 'youtube',
        'theme': theme,
        'mood': _split_text_list(mood) or ['calm'],
        'notes': (notes or '').strip(),
        'duration_hint': (duration_hint or '').strip() or 'long-form sleep track',
        'tags': _split_text_list(tags),
        'music_brief': {
            'style': (music_style or '').strip(),
            'influences': _split_text_list(music_influences),
            'tempo': (music_tempo or '').strip(),
            'energy': (music_energy or '').strip(),
            'avoid': _split_text_list(music_avoid),
        },
        'thumbnail_brief': {
            'scene': (thumbnail_scene or '').strip(),
            'elements': _split_text_list(thumbnail_elements),
            'text': (thumbnail_text or '').strip() or title,
            'style': (thumbnail_style or '').strip(),
            'avoid': _split_text_list(thumbnail_avoid),
        },
    }
