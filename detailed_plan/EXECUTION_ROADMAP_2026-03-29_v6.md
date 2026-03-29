# EXECUTION ROADMAP v6

## Zweck
Kompakte Roadmap mit kritischem Pfad, Gates und messbaren Zielen.  
Diese Datei beschreibt Reihenfolge, nicht alle Details.

## Kritischer Pfad
1. Baseline sichern
2. Domainmodell klären
3. Zielarchitektur klären
4. API-/Status-/Fehler-Verträge klären
5. Observability Minimum einführen
6. UI-Struktur und Seitentypen verbindlich machen
7. PublishJob / ProviderConfig / ConnectedAccount / Asset vorbereiten
8. YouTube kapseln
9. API-first Kernpfade starten
10. erst dann kontrollierte Expansion

---

## Phase 0 – Baseline und Kontrolle
**Ziel:** Alle arbeiten gegen dieselbe sichere Basis.

### Outputs
- Baseline-Tag
- Hauptpfad dokumentiert
- System Map
- Engineering Standards
- Risk Register
- Security/Secrets Review

### KPI / Exit
- kein Scope Drift
- Risiken priorisiert
- Standards aktiv
- Baseline für alle eindeutig

### Go zu Phase 1 nur wenn
- Baseline, Standards, Risk Register, Security Review fertig

---

## Phase 1 – Domain, Verträge, Zielbild
**Ziel:** Fachliches und strukturelles Fundament definieren.

### Outputs
- Domain Model v1
- Target Architecture v1
- API-/Status-/Fehler-Verträge
- Config-/Scope-Modell
- Produktfluss v1
- Legacy Mapping Start
- UI Information Architecture Guide

### KPI / Exit
- neue Kernarbeit referenziert diese Modelle
- kein neues Kernfeature ohne Bezug auf Domain + Verträge
- kein neuer größerer UI-Flow ohne Seitentyp- und Sichtbarkeitslogik

### Go zu Phase 2 nur wenn
- Domainmodell steht
- Zielarchitektur steht
- Vertragsmodell steht
- Config-Modell steht
- Legacy Mapping begonnen
- UI Guide steht

---

## Phase 2 – Härtung
**Ziel:** Vor Kernumbauten Betriebs- und Änderungsrisiko senken.

### Outputs
- Teststrategie
- Fixtures/Testdaten
- Migrationsstrategie
- Observability Minimum
- Release/ADR/Rollback Standard
- Deploy Verification / Smoke Checks

### KPI / Exit
- priorisierte Tests vorhanden
- erste Fixtures vorhanden
- Logs/Metriken/Korrelation vorhanden
- Deploys verifizierbar

### Go zu Phase 3 nur wenn
- Teststrategie + Fixtures fertig
- Migrationen reproduzierbar
- Observability Minimum aktiv
- Smoke Checks definiert
- Rollback-Regeln dokumentiert

---

## Phase 3 – Kernobjekte vorbereiten
**Ziel:** Speziallogik fachlich in neue Kernobjekte überführen.

### Outputs
- PublishJob Modell
- ProviderConfig / Capability Modell
- ConnectedAccount Modell
- Brand / Preset / Variant Modell
- Asset / Storage Abstraction
- Usage / Metering Grundmodell

### KPI / Exit
- Publish, Provider, Accounts, Assets sind fachlich trennbar
- House-System ist als Preset-Spezialfall erklärbar
- Usage ist modellierbar

### Go zu Phase 4 nur wenn
- PublishJob, ProviderConfig, ConnectedAccount, Asset-Modell und Preset-Mapping stehen

---

## Phase 4 – Legacy kapseln + UI sauber schneiden
**Ziel:** Das alte System bleibt funktionsfähig, aber der neue Kern und die neue Informationsarchitektur werden im Code sichtbar.

