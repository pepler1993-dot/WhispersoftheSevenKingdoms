# AGENT_SYNC.md – Übergaben, Feedback, Entscheidungen

Zweck dieser Datei:
- kurze Übergaben zwischen **Pako** und **Jarvis**
- Feedback zu Branches, Dokumenten oder Ideen
- Festhalten von Entscheidungen oder offenen Fragen
- Sichtbarer Verlauf, was zuletzt gemacht wurde

Diese Datei ist bewusst pragmatisch.
Kein Roman, kein Bürokratiekostüm – nur genug Struktur, damit nicht alles im Chat oder im Nirwana landet.

---

## Regeln zur Nutzung

1. **Nach wichtigen Änderungen** kurz eintragen:
   - was gemacht wurde
   - auf welchem Branch
   - welche Dateien betroffen waren
   - was der andere Agent jetzt wissen sollte

2. **Bei Feedback**:
   - kurz sagen, was gut ist
   - klar sagen, was fehlt oder geändert werden sollte
   - möglichst konkrete nächste Aktion nennen

3. **Bei Entscheidungen**:
   - Entscheidung knapp benennen
   - falls nötig auf Detaildatei verweisen (`TECH_DECISIONS.md`, `AI_STRATEGY.md`, etc.)

4. **Bei offenen Fragen**:
   - Frage formulieren
   - betroffenen Bereich nennen
   - Owner markieren, wenn klar

5. **Kein Müllabladeplatz**:
   - keine langen Entwürfe
   - keine geheimen Zugangsdaten
   - keine doppelten Volltexte aus anderen Dateien

---

## Template für Einträge

```md
### YYYY-MM-DD – Agentname
- Typ: Update | Feedback | Decision | Question
- Branch: `feature/...`
- Bereich: Schema | Templates | Upload | QA | Docs | etc.
- Gemacht:
  - ...
- Wichtig für den anderen:
  - ...
- Nächster sinnvoller Schritt:
  - ...
- Referenzen:
  - `DATEI.md`
```

---

## Einträge

### 2026-03-21 – Pako
- Typ: Update
- Branch: `feature/pako-repo-structure`
- Bereich: Struktur / Schema / technische Grundlage
- Gemacht:
  - Zielstruktur für `input/`, `work/`, `output/`, `templates/`, `docs/`, `scripts/` angelegt
  - `schemas/song.schema.json` als erstes Metadaten-Schema v1 angelegt
  - `templates/metadata/example.song.json` als Referenzdatei ergänzt
  - technische Doku für Repo-Struktur und Metadatenregeln ergänzt
- Wichtig für den anderen:
  - `upload/` bleibt für den einfachen Übergabe-Workflow bestehen
  - die größere Struktur ist das technische Grundgerüst für den PoC-Ausbau
  - Metadaten v1 ist bewusst klein gehalten und auf den aktuellen Demo-Stand zugeschnitten
- Nächster sinnvoller Schritt:
  - ersten Preflight-/Report-Schritt bauen und die Report-Struktur in `work/publish/` vorbereiten
- Referenzen:
  - `schemas/song.schema.json`
  - `templates/metadata/example.song.json`
  - `docs/technical/metadata.md`
  - `docs/technical/repo-structure.md`
  - `scripts/metadata/validate-song-metadata.js`
  - `docs/technical/validation.md`

### 2026-03-21 – Pako
- Typ: Update
- Branch: `feature/pako-repo-structure`
- Bereich: QA / Preflight / Repo-Struktur
- Gemacht:
  - `scripts/qa/preflight-metadata-report.js` angelegt
  - JSON-Report-Ausgabe nach `work/publish/reports/` ergänzt
  - `docs/technical/preflight.md` dokumentiert
  - `input/README.md` und `output/youtube/README.md` als Orientierung für die neue Struktur ergänzt
  - Metadaten-Preflight einmal gegen die Demo-Dateien ausgeführt
- Wichtig für den anderen:
  - der erste QA-Schritt liefert jetzt nicht nur PASS/FAIL auf Konsole, sondern auch einen verwertbaren JSON-Report
  - `work/publish/reports/metadata-preflight.latest.json` ist aktuell die einfachste Referenz für den Stand
- Nächster sinnvoller Schritt:
  - Demo-Content vervollständigen oder Platzhalter für Song/Thumbnail anlegen, damit der Vollständigkeitscheck sinnvoll grün werden kann
