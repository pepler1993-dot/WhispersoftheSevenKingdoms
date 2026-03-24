# Working in This Project

## Zweck
Diese Seite beschreibt, wie Agenten in diesem Repo arbeiten sollen.

Ziel ist nicht Bürokratie, sondern weniger Chaos, weniger Kollisionen und weniger kaputtgemergter Müll.

---

## Grundprinzipien

1. **Erst Ist-Zustand prüfen, dann ändern**
   - aktuelle Dateien lesen
   - relevanten Pfad prüfen
   - Git-Stand prüfen

2. **Kleine, klar abgegrenzte Änderungen bevorzugen**
   - ein Thema pro Commit
   - keine unnötigen Großumbauten

3. **Nicht parallel dieselbe Datei blind umschreiben**
   - vor allem bei `README.md`, `PROJECT_STATUS.md`, Templates, zentralen UI-Dateien

4. **Keine Secrets committen**
   - keine Tokens
   - keine OAuth-Secrets
   - keine lokalen Zugangsdaten

5. **Nicht fantasieren**
   - wenn Technikpfad instabil ist, Doku nicht so schreiben, als wäre alles fertig

---

## Bevor ein Agent loslegt

Checkliste:
- `README.md` lesen
- `PROJECT_STATUS.md` lesen
- relevante Doku lesen
- `git status` prüfen
- `git fetch --all --prune` ausführen
- feststellen, ob auf `main` oder einem Arbeitsbranch gearbeitet werden soll

---

## Issue-first und Sync-first

Für echte Aufgaben gilt in diesem Projekt ab jetzt:

1. **erst GitHub-Issue anlegen**
2. dadurch erscheint die Aufgabe als Task im Sync-Service
3. **erst dann** Task lesen, claimen und bearbeiten
4. während der Arbeit regelmäßig den Stand aus dem Sync-Service nachziehen

Ohne Issue kein sauberer Task. Ohne Task keine saubere Koordination.

---

## Branching-Regeln

### Direkt auf `main`
Erlaubt für:
- kleine saubere Doku-Änderungen
- klar isolierte Fixes
- sichere, konfliktarme Aktualisierungen

### Eigener Branch
Besser für:
- größere Refactors
- Änderungen mit Konfliktpotenzial
- experimentelle Doku- oder UI-Umbauten
- alles, was erst reviewed werden sollte

Branch-Namensmuster:

```text
agent/<name>-<kurzer-zweck>
feature/<name>-<kurzer-zweck>
docs/<name>-<kurzer-zweck>
fix/<name>-<kurzer-zweck>
```

Beispiele:
- `docs/pako-diataxis-tutorials`
- `fix/pako-dashboard-load-copy`
- `agent/jarvis-docs-audit`

---

## Commit-Regeln

Empfohlen:
- `docs: ...`
- `fix: ...`
- `feat: ...`
- `chore: ...`

Beispiele:
- `docs: refresh quickstart for monorepo`
- `fix(dashboard): clarify server load indicator`
- `docs: add agent operations manual`

Ein Commit soll verständlich sein, ohne Hellseherprüfung.

---

## Wann ein Agent pushen soll

Pushen ist okay, wenn:
- der Arbeitsstand konsistent ist
- keine offensichtlichen Konflikte offen sind
- die Änderung in sich verständlich ist
- `main` nicht blind überschrieben wird

Nicht pushen, wenn:
- man mitten in einem halben Umbau steckt
- man alte Inhalte versehentlich zurückdreht
- unklare Konflikte ungelöst sind
- Secrets oder lokale Artefakte im Diff hängen

---

## Review-Verhalten zwischen Agenten

Wenn ein Agent die Arbeit eines anderen reviewed:
- nicht blind mergen
- prüfen, ob alte Inhalte versehentlich wiederhergestellt werden
- auf Pfad- und Strukturdrift achten
- saubere Teilübernahmen bevorzugen, wenn der Gesamtbranch gemischt ist

Selektives Übernehmen ist besser als ein heroischer Komplettmerge, der wieder kaputt ist.

---

## Doku-Regeln für Agenten

Agenten sollen in Doku klar trennen zwischen:
- **aktuellem Stand**
- **Plan / Zielbild**
- **noch nicht stabilen Bereichen**

Besonders bei diesem Projekt gilt:
- Audio ist strategisch wichtig, aber nicht überall final stabil
- alte Pfade existieren in älteren Docs, sind aber nicht mehr Hauptwahrheit
- Monorepo-Struktur muss konsistent beschrieben werden

---

## Praktische Reihenfolge bei Arbeit im Repo

1. Status lesen
2. Git-Stand prüfen
3. Scope klein halten
4. ändern
5. Diff prüfen
6. committen
7. wenn sauber: pushen

---

## Was Agenten explizit vermeiden sollen

- blindes `git pull` auf schmutzigem Worktree
- blindes Mergen größerer Branches
- zurückdrehen neuerer Änderungen durch alte Branch-Stände
- Committen von `.claw/`-internen Notizen, Tokens oder lokalen Betriebsartefakten
- Dokumentation, die so tut als sei eine Baustelle bereits gelöst


---

## Task-Lifecycle im Sync Service

Jeder Agent **muss** den korrekten Task-Lifecycle einhalten:

### Phasen

| Phase | Bedeutung | API-Endpoint |
|-------|-----------|--------------|
| `released` | Offen, verfügbar zur Bearbeitung | Standard bei neuem Task |
| `working` | Agent arbeitet aktiv daran | `POST /api/tasks/{id}/claim` |
| `blocked` | Wartend auf externe Abhängigkeit | `POST /api/tasks/{id}/update` mit phase=blocked |
| `done` | **Abgeschlossen** | `POST /api/tasks/{id}/complete` |
| `archived` | Archiviert (nach Abschluss) | Manuell |
| `stale` | Lease abgelaufen, nicht mehr aktiv | Automatisch |

### Workflow

1. Task claimen → Phase wird `working`
2. Arbeit erledigen, regelmäßig Heartbeat senden
3. **Task abschließen → `/complete` aufrufen** → Phase wird `done`

### ⚠️ Häufiger Fehler

**FALSCH:** Task nach Abschluss auf `released` setzen (= Task erscheint wieder als offen!)
**RICHTIG:** Task über `/complete` Endpoint abschließen → Phase wird `done` (= "Abgeschlossen")

`released` bedeutet "offen und verfügbar" – **nicht** "fertig und freigegeben".

### Version & Release Workflow (Smith)

Vor jedem Merge/Deploy:
1. Code reviewen
2. Merge nach main
3. `CHANGELOG.md` aktualisieren
4. Git Tag mit Semantic Versioning erstellen
5. Deploy auf LXC 103 (git pull + restart)

