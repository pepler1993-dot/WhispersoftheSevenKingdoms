# Release Standard

**Owner:** Jarvis  
**Reviewer:** Smith  
**Stand:** 2026-03-29  
**Welle:** B09

---

## Zweck

Dieses Dokument definiert einen verbindlichen Standard für:

- Release-Vorbereitung
- Versionierung
- Changelog-Pflege
- Tagging
- Deploy-Freigabe
- Hotfix-Abläufe
- Verweis auf Rollback

Es soll verhindern, dass Releases nur über implizites Chat-Wissen oder Einzelpersonenwissen laufen.

---

## Geltungsbereich

Dieser Standard gilt für Änderungen, die in produktive oder gemeinsam genutzte Stände überführt werden.

Er betrifft insbesondere:
- `main`
- versionierte Releases
- Deployments auf die laufende Instanz
- Hotfixes nach einem fehlerhaften Release

---

## Release-Grundsätze

1. **Kein Release ohne nachvollziehbaren Stand**  
   Es muss klar sein, welche Änderungen enthalten sind.

2. **Version, Changelog und Deploy gehören zusammen**  
   Ein Release ist nicht nur ein Push, sondern ein nachvollziehbarer Zustand.

3. **Nicht jeder Merge ist automatisch ein Release**  
   Relevante Releases werden bewusst vorbereitet und markiert.

4. **Rollback muss vor dem Deploy denkbar sein**  
   Wenn unklar ist, wie man zurückkommt, ist der Release nicht fertig vorbereitet.

---

## Rollen

### Release-Verantwortlich
Laut `PROJECT_STATUS.md` liegt der produktive Deploy primär bei **Smith**, im Notfall auch bei **Jarvis**.

Die release-verantwortliche Person ist zuständig für:
- finale Auswahl des Release-Stands
- Versionserhöhung
- Changelog-Eintrag
- Git-Tag
- Push inkl. Tags
- Deploy + Verify
- Entscheidung über Rollback bei Problemen

### Reviewer
Der benannte Reviewer prüft bei relevanten Änderungen:
- ob der Release nachvollziehbar beschrieben ist
- ob Risiken/Breaking Changes erkennbar sind
- ob Rollback/Hotfix realistisch machbar sind

---

## SemVer-Regel

Das Projekt nutzt **Semantic Versioning**:

- **MAJOR** = Breaking Changes / fundamentale Umbauten
- **MINOR** = neue Features / neue Capability ohne harte Inkompatibilität
- **PATCH** = Bugfixes / kleine Doku- oder Stabilitätsänderungen

### Faustregel
- UI-/UX-Fix, Bugfix, kleine Stabilisierung → `PATCH`
- neue größere Funktion / neue Route / neue Capability → `MINOR`
- harte Strukturänderung / Migrationsschnitt / Breaking Contract → `MAJOR`

---

## Release-Arten

## 1. Standard-Release
Normaler geplanter Release eines sinnvollen Pakets aus Änderungen.

### Pflichtbestandteile
- sauberer Stand auf `main`
- `CHANGELOG.md` aktualisiert
- Version festgelegt
- Tag erstellt
- Deploy durchgeführt
- Verify dokumentiert

## 2. Hotfix-Release
Schneller Release zur Korrektur eines produktionsrelevanten Fehlers.

### Typische Fälle
- Upload kaputt
- Create-Flow blockiert
- kritischer Runtime-Fehler
- Auth-/Security-Defekt

### Regel
Hotfixes sind **gezielt klein**. Keine Sammel-Features „weil man eh gerade dran ist“.

## 3. Doku-/Enablement-Release
Optionaler Release für dokumentations- oder betriebsrelevante Standards, wenn sie für Teamkoordination wichtig sind.

Nicht jeder Doku-Merge braucht ein Release, aber Gate-relevante Governance-/Engineering-Dokumente können einen markieren Release rechtfertigen.

---

## Standard-Release-Prozess

## Schritt 1 – Scope festziehen
Vor dem Release muss klar sein:
- Welche Issues/Tickets sind enthalten?
- Welche Commits gehören hinein?
- Gibt es bekannte offene Risiken?
- Gibt es Breaking Changes oder Migrationen?

## Schritt 2 – Readiness prüfen
Mindestens prüfen:
- `main` ist in gewünschtem Zustand
- betroffene Deliverables sind vorhanden
- kritische Flows wurden grob verifiziert
- kein bekannter Blocker ist ungelöst mit im Release versteckt

