# Branching & Merge Strategie

## Branch-Namenskonvention
```
feature/{agent}-{beschreibung}
```
Beispiele:
- `feature/smith-publishing-v2`
- `feature/pako-video-rendering`
- `feature/jarvis-doku-update`

## Regeln

### 1. Main ist geschützt
- Niemand pusht direkt auf `main`
- Alles geht über Pull Requests
- Mindestens 1 Review (von einem anderen Agent oder Mensch)

### 2. Vor dem Arbeiten
1. `git checkout main && git pull origin main`
2. Neuen Branch erstellen: `git checkout -b feature/{agent}-{task}`
3. Issue im Sync-Service claimen

### 3. Während der Arbeit
- Nur auf eigenem Branch arbeiten
- Regelmäßig committen (kleine, beschreibende Commits)
- Heartbeats an Sync-Service senden

### 4. Vor dem PR
1. Main in eigenen Branch mergen: `git merge main`
2. Konflikte lokal lösen
3. Resync mit Sync-Service
4. Push + PR erstellen
5. PR verlinkt das Issue (`Closes #X`)

### 5. Merge-Reihenfolge bei Konflikten
Wenn mehrere PRs gleichzeitig offen sind:
1. Kleinere PRs zuerst (weniger Konflikt-Risiko)
2. Unabhängige PRs können parallel gemerged werden
3. Abhängige PRs warten (z.B. #10 wartet auf #7, #8, #9)

### 6. Nach dem Merge
1. Task im Sync-Service releasen
2. Issue wird automatisch geschlossen (durch `Closes #X`)
3. Lokalen Branch löschen: `git branch -D feature/{agent}-{task}`
4. Main pullen: `git checkout main && git pull`
5. Neuen Branch für nächsten Task

## Wer darf mergen?
- **Menschen** (Iwan, Kevin, Eddi): Immer
- **Agents**: Nur nach expliziter Freigabe durch einen Menschen
- **Ausnahme**: Doku-Updates (Jarvis) können self-merged werden

## Konflikt-Vermeidung
Jeder Agent arbeitet in seinem Bereich:
- **Smith**: `publishing/`, `scripts/metadata/`, `scripts/publish/`
- **Pako**: `scripts/video/`, `scripts/qa/`, `schemas/`, Pipeline-Root
- **Jarvis**: `*.md` Doku-Dateien (AUFGABEN, README, PIPELINE, CONTRIBUTING)

So gibt es kaum Überschneidungen.
