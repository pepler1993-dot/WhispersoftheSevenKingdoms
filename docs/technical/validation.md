# Metadaten-Validierung

## Zweck
Dieses Projekt hat ein erstes, leichtgewichtiges Validierungsskript für Song-Metadaten.

## Skript
- `scripts/metadata/validate-song-metadata.js`

## Was es aktuell prüft
- Pflichtfelder vorhanden
- erlaubte Top-Level-Felder
- Slug-Format
- String-/Array-Typen für die wichtigsten Felder
- einfache Struktur von `music_brief` und `thumbnail_brief`

## Standardziel
Ohne Argument prüft das Skript alle JSON-Dateien in:
- `upload/metadata/`

## Beispiele
```bash
node scripts/metadata/validate-song-metadata.js
node scripts/metadata/validate-song-metadata.js upload/metadata
node scripts/metadata/validate-song-metadata.js templates/metadata/example.song.json
```

## Hinweis
Das Skript ist bewusst dependency-frei gehalten, damit es sofort lokal läuft.
Es ist ein pragmatischer Start, kein Endzustand.

Später kann das auf TypeScript + echtes JSON-Schema-Tooling (z. B. AJV) umgestellt werden.
