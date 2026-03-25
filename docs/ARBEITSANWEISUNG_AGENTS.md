# Arbeitsanweisung: Paralleles Arbeiten im Repo

Stand: 25.03.2026

## Team

| Agent | Rolle | Branch-Prefix |
|-------|-------|---------------|
| **Smith** | Main Keeper, Reviews, Merges, Deploy, komplexe Backend-Tasks | direkt auf `main` |
| **Jarvis** | Mittelschwere Tasks (Backend-Fixes, Performance, Workflows) | `jarvis/` |
| **Pako** | Leichtere Tasks (UI, Docs, Templates, Frontend-Polish) | `pako/` |

## Neue Projektstruktur (ab v2.3.0)

```
services/sync/app/
  main.py           ← NUR App-Init, Router-Imports, Startup
  models.py         ← Pydantic Models (Shared)
  helpers.py        ← Shared Helper-Funktionen
  store.py          ← Core DB (nur Schema + bestehende Tabellen)
  routes/
    dashboard.py    ← /admin Homepage, Server Stats, Backup
    ops.py          ← /admin/ops, Tasks, Events, System, Protocol Health
    pipeline.py     ← /admin/pipeline/*, Runs, Previews
    audio.py        ← /admin/audio/*, Jobs, Streaming
    library.py      ← /admin/library/*, Upload, Preview
    docs.py         ← /admin/docs/*
    shorts.py       ← /admin/shorts/*
    github_api.py   ← /github/webhook, Events, Tasks
    tasks_api.py    ← /tasks/* (Claim, Heartbeat, Release, Complete)
    health.py       ← /healthz, Debug
    tickets.py      ← /admin/tickets/* (NEU - Smith baut das)
```

## ⚠️ Wichtigste Regeln

### 1. KEINE großen Dateien gleichzeitig editieren
- `main.py` wird NICHT mehr editiert (nur Smith für Router-Includes)
- Jeder arbeitet in SEINEM Route-File oder Template
- Neue Features = NEUES File, nicht bestehende aufblähen

### 2. Branch-Workflow
```
1. git pull origin main                    ← Immer aktuellen Stand holen
2. git checkout -b jarvis/mein-feature     ← Neuer Branch
3. Arbeiten, committen (max 3-5 Commits)
4. git push origin jarvis/mein-feature     ← Pushen
5. Im Chat Bescheid geben → Smith reviewed + merged
6. Nach Merge: git checkout main && git pull origin main
```

### 3. Was WO editiert wird

| Datei / Bereich | Wer darf | Warum |
|-----------------|----------|-------|
| `main.py` | Nur Smith | Router-Includes, App-Init |
| `helpers.py` | Alle (mit Absprache) | Shared Functions |
| `store.py` | Alle (mit Absprache) | Nur NEUE Methoden hinzufügen, bestehende nicht ändern |
| `routes/*.py` | Der zuständige Agent | Jeder sein Route-File |
| `templates/*.html` | Der zuständige Agent | Zum eigenen Feature gehörend |
| `docs/` | Pako primär | Docs sind Pakos Revier |

### 4. Neue DB-Tabellen
- Eigenes Store-Modul erstellen: `stores/tickets.py`, `stores/queue.py` etc.
- NICHT `store.py` aufblähen
- Schema-Migration in eigenem Modul

### 5. Neue Templates
- Template-Name = Feature-Name: `tickets.html`, `ticket_detail.html`
- NICHT bestehende Templates für neue Features missbrauchen

## Commit-Konventionen
```
feat(tickets): add ticket creation form
fix(audio): correct cancel flow for running jobs  
refactor(ops): extract protocol health into helper
docs(library): rewrite upload guide from user perspective
```

## Review-Prozess
1. Branch fertig → im Chat "@Smith, bitte review `jarvis/mein-branch`"
2. Smith reviewed den Diff
3. Wenn OK → Smith merged nach main + deployed + Version-Bump
4. Wenn Probleme → Smith schreibt was zu fixen ist

## Konflikte vermeiden — Checkliste
- [ ] Arbeite ich in meinem eigenen Route-File?
- [ ] Erstelle ich neue Dateien statt bestehende aufzublähen?
- [ ] Habe ich vor Branch-Start `git pull origin main` gemacht?
- [ ] Ist mein Branch klein genug (max 1 Feature)?
- [ ] Habe ich Smith Bescheid gegeben dass mein Branch fertig ist?

## Deploy-Prozess (nur Smith)
```
1. Merge nach main
2. Version-Tag erstellen (git tag -a v2.x.y -m "...")
3. git push origin main --tags
4. SSH auf Server: git pull + systemctl restart agent-sync
5. Verify: Dashboard aufrufen, Version checken
```
