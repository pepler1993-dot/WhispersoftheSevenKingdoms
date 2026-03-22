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

## Setup auf frischem System

### 1. Repository klonen
```bash
git clone <repo-url>
cd WhispersoftheSevenKingdoms
```

### 2. Python-Venv anlegen und aktivieren
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Python-Abhängigkeiten installieren
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. System-Tool installieren
Die Video-Render-Pipeline braucht `ffmpeg` lokal auf dem System.

Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y ffmpeg
```

### 5. YouTube-Upload vorbereiten
Für den Upload braucht ihr OAuth-Zugang zu YouTube.

- In der Google Cloud Console ein Projekt anlegen
- **YouTube Data API v3** aktivieren
- OAuth Client als **Desktop App** erstellen
- Datei als `client_secret.json` im Repo ablegen
  **oder** per Umgebungsvariable setzen:

```bash
export GOOGLE_CLIENT_SECRET=/pfad/zu/client_secret.json
```

Einmalig Auth-Setup ausführen:
```bash
python scripts/publish/youtube_upload.py --setup
```

Danach liegt der Token lokal in:
- `.youtube_token.json`

## Minimaler Input für einen Pipeline-Lauf
Damit `pipeline.py` direkt laufen kann, braucht ihr pro Song einen gemeinsamen **Slug**.

Beispiel-Slug:
- `whispers-of-winterfell`

Benötigte Dateien:
```text
upload/songs/whispers-of-winterfell.mp3
upload/metadata/whispers-of-winterfell.json
```

Optional:
```text
upload/thumbnails/whispers-of-winterfell.jpg
```

Wenn **kein Thumbnail** in `upload/thumbnails/` liegt, erzeugt die Pipeline selbst eins.

## Pipeline starten

### Voller Lauf inkl. YouTube-Upload
```bash
source .venv/bin/activate
python pipeline.py --slug whispers-of-winterfell --minutes 20
```

### Testlauf ohne Upload
```bash
source .venv/bin/activate
python pipeline.py --slug whispers-of-winterfell --minutes 20 --skip-upload
```

### Öffentlich statt privat hochladen
```bash
source .venv/bin/activate
python pipeline.py --slug whispers-of-winterfell --minutes 20 --public
```

### Audio für längere Version loopen
Beispiel: aus ~20 Minuten Audio einen 3-Stunden-Track bauen.
```bash
source .venv/bin/activate
python pipeline.py --slug whispers-of-winterfell --minutes 20 --loop-hours 3
```

### Animierten Renderer explizit aktivieren
Standardmäßig läuft jetzt der **statische** Renderer (`render.py`).
Der animierte Renderer läuft **nur noch mit Flag**:
```bash
source .venv/bin/activate
python pipeline.py --slug whispers-of-winterfell --minutes 20 --animated
```

## Was die Pipeline automatisch macht
1. Audio-Datei anhand des Slugs finden
2. Metadaten-JSON laden
3. optional Audio loopen (`--loop-hours`)
4. Thumbnail erzeugen oder vorhandenes verwenden
5. YouTube-Metadaten generieren
6. Video rendern
7. QA / Preflight ausführen
8. Video zu YouTube hochladen (wenn nicht `--skip-upload` gesetzt ist)
9. Status-Datei unter `work/jobs/<slug>/status.json` aktualisieren

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
