# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-03-24T19:00:01Z
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




## 🕐 Letzte Commits (auto-generated 2026-03-24T19:00:01Z)
```
124ff02 fix(audio-worker): shell logic in _wait_for_clip caused infinite poll
04954be fix(audio-worker): v2 - shell-safe job submission, proper numpy handling
e62a7d8 feat(audio-worker): daemon mode - submit jobs via JSON, model stays loaded
94cfba1 perf(audio-worker): reduce defaults to 30s clips, 30 steps for 4GB RAM
5fdc814 auto: update PROJECT_STATUS.md (2026-03-24T13:00:01Z)
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
```
---
