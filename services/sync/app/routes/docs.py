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
    query_terms = [t for t in query.split() if t]
    sections = []
    total_results = 0
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
            except OSError:
                pass
            title_l = item['title'].lower()
            kind_l = item['kind'].lower()
            summary_l = summary.lower()
            section_l = f"{section['title']} {section['subtitle']}".lower()
            haystack = ' '.join([title_l, kind_l, summary_l, section_l])

            score = 0
            matched_terms: list[str] = []
            if query_terms:
                for term in query_terms:
                    if term in title_l:
                        score += 3
                        matched_terms.append(term)
                    elif term in summary_l:
                        score += 2
                        matched_terms.append(term)
                    elif term in haystack:
                        score += 1
                        matched_terms.append(term)
                if score == 0:
                    continue
            items.append({**item, 'summary': summary, 'score': score, 'matched_terms': sorted(set(matched_terms))})
        if query_terms:
            items.sort(key=lambda i: i.get('score', 0), reverse=True)
        if items:
            total_results += len(items)
            sections.append({'key': key, 'title': section['title'], 'subtitle': section['subtitle'], 'items': items})
    quicklinks = [
        {'title': 'Quickstart', 'href': '/admin/docs/quickstart', 'icon': 'rocket'},
        {'title': 'Pipeline Guide', 'href': '/admin/docs/pipeline', 'icon': 'clapperboard'},
        {'title': 'Dashboard lokal starten', 'href': '/admin/docs/dashboard-local-start', 'icon': 'monitor-play'},
        {'title': 'Architecture Diagram', 'href': '/admin/docs/architecture-diagram', 'icon': 'network'},
    ]
    return shared.templates.TemplateResponse(
        request,
        'docs.html',
        {
            'page': 'docs',
            'sections': sections,
            'query': q or '',
            'quicklinks': quicklinks,
            'total_results': total_results,
        },
    )


@router.get('/admin/docs/{slug}', response_class=HTMLResponse)
def admin_doc_detail(request: Request, slug: str):
    doc = _docs_by_slug().get(slug)
    if not doc:
        raise HTTPException(status_code=404, detail='Doc not found')
    try:
        markdown = doc['path'].read_text(encoding='utf-8')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Doc file missing')
    return shared.templates.TemplateResponse(request, 'doc_detail.html', {'page': 'docs', 'doc': doc, 'doc_html': _markdown_to_html(markdown)})
