# Whisper Studio

Automated content production platform for YouTube — from audio generation to video rendering to publishing.

## What it does

1. **Choose a Preset** (House + Variant with pre-configured prompts)
2. **Generate Audio** (Stable Audio Open on local GPU)
3. **Render Video** (ffmpeg, static or animated backgrounds)
4. **Generate Thumbnail** (Pillow, house-themed palettes)
5. **Upload to YouTube** (OAuth2, auto or manual)

## Tech Stack

- **Backend:** FastAPI + SQLite + Jinja2
- **Audio:** Stable Audio Open 1.0 on GTX 1070 (daemon worker)
- **Video:** ffmpeg (looping, crossfade, post-processing)
- **Upload:** YouTube Data API v3
- **Deploy:** GitHub Actions → SSH → Proxmox LXC

## Architecture

```
services/sync/          FastAPI dashboard + workflow engine
pipeline/               Audio processing, video render, upload scripts
data/
  upload/               Input: songs, thumbnails, metadata
  output/youtube/       Output: rendered videos per slug
  assets/backgrounds/   Theme backgrounds for video renderer
ui_ux/                  Design roles, workflow, principles
docs/                   Architecture, guides, references
```

## Core Concepts

### Workflows
Everything is a **Workflow** — unified entity for all content types:
- `video` — Full video (audio → render → upload)
- `short` — YouTube Short from existing video
- `song` — Standalone audio export
- `audio_lab` — Audio generation experiment

### Phases
Each workflow progresses through phases: `audio` → `render` → `upload` → `done`

### Presets
House-based presets with variants. Each variant has:
- Audio prompts for generation
- Background image (bg_key)
- Thumbnail briefing
- Title template

## Quick Start

```bash
cd services/sync
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Dashboard: `http://localhost:8000/admin`

## Team

| Role | Who |
|------|-----|
| Infrastructure + Code | Smith (AI Agent) |
| UI/UX Reviews | Pako (AI Agent) |
| Documentation | Jarvis (AI Agent) |
| Project Lead | Iwan |
| Server + Hardware | Kevin |
| Sync Service + Vision | Eddi |

## Documentation

- [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [SaaS Concept & Roadmap](docs/SAAS_CONCEPT.md)
- [Use Cases](docs/USE_CASES.md)
- [Design Principles](docs/DESIGN_PRINCIPLES.md)
- [Pipeline Guide](docs/guides/PIPELINE.md)
- [Quick Start](docs/guides/QUICKSTART.md)

## SaaS Roadmap

| Phase | Status |
|-------|--------|
| Settings & Presets | ✅ Done |
| Content Types | ✅ Done |
| Auth & Team | ✅ Done |
| Unified Workflows | ✅ Done |
| UI/UX Production-Ready | 🔄 In Progress |
| Space Isolation | ⏸️ Parked |
| Onboarding & Self-Service | 📋 Planned |
| Billing (Stripe) | 📋 Planned |

See [SAAS_CONCEPT.md](docs/SAAS_CONCEPT.md) for full roadmap.
