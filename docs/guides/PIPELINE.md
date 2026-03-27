# PIPELINE – aktueller Produktionspfad

Ziel dieser Seite: den **real existierenden** Pipeline-Stand beschreiben, nicht Wunschdenken von vor drei Umbauten.

---

## Kurzüberblick

Der aktuelle Kernpfad lautet:

**Slug wählen → Audio bereitstellen → Metadaten laden → optional Thumbnail erzeugen → Video rendern → QA laufen lassen → optional YouTube-Upload**

Zentrale Datei:
- `pipeline/pipeline.py`

---

## Relevante Verzeichnisse

```text
pipeline/
  pipeline.py
  scripts/audio/
  scripts/metadata/
  scripts/publish/
  scripts/qa/
  scripts/thumbnails/
  scripts/video/

data/upload/songs/
data/upload/metadata/
data/upload/thumbnails/
data/upload/done/

data/output/youtube/
data/work/jobs/
```

---

## Minimaler Input

Jeder Lauf hängt an einem gemeinsamen **Slug**.

Beispiel:

```text
data/upload/songs/whispers-of-winterfell.wav
data/upload/metadata/whispers-of-winterfell.json
```

Optional:

```text
data/upload/thumbnails/whispers-of-winterfell.jpg
```

Der Slug ist der gemeinsame Schlüssel zwischen Audio, Thumbnail, Metadaten und Job-Status.

---

## Was `pipeline/pipeline.py` aktuell kann

### 1. Audio finden
Unterstützte Endungen:
- `.mp3`
- `.wav`
- `.ogg`

### 2. Metadaten laden
Pflicht ist eine JSON-Datei unter:
- `data/upload/metadata/<slug>.json`

### 3. optional Audio loopen
Für kurze Ausgangstracks kann die Laufzeit künstlich verlängert werden:
- `--loop-hours`
- `--crossfade`

### 4. optional Audio post-processen
Standardmäßig läuft Audio-Postprocessing, sofern nicht deaktiviert:
- `--audio-preset`
- `--skip-post-process`

### 5. Thumbnail bereitstellen
- vorhandenes Thumbnail verwenden
- oder automatisch generieren

### 6. Metadaten für Output erzeugen
Output typischerweise:
- `data/output/youtube/<slug>/metadata.json`

### 7. Video rendern
Zwei Pfade:
- **statisch** mit `render.py`
- **animiert** mit `render_animated.py` und `--animated`

### 8. QA / Preflight ausführen
Aktuell über:
- `pipeline/scripts/qa/preflight_metadata_report.py`

### 9. optional Upload zu YouTube
Nur wenn **nicht** `--skip-upload` gesetzt ist.

### 10. Quellen nach `done/` verschieben
Wenn nicht `--skip-done-move` gesetzt ist.

---

## Typische Kommandos

### Standard-Testlauf ohne Upload

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-upload
```

### Öffentlich hochladen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --public
```

### 20 Minuten Quelle zu 3 Stunden loopen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 20 --loop-hours 3 --skip-upload
```

### Animierten Renderer erzwingen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --animated --skip-upload
```

### Nur vorbereiten / trocken testen

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --dry-run --skip-upload
```

---

## Wichtige Outputs

### Fertige YouTube-Artefakte

```text
data/output/youtube/<slug>/
```

Dort liegen typischerweise:
- `video.mp4`
- `metadata.json`
- `thumbnail.jpg` oder vorhandenes Asset

### Laufstatus

```text
data/work/jobs/<slug>/status.json
```

Phasen werden dort fortgeschrieben, z. B.:
- `audio_ready`
- `audio_processed`
- `thumbnail_ready`
- `metadata_ready`
- `rendered`
- `qa_passed`
- `uploaded`
- `done`

---

## Beziehung zum Dashboard

Das Dashboard unter `services/sync/` ist die Bedienoberfläche.
Die Pipeline unter `pipeline/` ist der eigentliche Produktionspfad.

Praktisch heißt das:
- Dashboard sammelt Eingaben, zeigt Jobs, Status und Operations
- Pipeline verarbeitet Dateien und erzeugt Artefakte

---

## Beziehung zur Audio-Erzeugung

Audio ist aktuell der heikelste Teil des Gesamtsystems.

Audio kommt typischerweise aus dem Dashboard (**Stable Audio Local** auf dem GPU-Worker) oder aus manuellen Uploads. Für die Pipeline zählt nur: **gültige Datei** unter `data/upload/songs/` für den Slug.

---

## Was diese Seite bewusst nicht tut

Diese Seite erklärt **nicht**:
- die Architekturgeschichte des Projekts
- warum bestimmte Audio-Strategien bevorzugt wurden
- jede UI-Seite im Dashboard

Dafür sind andere Dokus zuständig:
- `PROJECT_STATUS.md`
- `ROADMAP.md`
- Explanation-Dokumente unter `docs/`

---

## Bekannte Schwachstellen

- ältere Doku referenziert noch alte Root-`scripts/`-Pfade
- Audio-Seite ist strategisch noch nicht final stabil
- manche QA-/Reference-Dokus hängen noch hinter dem echten Code her

---

## Praktische Empfehlung

Wenn du nur wissen willst, ob die Pipeline funktioniert:
1. gültigen Slug wählen
2. Audio + Metadata bereitstellen
3. `--skip-upload` Testlauf fahren
4. `data/output/youtube/<slug>/` prüfen
5. `data/work/jobs/<slug>/status.json` lesen

Das ist der kürzeste Weg zur Wahrheit.
