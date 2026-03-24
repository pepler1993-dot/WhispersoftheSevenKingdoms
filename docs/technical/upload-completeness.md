# Upload Completeness

## Zweck
Dieser Check prüft, ob für einen Slug die nötigen Grundbausteine im Upload-Workflow vorhanden sind.

Aktuell relevant für den pragmatischen Datei-Workflow unter `data/upload/`.

---

## Relevante Datei

- `pipeline/scripts/qa/check-upload-completeness.js`

---

## Geprüfte Verzeichnisse

```text
data/upload/songs/
data/upload/thumbnails/
data/upload/metadata/
```

---

## Vollständig bedeutet aktuell

Für einen Slug vorhanden:
- mindestens eine Songdatei (`.mp3`, `.wav`, `.ogg`)
- mindestens ein Thumbnail (`.jpg`, `.png`, `.webp`, ggf. weitere Bildformate je nach Skriptstand)
- genau genommen mindestens eine Metadaten-Datei (`.json`)

Mehrere Dateien pro Typ sind kein automatischer Weltuntergang, können aber als Warnsignal auftauchen.

---

## Typische Ausführung

```bash
node pipeline/scripts/qa/check-upload-completeness.js
```

---

## Report

Typischer Zielort:

```text
data/work/publish/reports/upload-completeness.latest.json
```

---

## Nutzen im Workflow

Der Check beantwortet früh die einfache, aber wichtige Frage:

**Liegt für einen Slug überhaupt genug Material vor, um sinnvoll weiterzumachen?**

Er verhindert damit, dass Render- oder Publish-Schritte an fehlenden Grundlagen scheitern.
