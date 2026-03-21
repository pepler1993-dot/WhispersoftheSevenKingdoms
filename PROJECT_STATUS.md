# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-03-21 22:46 UTC
> Aktualisiert von: Smith

**Agents: Lest diese Datei zuerst. Sie enthält alles was ihr wissen müsst.**

---

## 🎯 Projektziel
Vollautomatisierte YouTube-Pipeline für GoT-themed Sleep Music.
Ein Befehl → Audio generieren → Thumbnail → Video → Metadaten → YouTube Upload.

## 👥 Team
| Wer | Rolle | Modell |
|---|---|---|
| Smith | Publishing, Metadaten, Upload, Reviews | Claude Opus 4 |
| Pako | Video-Rendering, Pipeline, Technik | GPT-5.4 |
| Jarvis | Dokumentation | Step-3.5-Flash |
| Iwan | Projektleitung | Mensch |
| Kevin (@Kpepz189) | Infrastruktur, Proxmox | Mensch |
| Eddi (@xDisslike) | Sync-Service, Koordination | Mensch |

## ✅ PIPELINE IST CODE-COMPLETE (Stand 21.03.2026)

### Alle Komponenten fertig & getestet:
1. **Audio-Generation** → `publishing/MusicGen_Colab.ipynb` (Google Colab, GPU)
2. **Thumbnail-Generator** → `scripts/thumbnails/generate_thumbnail.py` (Pillow, 8 GoT-Paletten)
3. **Video-Rendering** → `scripts/video/render.py` (ffmpeg, 1920x1080)
4. **Metadaten-Generator** → `scripts/metadata/metadata_gen.py` (Titel, Tags, Beschreibung)
5. **YouTube Upload** → `scripts/publish/youtube_upload.py` (OAuth2 + API v3)
6. **Pipeline-Orchestrierung** → `pipeline.py` (ein Befehl für alles)
7. **Dokumentation** → `QUICKSTART.md`, `PROJECT_STATUS.md`

### Dry-Run bestanden ✅
`pipeline.py --slug whispers-of-winterfell --skip-upload` → Thumbnail + Video + Metadaten + QA ✅

### YouTube API connected ✅
- Kanal erstellt & verifiziert
- OAuth2 Credentials eingerichtet
- `client_secret.json` auf Server (gitignored)

## 🔶 Nächste Schritte

### JETZT: Erster echter Song
1. Colab öffnen → `publishing/MusicGen_Colab.ipynb` von GitHub laden
2. GPU (T4) auswählen, GitHub Token eintragen
3. Run All → ~30 Min → MP3 wird zu GitHub gepusht
4. Server: `git pull && python3 pipeline.py --slug whispers-of-winterfell`
5. Erster Song auf YouTube! 🚀

### SPÄTER: Volle Automatisierung
- GPU-Passthrough auf Kevins Proxmox (GTX 1070)
- Cron-Job für nächtliche Generierung
- Webhook für automatischen Pipeline-Start nach Audio-Push

## 📁 Wichtige Pfade
```
pipeline.py                         ← EIN BEFEHL FÜR ALLES
scripts/
  metadata/metadata_gen.py          ← Metadaten generieren
  publish/youtube_upload.py         ← YouTube Upload
  video/render.py                   ← Video rendern
  thumbnails/generate_thumbnail.py  ← Thumbnails
publishing/
  MusicGen_Colab.ipynb              ← Audio-Generation (Colab)
  musicgen/                         ← Prompts, Config, Scripts
upload/metadata/                    ← Song-JSONs (3 Demo-Songs)
upload/songs/                       ← Generierte Audio-Dateien
output/youtube/                     ← Fertige Videos + Metadaten
```

## 📋 Entscheidungen (FINAL – nicht mehr diskutieren)
- Audio-Speicher: GitHub als MP3
- Python CLI Scripts (kein Jupyter für Pipeline)
- MusicGen-medium für GoT-Sound
- Thumbnails: Template-basiert mit Pillow (kein API-Key)
- Tags: 15-25 pro Video
- Keine leeren Playlists
- Colab für Audio (manueller Start), Rest automatisch
- Prompts: stimmungsbasiert + technische Basics (BPM, Key)
- Später: Kevins Proxmox GPU für volle Automatisierung

## 🔧 Infrastruktur
- **Sync-Service**: `https://unsuitable-amina-tyrannizingly.ngrok-free.dev`
- **Backup**: Alle 6h automatisch (Cron)
- **YouTube API**: Connected (OAuth2 Token auf Server)
- **Audio**: Google Colab (T4 GPU, kostenlos)
- **Server**: Eddis Maschine (Pipeline, Upload, Cron)

## 📊 Erledigte PRs
| PR | Was | Wer |
|---|---|---|
| #4 | Publishing Templates + MusicGen Pipeline | Smith |
| #12 | Doku-Update | Jarvis |
| #16 | Metadaten-Generator + YouTube Upload | Smith |
| #17 | Templates + Checklist | Jarvis |
| #18 | Video-Rendering | Pako |
| #19 | Thumbnail-Generator | Smith |
| #20 | Pipeline-Orchestrierung | Pako |
| #25 | QUICKSTART.md | Jarvis |

---
*Diese Datei wird bei jedem Meilenstein aktualisiert. Smith pflegt sie.*
