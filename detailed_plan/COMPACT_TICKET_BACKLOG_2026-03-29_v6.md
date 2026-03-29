# COMPACT TICKET BACKLOG v6

## Zweck
Kompakter Backlog für die Agents.  
Keine langen Begründungen, nur steuerbare Tickets.

## Format
`ID | Typ | Bereich | Owner | Reviewer | Depends | Ergebnis`

---

## Welle A – Basis
A01 | Enablement | CP | Smith | Jarvis | - | Baseline-Tag + Hauptpfad + Freeze-Regeln  
A02 | Spike | PC | Smith | Jarvis | - | Current System Map  
A03 | Enablement | EN | Pako | Smith+Jarvis | - | Engineering Standards (DoR/DoD/Review/WIP)  
A04 | Spike | EN | Jarvis | Smith | A02 | Risk Register  
A05 | Spike | EN | Smith | Jarvis | A04 | Security/Secrets/Config Audit  

**Gate A -> B:** A01-A05 fertig

---

## Welle B – Verträge, Härtung, UI-Framework
B01 | Spike | PC | Jarvis | Smith | A02 | Domain Model v1  
B02 | Spike | PC | Smith | Jarvis | A02+B01 | Target Architecture v1  
B03 | Spike/ADR | PC | Smith | Pako+Jarvis | B01+B02 | API/Status/Fehler-Verträge  
B04 | Spike | PC | Smith | Jarvis | B01 | Config/Scope Modell  
B05 | Enablement | EN | Pako | Smith | A03 | Teststrategie  
B06 | Enablement/Impl | EN | Pako | Jarvis | B05 | Fixtures/Testdaten  
B07 | Enablement/Impl | EN | Smith | Jarvis | A02 | Observability Minimum  
B08 | Enablement | PC | Smith | Jarvis | A02 | Migrationsstrategie  
B09 | Enablement | EN | Jarvis | Smith | A03 | Release/ADR/Rollback Standard  
B10 | Enablement | EN | Smith | Pako | B05+B07 | Deploy Verification / Smoke Checks  
B11 | Enablement | EN | Pako | Smith+Jarvis | A03+B01 | UI Information Architecture Guide  

**Gate B -> C:** B01-B11 fertig, v. a. B01-B04+B06-B11

---

## Welle C – Kernobjekte
C01 | Spike/Impl | PC | Smith | Jarvis | B01+B02+B03 | PublishJob Modell  
C02 | Spike/Impl | PC | Smith | Jarvis | B01+B02+B04 | ProviderConfig / Capability Modell  
C03 | Spike | PC | Jarvis | Smith | B01+A05 | ConnectedAccount Modell  
C04 | Spike/Plan | PC | Pako | Smith | B01 | Brand/Preset/Variant Modell  
C05 | Spike/Plan | PC | Smith | Pako | B01+B02+B04 | Asset / Storage Abstraction  
C06 | Spike | PC | Smith | Jarvis | C02+C05 | Usage / Metering Grundmodell  

**Gate C -> D:** C01-C06 fertig

---

## Welle D – Legacy kapseln + UI sauber schneiden
D01 | Refactor/Impl | PC | Smith | Pako | C01+C03 | YouTube Adapter  
D02 | Refactor Plan | PC | Smith | Pako | B02+B03 | API-first Plan für neue Kernpfade  
D03 | Spike/Plan | EN | Pako | Smith+Jarvis | B11+D02 | Dashboard Home Blueprint  
D04 | Spike/Plan | EN | Pako | Smith+Jarvis | B11+D02 | Create Flow Blueprint  
D05 | Spike/Plan | EN | Jarvis | Pako+Smith | B11+D02 | Detail Page Blueprint (Workflow/Publish/Audio Job)  
D06 | Impl | CP+PC | Pako | Smith | C01+C04+D02+D03+D04 | Workflow-/Status-UI vereinheitlichen  
D07 | Enablement | PC | Jarvis | Smith | C01-C05+D05 | Legacy Mapping komplett  
D08 | Enablement | CP | Pako | Jarvis | D04+D06+B10 | Main-Flow Regression Check  

**Gate D -> E:** D01-D08 fertig, Hauptpfad stabil, Dashboard/Create/Detail sauberer

---

## Welle E – kontrollierte Expansion vorbereiten
E01 | Spike/RFC | PC | Jarvis | Smith+Pako | D01-D08 | Expansion Decision Memo  
E02 | Spike | PC | Jarvis | Smith | B01+C03+C06 | Workspace Isolation Review  
E03 | Spike | PC | Smith | Jarvis | B08+B02 | Postgres Migration Plan  
E04 | Spike | PC | Pako | Jarvis | C06+D06 | Product Analytics Konzept  
E05 | Spike/Enablement | EN | Smith | Pako | B10+E01 | Staging / Dry-Run Strategy  

**Gate E -> Expansion:** genau eine Expansionsrichtung auswählen

---

## Ticket-Ready-Minimum
Kein Ticket starten ohne:
- Typ
- Bereich
- Owner
- Reviewer
- Abhängigkeiten
- konkretes Ergebnis
- Risiken
- Akzeptanzkriterium im Tickettext

Bei UI-Tickets zusätzlich:
- Seitentyp
- Hauptaufgabe
- Hauptaktion
- Ebene A/B/C Sichtbarkeit

---

## Review-Härte
Zwei Reviews Pflicht bei:
- Domainmodell
- DB-/Schema-Änderungen
- API-/Status-/Fehler-Verträge
- Queue/Worker
- Provider/Platform Adapter
- Security/Secrets
- Asset/Storage
- Dashboard Home Schnitt
- Create Flow Schnitt
- Detailseiten-Blueprints
