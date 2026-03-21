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
- `AUFGABEN.md` → aktuelle Aufgabenverteilung
- `AUTOMATION.md` → pragmatischer Upload-Workflow
- `PARALLEL_WORK_PLAN.md` → Zusammenarbeit und konkrete Übergaberegeln
- `upload_automation_example.py` → einfacher PoC für den Upload-Flow

## Komponenten im Überblick
- **Publishing-Toolkit** unter `publishing/`:
  - Titel-, Beschreibungs- und Tag-Templates
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
