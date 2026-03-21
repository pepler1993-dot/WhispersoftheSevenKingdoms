# Preflight – erster QA-Schritt

## Zweck
Der erste Preflight-Schritt schreibt einen verwertbaren Report für die Metadaten-Prüfung.

## Skript
- `scripts/qa/preflight-metadata-report.js`

## Ablauf
Das Skript ruft die Metadaten-Validierung auf und schreibt das Ergebnis als JSON-Report nach:
- `work/publish/reports/metadata-preflight.latest.json`
- zusätzlich eine Zeitstempel-Datei für spätere Nachvollziehbarkeit

## Beispiel
```bash
node scripts/qa/preflight-metadata-report.js
node scripts/qa/preflight-metadata-report.js upload/metadata
```

## Zielbild
Preflight soll später mehrere Prüfschritte bündeln:
- Metadaten
- Dateivollständigkeit
- Audio-Technik
- Render-/Output-Vollständigkeit

Aktuell ist das noch die erste QA-Stufe, nicht die ganze Maschine.