## Schritt 3 – `CHANGELOG.md` pflegen
Ein neuer Abschnitt wird angelegt oder ergänzt mit:
- Version
- Datum
- relevante Kategorien (`Added`, `Changed`, `Fixed`, `Docs`, `Ops`, `Security`)
- kurze, reale Beschreibung statt Marketing-Sprache

## Schritt 4 – Version taggen
Beispiel:
- `v4.0.1`
- `v4.1.0`
- `v5.0.0`

## Schritt 5 – Push inkl. Tag
Sowohl Commit-Stand als auch Tag werden gepusht.

## Schritt 6 – Deploy
Deploy gemäß dem realen Projektpfad durchführen.

## Schritt 7 – Verify
Nach Deploy mindestens prüfen:
- Dienst startet sauber
- Haupt-UI erreichbar
- Kernpfad nicht offensichtlich gebrochen
- bei relevanten Änderungen gezielter Smoke-Test

---

## Minimaler Verify-Standard

Nach jedem produktiven Release mindestens prüfen:

- [ ] App / Dashboard startet
- [ ] Login bzw. Zugriff funktioniert
- [ ] Hauptnavigation lädt
- [ ] zentraler Kernpfad der betroffenen Änderung funktioniert
- [ ] keine sofort sichtbaren Server-/Traceback-Fehler
- [ ] Version / Stand ist nachvollziehbar

Bei Upload-/Pipeline-Änderungen zusätzlich:
- [ ] Workflow anlegbar
- [ ] Audio-/Render-/Upload-Pfad nicht offensichtlich gebrochen
- [ ] Logs / Statusanzeigen plausibel

---

## Changelog-Regeln

### Muss rein
- sichtbare neue Features
- relevante Architektur- oder Datenmodelländerungen
- operative Änderungen mit Deploy-/Betriebswirkung
- Security-relevante Fixes
- wichtige Stabilitätsfixes

### Muss nicht rein
- triviale Tippfehler
- rein lokale Zwischenstände
- Rauschen ohne Nutzer-/Betriebsrelevanz

### Stil
- konkret
- knapp
- wahr
- lieber technisch präzise als werblich

---

## ADR-Regel

Wenn ein Release auf einer wichtigen Architekturentscheidung beruht, sollte eine passende ADR vorhanden sein oder zeitnah ergänzt werden.

ADR-pflichtig sind insbesondere:
- Datenmodell-Schnitte
- API-/Status-/Fehler-Verträge
- Queue-/Worker-Grenzen
- Security-relevante Architekturänderungen
- Provider-/Storage-Abstraktionen

ADR-Ablage:
- `docs/adrs/`

Vorlage:
- `docs/adrs/ADR_TEMPLATE.md`

---

## Hotfix-Standard

## Wann Hotfix?
Wenn ein Defekt in einem bereits genutzten Stand schnell korrigiert werden muss und nicht auf den nächsten normalen Release warten sollte.

### Beispiele
- YouTube Upload komplett defekt
- OAuth-/Token-Handling bricht produktiven Pfad
- Create-Flow sendet falsche Daten
- Deploy startet App nicht mehr

## Hotfix-Regeln
- Scope so klein wie möglich
- Ursache und Auswirkung klar benennen
- Changelog als Fix dokumentieren
- Patch-Version erhöhen
- nach Deploy direkt verifizieren
- bei Fehlschlag nicht improvisieren, sondern Rollback prüfen

---

## Rollback-Verweis

Rollback ist nicht Teil dieses Dokuments im Detail.
Das operative Vorgehen steht in:

- `docs/engineering/ROLLBACK_RUNBOOK.md`

Vor jedem riskanteren Release muss klar sein, ob Rollback möglich ist und welcher Rücksprungzustand genutzt würde.

---

## Empfohlenes Release-Template

```markdown
## [vX.Y.Z] – YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Docs
- ...

### Ops
- ...
```

---

## Definition of Done für einen Release

Ein Release ist erst wirklich fertig, wenn:
- [ ] gewünschter Code-Stand gemerged ist
- [ ] `CHANGELOG.md` aktualisiert ist
- [ ] Version festgelegt ist
- [ ] Git-Tag erstellt wurde
- [ ] Tag gepusht wurde
- [ ] Deploy erfolgt ist
- [ ] Verify erfolgt ist
- [ ] bei Bedarf Rollback-Pfad benannt ist

---

## Nicht-Ziel

Dieses Dokument beschreibt keinen vollständigen CI/CD-Automatisierungsprozess und ersetzt keine konkrete Deploy-Dokumentation pro Host.  
Es definiert den **verbindlichen minimalen Standard**, damit Releases konsistent, reviewbar und rückbaubar bleiben.
