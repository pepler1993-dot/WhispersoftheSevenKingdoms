# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-03-24T13:00:01Z
> Aktualisiert von: Smith

**Agents: Lest diese Datei zuerst. Sie enthält alles was ihr wissen müsst.**

---

## ⚠️ PFLICHT: Agent Sync Service nutzen!
- **Jede Aufgabe** muss als GitHub Issue angelegt werden, damit sie als Task im Sync Service erscheint
- **Regelmäßig** den Stand vom Sync Service pullen (Tasks, Events, Status)
- **Kein stilles Arbeiten** – alles läuft über den Sync Service nach Protokoll
- **Dashboard URL:** über ngrok (aktuelle URL im Service prüfen)
- **Webhook:** GitHub → Sync Service läuft ✅

---

## 🎯 Projektziel
Vollautomatisierte YouTube-Pipeline für GoT-themed Sleep Music.
Haus wählen → Audio generieren (Kaggle) → Thumbnail → Video → Metadaten → YouTube Upload.

## 👥 Team
| Wer | Rolle | Modell |
|---|---|---|
| Smith | Publishing, Reviews, DB-Robustheit, Code | Claude Opus 4 |
| Pako | UI/Produktlogik, GPU-Worker-Begleitung, Reviews | (wird neu konfiguriert) |
| Jarvis | Dokumentation / Diátaxis-Struktur | Step-3.5-Flash |
| Iwan | Projektleitung | Mensch |
| Kevin (@Kpepz189) | Infrastruktur, Proxmox, Server | Mensch |
| Eddi (@xDisslike) | Sync-Service, Koordination, OpenClaw | Mensch |

## ✅ PIPELINE IST CODE-COMPLETE

### Alle Komponenten fertig & getestet:
1. **Audio-Generation** → Kaggle MusicGen-Medium (Dashboard-Integration)
2. **Thumbnail-Generator** → `pipeline/scripts/thumbnails/generate_thumbnail.py` (Pillow, 8 GoT-Paletten)
3. **Video-Rendering** → `pipeline/scripts/video/render.py` (ffmpeg, 1920x1080)
4. **Metadaten-Generator** → `pipeline/scripts/metadata/metadata_gen.py`
5. **YouTube Upload** → `pipeline/scripts/publish/youtube_upload.py` (OAuth2 + API v3)
6. **Pipeline-Orchestrierung** → `pipeline/pipeline.py`
7. **Sync-Service Dashboard** → `services/sync/` (FastAPI + Jinja2)

## 🆕 NEU SEIT 22.03.2026

