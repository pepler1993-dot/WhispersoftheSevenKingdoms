# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-03-24T07:04:45Z
> Aktualisiert von: Smith

**Agents: Lest diese Datei zuerst. Sie enthält alles was ihr wissen müsst.**

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


## 🕐 Letzte Commits (auto-generated 2026-03-23T20:00:01Z)
```
0f15590 feat(kaggle): pass model parameter through to notebook (small/medium)
6bb4ca1 docs: add pako feedback to smith review
e85dc10 docs: Smith's review and feedback on audio generation alternatives
fbb21f8 docs: evaluate alternatives to kaggle audio generation
70204c2 chore: bump version to v1.1.0 (Kaggle integration, server stats, activity timeline)
d511da8 fix(musicgen): full device-agnostic notebook, clean CPU fallback for P100
996e68a fix(musicgen): downgrade to torch 2.2.2+cu118 for P100, fix DEVICE reference
52c1d04 fix(kaggle): force T4 GPU type, revert CPU fallback (caused device mismatch)
b7a0f4a fix(musicgen): use Kaggle preinstalled PyTorch, auto CPU fallback for P100
430d8ab feat(ui): add version badge v1.0.0 in sidebar + versioning rules in PROJECT_STATUS
608e21b fix(musicgen): use torch 2.4.1+cu118 (available on Kaggle, supports P100)
f528f91 fix(musicgen): install P100-compatible PyTorch (CUDA 11.8) in notebook
8159648 fix(pipeline): fix undefined status display, add clearer phase descriptions
6cb7756 fix: use CET (UTC+1) timestamps instead of UTC
74e668c fix(kaggle): parse real kernel slug from push output, fix 403 on status poll
aa5e498 feat(pipeline): live progress tracker for Kaggle audio generation
1a458cd fix(pipeline): friendly error when audio missing, redirect back with message
e894e42 feat(pipeline): integrate Kaggle audio generation directly into house selection
6d446e2 feat(pipeline): remove uploads, use library-only for audio + thumbnails
eab6b03 auto: update PROJECT_STATUS.md (2026-03-23T14:00:01Z)
4b1efe8 feat(dashboard): activity timeline (recent pipeline runs + audio jobs)
9410eb9 feat(dashboard): simplify load average to emoji status (😴→😊→😤→🔥→💀)
ab1f8f1 fix(dashboard): fix gauge text rotation - rotate only rings, not text
b4e823e feat(dashboard): fancy gauge rings for server stats (CPU/RAM/Disk/Load)
9003a4e feat(dashboard): live server stats widget (CPU, RAM, Disk, Load)
8b8f1f3 feat(pipeline): vorhandene Audio-Tracks aus Bibliothek waehlen
34e1076 fix(requirements): include sync service runtime deps
```
---
