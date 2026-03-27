# Whisper Studio (Sync Service)

FastAPI-Dashboard für **Pipeline**, **Audio (Stable Audio Local)**, **Library**, **Tickets**, **Doku** und **Operations**. Persistenz: **SQLite** (`DATA_DIR` / `agent_sync.db`).

> **Nicht mehr gültig:** GitHub-Webhooks, Task-Claim-API (`/api/tasks/...`) und die früher hier beschriebene Task-Tabellen-Schicht — entfernt zugunsten **Tickets** im Dashboard.

---

## Wichtige Pfade

- Einstieg: `app/main.py`
- Audio-Jobs: `app/audio_jobs.py` → `app/stable_audio_gen.py` (GPU-Worker per SSH)
- Pipeline-Anbindung: `app/pipeline_runner.py`, `app/pipeline_queue.py`
- Datenhaltung: `app/store.py` (u. a. `pipeline_runs`, `audio_jobs`, `tickets`)
- UI: `templates/`, `static/`
- Deployment: `deploy/` (systemd, Setup)

---

## Lokales Setup

```bash
cd services/sync
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATA_DIR=./data      # optional, sonst default
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Audio-Generierung braucht einen erreichbaren **GPU-Worker** (siehe `app/stable_audio_gen.py`: `GPU_WORKER_HOST`, `GPU_WORKER_USER`, `GPU_WORKER_SSH_KEY`, …).

---

## Server-Deployment

Siehe `deploy/setup.sh` und `deploy/agent-sync.service`.  
Kein `GITHUB_WEBHOOK_SECRET` mehr — das alte Webhook-Setup ist obsolet.

### CI/CD per GitHub Actions (SSH via Tailscale)

Es gibt jetzt einen Workflow unter `.github/workflows/deploy.yml`.

Trigger:
- Push auf `main`
- manueller Start über **Actions → Deploy (SSH via Tailscale) → Run workflow**

Erwartete Defaults auf dem Server:
- Repo: `/opt/whispers/WhispersoftheSevenKingdoms`
- Venv: `.venv` im Repo-Root
- systemd-Service: `agent-sync`

Benötigte GitHub Actions Secrets:
- `SSH_HOST` → am besten die Tailscale-IP oder der MagicDNS-Name des Servers
- `SSH_USER`
- `SSH_PRIVATE_KEY`
- `TS_OAUTH_CLIENT_ID`
- `TS_OAUTH_SECRET`

Wichtig:
- Der Zielserver muss bereits im Tailnet sein.
- Der GitHub-Runner joint im Workflow kurz euer Tailnet und deployt dann per SSH über Tailscale.
- Das Tailnet muss den im Workflow verwendeten CI-Tag erlauben (`tag:ci`) oder ihr entfernt/ändert das Tag im Workflow.

Optionale Repository Variables:
- `DEPLOY_PATH` (Default: `/opt/whispers/WhispersoftheSevenKingdoms`)
- `SYSTEMD_SERVICE` (Default: `agent-sync`)
- `GIT_REMOTE` (Default: `origin`)

Ablauf im Workflow:
1. GitHub-Runner joint Tailscale
2. SSH-Key laden
3. per SSH über Tailscale auf den Server verbinden
4. `git fetch` + `git checkout/reset --hard` auf den Event-Branch
5. optional `.venv/bin/pip install -r services/sync/requirements.txt`
6. `systemctl restart agent-sync`

---

## Koordination im Team

Aufgaben laufen über **Tickets** im Dashboard (`/admin/tickets`), nicht über die entfernte GitHub-Task-Sync-Schicht. Details: `docs/guides/AGENT_SYNC.md`, `PROJECT_STATUS.md`.
