# Repo-Struktur – technisches Grundgerüst

## Ziel
Die Struktur soll zwischen Rohmaterial, Zwischenständen, Templates, Skripten und finalen Outputs sauber trennen.

## Verzeichnisse

```text
input/
  songs/
  artwork/
  metadata/

work/
  audio/
  video/
  thumbnails/
  publish/

output/
  youtube/
  spotify/
  soundcloud/

templates/
  metadata/
  descriptions/
  thumbnails/

schemas/

docs/
  technical/
  platform-guides/

scripts/
  metadata/
  qa/
  video/
  publish/
```

## Bedeutung
- `input/` → angelieferte Quelldateien
- `work/` → Zwischenstände und temporäre Verarbeitung
- `output/` → finale Pakete pro Plattform
- `templates/` → Vorlagen für Metadata, Texte und Visual-Regeln
- `schemas/` → maschinenlesbare Regeln
- `docs/technical/` → technische Entscheidungen und Standards
- `scripts/` → spätere CLI- und Pipeline-Werkzeuge

## Verhältnis zu `upload/`
`upload/` bleibt als pragmatische Übergabestruktur für den aktuellen einfachen Workflow bestehen.

Die größere Zielstruktur ist für den PoC-Ausbau und die spätere saubere Pipeline gedacht.
