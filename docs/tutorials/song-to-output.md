# Tutorial – Vom Song zum Output-Artefakt

## Ziel
Dieses Tutorial beschreibt den praktischen Minimalfluss:

**Audio + Metadaten bereitstellen → Pipeline ausführen → Output prüfen**

Es ist damit die einfachste Form eines echten Produktionsdurchlaufs ohne direkten Fokus auf YouTube-Veröffentlichung.

---

## Voraussetzungen

- lokales Repo eingerichtet
- Venv vorhanden
- `ffmpeg` installiert
- ein Slug mit Audio und Metadaten vorhanden

---

## Schritt 1 – Slug festlegen

Beispiel:

```text
whispers-of-winterfell
```

Der gleiche Slug muss für die Eingabedateien verwendet werden.

---

## Schritt 2 – Eingaben bereitstellen

```text
data/upload/songs/whispers-of-winterfell.wav
data/upload/metadata/whispers-of-winterfell.json
```

Optional:

```text
data/upload/thumbnails/whispers-of-winterfell.jpg
```

---

## Schritt 3 – Pipeline starten

```bash
source .venv/bin/activate
python pipeline/pipeline.py --slug whispers-of-winterfell --minutes 42 --skip-upload
```

---

## Schritt 4 – Output prüfen

Erwarteter Zielordner:

```text
data/output/youtube/whispers-of-winterfell/
```

Typischer Inhalt:
- `video.mp4`
- `metadata.json`
- `thumbnail.jpg`

---

## Schritt 5 – Status prüfen

```text
data/work/jobs/whispers-of-winterfell/status.json
```

Dort siehst du, welche Phase zuletzt erfolgreich erreicht wurde.

---

## Schritt 6 – Ergebnis bewerten

Ein brauchbarer Minimalerfolg ist erreicht, wenn:
- das Video erzeugt wurde
- die Metadaten plausibel sind
- der Job-Status nicht auf einem offensichtlichen Fehler hängen blieb

---

## Was dieses Tutorial bewusst nicht abdeckt

Nicht drin:
- echter OAuth-/YouTube-Upload
- GPU-Worker-Setup
- tiefer Audio-Provider-Vergleich
- vollständige Dashboard-Operationslogik

Dafür gibt es andere Dokus.

---

## Weiterführend

- [`../guides/PIPELINE.md`](../guides/PIPELINE.md)
- [`../technical/preflight.md`](../technical/preflight.md)
- [`../reference/architecture-diagram.md`](../reference/architecture-diagram.md)
