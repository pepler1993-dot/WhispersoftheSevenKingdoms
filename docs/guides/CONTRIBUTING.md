# Contributing

## Zweck
Diese Seite beschreibt, wie Beiträge im Projekt sauber eingebracht werden.

Sie gilt für Menschen und Agenten — bei Agenten kommen zusätzlich die speziellen Agent-Operations-Dokumente dazu.

---

## Grundregeln

1. Erst verstehen, dann ändern
2. Scope klein halten
3. Kleine, verständliche Commits
4. Keine Secrets ins Repo
5. Neue Änderungen dürfen nicht versehentlich neuere Arbeit zurückdrehen

---

## Bevor du etwas änderst

Mindestens prüfen:
- `README.md`
- `PROJECT_STATUS.md`
- relevante Doku im betroffenen Bereich
- `git status`
- `git fetch --all --prune`

---

## Branch oder `main`?

### Direkt auf `main`
Nur für:
- kleine, saubere, konfliktarme Änderungen
- isolierte Doku-Fixes
- sehr überschaubare Korrekturen

### Eigener Branch
Empfohlen für:
- größere Features
- Refactors
- konfliktträchtige Dateien
- experimentelle Änderungen
- alles, was erst reviewed werden sollte

---

## Commit-Stil

Bevorzugte Präfixe:
- `docs: ...`
- `fix: ...`
- `feat: ...`
- `chore: ...`

Beispiele:
- `docs: refresh quickstart for monorepo`
- `fix(dashboard): make server load indicator less misleading`
- `docs: add agent operations manual`

---

## Regeln für Zusammenarbeit

- gemeinsame zentrale Dateien nicht blind parallel umschreiben
- bei Konfliktpotenzial lieber Branch statt Heldentod auf `main`
- Reviews prüfen auch auf versehentliche Rollbacks
- operative Wahrheit steht nicht nur im Chat

---

## Tickets im Dashboard

Für abgestimmte Arbeit im Team gilt:
1. Ticket im Dashboard anlegen oder übernehmen
2. Status auf **in progress** setzen und ggf. Owner setzen
3. arbeiten, Status und Beschreibung aktuell halten
4. bei Abschluss auf **done** oder **closed** setzen

Mehr Details:
- [`AGENT_SYNC.md`](AGENT_SYNC.md)
- [`../agents/PLAYBOOKS.md`](../agents/PLAYBOOKS.md)
- [`../../PROJECT_STATUS.md`](../../PROJECT_STATUS.md)

---

## Quellen der Wahrheit

### Git / GitHub
- Code
- Branches
- Commits
- Reviews

### Dashboard (Tickets)
- offene / laufende Aufgaben
- Priorität und Owner

### `PROJECT_STATUS.md`
- aktueller Projektstand
- Prioritäten
- operative Lage

---

## Nicht tun

- kein Push mit Secrets im Diff
- keine alten Branch-Stände blind über neuere Arbeit schieben
- keine Doku schreiben, die instabile Technik als fertig verkauft
- kein großflächiger Umbau ohne klares Ziel

---

## Für Agenten zusätzlich relevant

Agenten sollten außerdem lesen:
- [`../agents/README.md`](../agents/README.md)
- [`../agents/WORKING_IN_THIS_PROJECT.md`](../agents/WORKING_IN_THIS_PROJECT.md)
- [`../agents/GITHUB_AND_PAT.md`](../agents/GITHUB_AND_PAT.md)
- [`../agents/PLAYBOOKS.md`](../agents/PLAYBOOKS.md)
