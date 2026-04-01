# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-04-01T19:00:01Z
> Aktualisiert von: Pako

**Wichtig:** Es gibt jetzt **zwei gültige Source-of-Truth-Ebenen**:
- **`PROJECT_STATUS.md`** = aktueller Ist-Stand des Projekts
- **`detailed_plan/*`** = Zielbild, Zukunftsplan, Struktur der Weiterentwicklung

Beide sind führend — aber **für unterschiedliche Zwecke**.

---

## ✅ Source of Truth

### 1) Aktueller Status
**`PROJECT_STATUS.md`** ist die maßgebliche Referenz für:
- aktuellen Stand
- laufende Umsetzung
- bereits vorhandene Systeme
- reale technische Situation im Repo / Projekt

### 2) Zukunftsplan
Die maßgeblichen Planungs- und Steuerdateien für die Weiterentwicklung liegen unter:
- `detailed_plan/AGENT_QUICK_START_2026-03-29.md`
- `detailed_plan/AGENT_OPERATING_RULES_2026-03-29_v6.md`
- `detailed_plan/MASTER_PLAN_FINAL_2026-03-29_v2.md`
- `detailed_plan/COMPACT_TICKET_BACKLOG_2026-03-29_v6.md`
- `detailed_plan/UI_INFORMATION_ARCHITECTURE_GUIDE_2026-03-29_v5.md`
- bei Bedarf: `detailed_plan/EXECUTION_ROADMAP_2026-03-29_v6.md`

### Kurzregel
- **`PROJECT_STATUS.md`** = was aktuell wirklich gilt
- **`detailed_plan/*`** = wie das System künftig strukturiert werden soll
- Bei Widersprüchen gilt: **Ist-Zustand in `PROJECT_STATUS.md`, Ziel-/Soll-Zustand in `detailed_plan/*`**

### Für Agents
- Für Statusfragen zuerst `PROJECT_STATUS.md` lesen
- Für Zielarchitektur, Regeln und Roadmap danach `detailed_plan/*` heranziehen
- Einstieg bei Bedarf über `detailed_plan/AGENT_QUICK_START_2026-03-29.md`

---

## Hinweis zu älteren Plan-/Backlog-Dateien
Ältere Roadmaps, Agent-Backlogs und ältere Architektur-/Review-Pläne sind als historischer Stand zu verstehen, **nicht mehr als führende Wahrheit**.
Wenn es Widersprüche gibt, gilt **`detailed_plan/*`**.

## 🚀 Deploy-Regeln
- **Smith deployed auf den Server.** Im Notfall auch Jarvis.
- **Derjenige der deployed ist verantwortlich für:**
  1. Release Notes in `CHANGELOG.md`
  2. Version-Tag (SemVer: `vMAJOR.MINOR.PATCH`)
  3. `git push --tags`
  4. Server pull + restart + verify
- **SemVer:** MAJOR = Breaking Changes, MINOR = neue Features, PATCH = Bugfixes

---

## 🎯 Projektziel
Vollautomatisierte YouTube-Pipeline für GoT-themed Sleep/Ambient Music.
Haus wählen → Audio generieren (GPU) → Thumbnail → Video → Metadaten → YouTube Upload.

## 👥 Team
| Wer | Rolle | Modell |
|---|---|---|
| Smith | Infra, GPU-Worker, Reviews, DB-Robustheit, Code | Claude Opus 4 |
| Pako | UI/Produktlogik, UI/UX-Testing, Reviews | (wird neu konfiguriert) |
| Jarvis | Dokumentation, Backlog-Planung, Diátaxis-Struktur | Step-3.5-Flash |
| Iwan | Projektleitung | Mensch |
| Kevin (@Kpepz189) | Infrastruktur, Proxmox, Server, Hardware | Mensch |
| Eddi (@xDisslike) | Sync-Service, Koordination, OpenClaw, Produktvision | Mensch |

## ✅ Was läuft