### Dashboard Redesign (23.03)
- **One-Click Video Factory**: Haus-Karte klicken → alle Felder auto-ausgefüllt → Go
- 8 Häuser als klickbare Karten (Winterfell, King's Landing, Targaryen, The Wall, Highgarden, Dorne, Godswood, Castamere)
- `house_templates.json`: Alle Defaults pro Haus (Prompts, Music Brief, Thumbnail Brief, Moods)
- Video-Übersicht: Karten-Layout mit farbcodiertem Status (statt Tabelle)
- Erweiterte Einstellungen hinter zuklappbarem `<details>`

### Kaggle Audio Generator (23.03)
- **Audio Generator Tab** im Dashboard (Pakos Grundgerüst + Smiths Kaggle-Verdrahtung)
- Notebook-Template wird automatisch gepatcht (TRACK_NAME, PROMPTS, TARGET_MINUTES)
- `kaggle kernels push` → Status-Polling alle 30s → Auto-Download bei "complete"
- Fertiges Audio landet in `data/upload/songs/{slug}.wav`
- Job-System mit Live-Logs, History, Cancel-Funktion
- Recovery bei Service-Restart (interrupted jobs → error)
- ⚠️ **Noch nicht live getestet** – Kaggle CLI muss auf Server installiert werden

### Metadata Form (22.03)
- JSON-Upload durch Dashboard-Formular ersetzt (Pako PR, Smith reviewed)
- Alle Felder editierbar: Title, Theme, Mood, Tags, Music Brief, Thumbnail Brief

### Monorepo Restrukturierung (22.03)
- `agent-sync-service/` → `services/sync/`
- `musicgen/` und `pipeline/` auf Root-Ebene

## 🔶 Nächste Schritte

### JETZT
1. **GPU-Worker priorisieren** – Pako begleitet Kevin jetzt direkt bei VM 104 / Treiber / `nvidia-smi`
2. **Lokalen Audio-Worker evaluieren** – danach Python-Umgebung + Modellstack + erster Mini-Test
3. **Audio-Strategie finalisieren** – Kaggle nicht mehr als Fundament betrachten; lokaler Worker zuerst, Colab als Übergangspfad mitdenken
4. **Dokumentation parallel aufbauen** – Jarvis übernimmt Diátaxis-Struktur (Tutorial / How-to / Reference / Explanation)
5. **DB-Robustheit** – Smith bearbeitet WAL / Recovery / Persistenz / Backup-Themen

### SPÄTER
- Providerfähiges Audio Lab (Local Worker / Colab / evtl. API)
- Operations um Problemansicht erweitern (`blocked`, `stale`, `failed`, `action needed`)
- Animated Renderer (30s Segmente → Loop auf 3h)
- YouTube Analytics im Dashboard
- SEO-Optimierung für YouTube-Metadaten
- README / Setup-Anleitungen ausbauen

## 📁 Wichtige Pfade (Monorepo)
```
services/sync/                      ← Dashboard (FastAPI)
  app/main.py                       ← Backend + Routes
  app/store.py                      ← SQLite DB
  app/kaggle_gen.py                 ← Kaggle Audio Generator
  data/house_templates.json         ← House-Karten Config
  templates/                        ← Jinja2 Templates
  static/css/admin.css              ← Styling

pipeline/
  pipeline.py                       ← Pipeline-Orchestrierung
  scripts/thumbnails/               ← Thumbnail-Generator
  scripts/video/                    ← Video-Renderer
  scripts/metadata/                 ← Metadaten-Generator
  scripts/publish/                  ← YouTube Upload

musicgen/
  MusicGen_Colab.ipynb              ← Kaggle Notebook Template
  prompts.json                      ← Prompt-Presets

data/upload/songs/                  ← Generierte Audio-Dateien
data/output/youtube/                ← Fertige Videos + Metadaten
```

## 🔖 Versionierung (PFLICHT für alle Agents!)
- **Aktuelle Version:** `v1.2.0`
- **Datei:** `services/sync/templates/base.html` → `sidebar-version`
- **Format:** SemVer (`vMAJOR.MINOR.PATCH`)
- **Regel:** Bei JEDER Änderung am Dashboard/Sync-Service **muss** die Version hochgezählt werden:
  - **PATCH** (z.B. v1.0.1): Bugfixes, kleine Anpassungen
  - **MINOR** (z.B. v1.1.0): Neue Features, UI-Änderungen
  - **MAJOR** (z.B. v2.0.0): Breaking Changes, großes Redesign
- **Wer:** Smith, Pako, Jarvis – jeder der Code ändert, zählt die Version hoch!
- **Wo sichtbar:** Sidebar unten links im Dashboard

## 📋 Entscheidungen (FINAL)
- MusicGen-medium für GoT-Sound
- Kaggle Free GPU für Audio (30h/Woche ≈ 40 Tracks)
- One-Click House-Karten UI (nicht 25-Felder-Formular)
- House Templates als Single Source of Truth
- Thumbnails: Template-basiert mit Pillow (kein API-Key)
- Tags: 15-25 pro Video
- Kein Auto-Start nach Audio-Gen (User reviewt erst)
- Abstract AudioGenerator Interface (Kaggle jetzt, Proxmox GPU später)
- bore.pub für SSH-Tunnel (ngrok Free kann kein TCP)

## 🔧 Infrastruktur
- **Server**: Kevins Proxmox LXC 103 (Debian 12)
- **LAN IP**: 192.168.178.65
- **Repo-Pfad**: /opt/whispers/WhispersoftheSevenKingdoms
- **Service**: `systemctl restart agent-sync`
- **SSH-Tunnel**: bore.pub (Port variiert bei Restart!)
- **Dashboard URL**: ngrok HTTP Tunnel (Eddi's Setup)
- **YouTube API**: Connected (OAuth2 Token auf Server)
- **Audio**: Kaggle Free GPU (MusicGen-Medium)
- **Backup**: Alle 6h automatisch (diese Datei)

## 📊 Erledigte PRs / Commits
| Was | Wer | Commit/PR |
|---|---|---|
| Publishing Templates + MusicGen Pipeline | Smith | PR #4 |
| Video-Rendering | Pako | PR #18 |
| Pipeline-Orchestrierung | Pako | PR #20 |
| Thumbnail-Generator | Smith | PR #19 |
| Metadaten + YouTube Upload | Smith | PR #16 |
| Dashboard Metadata Form | Pako | `5eb2d83` |
| UI Redesign Cherry-Pick | Smith | `51d172d` |
| Kaggle Dashboard MVP | Pako | `8998890` |
| One-Click House-Karten UI | Smith | `175cf98` |
| Kaggle Orchestration (real) | Smith | `c48fd0c` |

---
*Diese Datei wird bei jedem Meilenstein aktualisiert. Smith pflegt sie.*
*Automatisches Backup alle 6h per Cron.*



## 🕐 Letzte Commits (auto-generated 2026-03-24T13:00:01Z)
```
cc1dc9a feat(audio-lab): pass house_templates to audio page (#63)
3df77ef feat(audio-lab): house prompt presets dropdown (#63)
8ac26b9 fix(audio-lab): update prompt placeholder for GPU worker (#62)
cd10c2a feat(audio-lab): adapt job form for GPU worker (steps, clip length)
b4acd9a fix(audio-lab): show GPU worker health instead of Kaggle fields
d98eb0d fix(ops): remove duplicate endblock causing Jinja crash
815e253 docs: update CHANGELOG for v2.1.0
6a9daed Merge jarvis: Mobile-responsive UI polish (#60)
2e237f8 fix(ui): finish mobile polish for dashboard views
610d79a docs(agents): add Task-Lifecycle + Version/Release workflow
c31b415 fix(ui): polish mobile layout for create and detail views
b95c113 fix(ui): improve mobile responsiveness across dashboard
f7795b9 docs: add CHANGELOG.md
5897127 feat(releases): version detection + /admin/releases endpoint (#59)
9fcf90a feat(releases): add release notes template (#59)
f041d64 feat(releases): dynamic version badge + releases link in navbar (#59)
6e6606d Merge jarvis: Library Management page + asset browser
b8036f0 fix(pipeline): remove broken template fragment
badaa5e feat(gpu-worker): update StableAudioGenerator for diffusers + correct IP
a1e5807 feat(library): add previews and create-tab guidance
534656a Merge pako: Status-Labels verbessert (Freigegeben→offen, Erledigt→Abgeschlossen)
bdf3b20 feat(library): add asset library management page
8530918 fix(ops): clarify released vs completed task status labels
00a846f feat(ops): show issue title as actual task assignment
9adcf02 fix(docs): move docs under Operations + fix Jinja crash (Pako)
9ce4bd6 fix(docs): resolve landing page crash from Jinja dict.items clash
3e0eddf fix(docs): harden docs landing page and move nav under operations
a25c4a4 feat(ops): merge Pako ops improvements for project managers
68116ce feat(ops): simplify event language for project managers
fe54e54 feat(shorts): merge Jarvis shorts feature with fixes
091bf34 feat(ops): add human phase labels and issue links
414b466 fix(ops): url-encode task links in manager views
1384a2f feat(ops): make task views manager-friendly and berlin-time aware
f20cdc4 fix: f-string backslash compat for Python 3.11 (server)
1395991 chore: bump version to v1.3.0 (docs integration, webhook fix, timezone)
f8f5207 docs: cherry-pick Jarvis SHORTS_EXPANSION_PLAN + SYSTEM_ARCHITECTURE from jarvis/rebase branch
9575098 docs: update ROADMAP.md to current status (24.03.2026)
24b844d fix(dashboard): repair docs detail template
a3a5449 feat(dashboard): add search and richer user docs landing page
277add9 docs: add mandatory Sync Service protocol for all agents
6d94625 docs(agents): require issue-first sync-service workflow
ce31860 chore: webhook test 2
af10d18 fix(dashboard): repair docs markdown renderer
411a93f feat(dashboard): add user-facing docs section to navbar
b1a154c docs: clean up docs index for professional public navigation
a2967b1 docs: add changelog architecture diagram and more tutorials
50d4625 chore: webhook test
3ef22f2 docs: consolidate explanation layer with architecture and audio strategy
6f86a43 docs: modernize collaboration and automation guides
7a0b6f7 docs: expand agent playbooks and refresh reference pages
b101ba8 docs: add agent operations manual for project workflows
1ade6fc docs: refresh quickstart pipeline and repo structure for monorepo
8fd95d5 docs: establish diataxis audit and navigation structure
d60cdcf fix(dashboard): make server load indicator less misleading
4d27e24 docs: merge safe parts from Jarvis review branch
1a319c1 docs: Correct Jarvis feedback on audio generation alternatives
f84bcd2 docs: Add Smith's feedback on audio generation alternatives
6faad2d docs: Add Jarvis feedback on audio generation alternatives
8cc000b docs: refresh root README for current monorepo state
b82b35c auto: update PROJECT_STATUS.md (2026-03-24T07:04:45Z)
```
---
