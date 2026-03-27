# Whispers of the Seven Kingdoms

Monorepo für eine GoT-inspirierte Sleep-Music-Pipeline:
**Haus wählen → Audio erzeugen → Thumbnail/Video bauen → Metadaten generieren → YouTube vorbereiten oder hochladen**.

Der alte Stand war zu optimistisch und teilweise veraltet. Das hier bildet den aktuellen Projektzustand ab.

## Aktueller Stand

**Schon vorhanden:**
- FastAPI-Dashboard unter `services/sync/`
- End-to-End-Pipeline unter `pipeline/`
- Thumbnail-Generator
- Video-Renderer (statisch + optional animiert)
- Metadata-Generator
- YouTube-Upload via OAuth
- Stable-Audio-Local-Flow im Dashboard
- lokaler GPU-Worker für Audio-Generierung

**Gerade kritisch:**
- lokaler GPU-Worker / VM sauber ans Laufen bekommen
- Audio-Strategie finalisieren
- Stable-Audio-Local als einzige Audio-Quelle konsistent betreiben

Kurz: **UI und Pipeline sind weit**, aber **Audio-Infrastruktur ist noch der wacklige Teil**.

---

## Monorepo-Struktur

```text
services/sync/             FastAPI-Dashboard + Job-/Sync-Logik
pipeline/                  End-to-end Render-/Publish-Pipeline
data/
  upload/                  Eingangsordner für Songs / Thumbnails / Metadata
  output/youtube/          Fertige YouTube-Artefakte pro Slug
  work/jobs/               Laufstatus / Statusdateien
  assets/backgrounds/      Theme-Hintergründe für Renderer
schemas/                   JSON-Schemata
docs/                      Auswertungen, Reviews, Konzept-Dokus
```

---

## Hauptkomponenten

### 1) Dashboard / Control Panel
Pfad: `services/sync/`

Funktionen:
- Projekt-/Operations-Übersicht
- House-Templates für schnelle Video-Erstellung
- Audio-Generator-Ansicht
- Job-History / Status / Events
- System-/Operations-Seiten

Einstieg:
- App: `services/sync/app/main.py`
- Templates: `services/sync/templates/`
- House-Defaults: `services/sync/data/house_templates.json`

### 2) Pipeline
Pfad: `pipeline/`

Zentrale Datei:
- `pipeline/pipeline.py`

Die Pipeline kann aktuell:
- vorhandenes Audio anhand eines Slugs laden
- Audio optional loopen
- Audio optional post-processen
- Thumbnail übernehmen oder erzeugen
- YouTube-Metadaten generieren
- Video rendern
- QA/Preflight laufen lassen
- optional zu YouTube hochladen
- Quellen nach `data/upload/done/` verschieben

### 3) Audio-Generierung
Pfad: Teile in `services/sync/app/`

Aktuell relevant:
- Stable Audio Local ist der aktive Generierungspfad
- lokaler Worker ist die einzige vorgesehene Laufzeit für Audio

Nicht schönreden: **Audio ist noch nicht der endgültig stabile Produktionspfad**.

---

## Datenfluss

Minimaler gemeinsamer Schlüssel ist der **Slug**.

Beispiel:
```text
data/upload/songs/whispers-of-winterfell.wav
data/upload/metadata/whispers-of-winterfell.json
data/upload/thumbnails/whispers-of-winterfell.jpg
```

Output landet typischerweise hier:
```text
data/output/youtube/whispers-of-winterfell/
```

Status-Dateien:
```text
data/work/jobs/whispers-of-winterfell/status.json
```

---

## Schnellstart

## Voraussetzungen
- Python 3.11+
- `ffmpeg`
- optional: GPU für Audio-Experimente / lokale Generierung
- optional: Google OAuth Client für echten YouTube-Upload

## Setup

```bash
git clone <repo-url>
cd WhispersoftheSevenKingdoms
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`ffmpeg` installieren:

```bash
sudo apt update
sudo apt install -y ffmpeg
```

---

## Dashboard lokal starten

```bash
source .venv/bin/activate
uvicorn services.sync.app.main:app --reload --host 0.0.0.0 --port 8000
```

Dann im Browser öffnen:
- `http://127.0.0.1:8000`
- oder je nach Setup die Server-/Tunnel-URL

---

## Pipeline lokal ausführen

### Minimal: Testlauf ohne Upload

Voraussetzung:
- `data/upload/metadata/<slug>.json` existiert
- `data/upload/songs/<slug>.mp3|wav|ogg` existiert
- Thumbnail optional

Beispiel:

```bash
source .venv/bin/activate
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-upload
```

### Öffentlich statt privat hochladen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --public
```

### Audio auf längere Laufzeit loopen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 20 --loop-hours 3 --skip-upload
```

### Animierten Renderer benutzen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --animated --skip-upload
```

### Audio-Postprocessing überspringen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-post-process --skip-upload
```

