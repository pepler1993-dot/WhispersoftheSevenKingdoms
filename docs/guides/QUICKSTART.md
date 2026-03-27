# QUICKSTART – Whispers of the Seven Kingdoms

**Ziel:** Das Projekt lokal starten und einen ersten Pipeline-Test ohne Blindflug durchführen.

Diese Anleitung ist bewusst pragmatisch. Kein Architekturroman, sondern der schnellste sinnvolle Einstieg in den aktuellen Monorepo-Stand.

---

## Was du am Ende erreicht hast

Wenn alles klappt, kannst du danach:
- das Repo lokal starten
- das Dashboard ausführen
- einen Pipeline-Test mit vorhandenem Audio und Metadaten anstoßen
- verstehen, wo Input, Output und Statusdateien liegen

---

## Voraussetzungen

Minimum:
- Python **3.11+**
- `ffmpeg`
- geklontes Repo

Optional, aber oft relevant:
- Google OAuth Credentials für echten YouTube-Upload
- erreichbarer **GPU-Worker** (SSH), wenn du Audio über das Dashboard erzeugen willst

---

## 1. Repository klonen

```bash
git clone https://github.com/pepler1993-dot/WhispersoftheSevenKingdoms.git
cd WhispersoftheSevenKingdoms
```

---

## 2. Python-Umgebung aufsetzen

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Wenn du nur Teilbereiche nutzt, kann es zusätzliche Spezial-Dependencies geben. Für den normalen Einstieg reicht erst mal das Root-`requirements.txt`.

---

## 3. `ffmpeg` installieren

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install -y ffmpeg
```

Check:

```bash
ffmpeg -version
```

Wenn das nicht geht, brauchst du mit Video-Rendering gar nicht erst weiterzumachen.

---

## 4. Überblick über die aktuelle Struktur

Die aktuell relevanten Pfade sind:

```text
services/sync/                 Dashboard / FastAPI (inkl. Stable-Audio-Jobs)
pipeline/                      Orchestrierung + Render/Publish-Skripte

data/upload/songs/             Eingangs-Audio
data/upload/metadata/          Eingangs-Metadaten
data/upload/thumbnails/        optionale Thumbnails

data/output/youtube/           finale YouTube-Artefakte

data/work/jobs/                Statusdateien pro Lauf
```

Wichtig: ältere Docs sprechen teilweise noch von `input/`, `output/` oder `scripts/` direkt im Root. Das ist für den aktuellen Stand **nicht mehr die Hauptwahrheit**.

---

## 5. Dashboard lokal starten

```bash
source .venv/bin/activate
uvicorn services.sync.app.main:app --reload --host 0.0.0.0 --port 8000
```

Dann öffnen:
- `http://127.0.0.1:8000`

Was du dort sehen solltest:
- Dashboard / Overview
- Pipeline/Create
- Audio Generator
- Operations/System-Bereiche je nach aktuellem Stand

---

## 6. Ersten Pipeline-Test fahren

### Benötigte Dateien

Für einen Slug, z. B. `whispers-of-winterfell`:

```text
data/upload/songs/whispers-of-winterfell.mp3
oder
data/upload/songs/whispers-of-winterfell.wav

+ data/upload/metadata/whispers-of-winterfell.json
```

Optional:

```text
data/upload/thumbnails/whispers-of-winterfell.jpg
```

Wenn kein Thumbnail vorhanden ist, kann die Pipeline eins erzeugen.

---

## 7. Testlauf ohne Upload

```bash
source .venv/bin/activate
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-upload
```

Das macht im Kern:
1. Audio finden
2. Metadaten laden
3. optional Audio post-processen
4. Thumbnail übernehmen oder erzeugen
5. Metadaten für YouTube generieren
6. Video rendern
7. QA/Preflight laufen lassen
8. Statusdatei aktualisieren

Output typischerweise hier:

```text
data/output/youtube/whispers-of-winterfell/
```

Status typischerweise hier:

```text
data/work/jobs/whispers-of-winterfell/status.json
```

---

## 8. Weitere nützliche Varianten

### Längere Version durch Looping

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 20 --loop-hours 3 --skip-upload
```

### Animierten Renderer verwenden

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --animated --skip-upload
```

### Audio-Postprocessing überspringen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-post-process --skip-upload
```

---

## 9. Echten YouTube-Upload vorbereiten

Dafür brauchst du:
- Google Cloud Projekt
- aktivierte YouTube Data API v3
- OAuth Client vom Typ Desktop App

Credential-Datei:
- `client_secret.json` im Repo
- oder per Umgebungsvariable

Beispiel:

```bash
export GOOGLE_CLIENT_SECRET=/pfad/zu/client_secret.json
```

Danach kann die Pipeline ohne `--skip-upload` genutzt werden.

**Wichtig:** Secrets gehören nicht ins Repo. Wenn doch jemand sowas committed: rotieren, nicht schönreden.

---

## Typische Fehler

### `ffmpeg` nicht gefunden
Installieren und Shell neu laden.

### Audio fehlt für den Slug
Dann liegt die Datei nicht in `data/upload/songs/` oder heißt anders als die Metadata-Datei.

### Metadaten fehlen
Die Pipeline erwartet `data/upload/metadata/<slug>.json`.

### Dashboard startet nicht
Meist fehlen Python-Abhängigkeiten oder der Startpfad ist falsch.

### YouTube-Upload scheitert
OAuth / Credentials / lokaler Token prüfen.

---

## Was du als Nächstes lesen solltest

- [`PIPELINE.md`](PIPELINE.md)
- [`AUTOMATION.md`](AUTOMATION.md)
- [`../technical/repo-structure.md`](../technical/repo-structure.md)
- [`../../PROJECT_STATUS.md`](../../PROJECT_STATUS.md)

---

## In einem Satz

Wenn du nur schnell sinnvoll einsteigen willst: **Venv, ffmpeg, Dashboard starten, Test-Run mit `pipeline/pipeline.py` fahren, Output unter `data/output/youtube/` prüfen.**
