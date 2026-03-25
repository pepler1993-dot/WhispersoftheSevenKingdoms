from __future__ import annotations

import hashlib
import html
import markdown as _md_lib
import re
import subprocess as _sp
import hmac
import json
import shutil
import uuid
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Any

CET = timezone(timedelta(hours=1))

import psutil
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from app.config import get_settings
from app.github_sync import (
    DEFAULT_LEASE_SECONDS,
    apply_stale_state,
    build_event_record,
    build_internal_task_event,
    create_task_state,
    is_stale,
    lease_until_iso,
    normalize_task_event,
    update_snapshot_from_event,
    utc_now_iso,
)
from app.pipeline_runner import (
    PIPELINE_DIR,
    cancel_run,
    get_output_path,
    list_available_assets,
    list_available_themes,
    list_library_tracks_for_pipeline,
    start_run_async,
    trigger_upload,
)
from app.store import AgentSyncDB
from app.kaggle_gen import (
    create_audio_job,
    find_prompt_preset,
    get_audio_generator_health,
    list_prompt_presets,
    recover_interrupted_jobs,
)


HOUSE_TEMPLATES_PATH = Path(__file__).resolve().parent.parent / 'data' / 'house_templates.json'


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')
DOCS_ROOT = Path(__file__).resolve().parents[3] / 'docs'


def _human_size(size: int) -> str:
    units = ['B', 'KB', 'MB', 'GB']
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f'{value:.1f} {unit}' if unit != 'B' else f'{int(value)} B'
        value /= 1024
    return f'{value:.1f} GB'


def _format_local_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, CET).strftime('%Y-%m-%d %H:%M')


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
    if not HOUSE_TEMPLATES_PATH.exists():
        return {}
    try:
        return json.loads(HOUSE_TEMPLATES_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}




def _build_docs_nav() -> dict[str, Any]:
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
    key = name.strip().lower().replace("'", "'").replace(' ', '_')
    if key in tpl:
        return tpl[key]
    for k, v in tpl.items():
        if v.get('display_name', '').lower() == name.strip().lower():
            return v
    return None


class ClaimRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    lease_seconds: int = Field(default=DEFAULT_LEASE_SECONDS, ge=30, le=3600)
    phase: str = Field(default='working', min_length=1, max_length=64)
    blocked_reason: str | None = Field(default=None, max_length=500)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value not in {'working', 'blocked'}:
            raise ValueError('claim phase must be working or blocked')
        return value


class HeartbeatRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    lease_seconds: int = Field(default=DEFAULT_LEASE_SECONDS, ge=30, le=3600)
    phase: str | None = Field(default=None, min_length=1, max_length=64)
    blocked_reason: str | None = Field(default=None, max_length=500)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in {'working', 'blocked'}:
            raise ValueError('heartbeat phase must be working or blocked')
        return value


class ReleaseRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(default='released', min_length=1, max_length=64)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value != 'released':
            raise ValueError('release phase must be released')
        return value


class CompleteRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(default='done', min_length=1, max_length=64)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value != 'done':
            raise ValueError('complete phase must be done')
        return value


settings = get_settings()
db = AgentSyncDB(settings.data_dir)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))


# ── Version detection ─────────────────────────────────────────────────────

def _detect_version() -> str:
    """Read current version from latest git tag."""
    try:
        result = _sp.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, timeout=5,
            cwd=str(BASE_DIR),
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return 'dev'


APP_VERSION = _detect_version()
templates.env.globals['app_version'] = APP_VERSION


app = FastAPI(title='agent-sync-service')

BERLIN_TZ = ZoneInfo('Europe/Berlin')


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
        return '—'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(BERLIN_TZ)
    return dt.strftime('%d.%m.%Y %H:%M:%S' if with_seconds else '%d.%m.%Y %H:%M')






def _event_manager_summary(event: dict[str, Any]) -> str:
    et = event.get('event_type')
    action = event.get('action')
    sender = event.get('sender') or 'jemand'
    if et == 'issues' and action == 'opened':
        return f'Issue wurde von {sender} eröffnet.'
    if et == 'task.claimed':
        return f'{sender} hat die Aufgabe übernommen.'
    if et == 'task.heartbeat':
        return f'{sender} arbeitet weiter an der Aufgabe.'
    if et == 'task.released':
        return f'{sender} hat die Aufgabe wieder freigegeben.'
    if et == 'task.completed':
        return f'{sender} hat die Aufgabe als erledigt markiert.'
    if et == 'task.stale':
        return 'Ein Claim ist abgelaufen.'
    if et == 'pull_request' and action == 'opened':
        return f'{sender} hat einen Pull Request eröffnet.'
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
    }.get(phase or '', phase or '—')



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
    """Extrahiere den Issue-Body für detailliertere Beschreibungen."""
    if not detail:
        return None
    
    # Suche nach dem neuesten Issue-Event mit Body
    for event in detail.get('github_events') or []:
        payload = event.get('payload_json') or {}
        issue = payload.get('issue') or {}
        body = issue.get('body')
        if body and isinstance(body, str) and body.strip():
            # Kürze den Body auf eine sinnvolle Länge
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
    summary = 'Noch keine verständliche Zusammenfassung vorhanden.'

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
                last_action = f'Von {event.get("sender") or agent or "einem Agenten"} übernommen'
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
                last_action = f'Issue von {who} geöffnet'
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
        summary = f'Claim abgelaufen{(" – zuletzt bei " + last_agent) if last_agent else ""}.'
    
    # Verbesserte Fallback-Beschreibung
    if summary == 'Noch keine verständliche Zusammenfassung vorhanden.':
        if detail:
            issue_body = _extract_issue_body(detail)
            if issue_body:
                summary = issue_body
            else:
                # Suche nach sinnvollen Events für bessere Beschreibung
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
        'last_agent': last_agent or '—',
        'summary': summary,
        'updated_at_display': _format_berlin(task.get('updated_at')),
        'lease_until_display': _format_berlin(task.get('lease_until')),
        'heartbeat_at_display': _format_berlin(task.get('heartbeat_at')),
        'last_action': last_action or '—',
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
        'detailed_description': detailed_description,  # Neue detaillierte Beschreibung
        'protocol_flags': protocol_flags,
    }

