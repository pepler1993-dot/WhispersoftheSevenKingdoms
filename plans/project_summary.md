# Whispers of the Seven Kingdoms - Project Summary

## 1. Project Overview

Whispers of the Seven Kingdoms is a monorepo automation system for creating and publishing Game of Thrones-themed sleep/ambient music to YouTube and other platforms. The project enables users to select a Game of Thrones house/theme, generate appropriate audio, create visual assets, and publish the content automatically.

The core workflow is: **House selection → Audio generation → Thumbnail creation → Video rendering → Metadata generation → YouTube upload**.

## 2. Main Components

### 2.1 Dashboard and Coordination Layer (`services/sync/`)
- **Purpose**: Central control panel and user interface
- **Technology**: FastAPI web application with Jinja2 templates
- **Features**:
  - House selection interface with 8 GoT house templates
  - Audio lab for generating music based on prompts
  - Job management and status tracking
  - Library management for existing content
  - Operations dashboard with system metrics
  - Ticket system for task management

### 2.2 Pipeline Engine (`pipeline/`)
- **Purpose**: End-to-end orchestration of content creation
- **Core file**: `pipeline/pipeline.py`
- **Functions**:
  - Audio looping and post-processing
  - Thumbnail generation
  - Video rendering (static or animated)
  - Metadata generation
  - Quality assurance checks
  - YouTube upload via OAuth
  - File organization and cleanup

### 2.3 Audio Generation (`services/sync/app/audio_jobs.py` and `services/sync/app/stable_audio_gen.py`)
- **Purpose**: AI-powered music generation
- **Approach**: Stable Audio Open 1.0 via local GPU worker only (**stable-audio-local**)
- **Features**:
  - House-specific prompts and parameters
  - Short clip generation with stitching
  - Daemon mode for efficient processing

### 2.4 Data Management (`data/`)
- **Purpose**: Storage for assets, metadata, and generated content
- **Structure**:
  - `data/upload/`: Input files (songs, thumbnails, metadata)
  - `data/output/youtube/`: Final YouTube-ready assets
  - `data/assets/backgrounds/`: Theme-specific background images
  - `data/work/jobs/`: Job status and temporary files

### 2.5 Configuration (`services/sync/data/house_templates.json`)
- **Purpose**: Defines all Game of Thrones house themes
- **Content**: 10+ houses including Stark, Lannister, Targaryen, etc.
- **Features**:
  - House-specific color schemes and mottos
  - Detailed musical prompts for each house
  - Multiple variants per house (e.g., "winterfell", "godswood")
  - Default parameters for audio generation
  - Thumbnail and background generation instructions

## 3. Component Interactions and Workflow

### 3.1 User Workflow
1. User selects a house/theme in the dashboard
2. Audio generation is triggered via the preferred provider (local GPU worker)
3. Generated audio is stored in `data/upload/songs/`
4. Pipeline orchestrator processes the content:
   - Applies looping if needed (for longer durations)
   - Performs audio post-processing
   - Generates thumbnail using house-specific templates
   - Creates metadata with house-appropriate titles/descriptions
   - Renders video combining audio and visuals
   - Performs quality assurance checks
   - Optionally uploads to YouTube
5. Processed assets are organized in `data/output/youtube/`

### 3.2 Technical Architecture
```
User → Dashboard → Audio Job Layer → GPU Worker
                    ↓
              Pipeline Orchestrator → Thumbnail Generator
                                    → Metadata Generator  
                                    → Video Renderer
                                    → YouTube Uploader
                    ↓
              File System (data/upload & data/output)
                    ↓
              YouTube Platform
```

### 3.3 Data Flow
- **Input**: House selection, user parameters, existing audio (optional)
- **Processing**: Audio generation, visual asset creation, metadata generation
- **Output**: Complete YouTube-ready packages with video, thumbnail, and metadata
- **Storage**: Predictable directory structure for inspection and reuse

## 4. Technology Stack and Infrastructure

### 4.1 Core Technologies
- **Backend**: Python 3.11+, FastAPI, SQLite
- **Audio Processing**: PyTorch, Stable Audio Open, SoundFile, SciPy
- **Image Processing**: Pillow, FFmpeg
- **Web Interface**: Jinja2 templates, CSS
- **APIs**: YouTube Data API v3, OAuth2

### 4.2 Infrastructure
- **Hosting**: Proxmox virtualization environment
- **Containers**: LXC containers for services
- **Hardware**: GTX 1070 GPU for audio generation (8GB VRAM)
- **Services**:
  - LXC 103: Agent sync service (dashboard)
  - VM 104: Audio worker (GPU-enabled)
  - LXC 100: Pi-hole DNS
  - LXC 101: OpenClaw

### 4.3 Development Stack
- **Version Control**: Git with GitHub integration
- **Dependencies**: Managed via `requirements.txt`
- **Deployment**: systemd services, automated via deployment scripts
- **Monitoring**: Built-in dashboard with system metrics

## 5. Current State and Future Direction

### 5.1 Current Capabilities
- ✅ Complete end-to-end pipeline from house selection to YouTube upload
- ✅ 10+ Game of Thrones house themes with detailed configurations
- ✅ Local GPU worker for reliable audio generation
- ✅ Dashboard with comprehensive UI for operations
- ✅ Automated thumbnail and video generation
- ✅ Quality assurance and validation systems
- ✅ YouTube upload via OAuth integration

### 5.2 Active Development Areas
- **Audio Generation**: Operating and tuning Stable Audio Local on the GPU worker
- **Infrastructure**: Improving GPU worker reliability and performance
- **UI/UX**: Refining dashboard based on actual usage patterns
- **Documentation**: Implementing Diátaxis framework for comprehensive docs

### 5.3 Roadmap Priorities

#### P0 - GPU Worker Stabilization
- Complete local GPU worker setup with Stable Audio Open
- Resolve SSH connectivity issues between services
- Establish reliable audio generation pipeline

#### P1 - Audio operations documentation
- Document worker env vars, defaults, and runbook for short-track + looping
- Keep dashboard and pipeline docs aligned with stable-audio-local only

#### P2 - UI Enhancement
- Improve mobile responsiveness
- Enhance user experience based on actual usage
- Add advanced features like thumbnail editor

#### P3 - Product Logic
- Streamline workflow to reduce form inputs
- Implement YouTube Shorts pipeline
- Improve house-theme coupling

#### P4 - Robustness
- Enhance database reliability with persistent volumes
- Implement better backup strategies
- Improve error handling and recovery

### 5.4 Long-term Vision
The project aims to expand beyond Game of Thrones to other fictional universes (e.g., Lord of the Rings) while maintaining the same pipeline architecture. The focus is on creating a scalable system that can generate content for multiple themes and distribute it across various platforms (YouTube, Spotify, Apple Music, etc.).

The monetization strategy relies on YouTube's Partner Program, leveraging the unique advantage of sleep music having significantly higher watch times compared to typical content (3-8 hours per view vs 5-10 minutes).