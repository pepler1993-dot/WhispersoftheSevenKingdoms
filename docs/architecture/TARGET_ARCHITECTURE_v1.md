# Target Architecture v1

**Owner:** Smith  
**Stand:** 2026-03-29  
**Welle:** B02  
**Issue:** #138  
**Typ:** Architecture  
**Bereich:** System Design

---

## Zweck

Dieses Dokument beschreibt die Zielarchitektur für die nächste Ausbaustufe des Systems.
Es definiert ein sauberes Schichtenmodell, klare Provider-Abstraktionen und eine Migration
weg von den in `CURRENT_SYSTEM_MAP.md` dokumentierten Kopplungen.

---

## Schichtenmodell

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                           │
│              FastAPI Routes + Middleware                  │
│                                                         │
│  Verantwortung:                                         │
│  • HTTP Request/Response Handling                        │
│  • Input-Validierung (Pydantic)                         │
│  • Auth/Session-Prüfung                                 │
│  • Standardisierte Fehlerantworten                      │
│  • Rate Limiting (später)                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                         │
│              Business Logic + Orchestration              │
│                                                         │
│  Verantwortung:                                         │
│  • Workflow-Lifecycle-Management                        │
│  • Job-Erstellung und -Koordination                     │
│  • Preset/Variant-Auflösung                             │
│  • Config-Scope-Resolution                              │
│  • Validierung fachlicher Regeln                        │
│  • Event-Emission (für spätere Hooks)                   │
│                                                         │
│  Kernservices:                                          │
│  ├── WorkflowService                                    │
│  ├── AudioJobService                                    │
│  ├── PublishJobService                                   │
│  ├── AssetService                                       │
│  ├── PresetService                                      │
│  └── ConfigService                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   Adapter Layer                          │
│           Provider Interfaces + Implementations          │
│                                                         │
│  Verantwortung:                                         │
│  • Abstraktion externer Systeme                         │
│  • Austauschbare Implementierungen                      │
│  • Retry/Timeout/Error-Wrapping                         │
│                                                         │
│  Provider-Interfaces:                                   │
│  ├── AudioProvider     (GPU Worker, später Cloud APIs)   │
│  ├── PublishProvider    (YouTube, später weitere)        │
│  ├── StorageProvider    (Local FS, später S3)            │
│  └── ThumbnailProvider  (lokal, später API-basiert)     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 Persistence Layer                        │
│              Database + File Storage                     │
│                                                         │
│  Verantwortung:                                         │
│  • SQLite DB (agent_sync.db) → Entities, Jobs, Config   │
│  • File Storage (lokal, später S3) → Assets             │
│  • Migrations (Alembic oder eigenes Schema-Management)  │
│  • Repository Pattern für DB-Zugriff                    │
└─────────────────────────────────────────────────────────┘
```

---

## Provider-Abstraktionen

### AudioProvider

```python
class AudioProvider(Protocol):
    """Abstraktion für Audio-Generierung."""

    async def submit_job(self, params: AudioJobParams) -> str:
        """Gibt Job-ID zurück."""
        ...

    async def poll_status(self, job_id: str) -> JobStatus:
        """Fragt Status ab."""
        ...

    async def fetch_result(self, job_id: str) -> Asset:
        """Holt fertiges Audio als Asset."""
        ...

    async def cancel_job(self, job_id: str) -> None:
        """Bricht Job ab."""
        ...
```

**Implementierungen:**
- `SSHGpuAudioProvider` — heutiger GPU Worker über SSH/SCP (Default)
- `MockAudioProvider` — für Tests und Entwicklung
- später: `CloudAudioProvider` (Replicate, RunPod, etc.)

### PublishProvider

```python
class PublishProvider(Protocol):
    """Abstraktion für Veröffentlichung auf externe Plattformen."""

    async def upload(self, params: PublishParams) -> PublishResult:
        """Veröffentlicht Video + Metadata."""
        ...

    async def check_status(self, external_ref: str) -> PublishStatus:
        """Prüft Veröffentlichungsstatus."""
        ...
```

**Implementierungen:**
- `YouTubePublishProvider` — heutiger YouTube Upload via OAuth2
- `MockPublishProvider` — für Tests
- später: `TikTokPublishProvider`, `InstagramPublishProvider`

### StorageProvider

```python
class StorageProvider(Protocol):
    """Abstraktion für Asset-Speicherung."""

    async def store(self, data: bytes, asset_meta: AssetMeta) -> str:
        """Speichert Asset, gibt Storage-Referenz zurück."""
        ...

    async def retrieve(self, ref: str) -> bytes:
        """Holt Asset-Daten."""
        ...

    async def get_url(self, ref: str, expires_in: int = 3600) -> str:
        """Gibt (ggf. temporäre) URL zurück."""
        ...

    async def delete(self, ref: str) -> None:
        """Löscht Asset."""
        ...
