# Backlog – Jarvis

Mittelschwere Aufgaben. Backend-Fixes, Workflow-Logik, Performance.

## Aktive Aufgaben

### 1. Audio Job Cancel fixen (#3b) — Priority A
Cancel-Flow für alle Job-States zum Laufen bringen.
- Cancel-Logik für queued, pushing, running, downloading tracen
- Worker-Prozess sauber terminieren
- Job-Status konsistent in DB + UI updaten
- UI-Feedback wenn Cancel fehlschlägt (Grund anzeigen)

### 2. Audio Lab Ladezeit (#16) — Priority E
Audio Lab soll sofort laden, Health-Checks im Hintergrund.
- Profilen was den Page-Load blockt
- Health-Checks async per fetch nachladen
- Page sofort rendern, Status lazy hydratieren
- Loading-States für ausstehende Daten

### 3. Thumbnail-Herkunft anzeigen (#3c) — Priority A
Sichtbar machen woher das Thumbnail kommt.
- Source-Tracking: Library / Upload / Auto-generiert / Briefing
- Run-Detail-Page: Thumbnail-Source anzeigen
- Vor Pipeline-Start: Preview welches Thumbnail verwendet wird
- Fallback-Logik dokumentieren

### 4. PVE Temperatur im Dashboard (#14) — Priority D
Proxmox Host Temperatur-Daten anzeigen.
- Sensor-Abfrage über SSH/API vom PVE Host
- Relevante Sensoren identifizieren
- Dashboard-Widget mit Temperatur + Warning-Thresholds

### 5. Metadata-Formular in Library (#9) — Priority C
Metadata direkt im Dashboard erstellen statt nur Dateien hochladen.
- Formular: Titel, Beschreibung, Tags, Privacy, Playlist-Meta
- JSON-Export in Metadata-Library
- Optional: bestehende Metadata editieren

### 6. Animated Video Assets Konzept (#12) — Priority C
Asset-Modell für visuelle Inhalte in der Pipeline definieren.
- Neue Asset-Klasse: Backgrounds, Overlays, Motion Layers
- Speicher- und Referenzierungskonzept
- MVP-Scope: animierte Still-Image Videos vs. volle Animation