---

## YouTube-Upload vorbereiten

Für echten Upload braucht ihr OAuth-Zugang.

Benötigt:
- Google Cloud Projekt
- YouTube Data API v3 aktiviert
- OAuth Client vom Typ Desktop App

Ablage:
- `client_secret.json` im Repo
- oder per Umgebungsvariable

Beispiel:

```bash
export GOOGLE_CLIENT_SECRET=/pfad/zu/client_secret.json
```

Dann den Upload-Flow initialisieren bzw. nutzen. Token liegt lokal typischerweise in:
- `.youtube_token.json`

**Wichtig:** Keine echten Secrets committen. Wenn doch passiert: rotieren, nicht diskutieren.

---

## Wichtige Ordner und Dateien

### Root
- `README.md` → dieses Dokument
- `PROJECT_STATUS.md` → aktuelle Lage, Entscheidungen, Infrastruktur
- `ROADMAP.md` → Prioritäten und nächste Schritte
- `requirements.txt` → gemeinsame Python-Abhängigkeiten

### Pipeline
- `pipeline/pipeline.py` → Orchestrierung
- `pipeline/scripts/audio/loop_audio.py`
- `pipeline/scripts/audio/post_process.py`
- `pipeline/scripts/thumbnails/generate_thumbnail.py`
- `pipeline/scripts/video/render.py`
- `pipeline/scripts/video/render_animated.py`
- `pipeline/scripts/metadata/metadata_gen.py`
- `pipeline/scripts/publish/youtube_upload.py`
- `pipeline/scripts/qa/preflight_metadata_report.py`

### Dashboard / Sync
- `services/sync/app/main.py` → FastAPI-Einstieg
- `services/sync/app/store.py` → SQLite / Datenhaltung
- `services/sync/app/audio_jobs.py` → Audio-Job-Erstellung (stable-audio-local only)
- `services/sync/app/stable_audio_gen.py` → lokaler/alternativer Audiopfad
- `services/sync/templates/` → UI
- `services/sync/deploy/` → Deployment / systemd / Update-Skripte

## Typischer Arbeitsablauf

### Variante A: Audio schon vorhanden
1. Song-Datei nach `data/upload/songs/`
2. Metadata-JSON nach `data/upload/metadata/`
3. optional Thumbnail nach `data/upload/thumbnails/`
4. Pipeline mit `--slug ...` starten

### Variante B: über Dashboard / Audio-Flow
1. Haus / Stil im Dashboard wählen
2. Audio-Job anstoßen
3. Ergebnis prüfen
4. Pipeline / Render / Upload ausführen

---

## Reale Prioritäten

Wenn du neu ins Projekt kommst: nicht am falschen Ende optimieren.

### P0
- GPU-Worker / lokaler Audio-Worker
- `nvidia-smi`, Treiber, Python-Stack, erster brauchbarer Audio-Test

### P1
- Audio-Qualität und Laufzeit am GPU-Worker weiter optimieren
- kurze Tracks + Looping als Standard festigen

### P2
- Doku sauber nachziehen
- UI nur auf Basis echter Nutzung weiter polieren
- Operations / Fehlerfälle robuster machen

---

## Bekannte Baustellen

- README war veraltet → deshalb dieses Update
- Teile der älteren Doku referenzieren alte Pfade oder alte Struktur
- lokaler GPU-Worker ist noch nicht als „fertig“ zu betrachten
- im Repo liegen sensible lokale Dateien wie OAuth-/Token-Artefakte potenziell herum; sauberer Umgang ist Pflicht

---

## Deployment-Hinweise

Server-/Infra-Details stehen eher in:
- `PROJECT_STATUS.md`
- `services/sync/README.md`
- `services/sync/deploy/`

Bekannter Projektkontext zuletzt:
- Proxmox-/LXC-/VM-Setup
- Dashboard als Service
- YouTube OAuth auf Server vorhanden
- GPU-VM/Worker als aktueller Engpass

---

## Empfehlungen für Mitwirkende

- zuerst `PROJECT_STATUS.md` lesen
- dann `ROADMAP.md`
- dann den Bereich anfassen, den du wirklich bearbeitest
- bei Dashboard-Änderungen Version sauber hochziehen
- keine Fantasie-Dokumentation schreiben, wenn die Technik noch nicht validiert ist

---

## Verwandte Doku

- `PROJECT_STATUS.md`
- `ROADMAP.md`
- `services/sync/README.md`
- `docs/AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md`

---

## TL;DR

Das Projekt ist **kein simples Upload-Skript** mehr, sondern ein kleines Produktionssystem für GoT-Sleep-Music.

**Fertig genug für echte Pipeline-Tests:** ja.
**Fertig genug, um Audio als gelöst zu betrachten:** nein.
**Nächster echter Hebel:** lokaler GPU-Worker / stabile Audio-Erzeugung.
