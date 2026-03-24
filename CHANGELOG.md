# Changelog

Alle relevanten Änderungen am Projekt werden hier dokumentiert.
Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

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
