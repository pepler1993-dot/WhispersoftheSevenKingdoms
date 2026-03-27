"""Helper functions for the Whisper Studio dashboard."""
from __future__ import annotations

import html
import json
import re
import subprocess as _sp
import markdown as _md_lib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app import shared


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
    except (OSError, _sp.TimeoutExpired):
        pass
    return 'dev'


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def _format_berlin(value: str | None, with_seconds: bool = False) -> str:
    dt = _parse_iso(value)
    if not dt:
        return '\u2014'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(shared.BERLIN_TZ)
    return dt.strftime('%d.%m.%Y %H:%M:%S' if with_seconds else '%d.%m.%Y %H:%M')


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
                    except (ValueError, TypeError):
                        body_html = body_raw.replace('\n', '<br>')
                    current = {
                        'tag': parts[0],
                        'date': parts[1],
                        'body': body_html,
                    }
            elif current:
                try:
                    current['body'] += _md_lib.markdown(line)
                except (ValueError, TypeError):
                    current['body'] += '<br>' + line
        if current:
            releases.append(current)
    except (OSError, _sp.TimeoutExpired) as exc:
        import logging
        logging.warning('Failed to read release notes: %s', exc)
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
