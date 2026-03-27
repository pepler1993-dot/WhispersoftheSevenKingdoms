# ⚙️ Whisper Studio → SaaS Content Engine – Konzept

## Kernidee

Alles was aktuell hardcoded GoT ist, wird zu konfigurierbaren **Spaces** + **Content Types**.

---

## 1. Spaces (= Mandanten/Projekte)

Jeder User/Team bekommt einen Space. Ein Space definiert:

- **Branding** – Name, Logo, Farben, Fonts
- **Content Types** – welche Pipelines verfügbar sind
- **Presets** – aktuell die House-Templates, aber generisch
- **API Keys** – GPU-Provider, YouTube, Suno, etc.
- **Team Members** + Rollen

> Whispers of the Seven Kingdoms = ein Space.
> Jemand anderer könnte "Lo-Fi Study Beats" oder "Nature ASMR" als Space haben.

---

## 2. Content Types (ersetzt die harte Video-Pipeline)

Statt nur "Video mit Audio" als einziger Pipeline:

| Content Type | Output | Pipeline-Steps |
|---|---|---|
| Long-Form Video | YouTube Video | Audio → Background → Render → Upload |
| Short | YouTube Short / TikTok | Clip → Text Overlay → Upload |
| Audio Only | Spotify / Podcast | Generate → Master → Distribute |
| Thumbnail Pack | Bilder | Generate → Variants → Export |
| Livestream Loop | RTMP Stream | Audio → Visual → Loop → Stream |

Jeder Content Type ist eine **Pipeline-Definition** (JSON/YAML):

```yaml
content_type: long_form_video
steps:
  - id: audio
    provider: stable-audio | suno | upload
    config: {minutes, steps, prompts}
  - id: background
    provider: stable-diffusion | upload | library
    config: {prompt, resolution}
  - id: render
    provider: ffmpeg
    config: {loop_hours, crossfade, animated}
  - id: publish
    provider: youtube | s3
    config: {visibility, tags, schedule}
```

---

## 3. Settings-Seite (neue UI-Seite)

Aufgeteilt in Tabs:

- **General** – Space-Name, Branding, Timezone, Sprache
- **Providers** – GPU-Host, API-Keys (YouTube, Suno, S3, etc.), Verbindungsstatus
- **Pipelines** – Content Types aktivieren/deaktivieren, Step-Reihenfolge
- **Presets** – House-Templates werden zu generischen Presets (CRUD im UI statt JSON-Datei)
- **Team** – Mitglieder, Rollen (Admin/Editor/Viewer)
- **Billing** – (später) Plan, Usage, Limits

---

## 4. Migration vom Ist-Zustand

| Aktuell | Wird zu |
|---|---|
| `house_templates.json` | Preset-Tabelle in DB, editierbar via Settings |
| Hardcoded GoT-Häuser | Beispiel-Presets, löschbar/erweiterbar |
| `config.yaml` GPU-Host | Provider-Settings in DB pro Space |
| Feste Pipeline (Audio→Render→Upload) | Konfigurierbare Pipeline-Definition |
| Einzelner Admin | Multi-User mit Rollen |

---

## 5. Phasenplan

### Phase 1 – Settings-Seite (jetzt machbar)
- Settings-UI mit General + Providers Tabs
- Presets aus JSON in DB migrieren → CRUD im Dashboard
- Provider-Config (GPU-Host, YouTube Token) aus Settings statt config.yaml

### Phase 2 – Content Types
- Pipeline-Definitions-Engine
- "Audio Only" als zweiter Content Type neben Video
- Content Type Auswahl im Create-Flow

### Phase 3 – Multi-Tenancy
- Spaces / Accounts
- Auth (Login, API Keys)
- Team-Management
- Isolation (eigene Presets, eigene Library, eigene Jobs)

### Phase 4 – SaaS
- Billing / Stripe
- Usage Tracking (GPU-Minuten, Storage, Uploads)
- Onboarding Flow für neue Spaces
- Public Landing Page