### Outputs
- YouTube Adapter extrahiert
- API-first Plan für neue Kernpfade
- Dashboard Home Blueprint / Refactor
- Create Flow Blueprint / Refactor
- Detailseiten-Blueprint für Workflow / Publish / Audio Job
- Workflow-/Status-UI vereinheitlicht
- Legacy Mapping vervollständigt
- Main-Flow Regression Check

### KPI / Exit
- Hauptpfad weiter nutzbar
- YouTube ist nicht mehr Kernwahrheit
- UI bildet generischere Zustände ab
- neue Kernlogik ist API-first-fähig
- Overview/Create sind produktzentrierter, Detailseiten tragen technische Tiefe

### Go zu Phase 5 nur wenn
- YouTube gekapselt
- Hauptpfad nicht verschlechtert
- API-first Richtung klar
- UI auf neues Statusmodell vorbereitet
- Dashboard/Create/Detail klarer nach Seitentypen geschnitten

---

## Phase 5 – Erste kontrollierte Expansion
**Ziel:** Genau eine Expansionsachse auf sauberem Kern.

### Auswahl – genau eine
- zweiter Provider
- zweite Plattform
- generischer ContentRequest-Flow

### Outputs
- Expansion Decision Memo
- Minimaler Beta-Zielpfad
- Telemetrie / Failure Handling
- Staging / Dry-Run Strategy

### KPI / Exit
- genau eine Richtung gewählt
- Expansion ist messbar und rückbaubar
- keine neue Sonderarchitektur entsteht
- UI folgt weiter dem Seitentyp-Modell und bläht Studio Home nicht auf

### Go zu Phase 6 nur wenn
- eine Expansion sauber läuft
- Telemetrie vorhanden
- Current Product Hauptpfad weiter stabil

---

## Phase 6 – SaaS-Härtung
**Ziel:** Erst jetzt echte Vorbereitung auf allgemeines SaaS.

### Themen
- Workspace Isolation
- Postgres Plan
- RBAC
- Compliance / Retention / Auditability
- Connected Account Lifecycle
- Quotas / Usage
- Support / Incident Runbooks
- konsistente Produktnavigation für mehrere Objekte und Teams

### KPI / Exit
- generischer Kernpfad existiert
- Tenant-Grenzen klarer
- Betriebs- und Sicherheitsbasis vor Beta tragfähig

---

## Wellen für 3 Agents
### Welle A
- Smith: Baseline, System Map, Security Review
- Pako: Engineering Standards
- Jarvis: Risk Register

### Welle B
- Smith: Target Architecture, API-Verträge, Config-Modell
- Pako: UI Information Architecture Guide, Produktfluss
- Jarvis: Domain Model, Legacy Mapping Start

### Welle C
- Smith: Migrationsstrategie, Observability, Smoke Checks
- Pako: Teststrategie, Fixtures
- Jarvis: Release/ADR/Rollback Standard

### Welle D
- Smith: PublishJob, ProviderConfig, Asset/Storage, Usage
- Pako: Brand/Preset/Variant
- Jarvis: ConnectedAccount

### Welle E
- Smith: YouTube Adapter, API-first Plan
- Pako: Dashboard Home Blueprint, Create Flow Blueprint, Workflow-/Status-UI, Main-Flow Regression Check
- Jarvis: Detail-Blueprints, Legacy Mapping fertig

### Welle F
- Jarvis: Expansion Decision Memo
- danach genau eine Expansionsrichtung

---

## Change Budget
Pro Welle:
- max. 1 tiefer Kernumbau
- max. 1 größerer UX-/Flow-Umbau
- max. 1 Enablement-/Governance-Baustein
- keine parallele Plattform- und Provider-Expansion

---

## Stop-Kriterien
Welle/Phase stoppen, wenn:
- Hauptpfad destabilisiert
- mehrere Kernobjekte gleichzeitig unsicher
- kein Rollback existiert
- Status-/Vertragslogik inkonsistent
- Expansion wieder neue Ausnahmen statt Kernlogik erzeugt
- Overview/Create/Detail wieder vermischt werden
