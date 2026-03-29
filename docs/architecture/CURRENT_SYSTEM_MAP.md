# Current System Map

**Stand:** 2026-03-29 (Baseline `current-internal-tool-baseline`)

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (User)                        │
│                                                         │
│  Dashboard · Audio Lab · Create Video · Library · Shorts │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Sync Dashboard (FastAPI)                     │
│              Port 8000 · Uvicorn                         │
│                                                         │
│  Routes:                                                │
│  ├── /admin/dashboard     → Dashboard + Health Overview  │
│  ├── /admin/audio/*       → Audio Lab + Job Management   │
│  ├── /admin/pipeline/*    → Create Video + Workflow Mgmt │
│  ├── /admin/library/*     → Song/Background Library      │
│  ├── /admin/shorts/*      → YouTube Shorts Generator     │
│  ├── /admin/workflows/*   → Workflow List + Details      │
│  ├── /admin/ops/*         → Operations / Monitoring      │
│  ├── /admin/gpu/*         → GPU Worker Status            │
│  ├── /admin/tickets/*     → Ticket System                │
│  ├── /admin/settings/*    → Presets, Users, Providers    │
│  ├── /admin/docs/*        → Internal Documentation       │
│  ├── /api/health/*        → Health Check API             │
│  └── /auth/*              → Login / Session Management   │
│                                                         │
│  Core Modules:                                          │
│  ├── store.py          → SQLite DB (agent_sync.db)      │
│  ├── audio_jobs.py     → Audio Job CRUD + Generator API │
│  ├── stable_audio_gen.py → GPU Worker Communication     │
│  ├── pipeline_runner.py → Video Pipeline Orchestration  │
│  ├── pipeline_queue.py  → Background Queue Processing   │
│  └── helpers.py        → House Templates, Utilities     │
└────────────┬──────────────────┬─────────────────────────┘
             │                  │
             │ SSH/SCP          │ subprocess
             ▼                  ▼
┌─────────────────────┐  ┌─────────────────────────────┐
│   GPU Worker (VM)    │  │   Local Pipeline Scripts     │
│   192.168.178.152    │  │                             │
│                      │  │  audio/post_process.py      │
│  Stable Audio Open   │  │  audio/loop_audio.py        │
│  Worker Daemon       │  │  video/render_animated.py   │
│  Job Queue (/mnt/)   │  │  video/render_short.py      │
│  NVIDIA GTX 1070     │  │  thumbnails/generate_*.py   │
│  4GB VRAM            │  │  metadata/metadata_gen.py   │
│                      │  │  publish/youtube_upload.py  │
└─────────────────────┘  └──────────────┬──────────────┘
                                        │
                                        │ YouTube Data API v3
                                        ▼
                              ┌─────────────────────┐
                              │   YouTube (Google)    │
                              │   OAuth2 + Upload     │
                              │   client_secret.json  │
                              │   token.json          │
                              └─────────────────────┘
```

## Datenpfade

### Video-Erstellung (Happy Path)
```
1. User wählt Haus + Variante im Create Video UI
2. house_templates.json → Prompts, Backgrounds, Metadata
3. Audio-Job wird erstellt (SQLite) → GPU Worker generiert Clips via SSH
4. Clips werden per SCP zurückkopiert → data/upload/songs/
5. Post-Processing (ffmpeg): EQ, Reverb, Loudnorm
6. Loop Audio: Crossfade-Loop auf 3h
7. Video Render: Background + Audio → MP4 (ffmpeg)
8. YouTube Upload: OAuth2 → video.mp4 + metadata.json + thumbnail.jpg
```

### Dateistruktur
```
data/
├── upload/
│   ├── songs/           ← Audio-Dateien (generiert oder hochgeladen)
│   └── backgrounds/     ← Hintergrundbilder
├── output/
│   └── youtube/
│       └── {slug}/
│           ├── video.mp4
│           ├── metadata.json
│           └── thumbnail.jpg
└── db/
    └── agent_sync.db    ← SQLite Datenbank
```

## Externe Integrationen

| Service | Zweck | Auth | Risiko |
|---|---|---|---|
| **YouTube Data API v3** | Video-Upload, Metadata | OAuth2 (client_secret.json + token.json) | Token-Expiry, Quota-Limits |
| **GPU Worker VM** | Audio-Generierung | SSH Key (BatchMode) | VM nicht persistent, Netzwerk |
| **Stable Audio Open** | AI Audio Model | Lokal auf GPU-VM | 4GB VRAM Limit, 47s Max |
| **ngrok/Cloudflare** | Tunnel für Webhooks | Config-basiert | Instabil, kann ausfallen |

## Bekannte Kopplungen & Risikostellen

1. **Dateisystem-Kopplung:** Alles läuft über lokale Pfade (`data/upload/`, `data/output/`). Kein Object Storage.
2. **Subprocess im Webprozess:** Pipeline-Runner startet ffmpeg/Python-Scripts als subprocess im FastAPI-Prozess. Kein isolierter Worker.
3. **SQLite Single-File:** Keine Replikation, kein Backup-Automatismus (nur manueller Export).
4. **GPU-Worker über SSH:** Harte Abhängigkeit von Netzwerk-Erreichbarkeit der VM. Kein Fallback.
5. **OAuth Tokens auf Server:** `client_secret.json` und `token.json` liegen im Repo-Verzeichnis auf dem Server.
6. **Kein Health-Monitoring:** Dashboard zeigt Status, aber keine Alerts bei Ausfällen.
7. **Audio Job Threading:** Jobs laufen in daemon-Threads im Webprozess. Bei Crash gehen laufende Jobs verloren.

## Services & Ports

| Service | Host | Port | Technologie |
|---|---|---|---|
| Sync Dashboard | Server | 8000 | FastAPI + Uvicorn |
| GPU Worker Daemon | 192.168.178.152 | - (SSH) | Python + Stable Audio |
| SQLite DB | Server (lokal) | - | SQLite3 |
