# agent-sync-service

Minimaler FastAPI-Dienst für GitHub-Webhooks und einen kleinen lesbaren Sync-Layer für Agents.

## Zustandsmodell
### Gültige `phase`-Werte
- `working`
- `blocked`
- `released`
- `done`
- `archived`
- `stale`

### Semantik
- `working` -> Agent bearbeitet aktiv
- `blocked` -> Agent bearbeitet, ist aber blockiert
- `released` -> kein Agent besitzt den Task gerade, Task bleibt fachlich offen
- `done` -> fachlich abgeschlossen
- `archived` -> dauerhaft aus der aktiven Sicht raus
- `stale` -> Lease war vorhanden, ist aber abgelaufen

## Wichtige Trennung
- **release** = Besitz aufgeben, Task bleibt offen
- **complete** = Task fachlich abschließen

## Lokales Setup (Entwicklung)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_WEBHOOK_SECRET='dein-langes-zufallssecret'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Server-Deployment (Debian 12 LXC / VM)

Ressourcen: 1 CPU Core, 512 MB RAM, 2 GB Disk genuegt.

### Erstinstallation
```bash
bash deploy/setup.sh                 # auf main
bash deploy/setup.sh feature-branch  # auf bestimmtem Branch
```

Das Skript installiert System-Pakete, klont das Repo nach `/opt/whispers/`,
erstellt ein Python-venv und richtet einen systemd-Service ein.

Danach:
1. Webhook-Secret setzen: `GITHUB_WEBHOOK_SECRET` in `/etc/systemd/system/agent-sync.service` anpassen
2. `systemctl daemon-reload && systemctl start agent-sync`
3. Dashboard: `http://localhost:8000/admin`

### Update
```bash
bash /opt/whispers/WhispersoftheSevenKingdoms/services/sync/deploy/update.sh
```
Pullt den neuesten Stand, installiert Dependencies und startet den Service neu.

### Logs
```bash
journalctl -u agent-sync -f          # Live-Logs
systemctl status agent-sync          # Status
```

## GitHub Webhook konfigurieren
Im Repo unter `Settings -> Webhooks -> Add webhook`:
- **Payload URL:** `https://DEINE-URL/github/webhook`
- **Content type:** `application/json`
- **Secret:** muss **exakt** dem Wert von `GITHUB_WEBHOOK_SECRET` auf dem Server entsprechen
- **Events:**
  - `issues`
  - `issue_comment`
  - `pull_request`
  - `pull_request_review`
  - `pull_request_review_comment`
  - `push`

## Persistenz
Primärspeicher ist jetzt SQLite mit relationalen Tabellen:
- `github_events`
- `task_snapshots`
- `task_events`
- `task_states`

Datei:
- `data/agent_sync.db`

Altlast / Migration:
- vorhandene `data/*.json` Dateien oder alter Blob-Store werden beim ersten Start einmalig übernommen
- danach ist SQLite die Wahrheit

## task_state-Felder
- `owner_agent`
- `lease_until`
- `heartbeat_at`
- `phase`
- `blocked_reason`
- `latest_seq`
- `snapshot`

## Endpunkte
### Webhook / Debug
- `GET /healthz`
- `POST /github/webhook`
- `GET /github/events`
- `GET /github/events/{delivery_id}`
- `GET /github/tasks`
- `GET /github/task?task_id=owner/repo#123`
- `GET /debug/events`
- `GET /debug/tasks`

### Agent-Read-API
- `GET /tasks`
- `GET /tasks/{task_id}`
- `GET /tasks/{task_id}/events?after_seq=0`

### Agent-Write-API
- `POST /tasks/{task_id}/claim`
- `POST /tasks/{task_id}/heartbeat`
- `POST /tasks/{task_id}/release`
- `POST /tasks/{task_id}/complete`

Wichtig: In Pfad-Endpunkten muss `task_id` URL-encoded werden, also z. B. `owner%2Frepo%23123` statt `owner/repo#123`.

## Claim / Heartbeat / Release / Complete
### Claim
- setzt `owner_agent`, `lease_until`, `heartbeat_at`
- erlaubt nur `phase=working` oder `phase=blocked`
- überschreibt keinen fremden gültigen Lease

### Heartbeat
- nur aktueller Owner
- verlängert Lease
- erlaubt nur `phase=working` oder `phase=blocked`

### Release
- nur aktueller Owner
- gibt **nur den Besitz** auf
- setzt `owner_agent`, `lease_until`, `heartbeat_at` auf leer
- setzt `phase` auf `released`
- **schließt den Task nicht fachlich ab**

### Complete
- nur aktueller Owner
- setzt `phase` auf `done`
- leert `owner_agent`, `lease_until`, `heartbeat_at`
- setzt zusätzlich `snapshot.status` auf `done`
- schreibt Event `task.completed`

## Event-Log
Interne Ownership-/Koordinations-Events:
- `task.claimed`
- `task.heartbeat`
- `task.released`
- `task.completed`
- `task.stale`

## Stale-Erkennung
Ein Task ist stale, wenn ein Lease existiert, aber `lease_until` abgelaufen ist.
Dann wird `phase=stale` gesetzt. Der Task bleibt lesbar und kann danach neu geclaimt werden.

## Wie `/tasks` offene vs. erledigte Tasks behandelt
Standardmäßig zeigt `GET /tasks` **keine erledigten Tasks**.
Also: `done` und `archived` sind standardmäßig aus der normalen Liste raus.

Wenn du sie trotzdem sehen willst:
- `GET /tasks?include_done=true`

## Kurzablauf für Agents
1. Task lesen
2. claimen
3. periodisch heartbeat senden
4. Änderungen über `after_seq` nachziehen
5. bei fachlichem Abschluss `complete` senden
6. sonst bei Arbeitsende nur `release` senden
7. fremden gültigen Lease nicht übernehmen (Service antwortet `409`)

## Noch bewusst nicht implementiert
- keine Handoffs
- keine Bot-Automatik
- keine Agent-Subscriptions
- keine komplexe Rollenlogik
- keine automatische Reassign-Logik
- keine DB-Migration
