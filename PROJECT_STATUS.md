# PROJECT STATUS – Whispers of the Seven Kingdoms
> Letzte Aktualisierung: 2026-03-21 21:23 UTC
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

## ✅ Erledigte Meilensteine

### M1: Repo & Struktur (erledigt)
- Repo: `pepler1993-dot/WhispersoftheSevenKingdoms`
- Schema: `schemas/song.schema.json`
- 3 Demo-Songs in `upload/metadata/`
- Branch-Strategie: `BRANCHING.md`

### M2: Publishing Templates (erledigt, PR #4)
- `publishing/` – Titel, Beschreibung, Tags, Playlist-Strategie
- Competitive Analysis, SEO-Daten

### M3: MusicGen Pipeline (erledigt, PR #4)
- `publishing/musicgen/` – generate.py, merge.py, upload.py
- 8 GoT-Tracks × 5 Prompt-Variationen in prompts.json
- Google Colab Notebook bereit

### M4: Metadaten-Generator (erledigt, PR #16)
- `scripts/metadata/metadata_gen.py`
- song.json → YouTube-Titel, Beschreibung, Tags, Playlists
- 8 Lore-Einträge, Mood-basierte Titel-Varianten

### M5: YouTube Upload Script (erledigt, PR #16)
- `scripts/publish/youtube_upload.py`
- OAuth2 + YouTube Data API v3
- Resumable Upload, Retry-Logic, Playlist-Support

### M6: Video-Rendering (erledigt, PR #18)
- `scripts/video/render.py`
- Audio + Standbild → MP4 (1920x1080, H.264, AAC)

### M7: Thumbnail-Generator (erledigt, PR #19)
- `scripts/thumbnails/generate_thumbnail.py`
- 8 GoT-Farbpaletten, Text-Overlay, Vignette, Branding
- Pillow-basiert, kein API-Key nötig

### M8: Dokumentation (erledigt, PR #12, #17)
- README, PIPELINE, CONTRIBUTING, AUFGABEN aktualisiert
- Upload-Checklist, Templates

## 🔶 In Arbeit

### Pipeline-Orchestrierung (#10, Pako)
Ein Script das alles zusammenführt: Audio → Thumbnail → Video → Metadaten → Upload

## ❌ Offen / Blocker

| Was | Wer | Blocker? |
|---|---|---|
| YouTube-Kanal erstellen | Kevin | **JA** – ohne das kein Upload |
| Google Cloud + OAuth2 | Kevin | **JA** – Upload braucht API |
| GPU-Passthrough Proxmox | Kevin | Nein – Colab als Alternative |
| Erster E2E Testlauf (#15) | Alle | Wartet auf YouTube-API |
| HF Token rotieren | Kevin | Sicherheit |

## 📁 Wichtige Pfade
```
scripts/
  metadata/metadata_gen.py      ← Metadaten generieren
  publish/youtube_upload.py     ← YouTube Upload
  video/render.py               ← Video rendern
  thumbnails/generate_thumbnail.py  ← Thumbnails
  metadata/validate-song-metadata.js ← Schema-Validator
publishing/
  musicgen/                     ← Audio-Pipeline
  TAG_LIBRARY.md, TITLE_TEMPLATE.md, etc.
upload/metadata/                ← Song-JSONs
schemas/song.schema.json        ← Song-Schema
output/                         ← Generierte Dateien
```

## 🔧 Infrastruktur
- **Sync-Service**: `https://unsuitable-amina-tyrannizingly.ngrok-free.dev`
- **Protokoll**: Read → Claim → Work → Heartbeat → Resync → Release
- **Audio-Generation**: Proxmox (GTX 1070) oder Google Colab
- **Alles andere**: Eddis Server (kein GPU nötig)

## 📋 Entscheidungen (nicht mehr diskutieren)
- Audio-Speicher: GitHub als MP3
- Python CLI Scripts (kein Jupyter für Pipeline)
- MusicGen-melody für GoT-Sound
- Thumbnails: Template-basiert mit Pillow
- Tags: 15-25 pro Video
- Keine leeren Playlists

---
*Diese Datei wird bei jedem Meilenstein aktualisiert. Nicht manuell editieren – Smith pflegt sie.*
