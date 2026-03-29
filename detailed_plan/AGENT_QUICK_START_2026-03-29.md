# AGENT_QUICK_START_2026-03-29.md

## Zweck
Diese Datei ist der **erste Einstiegspunkt** für alle Agents.  
Ziel: nicht alles auf einmal lesen, sondern nur das, was für die aktuelle Welle und die eigene Rolle nötig ist.

---

## 1. Erstmal nur diese Reihenfolge lesen

### Pflicht für alle als erstes
1. `AGENT_OPERATING_RULES_2026-03-29_v6.md`
2. `MASTER_PLAN_FINAL_2026-03-29_v2.md`

Danach **nicht alles weitere blind lesen**.

---

## 2. Dann nur nach Rolle weiter

### Smith liest als Nächstes
3. `EXECUTION_ROADMAP_2026-03-29_v6.md`
4. `COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`

Nur bei Bedarf:
- `PROFESSIONAL_REVIEW_2026-03-29_v6.md`
- `UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`
- `GO_TO_MARKET_STRATEGY_2026-03-28_v6.md`

### Pako liest als Nächstes
3. `COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`
4. `UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`

Danach bei Bedarf:
- relevante Phase aus `EXECUTION_ROADMAP_2026-03-29_v6.md`
- `GO_TO_MARKET_STRATEGY_2026-03-28_v6.md`

### Jarvis liest als Nächstes
3. `EXECUTION_ROADMAP_2026-03-29_v6.md`
4. `PROFESSIONAL_REVIEW_2026-03-29_v6.md`
5. `UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`
6. `GO_TO_MARKET_STRATEGY_2026-03-28_v6.md`

Danach bei Bedarf:
- `COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`

---

## 3. Womit zuerst gearbeitet wird

## Welle A zuerst. Nichts überspringen.
Zuerst wird **nur Welle A** gemacht:

- Baseline
- System Map
- Engineering Standards
- Risk Register
- Security Review

Keine Expansion.  
Kein Plattformausbau.  
Kein Frontend-Rewrite.  
Keine parallelen Sonderfälle.

---

## 4. Welche Datei ist für was die Wahrheit?

### Regeln / Arbeitsweise
`AGENT_OPERATING_RULES_2026-03-29_v6.md`

### Reihenfolge / Gates / Wellen
`EXECUTION_ROADMAP_2026-03-29_v6.md`

### konkrete Tickets / Owners / Reviewer
`COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`

### Qualitätsmaßstab
`PROFESSIONAL_REVIEW_2026-03-29_v6.md`

### UI- und Seitenstruktur
`UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`

### Markt / Positionierung / Launch
`GO_TO_MARKET_STRATEGY_2026-03-28_v6.md`

---

## 5. Ab welchem Zeitpunkt welche Datei aktiv wichtig wird?

### Sofort wichtig
- Operating Rules
- Master Plan
- Roadmap
- Ticket Backlog

### Ab Welle B wichtig
- Professional Review
- UI Information Architecture Guide

### Ab Welle D besonders wichtig
- UI Information Architecture Guide aktiv für Dashboard / Create / Detailseiten

### Ab Welle E/F wichtig
- Go To Market Strategy aktiv für Packaging, Beta, Positionierung, Launch-Gates

### Später / nur bei Bedarf
- `PROJECT_FUTURE_DOCS_AND_WHEN_2026-03-29.md`
  - nur als Orientierung, was später noch nachgezogen werden muss
  - nicht als tägliche Arbeitsdatei

---

## 6. Praktische Arbeitsregel
Nicht mehr Dateien laden als nötig.

### Minimum im Kontext
#### Smith
- Operating Rules
- Roadmap
- Ticket Backlog

#### Pako
- Operating Rules
- Ticket Backlog
- UI Guide

#### Jarvis
- Operating Rules
- Roadmap
- Professional Review
- UI Guide
- GTM

---

## 7. Wenn Unsicherheit entsteht
Nicht raten.  
Nicht halb implementieren.

Dann:
1. prüfen, welche Datei dafür zuständig ist
2. bei Bedarf Spike oder RFC machen
3. erst danach umsetzen

---

## 8. Kurzfassung
### Erst lesen
- Operating Rules
- Master Plan

### Dann rollenbasiert weiterlesen
- Smith: Roadmap + Backlog
- Pako: Backlog + UI Guide
- Jarvis: Roadmap + Professional Review + UI Guide + GTM

### Erst arbeiten an
- nur Welle A

### Später aktiv dazunehmen
- UI Guide ab Welle B/D
- GTM ab Welle E/F

## Ein-Satz-Regel
**Nicht alles gleichzeitig lesen und laden — nur die Dateien nutzen, die für Rolle und aktuelle Welle wirklich nötig sind.**
