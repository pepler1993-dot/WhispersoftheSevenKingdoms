# Changelog

Alle relevanten Änderungen am Projekt werden hier dokumentiert.
Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [v2.6.0] – 2026-03-25

### Added
- **One-Click Workflow**: Audio → Pipeline → Upload in einem Rutsch
  - Orchestrator pollt automatisch und startet nächste Phase
  - Phase-Anzeige: 🎵 Audio → 🎬 Render → 📤 Upload → ✅ Fertig
  - Auto-Upload Option (opt-in)
  - Eigenes Store-Modul `stores/workflows.py`
  - Nav-Link "One-Click" in Sidebar

## [v2.5.0] – 2026-03-25

### Added
- **Pipeline Job Queue**: Warteschlange mit sequentieller Ausführung (max 1 gleichzeitig)
  - Queue-Banner auf Pipeline-Übersicht (running/waiting)
  - Cancel für queued Jobs, Auto-Recovery bei Server-Restart
  - API: `/api/pipeline/queue`
- **Thumbnail Source Tracking** (Jarvis): Quelle des Thumbnails wird erkannt + angezeigt
  - Library / Upload / Briefing / Fallback Unterscheidung
  - Live-Preview auf Create-Seite, Details auf Run-Seite

### Fixed
- `/` → `/admin` Redirect

## [v2.4.0] – 2026-03-25

### Added
- **Ticket-System**: Neuer Dashboard-Bereich `/admin/tickets` für Bugs, Features, Improvements
  - Ticket-Formular, Detailseite mit Status-Änderung, Filter nach Typ/Status
  - JSON API unter `/api/tickets`
  - Eigenes Store-Modul `stores/tickets.py` (modulare Architektur)
- **Audio Cancel Flow**: Echtes Cancellation mit State Guards (Jarvis, Co-authored)
  - Cancel-Checks an allen kritischen Stages (Kaggle + Stable Audio)
  - Final-State-Schutz (kein Cancel auf complete/cancelled/error)
  - Cancelled als eigener UI-State (Warning statt Error)
  - Cancel-Button auch im `downloading` State sichtbar

### Changed
- **Refactoring**: `main.py` von 2000 auf 85 Zeilen reduziert
  - 10 Route-Module unter `app/routes/`
  - Shared Helpers, Models, State ausgelagert
  - Arbeitsanweisung für paralleles Arbeiten (Jarvis/Pako/Smith)

### Fixed
- Python 3.11 Kompatibilität (f-string Backslash)
- Starlette 1.0 TemplateResponse Signatur-Änderung
- DB aus Git-Tracking entfernt (verhindert Merge-Korruption)
- `.venv/` in `.gitignore`

## [v2.1.0] – 2026-03-24

### Added
- Release Notes Page mit dynamischem Version-Badge (#59)
- Task-Lifecycle Dokumentation in WORKING_IN_THIS_PROJECT.md
- CHANGELOG.md

### Changed
- Mobile-responsive UI für gesamtes Dashboard (#60)
  - Tabellen werden auf Mobile zu Card-Layout
  - Buttons full-width auf kleinen Screens
  - Pipeline Create, Ops, Tasks, Library, Releases optimiert
- Version-Badge in Sidebar zeigt aktuelle Git-Tag Version

## [v2.0.0] – 2026-03-24

### Added
- **GPU Audio Worker**: Lokale Audio-Generierung mit Stable Audio Open 1.0 auf GTX 1070
- **SSH-Bridge Pipeline**: Dashboard → GPU-VM Integration via SSH + SCP
- **Library Management**: Neue `/admin/library` Seite für Songs, Thumbnails, Metadata
- **Release Notes Page**: `/admin/releases` mit automatischer Tag-Erkennung
- **Dynamischer Version Badge**: Sidebar zeigt aktuelle Version aus Git Tags
- **Task-Beschreibung**: Issue-Titel wird als Aufgabenbeschreibung in Ops angezeigt

### Changed
- `stable_audio_gen.py`: Von `stable_audio_tools` auf `diffusers` umgestellt (Python 3.13 kompatibel)
- GPU Worker IP korrigiert (192.168.178.152)
- Status-Labels: "Freigegeben" → "Freigegeben (offen)", "Erledigt" → "Abgeschlossen"
- Create-Tab verlinkt jetzt auf Library-Verwaltung

### Removed
- Kaggle als Audio-Provider (ersetzt durch lokalen GPU-Worker)

## [v1.5.0] – 2026-03-23

### Added
- Shorts Dashboard (Create, Detail, Render, Upload)
- Operations Dashboard mit Task-Tracking
- GitHub Webhook Integration
- Docs Landing Page unter Operations