### GPU Audio Worker ✅ (NEU 24.03)
- **Stable Audio Open 1.0** auf GTX 1070 (8GB VRAM)
- **Worker-Daemon** läuft als systemd Service auf VM 104
- Modell wird einmal geladen, bleibt im VRAM (~3GB)
- Jobs werden als JSON-Files submitted (shell-safe via Base64)
- **Performance:** ~2 min pro 30s Clip (30 Steps, fp16)
- **Erster erfolgreicher Multi-Clip-Run:** 5 Clips + Crossfade-Stitching ✅
- Default: 30s Clips, 30 Steps (optimiert für 4GB RAM Host)
- Fallback auf Single-Shot wenn Daemon nicht läuft
- Dashboard zeigt GPU-Status, Daemon-Mode, Live-Logs

### Dashboard & Sync Service ✅
- FastAPI + Jinja2 auf LXC 103
- systemd Services für Dashboard + ngrok (auto-start bei Boot)
- One-Click House-Karten UI (8 GoT-Häuser)
- Audio Lab mit GPU-Worker Integration
- Job-System mit Live-Logs, History, Cancel
- Library Management, Video-Übersicht
- Version: `v1.2.0` (in Sidebar)

### Pipeline (Code-Complete) ✅
1. **Audio-Generation** → GPU Worker (Stable Audio Open)
2. **Thumbnail-Generator** → Pillow, 8 GoT-Paletten
3. **Video-Rendering** → ffmpeg, 1920x1080
4. **Metadaten-Generator** → Auto-generated per House
5. **YouTube Upload** → OAuth2 + API v3
6. **Pipeline-Orchestrierung** → `pipeline/pipeline.py`

## 🔶 Aktuelle Baustellen

### Infrastruktur
- **RAM-Upgrade geplant:** 32GB DDR4 kaufen (Kevin sucht auf Kleinanzeigen)
- Bis dahin: GPU-VM nur bei Bedarf starten (4GB RAM Limit auf PVE Host)
- **Domain:** `dashboard.ka189.de` via Cloudflare Tunnel (Kevin richtet Cloudflare Account ein)
- **Reverse-Tunnel:** PVE → VPS via SSH (`ssh -R 2222:localhost:22`), nicht persistent
- **LXC 102 (Telegram-Bot):** gestoppt, kein Auto-Start konfiguriert

### Dashboard Backlog (aus Jarvis' Planung)
Siehe `docs/roadmaps/DASHBOARD_TASK_BACKLOG.md` für Details.

**Priorität A – Workflow & UX:**
- Ticket-Listen und Filter im Dashboard weiter verbessern (Lesbarkeit, schnelle Triage)
- Audio Lab Ladezeit und Status-Feedback optimieren
- Create-/Workflow-Flows weiter vereinfachen

**Priorität B – Features:**
- Tickets: Prioritäten, Zuweisung und Übersichten ausbauen
- Library: Metadata-Formular, MP3/WAV Upload, Song-Preview/Playback
- Thumbnail-Editor (Drag & Drop Template-System)
- Animated Video Asset-Handling
- GPU-Worker/Server Auslastung im Dashboard
- PVE Temperatur im Dashboard
- Admin-Login mit Sessions/Cookies

**Priorität C – Cleanup:**
- Doku konsistent aus Anwender-Sicht schreiben
- Version + Metrics in System-Tab verschieben
- Nav-Leiste Mobile-Fix

## 🔧 Infrastruktur

### Proxmox (PVE Host: 192.168.178.50)
| ID | Name | Typ | RAM | Status | Funktion |
|---|---|---|---|---|---|
| 100 | pihole | LXC | 512MB | running | DNS |
| 101 | openclaw | LXC | 1GB | running | OpenClaw (Pako) |
| 102 | telegram-bot | LXC | - | **gestoppt** | Telegram Bot |
| 103 | agent-sync-service | LXC | 2GB | running | Dashboard + Sync |
| 104 | audio-worker | VM | 4GB | running* | GPU Worker (GTX 1070) |

