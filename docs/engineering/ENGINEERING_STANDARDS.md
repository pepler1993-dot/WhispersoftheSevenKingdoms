# Engineering Standards

**Owner:** Pako
**Reviewer:** Smith, Jarvis
**Stand:** 2026-03-29
**Welle:** A03

---

## Zweck

Diese Datei definiert verbindliche Arbeitsregeln für alle Agents und Contributor im Projekt.
Sie gilt ab sofort und ist Voraussetzung für Gate A → B.

---

## Definition of Ready (DoR)

Ein Ticket darf erst begonnen werden, wenn folgendes klar ist:

| Pflichtfeld | Beschreibung |
|---|---|
| **Problem** | Was ist das konkrete Problem oder Ziel? |
| **Typ** | Spike / Implementierung / Refactor / Enablement |
| **Modus** | CP (Current Product) / PC (Product Core) / EN (Enablement) |
| **Owner** | Wer ist verantwortlich? |
| **Reviewer** | Wer reviewed das Ergebnis? |
| **Abhängigkeiten** | Welche anderen Tickets müssen vorher fertig sein? |
| **Deliverables** | Was konkret wird abgeliefert? (Datei, Code, Doku) |
| **Akzeptanzkriterien** | Wann ist es wirklich done? |
| **Risiken** | Was kann schiefgehen? |
| **Rollback** | Gibt es einen Rückbauweg, falls nötig? |

Bei UI-Tickets zusätzlich:

| Pflichtfeld | Beschreibung |
|---|---|
| **Seitentyp** | Overview / List / Detail / Create / Settings / Ops |
| **Hauptaufgabe** | Was soll der Nutzer auf dieser Seite verstehen oder entscheiden? |
| **Hauptaktion** | Was ist die eine wichtigste Aktion auf dieser Seite? |
| **Sichtbarkeit A/B/C** | Was ist sofort sichtbar (A), nach kurzem Scan (B), nur bei Bedarf (C)? |

---

## Definition of Done (DoD)

Ein Ticket ist erst done, wenn:

- [ ] Alle Deliverables vollständig vorhanden
- [ ] Review durch alle benannten Reviewer erfolgt
- [ ] Dokumentation angepasst (falls betroffen)
- [ ] Logging/Observability bedacht (falls Code betroffen)
- [ ] Migrations-/Rollback-Folgen benannt oder explizit als nicht relevant markiert
- [ ] Keine neue implizite Speziallogik entstanden
- [ ] Issue im GitHub-Tracker geschlossen oder auf Done gesetzt

Bei UI-Tickets zusätzlich:

- [ ] Seite folgt der UI Guide Logik (`UI_INFORMATION_ARCHITECTURE_GUIDE_*`)
- [ ] Debug/Ops sind nicht im primären Sichtbereich gelandet
- [ ] Hauptzweck und Hauptaktion sind klar erkennbar ohne Scrollen

---

## Review-Regeln

### Ein Review reicht bei
- Doku-Patches ohne Architekturrelevanz
- Kleine UI-Fixes (Styling, Texte, Korrekturen)
- Refactoring mit klar begrenztem Scope und ohne DB-/API-Änderung

### Zwei Reviews Pflicht bei
- Domain-/Datenmodell-Änderungen
- DB-/Schema-Änderungen (inkl. Migrationen)
- API-, Status- oder Fehler-Vertragsänderungen
- Queue-/Worker-Grenzen
- Provider- oder Platform-Adapter
- Security- und Secrets-bezogene Änderungen
- Asset-/Storage-Modell
- Dashboard-Home-Schnitt oder Create-Flow-Schnitt
- Detailseiten-Blueprints
- Neue Seitentypen oder größere Statusdarstellungsänderungen

### ADR-Pflicht bei
- Datenmodell
- API-/Status-/Fehler-Vertrag
- Queue-/Worker-Grenzen
- Provider-/Platform-Abstraktion
- Asset-/Storage-Modell
- Sicherheitsrelevanten Architekturentscheidungen

---

## WIP-Limits

### Pro Agent
- Max. **2 aktive Tickets** gleichzeitig
- Davon max. **1 Ticket mit hohem Architektur- oder Migrationsrisiko**

### Gesamtteam
- Max. **1 tiefer Kernumbau** gleichzeitig
- Max. **1 größerer UX-/Flow-Umbau** gleichzeitig
- Max. **1 Enablement-/Governance-Welle** gleichzeitig

---

## Ticket-Typen

| Typ | Ziel | Erwarteter Output |
|---|---|---|
| **Spike** | Unsicherheit reduzieren | Empfehlung, Optionen, Risiken, Folgetickets |
| **Implementierung** | Neues oder angepasstes Verhalten | Code + Tests/Checks + Doku |
| **Refactor** | Struktur verbessern ohne neue Funktion | Saubererer Code + kein Funktionsverlust + Mapping/Doku |
| **Enablement** | Prozess, Tests, Migrations- oder Betriebsfähigkeit verbessern | Guide, Script, Checkliste, Setup, ADR oder Testbasis |

**Kein Spike mit Teil-Implementierung als Zwischending.**
Entweder Spike (Entscheidungsgrundlage) oder Implementierung (fertiger Code).

---

## Übergabeformat

Jede Übergabe zwischen Agents (Handoff-Kommentar im Issue oder in der PR) enthält:

1. **Kontext** – Warum wurde das gemacht?
2. **Aktueller Stand** – Was ist jetzt vorhanden?
3. **Was fix ist** – Was kann der nächste Agent als gegeben betrachten?
4. **Was offen ist** – Was wurde bewusst nicht gelöst?
5. **Risiken** – Was könnte noch problematisch sein?
6. **Reviewbedarf** – Was braucht besondere Aufmerksamkeit?
7. **Nächste Aktion** – Was ist der empfohlene nächste Schritt?

---

## Branching und Commits

- Commits immer mit sprechendem Präfix: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`
- Kein direkter Push auf `main` bei Änderungen mit Architekturrisiko
- Bei größeren Änderungen: PR mit mindestens einem Review
- Baseline-Tag `current-internal-tool-baseline` darf nicht überschrieben werden

---

## Stop-Kriterien

Arbeit stoppen und Spike/RFC einleiten, wenn:

- Hauptpfad instabil wird
- Mehr als 2 Kernobjekte gleichzeitig wackeln
- Kein klarer Rollback existiert
- Status-/Vertragslogik inkonsistent wird
- Mehrere Ausnahmen gleichzeitig nötig wären
- Eine Seite gleichzeitig mehrere Seitentypen lösen soll

---

## Kurzmaßstab für jede Änderung

Vor jedem Commit/PR drei Fragen:

1. **Stabilisiert es den Hauptpfad heute?**
2. **Macht es den Kern morgen allgemeiner?**
3. **Ist die Oberfläche klarer priorisiert statt nur voller?**

Wenn die Antworten nicht gut sind, gehört es nicht in die aktuelle Welle.
