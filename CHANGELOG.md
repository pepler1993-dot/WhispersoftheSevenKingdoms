# Changelog

Alle relevanten Änderungen am Projekt werden hier dokumentiert.
Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [v2.9.0] – 2026-03-25

### Added
- **Alle 9 GoT-Häuser + The Wall**: Stark 🐺, Lannister 🦁, Targaryen 🐉, Baratheon 🦌, Arryn 🦅, Tully 🪼, Tyrell 🌹, Greyjoy 🐙, Martell ☀️, The Wall 🧊
- **5 Varianten pro Haus**: Verschiedene Stimmungen/Orte zum Auswählen
- **House-Presets**: Defaults für Dauer, Loop, Crossfade, Musik-Stil, Thumbnail aus Haus-Config
- Motto, Sitz, Sigil für jedes Haus

### Changed
- **Animiertes Video** ist jetzt Default (vorher unchecked)
- Animated + Public Checkboxen über die erweiterten Einstellungen verschoben
- Erweiterte Einstellungen werden aus House-Presets vorausgefüllt
- Default Dauer: 20 Minuten Song + 3h Loop (statt 42 Minuten)
- Redundante Tooltips und Step-Labels aus Create-Seite entfernt

## [v2.8.0] – 2026-03-25

### Added
- **Auto-Timestamps**: Clip-Grenzen → thematische Timestamps pro House (10 Labels je Haus)
- **Cross-Pollination Playlists**: min. 3, max. 6 Playlists pro Video automatisch zugewiesen
- **Endscreen-Empfehlung**: Passende Playlist-Empfehlung basierend auf Mood/House
- **Auto-Description**: YouTube-Beschreibung aus Template + Lore generiert (inkl. Timestamps)
- **Auto-Hashtags/Tags**: 23 Tags pro Video (Core + House + Mood)
- **Titel-Varianten**: 2-3 A/B-Test-Varianten pro Video
- **Metadata Preview API**: `/api/pipeline/preview-metadata` für Dashboard-Vorschau
- **Duration Fix**: Pipeline nutzt loop_hours für Titel (z.B. "3 Hours" statt "42 Minutes")

## [v2.7.1] – 2026-03-25

### Fixed
- **Audio Steps Bug**: Steps-Auswahl im UI wurde nicht an den Generator weitergereicht (war immer hardcoded)
- **Zeitschätzung**: Adaptive Messung nach Clip 1 statt statischer Schätzung (steps × 4s)

### Changed
- 40-Steps-Option entfernt, nur noch 30/50/100 (Default: 50)
- PROJECT_STATUS.md: Ticket-System ist jetzt Single Source of Truth, Deploy-Regeln dokumentiert

## [v2.7.0] – 2026-03-25

### Added
- **GPU Metrics Widget**: Live GPU-Auslastung, VRAM, Temperatur, Fan, Watt auf dem Dashboard
  - Auto-Refresh alle 10s, Warning-Thresholds
  - API: `/api/gpu/metrics`
- **Audio Job Retry**: 🔄 Button für failed/cancelled Jobs (Detail + Liste)
- **Ticket Bearbeiter**: `assigned_to` Feld in Tickets (wer arbeitet dran)
- **User Stories**: `docs/USER_STORIES.md` mit 9 Use Cases

### Fixed
- Ticket-Redirect nach Erstellen → Übersicht statt Detailseite
- Prioritäts-Badges konsistent (Low hatte falsche Farbe)
- One-Click Flow integriert in pipeline/new (kein separater Button mehr)

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

