# Technologie-Entscheidungen

Dieses Dokument sammelt technische Entscheidungen für das Projekt, damit nicht derselbe Grundsatz fünfmal im Chat gesagt und sechsmal unterschiedlich umgesetzt wird.

---

## Entscheidung 001 – Hauptsprache für die Pipeline

### Status
Vorgeschlagen

### Entscheidung
Für die Automations- und Workflow-Logik soll **Node.js mit TypeScript** als Hauptsprache verwendet werden.

### Begründung
Das Projekt braucht vor allem:
- Datei- und Ordnerverwaltung
- JSON-/Metadaten-Verarbeitung
- CLI-Tools für wiederkehrende Abläufe
- Aufruf externer Tools wie `ffmpeg` / `ffprobe`
- spätere API-Integrationen (z. B. YouTube)

TypeScript passt dafür gut, weil:
- es stark für **CLI- und Datei-Workflows** ist
- **strukturierte JSON-Daten** gut typisiert werden können
- es bei mehreren Mitwirkenden besser skaliert als lose Skriptsammlungen
- es sich gut mit externen Medien-Tools kombinieren lässt
- es später leichter in größere Toolchains wachsen kann

### Vorgesehene Aufgaben in TypeScript
- `init-song`
- `validate-song`
- `generate-metadata`
- `render-video` (Steuerlogik, nicht Videocodec-Zauberei)
- `build-package`
- `preflight-check`
- später optional `upload-youtube`

### Medienverarbeitung
Die eigentliche Audio-/Videoverarbeitung soll **nicht** in TypeScript selbst implementiert werden, sondern über etablierte Tools laufen:
- `ffmpeg`
- `ffprobe`

Das bedeutet:
- **TypeScript = Orchestrierung, Validierung, CLI, Metadaten, Pipeline-Logik**
- **ffmpeg/ffprobe = Rendering, Analyse, Konvertierung**

### Alternative
**Python** wäre eine legitime Alternative für schnelle Skripte und Prototypen.

Warum aktuell trotzdem TypeScript bevorzugt wird:
- besseres Typing für Schemata und Reports
- klarere Struktur für wachsende CLI-Tools
- gute Eignung für Teamarbeit und langfristige Wartung

### Nicht empfohlen als Hauptbasis
- **Bash-only** → okay für kleine Hilfsskripte, schlecht als Rückgrat einer komplexeren Pipeline
- **Go / Rust** → technisch stark, aber für dieses Projekt unnötig schwergewichtig

### Empfehlung für den Start
1. TypeScript als Hauptsprache festlegen
2. `ffmpeg`/`ffprobe` als Pflichtwerkzeuge definieren
3. CLI-Kommandos früh standardisieren
4. `song.json`-Schema und QA-Reports typisiert aufbauen

### Nächste Umsetzungsschritte
- TypeScript-Entscheidung im Projekt bestätigen
- Projektstruktur für CLI-Tools anlegen
- erstes Kommando-Grundgerüst definieren
- Schema- und Report-Typen vorbereiten

---

## Offene Punkte
- Wird ESM oder CommonJS genutzt?
- Welche CLI-Bibliothek wird verwendet (`commander`, `yargs` oder minimal eigenständig)?
- Wird JSON Schema, Zod oder AJV für Validierung bevorzugt?
- Wird Thumbnail-Erzeugung nur mit `ffmpeg` gemacht oder zusätzlich mit `sharp`?
