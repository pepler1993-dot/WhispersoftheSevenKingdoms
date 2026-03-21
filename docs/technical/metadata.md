# Technische Metadaten-Regeln

## Zweck
Diese Datei beschreibt das erste belastbare Metadatenformat für Songs im Projekt.

## Zielschema
- JSON-Datei pro Song
- Dateiname: `<slug>.json`
- Schema-Datei: `schemas/song.schema.json`
- Beispiel: `templates/metadata/example.song.json`

## Pflichtfelder v1
- `slug`
- `title`
- `platform`
- `theme`
- `mood`

## Feldregeln

### `slug`
- nur Kleinbuchstaben, Zahlen und Bindestriche
- keine Leerzeichen
- gemeinsamer Schlüssel für Song, Thumbnail und Metadaten
- Beispiel: `whispers-of-winterfell`

### `title`
- menschlich lesbarer Arbeitstitel oder finaler Titel

### `platform`
- aktuell vorgesehen: `youtube`, später optional `spotify`, `soundcloud`

### `theme`
- inhaltlicher Bezug, z. B. Ort, Haus oder Stimmungskern

### `mood`
- Array aus Stimmungsbegriffen
- mindestens ein Wert

## Optionale Felder
- `notes`
- `duration_hint`
- `music_brief`
- `thumbnail_brief`

## Ziel der optionalen Brief-Felder
Die Brief-Felder sollen genug Kontext liefern, damit Content- und Publishing-Seite:
- nicht raten müssen
- konsistente Titel/Beschreibungen bauen können
- Musik- und Thumbnail-Richtung nachvollziehen können

## V1-Regel
Für den ersten PoC gilt bewusst: lieber ein kleines, sauberes Schema als ein Datenfriedhof mit 40 halbgenutzten Feldern.