app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')



def verify_signature(raw_body: bytes, signature_header: str | None) -> None:
    secret = settings.github_webhook_secret
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
    return db.append_task_event(task_event)



def _write_task_state(task_id: str, task_state: dict[str, Any]) -> None:
    db.upsert_task_state(task_id, task_state)



def _mark_task_stale_if_needed(task_id: str) -> dict[str, Any] | None:
    current = db.get_task_state(task_id)
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
    for task in db.list_task_states(include_done=True):
        current = db.get_task_state(task['task_id'])
        if not current:
            continue
        if is_stale(current) and current.get('phase') != 'stale':
            updated = _mark_task_stale_if_needed(task['task_id'])
            if updated:
                updated_tasks.append(updated)
    return updated_tasks


def _build_protocol_health() -> dict[str, Any]:
    _sweep_stale_tasks()
    tasks = db.list_task_states(include_done=True)
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
        events, _latest_seq = db.get_task_events(task['task_id'], after_seq=0)
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


@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/github/events')
def list_github_events(
    limit: int = Query(default=20, ge=1, le=200),
    task_id: str | None = Query(default=None),
) -> dict[str, Any]:
    events = db.list_github_events(limit=limit, task_id=task_id)
    return {'events': events, 'count': len(events)}


@app.get('/api/filters')
def get_filter_options():
    """Bereitstellung aller verfügbaren Filterwerte."""
    agents = db.get_unique_agents()
    phases = db.get_unique_phases()
    return {'agents': agents, 'phases': phases}


@app.get('/github/events/{delivery_id}')
def get_github_event(delivery_id: str) -> dict[str, Any]:
    event = db.get_github_event(delivery_id)
    if event:
        return event
    raise HTTPException(status_code=404, detail='Delivery not found')


