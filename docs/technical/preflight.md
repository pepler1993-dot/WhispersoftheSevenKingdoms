# Preflight

## Zweck
Preflight ist die QA-Stufe vor dem eigentlichen Publish-Schritt.

Aktuell ist das noch kein allwissendes Kontrollzentrum, sondern ein pragmatischer Prüfpunkt im Pipeline-Prozess.

---

## Relevante Dateien

- `pipeline/scripts/qa/preflight_metadata_report.py`
- `pipeline/scripts/qa/preflight-metadata-report.js`
- `data/work/publish/reports/`

---

## Was Preflight aktuell prüft

Der aktuelle Schwerpunkt liegt auf Metadaten-Prüfung und Report-Erzeugung.

Ziel:
- verwertbaren Report schreiben
- Fehler/Warnungen sichtbar machen
- Pipeline nicht völlig blind weiterlaufen lassen

---

## Typische Ausführung

### Python

```bash
python pipeline/scripts/qa/preflight_metadata_report.py
```

### JavaScript

```bash
node pipeline/scripts/qa/preflight-metadata-report.js
```

---

## Output

Reports liegen typischerweise unter:

```text
data/work/publish/reports/
```

Je nach Skript und Stand z. B. als:
- latest-Report
- Zeitstempel-Report

---

## Rolle im Gesamtfluss

Preflight sitzt zwischen:
- Metadaten-/Asset-Vorbereitung
- und Render/Publish- bzw. Freigabeentscheidungen

Es ist eine Sicherungsschicht, kein Ersatz für echte Sichtprüfung.

---

## Ausbaupfad

Später kann Preflight zusätzlich bündeln:
- Upload-Vollständigkeit
- Audio-Technik
- Render-Vollständigkeit
- Asset-Präsenz
- Plattform-spezifische Checks

Aktuell gilt: lieber ein kleiner ehrlicher Preflight als ein großer imaginärer.