*VM 104 nur bei Bedarf starten bis RAM-Upgrade

### Netzwerk
- PVE Host: `192.168.178.50` (lokal, kein direkter VPS-Zugang)
- GPU-VM: `192.168.178.152`
- LXC 103: `192.168.178.65`
- VPS (Smith): `46.225.57.111`
- SSH Reverse-Tunnel: PVE → VPS Port 2222

### GPU-VM (104) Details
- GPU: NVIDIA GTX 1070, 8GB VRAM, CUDA 12.4, Driver 550.163.01
- Python 3.13, PyTorch 2.5.1+cu121
- Modell: `/mnt/data/models/stable-audio-open-1.0` (~3GB fp16)
- Worker: `/opt/stable-audio-worker/worker_daemon.py`
- Jobs: `/mnt/data/jobs/` (JSON-File Protokoll)
- Output: `/mnt/data/output/`
- 200GB Daten-Disk auf `/mnt/data`
- Service: `systemctl restart audio-worker`

## 📁 Repo-Struktur
```
services/sync/                      ← Dashboard (FastAPI)
  app/main.py                       ← Backend + Routes
  app/store.py                      ← SQLite DB
  app/stable_audio_gen.py           ← GPU Audio Worker Integration
  app/audio_jobs.py                 ← Audio-Job-Erstellung (stable-audio-local only)
  data/house_templates.json         ← House-Karten Config
  templates/                        ← Jinja2 Templates
  static/css/admin.css              ← Styling
  deploy/                           ← systemd Service Files

pipeline/
  pipeline.py                       ← Pipeline-Orchestrierung
  scripts/thumbnails/               ← Thumbnail-Generator
  scripts/video/                    ← Video-Renderer
  scripts/metadata/                 ← Metadaten-Generator
  scripts/publish/                  ← YouTube Upload
  scripts/audio/                    ← Audio Tools (loop, etc.)


data/upload/songs/                  ← Generierte Audio-Dateien
data/output/youtube/                ← Fertige Videos + Metadaten

docs/
  architecture/                     ← System-Architektur, Guardrails
  roadmaps/                         ← Backlog, Expansion Plans
  technical/                        ← Tech Decisions
```

## 📋 Entscheidungen (FINAL)
- **Audio:** Stable Audio Open 1.0 via lokalen GPU-Worker
- **GPU:** GTX 1070 auf Kevins Proxmox, Worker-Daemon Modus
- **Dashboard:** ngrok → Cloudflare Tunnel Migration geplant
- **Thumbnails:** Template-basiert mit Pillow (kein API-Key)
- **Video:** ffmpeg 1920x1080
- **Tags:** 15-25 pro Video
- **Workflow:** Kein Auto-Start nach Audio-Gen (User reviewt erst)
- **RAM:** 32GB Upgrade geplant statt Server mieten

## 📊 Heutige Commits (24.03)
```
ed3d1ec fix(audio): correct gpu-worker job metadata and status logs
a4c452c docs(backlog): refine dashboard task backlog structure
d8c36bf docs(backlog): add structured dashboard task backlog
124ff02 fix(audio-worker): shell logic in _wait_for_clip caused infinite poll
04954be fix(audio-worker): v2 - shell-safe job submission, proper numpy handling
e62a7d8 feat(audio-worker): daemon mode - submit jobs via JSON, model stays loaded
94cfba1 perf(audio-worker): reduce defaults to 30s clips, 30 steps for 4GB RAM
cc1dc9a feat(audio-lab): pass house_templates to audio page (#63)
3df77ef feat(audio-lab): house prompt presets dropdown (#63)
```

---
*Diese Datei wird bei jedem Meilenstein aktualisiert. Smith pflegt sie.*


















## 🕐 Letzte Commits (auto-generated 2026-04-01T19:00:01Z)
```
d1288b9 auto: update PROJECT_STATUS.md (2026-04-01T13:00:01Z)
```
---