```

**Implementierungen:**
- `LocalStorageProvider` — heutige Dateisystem-Ablage (`data/upload/`, `data/output/`)
- `MockStorageProvider` — für Tests
- später: `S3StorageProvider`

---

## Job/Queue-Architektur

### Ist-Zustand (CURRENT_SYSTEM_MAP.md)
- Audio-Jobs laufen als **daemon-Threads im FastAPI-Prozess**
- Pipeline-Runner startet **subprocess** direkt im Webprozess
- Bei Crash gehen laufende Jobs verloren
- Kein Retry, kein Dead-Letter, keine Job-Isolation

### Ziel-Zustand
Zwei-Phasen-Ansatz:

#### Phase 1: DB-basierte Queue (sofort umsetzbar)
```
┌────────────┐     ┌─────────────┐     ┌────────────────┐
│  API/UI    │────▶│  DB Queue    │────▶│  Worker Loop   │
│  (enqueue) │     │  (jobs table)│     │  (polling)     │
└────────────┘     └─────────────┘     └────────────────┘
```

- Jobs werden in der DB als Rows mit Status `queued` erstellt
- Ein separater Worker-Prozess (oder separater Thread-Pool) pollt die Queue
- Status-Updates via DB (`running` → `completed` / `failed`)
- Vorteile: kein neuer Stack, Crash-Recovery durch DB-Persistenz
- Jobs überleben Server-Neustarts

#### Phase 2: Task Queue (optional, bei Skalierungsbedarf)
- Migration zu Celery, ARQ oder ähnlichem
- Redis/RabbitMQ als Broker
- Nur nötig wenn: Multi-Worker, verteilte Ausführung, hohe Parallelität

### Job-Tabelle (Phase 1)

```sql
CREATE TABLE job_queue (
    id          TEXT PRIMARY KEY,
    job_type    TEXT NOT NULL,        -- 'audio', 'publish', 'pipeline'
    workflow_id TEXT,
    space_id    TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'queued',
    priority    INTEGER DEFAULT 0,
    payload     TEXT NOT NULL,         -- JSON
    result      TEXT,                  -- JSON
    error       TEXT,
    attempts    INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    created_at  TEXT NOT NULL,
    started_at  TEXT,
    finished_at TEXT,
    locked_by   TEXT,                  -- Worker-ID für Lease
    locked_at   TEXT
);
```

---

## Storage-Abstraktion

### Ist-Zustand
- Assets = Dateien mit impliziter Pfadlogik
- `data/upload/songs/{filename}` für Audio
- `data/output/youtube/{slug}/video.mp4` für Videos
- Pfade hart verdrahtet in Code und Templates

### Ziel-Zustand: Asset-Modell

```sql
CREATE TABLE assets (
    id              TEXT PRIMARY KEY,
    space_id        TEXT NOT NULL,
    asset_type      TEXT NOT NULL,      -- 'audio', 'thumbnail', 'video', 'background', 'metadata'
    status          TEXT NOT NULL DEFAULT 'available',
    storage_backend TEXT NOT NULL DEFAULT 'local',
    storage_ref     TEXT NOT NULL,       -- Backend-spezifischer Pfad/Key
    mime_type       TEXT,
    file_size       INTEGER,
    origin          TEXT,                -- 'uploaded', 'generated', 'derived'
    source_job_id   TEXT,
    workflow_id     TEXT,
    metadata_json   TEXT,
    created_at      TEXT NOT NULL,
    created_by      TEXT
);
```

**Zugriff immer über AssetService:**
```python
# Statt: open(f"data/upload/songs/{filename}")
# Jetzt:
asset = await asset_service.get(asset_id)
data = await storage.retrieve(asset.storage_ref)
url = await storage.get_url(asset.storage_ref)
```

---

## Delta zum Ist-Zustand

| Bereich | Heute (CURRENT_SYSTEM_MAP) | Ziel (Target Architecture) |
|---|---|---|
| **Struktur** | Monolithische Routes + Logik in einem Prozess | 4-Schichten-Modell mit klarer Trennung |
| **Audio-Jobs** | Daemon-Threads im Webprozess | DB-basierte Queue + separater Worker |
| **Pipeline** | subprocess im FastAPI-Prozess | Job-Queue + isolierter Pipeline-Worker |
| **GPU-Zugriff** | Direkter SSH/SCP in Route-Handlern | AudioProvider-Abstraktion |
| **YouTube** | Upload-Script direkt aufgerufen | PublishProvider-Abstraktion |
| **Dateien** | Feste Pfade (`data/upload/songs/...`) | Asset-Modell + StorageProvider |
| **Konfiguration** | house_templates.json + verstreute Defaults | Config-Scope-Modell (→ B04) |
| **Fehlerbehandlung** | Uneinheitlich, teils exception-logging | Standardisierte Error-Contracts (→ B03) |
| **Health/Monitoring** | Dashboard zeigt Status, keine Alerts | Health-Endpoints + Smoke Tests (→ B10) |

---

## Migrationsplan

### Prinzip: Inkrementell, nicht Big-Bang

Jeder Schritt liefert einen eigenständigen Mehrwert. Das System bleibt in jedem
Zwischenzustand lauffähig.

### Schritt 1: Service-Layer extrahieren
**Was:** Business-Logik aus Route-Handlern in Service-Klassen ziehen.  
**Warum:** Trennung von HTTP-Handling und Fachlogik. Testbarkeit.  
**Aufwand:** Mittel  
**Risiko:** Gering (reine Refactoring-Arbeit)

```
Vorher:  Route → DB + SSH + subprocess
Nachher: Route → Service → (noch direkt DB/SSH)
```

### Schritt 2: Provider-Interfaces einführen
**Was:** AudioProvider, PublishProvider, StorageProvider als Interfaces definieren.  
**Warum:** Austauschbarkeit, Testbarkeit (Mock-Provider).  
**Aufwand:** Mittel  
**Risiko:** Gering

```
Vorher:  Service → direkt SSH/YouTube/Filesystem
Nachher: Service → Provider Interface → SSH/YouTube/Filesystem
```

### Schritt 3: Job-Queue (DB-basiert)
**Was:** Daemon-Threads durch DB-basierte Queue ersetzen.  
**Warum:** Crash-Recovery, Retry-Logik, Job-Persistenz.  
**Aufwand:** Mittel-Hoch  
**Risiko:** Mittel (parallele Ausführung muss sauber sein)

```
Vorher:  Route startet Thread → Thread stirbt bei Crash
Nachher: Route enqueued Job → Worker pollt und führt aus
```

### Schritt 4: Asset-Modell einführen
**Was:** Assets als DB-Entitäten mit StorageProvider-Zugriff.  
**Warum:** Weg von Dateipfad-Kopplung, Vorbereitung für S3.  
**Aufwand:** Hoch  
**Risiko:** Mittel (bestehende Pfadlogik muss migriert werden)

```
Vorher:  Code kennt data/upload/songs/{name}
Nachher: Code kennt Asset-ID → StorageProvider liefert Daten
```

### Schritt 5: Persistence Layer formalisieren
**Was:** Repository-Pattern für DB-Zugriff, Schema-Migrations.  
**Warum:** Saubere DB-Abstraktion, versionierte Schema-Änderungen.  
**Aufwand:** Mittel  
**Risiko:** Gering

### Reihenfolge (empfohlen)

```
Schritt 1 (Service Layer)
    ↓
Schritt 2 (Provider Interfaces)  ←── kann parallel zu Schritt 3
    ↓
Schritt 3 (Job Queue)
    ↓
Schritt 4 (Asset Model)
    ↓
Schritt 5 (Persistence Layer)
```

---

## Nicht-Ziele für v1

- Kein Wechsel weg von SQLite (reicht für aktuelle Skala)
- Kein Kubernetes/Container-Orchestrierung
- Kein Event-Sourcing oder CQRS
- Kein Multi-Region-Deployment
- Keine vollständige API-first-Umstellung (Dashboard bleibt Server-Rendered)

---

## Zusammenfassung

Die Zielarchitektur führt ein sauberes 4-Schichten-Modell ein, das die heutigen
Kopplungen (Threads im Webprozess, harte Dateipfade, direkte SSH-Aufrufe) durch
klare Abstraktionen ersetzt. Die Migration erfolgt inkrementell — jeder Schritt
liefert eigenständigen Wert und das System bleibt durchgehend lauffähig.
