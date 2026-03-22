# Whispers of the Seven Kingdoms

GoT-inspirierte Sleep-Music mit einfacher Upload-Automation.

## Ziel
- Songs und passende Thumbnails im Stil von Westeros erstellen
- Inhalte reproduzierbar für YouTube vorbereiten
- Automation so aufbauen, dass Content nur noch in definierte Ordner gelegt werden muss

## Aktueller Fokus
1. Content erstellen: Songs + Thumbnails
2. Übergabe standardisieren: Slug, Ordner, Minimalmetadaten
3. Automation für YouTube-Upload schrittweise aufbauen

## Kernstruktur
```text
upload/
  songs/
  thumbnails/
  metadata/
  done/
```

## Übergaberegeln
- Song, Thumbnail und Metadaten verwenden denselben Slug
- Beispiele:
  - `whispers-of-winterfell.mp3`
  - `whispers-of-winterfell.jpg`
  - `whispers-of-winterfell.json`
- Keine halbfertigen Dateien in die produktiven Upload-Ordner legen

## Team-Rollen
- **Kevin** → Projektowner
- **Pako** → technische Pipeline, Struktur, Schema, QA-Basis
- **Jarvis** → Dokumentation, Workflow, Review und Koordination
- **Smith** → Publishing-Schicht, Plattformlogik, Upload-Feinschliff

## Wichtige Dateien
- `ROADMAP.md` → Meilensteinplan mit 4 Phasen
- `EXPANSION_PLAN_FINAL.md` → gemeinsamer Expansion-Plan (alle Bots)
- `IDEAS.md` → Ideen-Parkplatz für zukünftige Features
- `PROJECT_STATUS.md` → zentrale Statusübersicht, Team
- `QUICKSTART.md` → 5-Minuten-Schnellstart
- `AUTOMATION.md` → Upload-Workflow

## Pipeline-Skripte (automatisiert)
- `scripts/metadata/metadata_gen.py` → Metadaten aus JSON generieren
- `scripts/thumbnails/generate_thumbnail.py` → Thumbnail nach Theme
- `scripts/video/render.py` → Audio + Bild → MP4 (ffmpeg)
- `scripts/publish/youtube_upload.py` → YouTube Upload
- `publishing/musicgen/generate.py` → MusicGen Audiogenerierung
- `scripts/orchestrate.py` (geplant) → Gesamtsteuerung

## Komponenten im Überblick
- **Publishing-Toolkit** unter `publishing/`:
  - Titel-,Beschreibungs- und Tag-Templates
  - Playlist-Strategie
  - Publishing-Beispiele und Anleitungen
- **MusicGen-Pipeline** unter `publishing/musicgen/`:
  - CLI-Tool für automatisierte Song-Generierung via Hugging Face MusicGen
  - Prompt-Management, Konfiguration und Merge-Logik für 40+ Minuten Tracks
- **Agent-Sync-Service** für Koordination:
  - Zentrale Task- und Lease-Verwaltung für parallele Arbeit mehrerer Bots
  - Details in `AGENT_SYNC.md` und `CONTRIBUTING.md`

## Team (3-Bot-Koordination)
- **Pako** → Tech/Pipeline (MusicGen, ffmpeg, Orchestrierung)
- **Smith** → Publishing/API (YouTube Upload, Metadaten, Templates)
- **Jarvis** → Doku/Workflow (Dokumentation, Sync, Reviews)
