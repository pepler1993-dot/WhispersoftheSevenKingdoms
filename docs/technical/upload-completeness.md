# Upload-Vollständigkeitscheck

## Zweck
Dieser Check prüft im einfachen `upload/`-Workflow, ob zu einem Slug alle drei Kernbestandteile vorhanden sind:
- Song
- Thumbnail
- Metadaten

## Skript
- `scripts/qa/check-upload-completeness.js`

## Geprüfte Ordner
- `upload/songs/`
- `upload/thumbnails/`
- `upload/metadata/`

## Regeln
Ein Slug gilt als vollständig, wenn vorhanden sind:
- mindestens 1 Songdatei (`.mp3`, `.wav`, `.ogg`)
- mindestens 1 Thumbnail (`.jpg`, `.png`, `.webp`)
- mindestens 1 Metadatei (`.json`)

Mehrere Dateien pro Typ werden aktuell als Warnung markiert.

## Report
Das Skript schreibt einen Report nach:
- `work/publish/reports/upload-completeness.latest.json`

## Beispiel
```bash
node scripts/qa/check-upload-completeness.js
```

## Zweck im PoC
Damit wird vor Render- oder Upload-Logik zuerst geprüft, ob die Grundbausteine überhaupt vollständig vorliegen.
