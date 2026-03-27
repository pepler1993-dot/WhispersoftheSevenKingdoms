# Repo-Struktur – aktueller Monorepo-Stand

## Zweck
Diese Seite beschreibt die **real relevante Struktur** des aktuellen Repositories.
Nicht jede historische Schicht, sondern das, woran man sich beim Arbeiten orientieren sollte.

---

## Top-Level-Überblick

```text
services/sync/                 Dashboard / FastAPI / Operations
pipeline/                      End-to-end Pipeline + Produktionsskripte

data/
  upload/                      Eingangsdateien für Pipeline-Läufe
  output/                      erzeugte Artefakte
  work/                        Status, Jobs, Zwischenstände
  assets/                      Hintergründe / Assets

schemas/                       JSON-Schemata
scripts/                       einzelne Hilfsskripte außerhalb der Kernpipeline

docs/                          Projektdokumentation
README.md                      Repo-Einstieg
PROJECT_STATUS.md              operative Wahrheit / aktueller Stand
ROADMAP.md                     priorisierte nächste Schritte
requirements.txt               gemeinsame Python-Abhängigkeiten
```

---

## Wichtige Bereiche im Detail

## `services/sync/`

Der Dashboard-/Control-Panel-Bereich.

Wichtig:
- `app/main.py` → FastAPI-Einstieg
- `app/store.py` → SQLite / Persistenz
- `app/audio_jobs.py` → Audio-Job-Erstellung (stable-audio-local only)
- `app/stable_audio_gen.py` → lokaler/alternativer Audio-Pfad
- `templates/` → UI-Templates
- `deploy/` → systemd / Setup / Update

Nutzen:
- Bedienoberfläche
- Job-Ansicht
- Operations / System / Status
- Audio-Generator-Workflows

---

## `pipeline/`

Der eigentliche Produktionspfad.

Wichtig:
- `pipeline.py` → Orchestrierung
- `scripts/audio/` → Looping / Postprocessing
- `scripts/thumbnails/` → Thumbnail-Erzeugung
- `scripts/video/` → Render-Pfade
- `scripts/metadata/` → Metadata-Generierung / Validierung
- `scripts/qa/` → Preflight / Checks
- `scripts/publish/` → YouTube-Upload

---

## `data/`

Hier landen operative Dateien.

### `data/upload/`
Eingabe für Pipeline-Läufe:

```text
data/upload/songs/
data/upload/metadata/
data/upload/thumbnails/
data/upload/done/
```

### `data/output/`
Ausgabe-Artefakte, z. B.:

```text
data/output/youtube/
```

### `data/work/`
Arbeitsstände, Statusdateien, Reports:

```text
data/work/jobs/
data/work/publish/
data/work/video/
data/work/thumbnails/
```

### `data/assets/`
Projekt-Assets, z. B. Hintergrundbilder für Renderer.

---

## `schemas/`

Maschinenlesbare Regeln, z. B.:
- `schemas/song.schema.json`

---

## `docs/`

Die Projektdokumentation wird schrittweise nach Diátaxis organisiert:
- Tutorials
- Guides
- Reference
- Explanation

Siehe:
- `docs/README.md`
- `docs/DOCS_AUDIT.md` (falls noch vorhanden; sonst ignorieren)

---

## Historische Stolperfallen

Ältere Dokumente oder Commits sprechen teils noch von:
- `input/`
- `output/`
- `work/`
- `templates/`
- `scripts/` direkt im Root
- `musicgen/` (früher; im aktuellen Repo entfernt)
- `agent-sync-service/`

Das kann als historischer Kontext relevant sein, ist aber **nicht** die beste Orientierung für den aktuellen Stand.

---

## Praktische Faustregel

Wenn du neu ins Repo kommst, orientiere dich zuerst an:
1. `README.md`
2. `PROJECT_STATUS.md`
3. `docs/README.md`
4. `services/sync/`
5. `pipeline/`
6. `data/`

Sonst verläufst du dich schnell in den Sedimenten früherer Ausbaustufen.
