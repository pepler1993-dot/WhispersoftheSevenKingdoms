# Baseline & Freeze Rules

## Baseline Tag

**Tag:** `current-internal-tool-baseline`  
**Datum:** 2026-03-29  
**Commit:** Aktueller `main` Stand nach Audio v2 Quality Improvements

## Was heute produktiv genutzt wird

| Komponente | Status | Beschreibung |
|---|---|---|
| **Sync Dashboard** (FastAPI) | ✅ Produktiv | Web-UI für Video-Erstellung, Audio-Jobs, Library, Workflows |
| **Audio Generator** (Stable Audio) | ✅ Produktiv | GPU-Worker-basierte Clip-Generierung via SSH/Daemon |
| **Video Renderer** (ffmpeg) | ✅ Produktiv | Hintergrund + Audio → MP4 Rendering |
| **YouTube Upload** | ✅ Produktiv | OAuth2-basierter Upload mit Metadata |
| **Post-Processing** (ffmpeg) | ✅ Produktiv | EQ, Reverb, Loudnorm, Limiter |
| **Loop Audio** (ffmpeg) | ✅ Produktiv | Crossfade-Loop auf 3h Zieldauer |
| **House Templates** (JSON) | ✅ Produktiv | 10 Häuser × 5 Varianten mit Prompts, Thumbnails, Configs |
| **Shorts Generator** | ✅ Produktiv | YouTube Shorts aus bestehendem Content |

## Was experimentell ist

| Komponente | Status | Beschreibung |
|---|---|---|
| **Audio v2 Features** | 🧪 Experimentell | Clip-Roles, Similarity-Stitching, Sleep-first Prompts, 47s Clips, 60min Unique |
| **SaaS-Konzept** | 📋 Konzeptphase | Roadmap und Konzeptdokumente vorhanden, keine Implementierung |
| **Analytics Integration** | 📋 Geplant | YouTube API Views/Revenue (#90) |
| **Content Scheduling** | 📋 Geplant | Calendar-Integration (#89) |
| **Approval Flow** | 📋 Geplant | Review-Workflow (#88) |

## Was eingefroren wird

Ab diesem Baseline-Tag gelten folgende Regeln:

1. **Keine strukturellen Änderungen** an der Datenbank-Schicht ohne Review
2. **Keine neuen externen Abhängigkeiten** ohne vorherige Diskussion
3. **OAuth/Secrets-Handling** nicht ändern ohne Security-Review (#136)
4. **Pipeline-Runner** (subprocess-basiert) bleibt stabil bis Architektur-Review abgeschlossen

## Branch- und PR-Regeln

### Ab sofort gilt:

1. **Kein direkter Push auf `main`** für Feature-Arbeit
   - Ausnahme: Hotfixes und Dokumentation
2. **Feature-Branches** verwenden: `feature/<beschreibung>` oder `fix/<beschreibung>`
3. **PRs müssen reviewed werden** bevor sie nach main gemerged werden
   - Owner erstellt PR
   - Reviewer (siehe Issue) gibt Approval
4. **Commit-Messages** folgen dem Format: `type(scope): beschreibung`
   - Types: `feat`, `fix`, `docs`, `refactor`, `chore`
5. **Tags** für Releases: `vX.Y.Z` mit CHANGELOG-Eintrag

### Reviewer-Matrix:

| Wer erstellt | Wer reviewed |
|---|---|
| Smith (Agent) | Jarvis / Eddi |
| Jarvis (Agent) | Smith / Eddi |
| Eddi | Smith oder Jarvis |
| Kevin | Eddi oder Agent |
