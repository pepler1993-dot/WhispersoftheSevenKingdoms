# Tutorial – First Local Pipeline Run

## Ziel
In diesem Tutorial führst du einen ersten lokalen Pipeline-Lauf aus und prüfst danach das Ergebnis im Output-Ordner.

Das Ziel ist **nicht** YouTube-Upload, sondern ein funktionierender lokaler End-to-End-Test ohne Mythologie.

---

## Was du am Ende haben solltest

- eine lauffähige lokale Python-Umgebung
- einen Testlauf mit `pipeline/pipeline.py`
- einen Output-Ordner unter `data/output/youtube/<slug>/`
- eine Statusdatei unter `data/work/jobs/<slug>/status.json`

---

## Voraussetzungen

- Repo geklont
- Python 3.11+
- `ffmpeg` installiert
- mindestens ein vorhandener Test-Slug mit Audio und Metadaten

Wenn du noch keine Umgebung hast, lies zuerst:
- [`../guides/QUICKSTART.md`](../guides/QUICKSTART.md)

---

## Schritt 1 – Umgebung aktivieren

```bash
cd WhispersoftheSevenKingdoms
source .venv/bin/activate
```

Wenn `.venv` noch nicht existiert, zuerst den Quickstart machen.

---

## Schritt 2 – Prüfen, ob Eingabedateien da sind

Beispielhaft für den Slug `whispers-of-winterfell`:

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

Wichtig ist: Audio und Metadata müssen denselben Slug haben.

---

## Schritt 3 – Testlauf ohne Upload starten

```bash
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-upload
```

Damit vermeidest du, dass ein erster Test gleich externe Seiteneffekte produziert.

---

## Schritt 4 – Konsole grob verstehen

Ein erfolgreicher Lauf arbeitet sich typischerweise durch diese Stationen:
1. Audio laden
2. optional Audio post-processen
3. Thumbnail bereitstellen oder erzeugen
4. Metadaten generieren
5. Video rendern
6. QA / Preflight ausführen
7. Status aktualisieren

Wenn der Lauf scheitert, ist die Fehlermeldung meist ehrlicher als jede Vermutung. Lies sie zuerst, statt sofort an fünf anderen Stellen rumzustochern.

---

## Schritt 5 – Output prüfen

Danach sollte es hier etwas geben:

```text
data/output/youtube/whispers-of-winterfell/
```

Typisch:
- `video.mp4`
- `metadata.json`
- `thumbnail.jpg`

---

## Schritt 6 – Statusdatei prüfen

```text
data/work/jobs/whispers-of-winterfell/status.json
```

Dort sollte die letzte Pipeline-Phase sichtbar sein.

Beispiele:
- `thumbnail_ready`
- `metadata_ready`
- `rendered`
- `qa_passed`
- `done`

---

## Schritt 7 – Ergebnis bewerten

Ein sinnvoller erster Erfolg ist erreicht, wenn:
- das Video existiert
- die Metadata-Datei erzeugt wurde
- kein offensichtlicher Fehler im Output liegt
- der Job-Status plausibel aussieht

Damit ist noch nicht alles perfekt, aber der Kernpfad lebt.

---

## Häufige Probleme

### Audio nicht gefunden
Dann stimmt der Slug nicht oder die Datei liegt nicht in `data/upload/songs/`.

### Metadaten fehlen
Dann fehlt `data/upload/metadata/<slug>.json`.

### `ffmpeg` fehlt
Ohne `ffmpeg` kein sinnvoller Video-Render.

### Upload-Probleme
In diesem Tutorial irrelevant, weil `--skip-upload` gesetzt ist.

---

## Nächste Schritte

Wenn dieser Test funktioniert, dann sind die nächsten sinnvollen Schritte:
- anderer Slug
- Looping testen
- animierten Renderer testen
- Dashboard parallel dazu starten
- später echten Upload-Pfad vorbereiten

Weiterführend:
- [`../guides/PIPELINE.md`](../guides/PIPELINE.md)
- [`../technical/repo-structure.md`](../technical/repo-structure.md)
- [`../../PROJECT_STATUS.md`](../../PROJECT_STATUS.md)
