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