@app.get('/github/tasks')
def list_github_task_snapshots(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    ordered = db.list_snapshots(task_id=task_id)
    return {'tasks': ordered, 'count': len(ordered)}


@app.get('/debug/tasks')
def debug_tasks(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    return list_github_task_snapshots(task_id=task_id)


@app.get('/github/task')
def get_github_task_snapshot(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    snapshot = db.get_snapshot(task_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail='Task snapshot not found')
    return snapshot


@app.get('/tasks')
def list_tasks(include_done: bool = Query(default=False)) -> dict[str, Any]:
    tasks = db.list_task_states(include_done=include_done)
    normalized = [_normalize_task_state_for_response(task) for task in tasks]
    return {'tasks': normalized, 'count': len(normalized)}


@app.get('/tasks/{task_id:path}/events')
def get_task_events(task_id: str, after_seq: int = Query(default=0, ge=0)) -> dict[str, Any]:
    _mark_task_stale_if_needed(task_id)
    events, latest_seq = db.get_task_events(task_id, after_seq=after_seq)
    return {
        'task_id': task_id,
        'events': events,
        'count': len(events),
        'latest_seq': latest_seq,
    }


@app.post('/tasks/{task_id:path}/claim')
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


@app.post('/tasks/{task_id:path}/heartbeat')
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


@app.post('/tasks/{task_id:path}/release')
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


@app.post('/tasks/{task_id:path}/complete')
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


@app.get('/tasks/{task_id:path}')
def get_task(task_id: str) -> dict[str, Any]:
    task = _mark_task_stale_if_needed(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task state not found')
    return _normalize_task_state_for_response(task)


@app.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request):
    protocol_health = _build_protocol_health()
    summary = db.get_dashboard_summary()
    # Activity timeline: recent pipeline runs + audio jobs
    recent_runs = db.list_runs(limit=5)
    recent_audio = db.list_audio_jobs(limit=5)
    return templates.TemplateResponse('dashboard.html', {
        'request': request,
        'page': 'dashboard',
        'summary': summary,
        'protocol_health': protocol_health,
        'recent_runs': recent_runs,
        'recent_audio': recent_audio,
    })


@app.get('/admin/tasks', response_class=HTMLResponse)
def admin_tasks(
    request: Request,
    phase: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    q: str | None = Query(default=None),
    include_done: bool = Query(default=False),
):
    tasks = [_humanize_task_for_manager(task, db.get_task_detail(task['task_id'])) for task in db.list_tasks_for_admin(phase=phase, owner=owner, query=q, include_done=include_done)]
    return templates.TemplateResponse('tasks.html', {
        'request': request,
        'page': 'ops',
        'tasks': tasks,
        'filters': {'phase': phase, 'owner': owner, 'q': q, 'include_done': include_done},
    })


@app.get('/admin/tasks/{task_id:path}', response_class=HTMLResponse)
def admin_task_detail(request: Request, task_id: str):
    detail = db.get_task_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail='Task not found')
    detail = _humanize_task_detail_for_manager(task_id, detail)
    return templates.TemplateResponse('task_detail.html', {
        'request': request,
        'page': 'ops',
        'task_id': task_id,
        'detail': detail,
    })


@app.get('/admin/events', response_class=HTMLResponse)
def admin_events(request: Request, limit: int = Query(default=100, ge=1, le=500)):
    events = db.list_github_events(limit=limit)
    return templates.TemplateResponse('events.html', {
        'request': request,
        'page': 'ops',
        'events': events,
        'limit': limit,
    })


@app.get('/admin/system', response_class=HTMLResponse)
def admin_system(request: Request):
    system = db.get_system_summary()
    protocol_health = _build_protocol_health()
    system['latest_github_event_at_display'] = _format_berlin(system.get('latest_github_event_at'), with_seconds=True)
    system['latest_task_update_at_display'] = _format_berlin(system.get('latest_task_update_at'), with_seconds=True)
    return templates.TemplateResponse('system.html', {
        'request': request,
        'page': 'ops',
        'system': system,
        'protocol_health': protocol_health,
    })


@app.post('/admin/api/backup')
def admin_api_backup():
    """Create a hot backup of the database. Returns backup path."""
    try:
        backup_path = db.backup()
        return {'status': 'ok', 'backup_path': str(backup_path), 'size_mb': round(backup_path.stat().st_size / 1024 / 1024, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Backup failed: {e}')


@app.get('/admin/ops', response_class=HTMLResponse)
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
    raw_tasks = db.list_tasks_for_admin(phase=phase, owner=owner, query=q, include_done=include_done)
    tasks = [_humanize_task_for_manager(task, db.get_task_detail(task['task_id'])) for task in raw_tasks]
    events = [{**event, 'received_at_display': _format_berlin(event.get('received_at'), with_seconds=True), 'summary': _event_manager_summary(event)} for event in db.list_github_events(limit=limit)]
    system = db.get_system_summary()
    system['latest_github_event_at_display'] = _format_berlin(system.get('latest_github_event_at'), with_seconds=True)
    system['latest_task_update_at_display'] = _format_berlin(system.get('latest_task_update_at'), with_seconds=True)
    summary = db.get_dashboard_summary()
    return templates.TemplateResponse('ops.html', {
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
    })


@app.get('/api/protocol-health')
def api_protocol_health() -> dict[str, Any]:
    return _build_protocol_health()


@app.get('/admin/api/server-stats')
def admin_server_stats():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage('/')
    load1, load5, load15 = psutil.getloadavg()
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc).isoformat()
    return {
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count(),
            'load_1m': round(load1, 2),
            'load_5m': round(load5, 2),
            'load_15m': round(load15, 2),
        },
        'memory': {
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent,
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': round(disk.used / disk.total * 100, 1),
        },
        'boot_time': boot_time,
    }


# ── audio generator ──



# ── Release Notes ─────────────────────────────────────────────────────────

def _get_release_notes() -> list[dict[str, str]]:
    """Parse git tags into release notes."""
    releases = []
    try:
        result = _sp.run(
            ['git', 'tag', '-l', 'v*', '--sort=-creatordate', '--format=%(refname:short)|%(creatordate:short)|%(contents)'],
            capture_output=True, text=True, timeout=10,
            cwd=str(BASE_DIR),
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


@app.get('/admin/releases', response_class=HTMLResponse)
def admin_releases(request: Request):
    releases = _get_release_notes()
    return templates.TemplateResponse('releases.html', {
        'request': request, 'page': 'releases', 'releases': releases,
    })


@app.get('/admin/docs', response_class=HTMLResponse)
def admin_docs(request: Request, q: str | None = Query(default=None)):
    nav = _build_docs_nav()
    query = (q or '').strip().lower()
    sections = []
    for key, section in nav.items():
        items = []
        for item in section['items']:
            summary = ''
            try:
                content = item['path'].read_text(encoding='utf-8')
                for line in content.splitlines():
                    s = line.strip()
                    if s and not s.startswith('#') and not s.startswith('```'):
                        summary = s[:180]
                        break
            except Exception:
                pass
            haystack = ' '.join([item['title'], item['kind'], summary, section['title'], section['subtitle']]).lower()
            if query and query not in haystack:
                continue
            items.append({**item, 'summary': summary})
        if items:
            sections.append({'key': key, 'title': section['title'], 'subtitle': section['subtitle'], 'items': items})
    quicklinks = [
        {'title': 'Quickstart', 'href': '/admin/docs/quickstart', 'icon': 'rocket'},
        {'title': 'Pipeline Guide', 'href': '/admin/docs/pipeline', 'icon': 'clapperboard'},
        {'title': 'Dashboard lokal starten', 'href': '/admin/docs/dashboard-local-start', 'icon': 'monitor-play'},
        {'title': 'Architecture Diagram', 'href': '/admin/docs/architecture-diagram', 'icon': 'network'},
    ]
    return templates.TemplateResponse('docs.html', {'request': request, 'page': 'docs', 'sections': sections, 'query': q or '', 'quicklinks': quicklinks})


@app.get('/admin/docs/{slug}', response_class=HTMLResponse)
def admin_doc_detail(request: Request, slug: str):
    doc = _docs_by_slug().get(slug)
    if not doc:
        raise HTTPException(status_code=404, detail='Doc not found')
    try:
        markdown = doc['path'].read_text(encoding='utf-8')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Doc file missing')
    return templates.TemplateResponse('doc_detail.html', {'request': request, 'page': 'docs', 'doc': doc, 'doc_html': _markdown_to_html(markdown)})

@app.get('/admin/audio', response_class=HTMLResponse)
def admin_audio(request: Request):
    health = get_audio_generator_health()
    presets = list_prompt_presets()
    jobs = db.list_audio_jobs(limit=100)
    return templates.TemplateResponse('audio_generator.html', {
        'request': request,
        'page': 'audio',
        'health': health,
        'presets': presets,
        'jobs': jobs,
        'house_templates': _load_house_templates(),
    })


@app.get('/admin/library', response_class=HTMLResponse)
def admin_library(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    songs = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'})
    thumbnails = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'thumbnails', {'.jpg', '.jpeg', '.png', '.webp'})
    metadata = _list_library_dir(PIPELINE_DIR / 'data' / 'upload' / 'metadata', {'.json', '.md'})
    return templates.TemplateResponse('library.html', {
        'request': request,
        'page': 'library',
        'songs': songs,
        'thumbnails': thumbnails,
        'metadata': metadata,
        'success_message': success or '',
        'error_message': error or '',
    })


@app.post('/admin/library/upload')
async def admin_library_upload(asset_type: str = Form(...), file: UploadFile = File(...)):
    mapping = {
        'songs': (PIPELINE_DIR / 'data' / 'upload' / 'songs', {'.mp3', '.wav', '.ogg'}),
        'thumbnails': (PIPELINE_DIR / 'data' / 'upload' / 'thumbnails', {'.jpg', '.jpeg', '.png', '.webp'}),
        'metadata': (PIPELINE_DIR / 'data' / 'upload' / 'metadata', {'.json', '.md'}),
    }
    if asset_type not in mapping:
        return RedirectResponse('/admin/library?error=Ung%C3%BCltiger+Asset-Typ', status_code=303)
    target_dir, allowed = mapping[asset_type]
    filename = Path(file.filename or '').name
    if not filename:
        return RedirectResponse('/admin/library?error=Dateiname+fehlt', status_code=303)
    if Path(filename).suffix.lower() not in allowed:
        return RedirectResponse('/admin/library?error=Dateityp+nicht+erlaubt', status_code=303)
    target_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    (target_dir / filename).write_bytes(content)
    return RedirectResponse(f'/admin/library?success={asset_type}+Datei+{filename}+hochgeladen', status_code=303)


@app.get('/admin/library/preview/{asset_type}/{filename}')
def admin_library_preview(asset_type: str, filename: str):
    mapping = {
        'songs': PIPELINE_DIR / 'data' / 'upload' / 'songs',
        'thumbnails': PIPELINE_DIR / 'data' / 'upload' / 'thumbnails',
        'metadata': PIPELINE_DIR / 'data' / 'upload' / 'metadata',
    }
    if asset_type not in mapping:
        raise HTTPException(status_code=404, detail='Asset type not found')
    path = mapping[asset_type] / Path(filename).name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@app.get('/admin/shorts', response_class=HTMLResponse)
def admin_shorts(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    library_tracks = list_library_tracks_for_pipeline(db)
    short_runs = [run for run in db.list_runs(limit=100) if (run.get('config') or {}).get('content_type') == 'short']
    return templates.TemplateResponse('shorts.html', {
        'request': request,
        'page': 'shorts',
        'library_tracks': library_tracks,
        'short_runs': short_runs[:20],
        'success_message': success or '',
        'error_message': error or '',
    })


@app.post('/admin/shorts/create')
def admin_shorts_create(
    source_audio: str = Form(...),
    title: str = Form(...),
    slug: str = Form(''),
    clip_start_seconds: int = Form(0),
    clip_duration_seconds: int = Form(30),
    visual_mode: str = Form('static-artwork'),
    visibility: str = Form('private'),
):
    source_audio = source_audio.strip()
    title = title.strip()
    slug = slugify(slug.strip() or title)

    if not source_audio:
        raise HTTPException(status_code=400, detail='Quelle für Audio ist erforderlich')
    if not title:
        raise HTTPException(status_code=400, detail='Titel ist erforderlich')
    if not slug:
        raise HTTPException(status_code=400, detail='Slug ist erforderlich')
    if clip_start_seconds < 0:
        raise HTTPException(status_code=400, detail='Clip-Start darf nicht negativ sein')
    if clip_duration_seconds < 15 or clip_duration_seconds > 60:
        raise HTTPException(status_code=400, detail='Clip-Länge muss zwischen 15 und 60 Sekunden liegen')
    if visual_mode not in {'static-artwork', 'blurred-background', 'cinematic-gradient'}:
        raise HTTPException(status_code=400, detail='Ungültiger Visual Mode')
    if visibility not in {'private', 'unlisted', 'public'}:
        raise HTTPException(status_code=400, detail='Ungültige Sichtbarkeit')

    source_path = PIPELINE_DIR / 'data' / 'upload' / 'songs' / source_audio
    if not source_path.exists():
        raise HTTPException(status_code=400, detail='Gewählte Audio-Datei existiert nicht')

    now = datetime.now(CET).isoformat()
    run_id = uuid.uuid4().hex[:12]
    metadata = {
        'slug': slug,
        'title': title,
        'platform': 'youtube',
        'content_type': 'short',
        'source_audio': source_audio,
        'clip_start_seconds': clip_start_seconds,
        'clip_duration_seconds': clip_duration_seconds,
        'visual_mode': visual_mode,
        'visibility': visibility,
        'hashtags': ['shorts'],
    }

    metadata_dir = PIPELINE_DIR / 'data' / 'upload' / 'shorts' / 'metadata'
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_dir / f'{slug}.json'
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    config = {
        'content_type': 'short',
        'format': 'youtube_short',
        'aspect_ratio': '9:16',
        'source_audio': source_audio,
        'source_audio_path': str(source_path),
        'clip_start_seconds': clip_start_seconds,
        'clip_duration_seconds': clip_duration_seconds,
        'visual_mode': visual_mode,
        'visibility': visibility,
        'metadata_path': str(metadata_path),
    }

    db.create_run({
        'run_id': run_id,
        'slug': slug,
        'title': title,
        'status': 'created',
        'config': config,
        'created_at': now,
    })
    db.append_run_log(run_id, 'system', f'Short draft created from {source_audio}', now)
    db.append_run_log(run_id, 'system', f'Clip window: start={clip_start_seconds}s duration={clip_duration_seconds}s', now)
    db.append_run_log(run_id, 'system', f'Visual mode: {visual_mode} · visibility: {visibility}', now)

    return RedirectResponse(url=f'/admin/shorts/{run_id}?success=Short-Entwurf+{slug}+wurde+angelegt', status_code=303)


@app.get('/admin/shorts/{run_id}', response_class=HTMLResponse)
def admin_shorts_detail(request: Request, run_id: str, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    run = db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    logs = db.get_run_logs(run_id, limit=1000)
    output_files: list[dict[str, str]] = []
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / run['slug']
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({'name': f.name, 'size': f'{f.stat().st_size / 1024 / 1024:.1f} MB'})
    return templates.TemplateResponse('short_detail.html', {
        'request': request,
        'page': 'shorts',
        'run': run,
        'logs': logs,
        'output_files': output_files,
        'success_message': success or '',
        'error_message': error or '',
    })


@app.post('/admin/shorts/{run_id}/render')
def admin_shorts_render(run_id: str):
    run = db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    if run['status'] not in {'created', 'failed'}:
        raise HTTPException(status_code=409, detail=f'Cannot render short from status {run["status"]}')

    now = datetime.now(CET).isoformat()
    config = run.get('config', {})
    db.update_run(run_id, status='running', started_at=now, error_message=None)
    db.append_run_log(run_id, 'system', 'Short render requested from dashboard', now)
    db.append_run_log(run_id, 'system', f"Source audio: {config.get('source_audio')}", now)
    db.append_run_log(run_id, 'system', f"Clip window: {config.get('clip_start_seconds', 0)}s → +{config.get('clip_duration_seconds', 30)}s", now)
    db.append_run_log(run_id, 'system', f"Visual mode: {config.get('visual_mode', 'static-artwork')}", now)
    db.append_run_log(run_id, 'system', 'Render backend for Shorts is not wired yet — this draft is now queued for implementation.', now)
    db.update_run(run_id, status='queued')

    return RedirectResponse(url=f'/admin/shorts/{run_id}?success=Short-Render+wurde+angestoßen', status_code=303)


@app.get('/admin/shorts/{run_id}/logs')
def admin_shorts_logs(run_id: str, after_id: int = Query(default=0, ge=0)):
    run = db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    logs = db.get_run_logs(run_id, after_id=after_id)
    return JSONResponse({'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')})


@app.post('/admin/shorts/{run_id}/upload')
def admin_shorts_upload(run_id: str):
    run = db.get_run(run_id)
    if not run or (run.get('config') or {}).get('content_type') != 'short':
        raise HTTPException(status_code=404, detail='Short run not found')
    if run['status'] != 'rendered':
        raise HTTPException(status_code=409, detail=f'Cannot upload short from status {run["status"]}')

    slug = run['slug']
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'shorts' / slug
    video_path = output_dir / 'video.mp4'
    metadata_path = output_dir / 'metadata.json'
    if not video_path.exists() or not metadata_path.exists():
        raise HTTPException(status_code=400, detail='Rendered short output is incomplete')

    run_cfg = run.get('config', {})
    cmd = [
        sys.executable,
        str(PIPELINE_DIR / 'pipeline' / 'scripts' / 'publish' / 'youtube_upload.py'),
        '--video', str(video_path),
        '--metadata', str(metadata_path),
    ]
    if run_cfg.get('visibility') == 'public':
        cmd.append('--public')

    db.update_run(run_id, status='uploading', error_message=None)
    cmd_str = ' '.join(cmd)
    db.append_run_log(run_id, 'system', f'Starting Shorts upload: {cmd_str}', datetime.now(CET).isoformat())

    def worker():
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(PIPELINE_DIR))
        except Exception as exc:
            db.update_run(run_id, status='rendered', error_message=f'Upload start failed: {exc}')
            db.append_run_log(run_id, 'system', f'Upload start failed: {exc}', datetime.now(CET).isoformat())
            return
        t_out, t_err = _append_process_logs(run_id, proc)
        code = proc.wait()
        t_out.join(timeout=5)
        t_err.join(timeout=5)
        now = datetime.now(CET).isoformat()
        if code == 0:
            db.update_run(run_id, status='uploaded', finished_at=now, error_message=None)
            db.append_run_log(run_id, 'system', 'Short uploaded successfully', now)
        else:
            db.update_run(run_id, status='rendered', error_message=f'Shorts upload failed (exit {code})')
            db.append_run_log(run_id, 'system', f'Shorts upload failed with exit code {code}', now)

    threading.Thread(target=worker, daemon=True).start()
    return RedirectResponse(url=f'/admin/shorts/{run_id}?success=Short-Upload+wurde+gestartet', status_code=303)


@app.get('/admin/shorts/preview/{slug}/{filename}')
def admin_shorts_preview_file(slug: str, filename: str):
    path = PIPELINE_DIR / 'data' / 'output' / 'shorts' / slug / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@app.post('/admin/audio/generate')
def admin_audio_generate(
    slug: str = Form(...),
    title: str = Form(''),
    prompt_text: str = Form(''),
    preset_name: str = Form(''),
    minutes: int = Form(42),
    model: str = Form('medium'),
    clip_seconds: int = Form(30),
):
    slug = slug.strip().lower()
    title = title.strip() or slug.replace('-', ' ').title()
    preset_name = preset_name.strip()
    prompt_text = prompt_text.strip()

    if not slug:
        raise HTTPException(status_code=400, detail='Slug is required')
    if not prompt_text and not preset_name:
        raise HTTPException(status_code=400, detail='Provide prompt text or choose a preset')
    if preset_name and not find_prompt_preset(preset_name):
        raise HTTPException(status_code=400, detail='Unknown preset selected')

    job_id = create_audio_job(
        slug=slug,
        title=title,
        prompt_text=prompt_text,
        preset_name=preset_name or None,
        minutes=minutes,
        model=model,
        clip_seconds=clip_seconds,
        db=db,
    )
    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)


@app.get('/admin/audio/jobs/{job_id}', response_class=HTMLResponse)
def admin_audio_job_detail(request: Request, job_id: str):
    job = db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    logs = db.get_audio_job_logs(job_id, limit=1000)
    return templates.TemplateResponse('audio_job_detail.html', {
        'request': request,
        'page': 'audio',
        'job': job,
        'logs': logs,
    })


@app.get('/admin/audio/stream/{job_id}')
def admin_audio_stream(job_id: str):
    """Stream audio file for in-browser playback."""
    job = db.get_audio_job(job_id)
    if not job or not job.get('output_path'):
        raise HTTPException(status_code=404, detail='Audio file not found')
    audio_path = Path(job['output_path'])
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail='Audio file missing from disk')
    return FileResponse(audio_path, media_type='audio/wav', filename=audio_path.name)


@app.get('/admin/audio/jobs/{job_id}/logs')
def admin_audio_job_logs(job_id: str, after_id: int = Query(default=0, ge=0)):
    job = db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    logs = db.get_audio_job_logs(job_id, after_id=after_id)
    return {'logs': logs, 'status': job['status'], 'error_message': job.get('error_message')}


@app.post('/admin/audio/jobs/{job_id}/cancel')
def admin_audio_job_cancel(job_id: str):
    job = db.get_audio_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Audio job not found')
    db.update_audio_job(job_id, status='cancelled', finished_at=datetime.now(CET).isoformat(), error_message='Cancelled by user')
    db.append_audio_job_log(job_id, 'system', 'Cancellation requested by user', datetime.now(CET).isoformat())
    return RedirectResponse(url=f'/admin/audio/jobs/{job_id}', status_code=303)


# ── pipeline control panel ──

ALLOWED_AUDIO_EXT = {'.mp3', '.wav', '.ogg'}
ALLOWED_THUMB_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB


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


@app.get('/admin/pipeline', response_class=HTMLResponse)
def admin_pipeline(request: Request):
    runs = db.list_runs(limit=100)
    houses = _load_house_templates()
    return templates.TemplateResponse('pipeline_runs.html', {
        'request': request,
        'page': 'pipeline',
        'runs': runs,
        'houses': houses,
    })


@app.get('/admin/pipeline/new', response_class=HTMLResponse)
def admin_pipeline_new(request: Request, slug: str | None = Query(default=None), error: str | None = Query(default=None)):
    assets = list_available_assets()
    themes = list_available_themes()
    houses = _load_house_templates()
    library_tracks = list_library_tracks_for_pipeline(db)
    # Thumbnails from data/output/thumbnails/
    thumb_dir = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'output' / 'thumbnails'
    library_thumbnails = sorted(f.name for f in thumb_dir.iterdir() if f.is_file() and f.suffix in {'.jpg', '.jpeg', '.png', '.webp'}) if thumb_dir.exists() else []
    return templates.TemplateResponse('pipeline_new.html', {
        'request': request,
        'page': 'pipeline',
        'assets': assets,
        'themes': themes,
        'houses': houses,
        'library_tracks': library_tracks,
        'library_thumbnails': library_thumbnails,
        'prefill_slug': (slug or '').strip().lower(),
        'error_message': error or '',
    })


@app.get('/admin/api/house/{name}')
def api_house_template(name: str):
    tpl = _get_house_template(name)
    if not tpl:
        raise HTTPException(status_code=404, detail='House template not found')
    return tpl


@app.post('/admin/pipeline/upload-asset')
async def admin_pipeline_upload_asset(
    asset_type: str = Form(...),
    slug: str = Form(...),
    file: UploadFile = File(...),
):
    slug = slug.strip().lower()
    if not slug:
        raise HTTPException(status_code=400, detail='Slug is required')

    upload_dir = PIPELINE_DIR / 'data' / 'upload'

    if asset_type == 'audio':
        ext = Path(file.filename or '').suffix.lower()
        if ext not in ALLOWED_AUDIO_EXT:
            raise HTTPException(status_code=400, detail=f'Audio must be {", ".join(ALLOWED_AUDIO_EXT)}')
        target = upload_dir / 'songs' / f'{slug}{ext}'
    elif asset_type == 'thumbnail':
        ext = Path(file.filename or '').suffix.lower()
        if ext not in ALLOWED_THUMB_EXT:
            raise HTTPException(status_code=400, detail=f'Thumbnail must be {", ".join(ALLOWED_THUMB_EXT)}')
        target = upload_dir / 'thumbnails' / f'{slug}{ext}'
    else:
        raise HTTPException(status_code=400, detail='asset_type must be audio or thumbnail')

    target.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail='File too large (max 500MB)')

    target.write_bytes(content)
    return {'ok': True, 'path': str(target.relative_to(PIPELINE_DIR)), 'size': len(content)}


