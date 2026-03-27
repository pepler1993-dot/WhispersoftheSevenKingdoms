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

---

## Koordination im Team

Aufgaben laufen über **Tickets** im Dashboard (`/admin/tickets`), nicht über die entfernte GitHub-Task-Sync-Schicht. Details: `docs/guides/AGENT_SYNC.md`, `PROJECT_STATUS.md`.
