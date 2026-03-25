"""Documentation routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from app import shared
from app.helpers import _build_docs_nav, _docs_by_slug, _markdown_to_html

router = APIRouter()


@router.get('/admin/docs', response_class=HTMLResponse)
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
    return shared.templates.TemplateResponse('docs.html', {'request': request, 'page': 'docs', 'sections': sections, 'query': q or '', 'quicklinks': quicklinks})


@router.get('/admin/docs/{slug}', response_class=HTMLResponse)
def admin_doc_detail(request: Request, slug: str):
    doc = _docs_by_slug().get(slug)
    if not doc:
        raise HTTPException(status_code=404, detail='Doc not found')
    try:
        markdown = doc['path'].read_text(encoding='utf-8')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Doc file missing')
    return shared.templates.TemplateResponse('doc_detail.html', {'request': request, 'page': 'docs', 'doc': doc, 'doc_html': _markdown_to_html(markdown)})