@app.get('/admin/pipeline/assets')
def admin_pipeline_assets():
    return list_available_assets()


@app.post('/admin/pipeline/start')
def admin_pipeline_start(
    slug: str = Form(''),  # ignored – always generated from title
    title: str = Form(...),
    theme: str = Form(...),
    minutes: int = Form(42),
    loop_hours: float = Form(0),
    crossfade: int = Form(8),
    audio_preset: str = Form('ambient'),
    animated: bool = Form(False),
    public: bool = Form(False),
    skip_post_process: bool = Form(False),
    mood: str = Form(''),
    notes: str = Form(''),
    duration_hint: str = Form('long-form sleep track'),
    tags: str = Form(''),
    music_style: str = Form(''),
    music_influences: str = Form(''),
    music_tempo: str = Form(''),
    music_energy: str = Form(''),
    music_avoid: str = Form(''),
    thumbnail_scene: str = Form(''),
    thumbnail_elements: str = Form(''),
    thumbnail_text: str = Form(''),
    thumbnail_style: str = Form(''),
    thumbnail_avoid: str = Form(''),
    house: str = Form(''),
):
    title = title.strip()
    slug = slugify(title)  # always auto-generated from title
    theme = theme.strip()
    if not slug:
        raise HTTPException(status_code=400, detail='Title must produce a valid slug')
    if not title:
        raise HTTPException(status_code=400, detail='Title is required')
    if not theme:
        raise HTTPException(status_code=400, detail='Theme is required')

    audio_found = any(
        (PIPELINE_DIR / 'data' / 'upload' / 'songs' / f'{slug}{ext}').exists()
        for ext in ALLOWED_AUDIO_EXT
    )
    if not audio_found:
        return RedirectResponse(
            url=f'/admin/pipeline/new?slug={slug}&error=Kein+Audio-Track+für+"{slug}"+gefunden.+Generiere+zuerst+einen+Track+im+Audio+Lab.',
            status_code=303,
        )

    metadata = _build_song_metadata(
        slug=slug,
        title=title,
        theme=theme,
        mood=mood,
        notes=notes,
        duration_hint=duration_hint,
        tags=tags,
        music_style=music_style,
        music_influences=music_influences,
        music_tempo=music_tempo,
        music_energy=music_energy,
        music_avoid=music_avoid,
        thumbnail_scene=thumbnail_scene,
        thumbnail_elements=thumbnail_elements,
        thumbnail_text=thumbnail_text,
        thumbnail_style=thumbnail_style,
        thumbnail_avoid=thumbnail_avoid,
    )

    metadata_path = PIPELINE_DIR / 'data' / 'upload' / 'metadata' / f'{slug}.json'
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    config = {
        'minutes': minutes,
        'loop_hours': loop_hours,
        'crossfade': crossfade,
        'audio_preset': audio_preset,
        'animated': animated,
        'public': public,
        'skip_post_process': skip_post_process,
        'mood': mood or None,
        'house': house or theme or None,
        'metadata': metadata,
    }

    run_id = uuid.uuid4().hex[:12]
    now = datetime.now(CET).isoformat()

    db.create_run({
        'run_id': run_id,
        'slug': slug,
        'title': title,
        'status': 'created',
        'config': config,
        'created_at': now,
    })

    start_run_async(run_id, slug, config, db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.get('/admin/pipeline/run/{run_id}', response_class=HTMLResponse)
def admin_pipeline_run_detail(request: Request, run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = db.get_run_logs(run_id, limit=1000)

    output_files: list[dict[str, str]] = []
    output_dir = PIPELINE_DIR / 'data' / 'output' / 'youtube' / run['slug']
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({'name': f.name, 'size': f'{f.stat().st_size / 1024 / 1024:.1f} MB'})

    return templates.TemplateResponse('pipeline_run_detail.html', {
        'request': request,
        'page': 'pipeline',
        'run': run,
        'logs': logs,
        'output_files': output_files,
    })


@app.get('/admin/pipeline/run/{run_id}/logs')
def admin_pipeline_run_logs(run_id: str, after_id: int = Query(default=0, ge=0)):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    logs = db.get_run_logs(run_id, after_id=after_id)
    return {'logs': logs, 'status': run['status'], 'error_message': run.get('error_message')}


@app.post('/admin/pipeline/run/{run_id}/upload')
def admin_pipeline_run_upload(run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] not in {'rendered', 'failed'}:
        raise HTTPException(status_code=409, detail=f'Cannot upload from status {run["status"]}')

    trigger_upload(run_id, run['slug'], run.get('config', {}), db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.post('/admin/pipeline/run/{run_id}/cancel')
def admin_pipeline_run_cancel(run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] != 'running':
        raise HTTPException(status_code=409, detail='Can only cancel running pipelines')
    cancel_run(run_id, db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.get('/admin/pipeline/preview/{slug}/{filename}')
def admin_pipeline_preview_file(slug: str, filename: str):
    path = get_output_path(slug, filename)
    if not path:
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@app.post('/github/webhook')
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
    was_inserted = db.insert_github_event(event_record)

    snapshot_updated = False
    updated_snapshot: dict[str, Any] | None = None
    task_id = event_record.get('task_id')
    if task_id:
        existing_snapshot = db.get_snapshot(task_id)
        updated_snapshot = update_snapshot_from_event(existing_snapshot, event_record)
        if updated_snapshot:
            db.upsert_snapshot(updated_snapshot)
            snapshot_updated = True

    normalized_event = normalize_task_event(event_record, updated_snapshot)
    task_event_inserted, assigned_seq = _append_task_event(normalized_event)

    task_state_updated = False
    if normalized_event and updated_snapshot and assigned_seq:
        existing = db.get_task_state(normalized_event['task_id'])
        if existing:
            task_state = existing.copy()
            task_state['snapshot'] = updated_snapshot
            task_state['latest_seq'] = assigned_seq
            task_state['updated_at'] = updated_snapshot.get('updated_at', utc_now_iso())
        else:
            task_state = create_task_state(normalized_event['task_id'], updated_snapshot, assigned_seq)
        db.upsert_task_state(normalized_event['task_id'], task_state)
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


@app.post('/admin/pipeline/run/{run_id}/cancel')
def admin_pipeline_run_cancel(run_id: str):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail='Run not found')
    if run['status'] != 'running':
        raise HTTPException(status_code=409, detail='Can only cancel running pipelines')
    cancel_run(run_id, db)
    return RedirectResponse(url=f'/admin/pipeline/run/{run_id}', status_code=303)


@app.get('/admin/pipeline/preview/{slug}/{filename}')
def admin_pipeline_preview_file(slug: str, filename: str):
    path = get_output_path(slug, filename)
    if not path:
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path)


@app.post('/github/webhook')
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
    was_inserted = db.insert_github_event(event_record)

    snapshot_updated = False
    updated_snapshot: dict[str, Any] | None = None
    task_id = event_record.get('task_id')
    if task_id:
        existing_snapshot = db.get_snapshot(task_id)
        updated_snapshot = update_snapshot_from_event(existing_snapshot, event_record)
        if updated_snapshot:
            db.upsert_snapshot(updated_snapshot)
            snapshot_updated = True

    normalized_event = normalize_task_event(event_record, updated_snapshot)
    task_event_inserted, assigned_seq = _append_task_event(normalized_event)

    task_state_updated = False
    if normalized_event and updated_snapshot and assigned_seq:
        existing = db.get_task_state(normalized_event['task_id'])
        if existing:
            task_state = existing.copy()
            task_state['snapshot'] = updated_snapshot
            task_state['latest_seq'] = assigned_seq
            task_state['updated_at'] = updated_snapshot.get('updated_at', utc_now_iso())
        else:
            task_state = create_task_state(normalized_event['task_id'], updated_snapshot, assigned_seq)
        db.upsert_task_state(normalized_event['task_id'], task_state)
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