- Referenzen:
  - `scripts/qa/preflight-metadata-report.js`
  - `docs/technical/preflight.md`
  - `work/publish/reports/metadata-preflight.latest.json`
  - `input/README.md`
  - `output/youtube/README.md`

### 2026-03-21 – Pako
- Typ: Update
- Branch: `feature/pako-asset-completeness-check`
- Bereich: QA / Upload-Übergabe / PoC
- Gemacht:
  - `scripts/qa/check-upload-completeness.js` angelegt
  - `docs/technical/upload-completeness.md` dokumentiert
  - Vollständigkeits-Report für den `upload/`-Workflow ergänzt
  - Check gegen den aktuellen Demo-Stand ausgeführt
- Wichtig für den anderen:
  - aktuell existieren pro Slug nur Metadaten, aber noch keine Songs oder Thumbnails in `upload/songs/` und `upload/thumbnails/`
  - deshalb schlägt der Vollständigkeitscheck korrekt für alle drei Demo-Slugs fehl
- Nächster sinnvoller Schritt:
  - Demo-Assets liefern oder Platzhalter-/Testdateien definieren, damit der nächste PoC-Schritt vorbereitet werden kann
- Referenzen:
  - `scripts/qa/check-upload-completeness.js`
  - `docs/technical/upload-completeness.md`
  - `work/publish/reports/upload-completeness.latest.json`

### 2026-03-21 – Pako
- Typ: Decision
- Branch: `pako/parallel-work-plan`
- Bereich: Teamstruktur / Aufgabenverteilung / Doku
- Gemacht:
  - Doku auf dritten Bot **Smith** erweitert
  - Rollen in `AGENT_INFO.md`, `AUFGABEN.md`, `README.md` und `CONTRIBUTING.md` angepasst
  - `PARALLEL_WORK_PLAN.md` um aktualisierte Teamlogik für drei Agenten ergänzt
- Wichtig für den anderen:
  - Pako fokussiert technische Grundlage
  - Smith fokussiert Publishing- und Plattform-Schicht
  - Jarvis hält Workflow, Doku, Review und Koordination zusammen
- Nächster sinnvoller Schritt:
  - Parallelplan später noch feiner auf konkrete Smith-Branch-Pakete erweitern
- Referenzen:
  - `AGENT_INFO.md`
  - `AUFGABEN.md`
  - `README.md`
  - `CONTRIBUTING.md`
  - `PARALLEL_WORK_PLAN.md`

### 2026-03-21 – Pako
- Typ: Update
- Branch: `pako/tech-decision-docs`
- Bereich: Docs / Planung / Zusammenarbeit
- Gemacht:
  - `TECH_DECISIONS.md` für Technologie-Vorschlag angelegt
  - `AI_STRATEGY.md` für KI-Einsatz im Projekt angelegt
  - `NEXT_STEPS.md` aus Feedback abgeleitet
  - `POC_WORKFLOW.md` für ersten minimalen End-to-End-Test definiert
  - diese `AGENT_SYNC.md` als gemeinsame Übergabe-/Feedback-Datei angelegt
- Wichtig für den anderen:
  - Songs sollen voraussichtlich extern generiert werden; KI ist dafür eingeplant
  - Kernpipeline soll trotzdem generator-unabhängig bleiben
  - nächster sinnvoller technischer Schritt ist Schema + Ordnerstruktur für den PoC
- Nächster sinnvoller Schritt:
  - Jarvis kann Content-Templates und Upload-Checkliste auf den PoC ausrichten
- Referenzen:
  - `TECH_DECISIONS.md`
  - `AI_STRATEGY.md`
  - `NEXT_STEPS.md`
  - `POC_WORKFLOW.md`

### 2026-03-21 – Pako
- Typ: Decision
- Branch: `pako/readiness-review`
- Bereich: Zusammenarbeit / Startfreigabe
- Gemacht:
  - `READINESS_REVIEW.md` erstellt
  - `START_READY.md` erstellt
  - aktuellen Projektstand auf Startklarheit für Pako/Jarvis bewertet
- Wichtig für den anderen:
  - paralleles Arbeiten ist jetzt freigegeben, aber noch mit engem Scope
  - erster Sprint soll sich auf Struktur, Schema und PoC-Content-Templates beschränken
  - nächste sinnvolle Branches sind `feature/pako-repo-structure` und `feature/jarvis-content-templates`
- Nächster sinnvoller Schritt:
  - Jarvis startet Content-Templates; Pako startet Repo-Struktur
- Referenzen:
  - `READINESS_REVIEW.md`
  - `START_READY.md`
