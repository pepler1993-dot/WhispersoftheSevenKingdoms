# Validation

## Zweck
Diese Seite beschreibt die aktuelle Validierung rund um Song-Metadaten im Projekt.

Sie ist Lookup-Doku: knapp, technisch, ohne Strategiepredigt.

---

## Relevante Dateien

- `schemas/song.schema.json`
- `pipeline/scripts/metadata/validate_song_metadata.py`
- `pipeline/scripts/metadata/validate-song-metadata.js`
- `data/upload/metadata/`

---

## Was validiert wird

Der Kernfokus liegt aktuell auf Metadaten-Dateien pro Slug.

Typische Prüfungen:
- Pflichtfelder vorhanden
- erlaubte Top-Level-Felder
- Slug-Format
- Typen für Strings / Arrays
- grobe Struktur von Briefing-Feldern

---

## Erwartete Eingaben

Typischerweise:

```text
data/upload/metadata/<slug>.json
```

Schema:
- `schemas/song.schema.json`

---

## CLI / Skripte

### Python-Variante

```bash
python pipeline/scripts/metadata/validate_song_metadata.py
```

### JS-Variante

```bash
node pipeline/scripts/metadata/validate-song-metadata.js
```

Je nach Skriptversion kann auch ein Pfad übergeben werden, z. B. für Einzeldateien oder Verzeichnisse.

---

## Zweck im Workflow

Validation ist die erste technische Hürde vor:
- Metadaten-Generierung
- QA / Preflight
- Render / Publish-Schritten

Sie soll früh verhindern, dass kaputte oder unvollständige JSON-Dateien weiter durch die Pipeline fallen.

---

## Grenzen

Validation garantiert nicht:
- inhaltlich gute Titel
- gute Tags
- gutes Audio
- funktionierenden Upload

Sie prüft primär Struktur und Grundkonsistenz.
