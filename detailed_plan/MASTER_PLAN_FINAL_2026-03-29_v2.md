# MASTER PLAN FINAL v2 – Whispers -> Content Operating System

## Zweck
Diese Datei ist der Einstiegspunkt für alle Agents.  
Sie erklärt:
- welche Dateien die Wahrheit sind
- wer was laden soll
- in welcher Reihenfolge gearbeitet wird
- wo die UI-Regeln im Gesamtplan sitzen

---

## Finaler Dokumentensatz

### 1. Immer zuerst lesen
- `AGENT_OPERATING_RULES_2026-03-29_v6.md`

### 2. Für die eigentliche Umsetzung
- `EXECUTION_ROADMAP_2026-03-29_v6.md`
- `COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`

### 3. Für Bewertung, Qualitätsmaßstab und Architekturdisziplin
- `PROFESSIONAL_REVIEW_2026-03-29_v6.md`

### 4. Für UI-Struktur und zukünftige Seiten
- `UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`

### 5. Für Marktstart / Positionierung / Launch-Timing
- `GO_TO_MARKET_STRATEGY_2026-03-28_v6.md`
- optional: `GTM_ONE_PAGER_2026-03-28.md`

---

## Welche Datei ist wofür da?

### AGENT_OPERATING_RULES
Kleine operative Regeldatei.  
Soll fast immer im Kontext bleiben.

### EXECUTION_ROADMAP
Beschreibt Reihenfolge, Gates, kritischen Pfad und wann UI-Themen drankommen.

### COMPACT_TICKET_BACKLOG
Ist der konkrete Arbeitsbacklog.

### PROFESSIONAL_REVIEW
Ist der Qualitätsmaßstab.

### UI_INFORMATION_ARCHITECTURE_GUIDE
Ist die verbindliche UI-Leitdatei.

Enthält:
- Seitentypen
- Sichtbarkeitsstufen
- Dashboard-/Create-/Detail-Regeln
- Regeln für zukünftige Funktionen und Seiten

### GO_TO_MARKET_STRATEGY
Ist die Markt- und Angebotslogik.

---

## Welche Datei lädt welcher Agent standardmäßig?

### Smith
Immer:
- AGENT_OPERATING_RULES
- EXECUTION_ROADMAP
- COMPACT_TICKET_BACKLOG

Bei Bedarf:
- PROFESSIONAL_REVIEW
- UI_INFORMATION_ARCHITECTURE_GUIDE
- GO_TO_MARKET_STRATEGY

### Pako
Immer:
- AGENT_OPERATING_RULES
- COMPACT_TICKET_BACKLOG
- UI_INFORMATION_ARCHITECTURE_GUIDE

Je nach Aufgabe:
- relevante Phase aus EXECUTION_ROADMAP
- GO_TO_MARKET_STRATEGY für Positionierung / Packaging / Onboarding / Pricing

### Jarvis
Immer:
- AGENT_OPERATING_RULES
- EXECUTION_ROADMAP
- PROFESSIONAL_REVIEW
- UI_INFORMATION_ARCHITECTURE_GUIDE
- GO_TO_MARKET_STRATEGY

Je nach Aufgabe:
- COMPACT_TICKET_BACKLOG

---

## Reihenfolge der Arbeit

### Sofort
Welle A:
- Baseline
- System Map
- Engineering Standards
- Risk Register
- Security Review

### Danach
Welle B:
- Domain Model
- Target Architecture
- API-/Status-/Fehler-Verträge
- Config-Modell
- Teststrategie / Fixtures
- Observability
- Migrationsstrategie
- Rollback / Smoke Checks
- UI Information Architecture Guide

### Erst danach
Welle C und D:
- Kernobjekte
- YouTube-Kapselung
- API-first Kernpfade
- Dashboard/Create/Detail-Blueprints
- Workflow-/Status-UI
- Legacy Mapping

### Noch nicht
Keine echte Expansion vor Gate E.

---

## Source of Truth

### Für Regeln
`AGENT_OPERATING_RULES_2026-03-29_v6.md`

### Für Reihenfolge
`EXECUTION_ROADMAP_2026-03-29_v6.md`

### Für konkrete Arbeit
`COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`

### Für Qualitätsentscheidung
`PROFESSIONAL_REVIEW_2026-03-29_v6.md`

### Für UI-Struktur
`UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`

### Für Markt-/Launch-Entscheidungen
`GO_TO_MARKET_STRATEGY_2026-03-28_v6.md`

---

## Nicht tun
- keine zweite Plattform ohne passendes Kernmodell
- keinen zweiten Provider als Sonderfall
- kein Frontend-Rewrite
- keine breite Beta / kein Public Launch zu früh
- keine parallelen Expansionsachsen
- keine UI-Sonderlogik, die ein schlechtes Modell kaschiert
- keine Mischseiten aus Overview + Create + Debug + Settings

---

## Maßstab
Das Ziel ist nicht, Whispers größer zu machen.

Das Ziel ist:
**aus Whispers kontrolliert einen belastbaren Produktkern zu extrahieren – mit klarer Informationsarchitektur, ohne den aktuellen Produktionswert zu zerstören.**
