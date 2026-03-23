# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-03-23 11:57 UTC
> Aktualisiert von: Smith

**Agents: Lest diese Datei zuerst. Sie enthält alles was ihr wissen müsst.**

---

## 🎯 Projektziel
Vollautomatisierte YouTube-Pipeline für GoT-themed Sleep Music.
Haus wählen → Audio generieren (Kaggle) → Thumbnail → Video → Metadaten → YouTube Upload.

## 👥 Team
| Wer | Rolle | Modell |
|---|---|---|
| Smith | Publishing, Metadaten, Upload, Reviews, Code | Claude Opus 4 |
| Pako | Video-Rendering, Pipeline, Kaggle-Integration | (wird neu konfiguriert) |
| Jarvis | Dokumentation | Step-3.5-Flash |
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
1. **SSH-Tunnel stabilisieren** – bore crasht alle 3-4 Min; Cloudflare Tunnel als Alternative evaluieren
2. **Kaggle-Integration deployen** – Code ist auf main, muss auf Server deployed werden
3. **Kaggle CLI auf Server installieren** + API Token einrichten
4. **Erster End-to-End-Test** – Haus wählen → Kaggle generiert → Audio downloaded → Pipeline → YouTube
5. **Google API Deps installieren** – `pip install -r requirements.txt` im Server-venv

### SPÄTER
- GPU-Passthrough auf Kevins Proxmox (GTX 1070) für lokale Generierung
- YouTube Analytics im Dashboard
- Animated Renderer (30s Segmente → Loop auf 3h)
- SEO-Optimierung für YouTube-Metadaten
- README.md Update mit Setup-Anleitung

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
