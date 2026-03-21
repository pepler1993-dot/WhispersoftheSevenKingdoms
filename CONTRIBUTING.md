# Contributing

## Grundregeln
1. Änderungen im eigenen Branch machen
2. Vor neuer Arbeit `git pull` auf aktuellen Stand
3. Kleine, klar abgegrenzte Commits
4. Erst nach kurzem Review nach `main`
5. Keine Secrets ins Repo

## Zusammenarbeit
- **Jarvis**: Workflow, Doku, Review, Aufgabenkoordination
- **Pako**: Struktur, technische Pipeline, Schema, QA-Basis
- **Smith**: Publishing, Plattformlogik, Upload-Metadaten, YouTube-Flow
- Gemeinsame Dateien nur mit Absprache bearbeiten

## Sync-Service ist Pflicht

Für aktive Task-Arbeit gilt nicht mehr „Chat lesen und loslegen".

### Verbindlicher Ablauf

1. **Task lesen**
   - `GET /tasks` und `GET /tasks/{task_id}` nutzen
   - Aktuellen Snapshot, Owner, Lease, Phase prüfen

2. **Claim versuchen**
   - `POST /tasks/{task_id}/claim` mit `{ "agent_id": "<deine_agent_id>" }`
   - Nur bei Erfolg (status 200) weiterarbeiten

3. **Während der Arbeit**
   - Regelmäßig Heartbeats senden: `POST /tasks/{task_id}/heartbeat`
   - Lease aktiv halten
   - Inkrementell neue Events holen: `GET /tasks/{task_id}/events?after_seq=<letzter_seq>`

4. **Vor jedem schreibenden GitHub-Schritt**
   - Resync: aktuellen Task-State lesen und Events nachziehen
   - Lease gültig? Kein fremder Lease?
   - Erst danach committen/pushen/PR erstellen

5. **Bei Claim-Fehler**
   - Nicht parallel arbeiten
   - Task neu lesen, abwarten oder anderen Task wählen

6. **Fertigstellen**
   - Finalen Stand prüfen
   - `POST /tasks/{task_id}/release` mit `{ "agent_id": "...", "phase": "released" }`

### Wichtige Regeln
- Kein Commit/Push/PR/Kommentar/Review ohne gültigen Claim
- Kein paralleles Arbeiten an demselben Task bei gültigem fremdem Lease
- Vor jedem GitHub-Write immer resyncen
- Bei abgelaufenem/unklarem Lease: sofort stoppen, neu claimen
- Telegram ist nur Steuerung/Kontext, nicht Wahrheitsquelle

### Quellen der Wahrheit
- **GitHub**: Code, Commits, PRs, Reviews, Kommentare
- **agent-sync-service**: Ownership, Lease, Aktivitätszustand, inkrementeller Änderungsabgleich

## Regeln für GitHub-Arbeit
- Kein Commit, Push, PR, Review oder Kommentar ohne gültigen Claim
- Kein paralleles Arbeiten an demselben Task gegen einen gültigen fremden Lease
- Vor jedem schreibenden GitHub-Schritt immer aktuellen Task-State und neue Events prüfen
- Bei abgelaufenem oder unklarem Lease: sofort stoppen, neu lesen, neu claimen oder warten
- Telegram ist für Steuerung und Kontext nützlich, aber nicht die primäre Wahrheitsquelle

## Quellen der Wahrheit
- **GitHub** → Code, Commits, PRs, Reviews, Kommentare
- **agent-sync-service** → Ownership, Lease, Aktivitätszustand, inkrementeller Änderungsabgleich

## Wichtige gemeinsame Konventionen
- gleicher Slug für Song, Thumbnail und Metadaten
- keine halbfertigen Dateien in die Upload-Ordner
- Übergaberegeln stehen in `PARALLEL_WORK_PLAN.md`
