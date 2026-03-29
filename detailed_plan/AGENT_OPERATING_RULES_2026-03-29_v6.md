# AGENT OPERATING RULES v6

## Zweck
Kompakte Regeln für alle 3 Agents.  
Diese Datei soll fast immer im Kontext bleiben.

## Kontext-Ladestrategie
### Smith lädt standardmäßig
1. diese Datei
2. `EXECUTION_ROADMAP_..._v6.md`
3. `COMPACT_TICKET_BACKLOG_..._v6.md`

### Pako lädt standardmäßig
1. diese Datei
2. `COMPACT_TICKET_BACKLOG_..._v6.md`
3. `UI_INFORMATION_ARCHITECTURE_GUIDE_..._v5.md`

### Jarvis lädt standardmäßig
1. diese Datei
2. `EXECUTION_ROADMAP_..._v6.md`
3. `PROFESSIONAL_REVIEW_..._v6.md`
4. `UI_INFORMATION_ARCHITECTURE_GUIDE_..._v5.md`

Nur bei Bedarf zusätzliche Dateien laden.

---

## Zielbild
Ihr entwickelt nicht nur das bestehende interne Tool weiter.  
Ihr extrahiert daraus schrittweise einen generischen Produktkern.

Arbeit fällt immer in genau einen Hauptmodus:
- **CP** = Current Product stabilisieren
- **PC** = Product Core generalisieren
- **EN** = Enablement / Safety / Process

Jedes Ticket markiert genau einen Hauptmodus.

---

## Nicht verhandelbare Regeln
1. Keine zweite Plattform oder zweiter Provider als Sonderfall ohne passendes Kernmodell.
2. Keine UI-Sonderlösung, die ein schlechtes Domainmodell kaschiert.
3. Keine große Änderung ohne Owner, Reviewer, Abhängigkeiten und Akzeptanzkriterien.
4. Kein Spike mit Teil-Implementierung als Zwischending.
5. Kein stilles Entfernen von Legacy ohne Mapping oder Abschaltpfad.
6. Keine parallele Expansion auf mehreren Achsen.
7. Keine Mischseite aus Overview + Create + Debug + Settings ohne klare Begründung.

---

## WIP-Limits
### Pro Agent
- max. 2 aktive Tickets
- davon max. 1 Ticket mit hohem Architektur-/Migrationsrisiko

### Gesamtteam
- max. 1 tiefer Kernumbau gleichzeitig
- max. 1 größerer UX-/Flow-Umbau gleichzeitig
- max. 1 Enablement-/Governance-Welle gleichzeitig

---

## Ticket-Typen
### Spike
Ziel: Unsicherheit reduzieren.  
Output: Empfehlung, Optionen, Risiken, Folgetickets.

### Implementierung
Ziel: neues/angepasstes Verhalten.  
Output: Code + Tests/Checks + Doku.

### Refactor
Ziel: Struktur verbessern ohne neue Funktion.  
Output: saubererer Code + kein Funktionsverlust + Mapping/Doku.

### Enablement
Ziel: Prozess, Tests, Migrations- oder Betriebsfähigkeit verbessern.  
Output: Guide, Script, Checkliste, Setup, ADR oder Testbasis.

---

## Definition of Ready
Ein Ticket ist erst ready, wenn klar ist:
- Problem
- Hauptmodus (CP/PC/EN)
- Typ (Spike/Implementierung/Refactor/Enablement)
- Owner + Reviewer
- Abhängigkeiten
- Deliverables
- Akzeptanzkriterien
- Risiken
- ob Rollback/Fallback nötig ist

Bei UI-Tickets zusätzlich:
- Seitentyp (Overview/List/Detail/Create/Settings/Ops)
- Hauptaufgabe der Seite
- Hauptaktion der Seite
- was auf Ebene A/B/C sichtbar sein darf

---

## Definition of Done
Ein Ticket ist nur done, wenn:
- Deliverables vollständig
- Review erfolgt
- Doku angepasst
- Logging/Observability bedacht
- Migrations-/Rollback-Folgen benannt
- keine neue implizite Speziallogik entstanden
- Dashboard-Ticket sauber aktualisiert

Bei UI-Tickets zusätzlich:
- Seite folgt der UI Guide Logik
- Debug/Ops sind nicht im primären Sichtbereich gelandet
- Hauptzweck und Hauptaktion sind klar erkennbar

---

## Übergabeformat
Jede Übergabe zwischen Agents enthält:
- Kontext
- aktueller Stand
- was fix ist
- was offen ist
- Risiken
- Reviewbedarf
- nächste empfohlene Aktion

---

## Rollen
### Smith
Architektur, Datenmodell, Persistenz, Worker/Queue, Provider/Platform Adapter, Security, Migrationspfade

### Pako
Studio-Flow, UI/UX, Workflow-Darstellung, Preset-/Brand-/Variant-Logik aus Produktsicht, Fixtures aus Nutzersicht, Seitentyp- und Informationsarchitektur

### Jarvis
ADRs, Risiko-Register, Teststrategie, Release-/Rollback-Disziplin, Legacy Mapping, Prozesskonsistenz, UI-Konsistenz gegen Guide und Roadmap

---

## ADR-Pflicht
ADR nötig bei:
- Datenmodell
- API-/Status-/Fehler-Vertrag
- Queue-/Worker-Grenzen
- Provider-/Platform-Abstraktion
- Asset-/Storage-Modell
- sicherheitsrelevanten Architekturentscheidungen

RFC oder strukturierter Spike nötig bei:
- Dashboard-Home-Schnitt
- Create-Flow-Schnitt
- neuen Seitentypen oder größeren Statusdarstellungsänderungen

---

## UI-Mindestregeln
Jede Seite braucht:
- 1 Hauptzweck
- 1 Hauptaktion
- 3–5 sofort sichtbare Kerninfos

Seitentypen:
- Overview
- List
- Detail
- Create
- Settings
- Ops

Sichtbarkeitsstufen:
- A = sofort sichtbar
- B = nach kurzem Scan
- C = nur bei Bedarf

Debug/Tech darf nicht denselben visuellen Rang wie Produktentscheidungen haben.

---

## Anti-Patterns
- Sonderfall zuerst
- UI kompensiert fehlendes Modell
- Runtime-Migration als Standard
- mehrere Expansionsachsen gleichzeitig
- Dokumentation ohne Entscheidungspfad
- nur kurz Architektur im Tickettext ändern ohne ADR/RFC
- neue Tabs als Müllhalde für unklare Struktur
- Health/Ops gleichrangig mit Produktentscheidungen

---

## Stop-Kriterien
Arbeit stoppen und in Spike/RFC zurückführen, wenn:
- Hauptpfad instabil wird
- mehr als 2 Kernobjekte gleichzeitig wackeln
- kein klarer Rollback existiert
- Status-/Vertragslogik inkonsistent wird
- mehrere Ausnahmen nötig wären
- eine Seite gleichzeitig mehrere Seitentypen lösen soll

---

## Kurzmaßstab für jede Änderung
Frage immer:
1. Stabilisiert es den Hauptpfad heute?
2. Macht es den Kern morgen allgemeiner?
3. Ist die Oberfläche klarer priorisiert statt nur voller?

Wenn die Antworten nicht gut sind, gehört es nicht in die aktuelle Welle.
