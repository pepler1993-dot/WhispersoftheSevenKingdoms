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
