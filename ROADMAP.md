# Roadmap – Whisper Studio
> Stand: 28.03.2026

## Aktuelle Prioritäten

### 1. UI/UX Production-Ready (Phase 3d) 🔄
- Alle Seiten konsistent nach Design Principles
- Haus/Varianten-Cards mit Hintergrundbildern ✅
- Step-Indicator + Review-Summary im Create-Flow ✅
- Status-Mapping auf 5 UI-Status ✅
- Pagination/Show-More für lange Listen ✅
- Detail-Seiten aufgeräumt ✅
- Weiter: Settings, Shorts, Detail-Pages polieren

### 2. API absichern
- Token-Auth für alle POST-Endpoints
- Service-Tokens für AI-Agents
- Rate Limiting

### 3. Songs MVP
- Standalone Audio → Export als MP3/WAV
- Eigene Songs-Seite fertig bauen

### 4. Landing Page
- whisperstudio.io oder ähnlich
- Pricing Page
- Demo Video

### 5. Infra
- Domain dashboard.ka189.de via Cloudflare
- Docker Deployment
- Tests (Auth + Workflows + Migration)

## Erledigte Meilensteine

- ✅ GPU Audio Worker (Stable Audio Open, GTX 1070)
- ✅ End-to-End Pipeline (Audio → Video → YouTube)
- ✅ Dashboard mit Auth + Team Management
- ✅ Unified Workflow Architecture
- ✅ Dashboard Redesign (SaaS Command Center)
- ✅ Shorts-Flow
- ✅ Presets + House Templates
- ✅ CI/CD (GitHub Actions → SSH → PVE)

## Spätere Phasen

Siehe [SAAS_CONCEPT.md](docs/SAAS_CONCEPT.md) für:
- Phase 4: Onboarding & Self-Service
- Phase 5: Billing (Stripe)
- Phase 6: Managed GPU
- Phase 7: Multi-Platform Publishing
- Phase 8: AI Automation
- Phase 9: Enterprise & White-Label
