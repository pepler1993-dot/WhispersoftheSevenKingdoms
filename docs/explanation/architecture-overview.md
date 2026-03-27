# Architecture Overview

## Zweck
Diese Seite erklärt die aktuelle Architektur des Projekts auf hoher Ebene.

Sie soll beantworten:
- Welche Hauptbausteine gibt es?
- Wie hängen sie zusammen?
- Wo liegen die aktuellen Stärken und Schwachstellen?

---

## System in einem Satz

Das Projekt ist ein kleines Produktionssystem für GoT-inspirierte Sleep-Music:

**Dashboard / Steuerung → Audio-Erzeugung → Pipeline → QA → Publish-Artefakte → optional YouTube-Upload**

---

## Hauptbausteine

## 1. Dashboard / Control Plane
Pfad:
- `services/sync/`

Aufgaben:
- Eingaben erfassen
- Jobs und Status anzeigen
- Audio-Generator-Workflows begleiten
- Operations-/Systemsicht bereitstellen
- Sync-/Koordinationsfunktionen unterstützen

---

## 2. Produktionspipeline
Pfad:
- `pipeline/`

Aufgaben:
- Audio-Dateien verarbeiten
- Thumbnails erzeugen oder übernehmen
- Metadaten erzeugen
- Video rendern
- QA / Preflight ausführen
- optional YouTube-Upload starten

---

## 3. Audio-Erzeugung
Pfade:
- `services/sync/app/audio_jobs.py` — Audio-Jobs anlegen und orchestrieren
- `services/sync/app/stable_audio_gen.py` — Stable Audio Open auf dem GPU-Worker (**stable-audio-local**)

Rolle:
- erzeugt Tracks und legt sie unter `data/upload/songs/` ab
- wird vom Dashboard (Audio Lab, Create-Flow, Workflows) angestoßen

Wichtig:
- Produktionspfad ist nur noch dieser eine Stack; Feintuning und Betrieb am Worker können trotzdem Baustelle sein

---

## 4. Operative Datenablage
Pfad:
- `data/`

Bedeutung:
- `data/upload/` → Eingabe
- `data/output/` → Artefakte
- `data/work/` → Status / Jobs / Reports
- `data/assets/` → Medien-Assets

---

## 5. Dokumentation / Betriebswissen
Pfad:
- `docs/`
- plus `README.md`, `PROJECT_STATUS.md`, `ROADMAP.md`

Rolle:
- Orientierung
- Regeln
- technische Fakten
- Strategie

---

## Datenfluss auf hoher Ebene

```text
Dashboard / Input
        ↓
Audio-Quelle / Generator
        ↓
data/upload/*
        ↓
pipeline/pipeline.py
        ↓
Thumbnail / Metadata / Render / QA
        ↓
data/output/youtube/<slug>/
        ↓
optional Upload
```

---

## Architekturentscheidungen, die aktuell zählen

### 1. Slug als gemeinsamer Schlüssel
Audio, Thumbnail, Metadaten und Status hängen an einem gemeinsamen Slug.

### 2. Pipeline und Generator entkoppeln
Die Pipeline soll nicht davon abhängen, *wie* Audio entstanden ist — nur *dass* gültiges Audio vorliegt.

### 3. Dashboard ist Control Plane, nicht die ganze Wahrheit
Die UI ist wichtig, aber die eigentliche Wahrheit entsteht aus Code, Dateien, Jobs und Status.

### 4. Audio-Worker und Betrieb
Die Architektur ist festgelegt (Stable Audio Local). Offen können sein: GPU-/SSH-Betrieb, Qualität, Laufzeiten — nicht mehr die Wahl des Modells im Repo.

---

## Aktuelle Stärke

- Dashboard + Pipeline + grundlegende Publish-Schicht sind bereits brauchbar
- Monorepo-Struktur ist klarer als früher
- Audio-Erzeugung und Pipeline sind klar getrennt (Slug + Dateien)

---

## Aktuelle Schwäche

- GPU-Worker-Betrieb kann noch Reibung haben (Netzwerk, Ressourcen)
- ältere Dokumente enthalten historische Schichten und frühere Pfade
- nicht jede strategische Entscheidung ist bereits vollständig verdichtet

---

## Praktische Lesereihenfolge

Wenn du Architektur verstehen willst:
1. `README.md`
2. `PROJECT_STATUS.md`
3. diese Datei
4. `audio-strategy.md`
5. danach erst tiefere Reviews / ältere Strategie-Dokumente
