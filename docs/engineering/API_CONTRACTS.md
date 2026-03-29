# API / Status / Fehler-Verträge

**Owner:** Smith  
**Stand:** 2026-03-29  
**Welle:** B03  
**Issue:** #139  
**Typ:** Engineering Standard  
**Bereich:** API Design

---

## Zweck

Dieses Dokument definiert verbindliche Verträge für:
- API-Antwortformate
- Status-Lifecycles aller Kernentitäten
- HTTP-Statuscode-Konventionen
- Fehlerklassifikation

Alle neuen und überarbeiteten Endpoints müssen diese Verträge einhalten.

---

## Standard API Response Format

### Erfolg

```json
{
  "status": "ok",
  "data": {
    "id": "wf_abc123",
    "title": "Dragonstone 3h Loop",
    "status": "running"
  }
}
```

### Erfolg mit Liste + Pagination

```json
{
  "status": "ok",
  "data": [
    { "id": "wf_abc123", "title": "Dragonstone 3h Loop" },
    { "id": "wf_def456", "title": "Old Valyria Night" }
  ],
  "meta": {
    "total": 42,
    "page": 1,
    "per_page": 20
  }
}
```

### Fehler

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'title' is required.",
    "details": [
      {
        "field": "title",
        "issue": "required",
        "message": "Title must not be empty."
      }
    ]
  }
}
```

### Regeln

- `status` ist immer `"ok"` oder `"error"` — kein dritter Wert.
- Bei `"ok"` ist `data` immer vorhanden (kann `null` sein bei 204-artigen Responses).
- Bei `"error"` ist `error` immer vorhanden mit mindestens `code` und `message`.
- `error.details` ist optional und enthält feldspezifische oder kontextbezogene Info.
- `meta` ist optional, nur bei paginierten Listen.

---

## Status-Lifecycles

### Workflow Status

```
                    ┌──────────┐
                    │  draft   │
                    └────┬─────┘
                         │ configure / validate
                         ▼
                    ┌──────────┐
             ┌──────│  ready   │──────┐
             │      └────┬─────┘      │
             │           │ start      │ cancel
             │           ▼            ▼
             │      ┌──────────┐  ┌───────────┐
             │      │ running  │  │ canceled   │
             │      └────┬─────┘  └───────────┘
             │           │
             │     ┌─────┴──────┐
             │     │            │
             │     ▼            ▼
             │ ┌────────────┐ ┌──────────┐
             │ │needs_review│ │  failed   │
             │ └─────┬──────┘ └─────┬────┘
             │       │              │
             │       │ approve      │ retry
             │       ▼              │
             │ ┌───────────┐        │
             │ │ completed  │◄──────┘
             │ └───────────┘
             │       ▲
             └───────┘ (direct complete, z.B. simple workflows)
```

**Gültige Übergänge:**

| Von | Nach | Auslöser |
|---|---|---|
| `draft` | `ready` | Konfiguration vollständig, Validierung bestanden |
| `ready` | `running` | Workflow gestartet |
| `ready` | `canceled` | Nutzer bricht ab |
| `running` | `needs_review` | Automatische Schritte fertig, Review nötig |
| `running` | `completed` | Alle Schritte erfolgreich (kein Review nötig) |
| `running` | `failed` | Fehler in einem Job |
| `running` | `canceled` | Nutzer bricht ab |
| `needs_review` | `completed` | Review bestätigt |
| `needs_review` | `canceled` | Nutzer bricht ab |
| `failed` | `ready` | Retry (zurück zu ready, Neukonfiguration möglich) |

**Ungültig (Beispiele):**
- `completed` → `running` (kein Rückschritt)
- `canceled` → `running` (abgebrochen = endgültig)
- `draft` → `running` (muss erst `ready` werden)

---

### AudioJob Status

```
  ┌──────────┐
  │  queued   │
  └────┬─────┘
       │ worker picks up
       ▼
  ┌──────────┐
  │ running   │
  └────┬─────┘
       │
  ┌────┴─────┬───────────┐
  │          │           │
  ▼          ▼           ▼
┌─────────┐ ┌────────┐ ┌──────────┐
│completed│ │ failed │ │ canceled │
└─────────┘ └───┬────┘ └──────────┘
                │
                │ retry
                ▼
           ┌──────────┐
           │  queued   │
           └──────────┘
```

**Gültige Übergänge:**

| Von | Nach | Auslöser |
|---|---|---|
| `queued` | `running` | Worker übernimmt Job |
| `queued` | `canceled` | Nutzer/System bricht ab |
| `running` | `completed` | Audio erfolgreich generiert |
| `running` | `failed` | Fehler bei Generierung |
| `running` | `canceled` | Nutzer bricht ab |
| `failed` | `queued` | Retry angefordert |

---

### PublishJob Status

```
  ┌──────────┐
  │  queued   │
  └────┬─────┘
       │ worker picks up
       ▼
  ┌──────────┐
  │ running   │
  └────┬─────┘
       │
  ┌────┴─────┬───────────┐
  │          │           │
  ▼          ▼           ▼
┌─────────┐ ┌────────┐ ┌──────────┐
│completed│ │ failed │ │ canceled │
└─────────┘ └───┬────┘ └──────────┘
                │
                │ retry
                ▼
           ┌──────────┐
           │  queued   │
           └──────────┘
```

**Gültige Übergänge:** Identisch zu AudioJob.

| Von | Nach | Auslöser |
|---|---|---|
| `queued` | `running` | Worker übernimmt Job |
| `queued` | `canceled` | Nutzer/System bricht ab |
| `running` | `completed` | Upload erfolgreich |
| `running` | `failed` | Fehler bei Upload (OAuth, Quota, etc.) |
| `running` | `canceled` | Nutzer bricht ab |
| `failed` | `queued` | Retry angefordert |

---

## HTTP Status Code Konventionen

| Code | Bedeutung | Wann verwenden |
|---|---|---|
| **200** | OK | Erfolgreiche GET, PUT, PATCH, DELETE |
| **201** | Created | Erfolgreiche POST die neue Ressource erzeugt |
| **400** | Bad Request | Syntaktisch ungültiger Request Body |
| **401** | Unauthorized | Nicht authentifiziert / Session abgelaufen |
| **403** | Forbidden | Authentifiziert, aber nicht berechtigt |
| **404** | Not Found | Ressource existiert nicht |
| **409** | Conflict | Status-Übergang ungültig, Duplikat, Race Condition |
| **422** | Unprocessable Entity | Syntaktisch korrekt, aber fachlich ungültig |
| **500** | Internal Server Error | Unerwarteter Serverfehler |

### Abgrenzung 400 vs. 422

- **400:** JSON ist kaputt, Pflichtfeld fehlt im Request, falscher Content-Type
- **422:** JSON ist valide, aber Inhalt verletzt fachliche Regel (z.B. `duration: -5`)

### Abgrenzung 401 vs. 403

- **401:** Wer bist du? (kein Token, Token abgelaufen)
- **403:** Ich weiß wer du bist, aber du darfst das nicht.

---

## Fehlerklassifikation

Alle Fehler gehören zu genau einer Klasse. Der `error.code` im Response entspricht
dem Klassennamen.

### ValidationError
- **HTTP:** 400 oder 422
- **Bedeutung:** Input ist ungültig
- **Codes:** `VALIDATION_ERROR`, `INVALID_FIELD`, `MISSING_FIELD`
- **Beispiel:** Titel fehlt, Duration negativ, unbekannter Preset-Key

### NotFoundError
- **HTTP:** 404
- **Bedeutung:** Angefragte Ressource existiert nicht
- **Codes:** `NOT_FOUND`, `WORKFLOW_NOT_FOUND`, `ASSET_NOT_FOUND`
- **Beispiel:** Workflow-ID existiert nicht, Asset gelöscht

### ConflictError
- **HTTP:** 409
- **Bedeutung:** Aktion ist im aktuellen Zustand nicht möglich
- **Codes:** `CONFLICT`, `INVALID_TRANSITION`, `ALREADY_EXISTS`, `JOB_ALREADY_RUNNING`
- **Beispiel:** Workflow `completed` → `running`, Job läuft bereits

### ProviderError
- **HTTP:** 502 oder 503
- **Bedeutung:** Externes System hat Fehler geliefert oder ist nicht erreichbar
- **Codes:** `PROVIDER_ERROR`, `GPU_UNAVAILABLE`, `YOUTUBE_QUOTA_EXCEEDED`, `UPLOAD_FAILED`
- **Beispiel:** GPU-VM nicht erreichbar, YouTube OAuth abgelaufen

### InternalError
- **HTTP:** 500
- **Bedeutung:** Unerwarteter interner Fehler
- **Codes:** `INTERNAL_ERROR`, `DB_ERROR`, `UNEXPECTED`
- **Beispiel:** SQLite locked, unbehandelte Exception

---

## Fehler-Response-Beispiele

### ValidationError (422)
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input.",
    "details": [
      { "field": "duration_hours", "issue": "min_value", "message": "Must be at least 0.5." },
      { "field": "preset_id", "issue": "not_found", "message": "Preset 'xyz' does not exist." }
    ]
  }
}
```

### ConflictError (409)
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_TRANSITION",
    "message": "Cannot transition workflow from 'completed' to 'running'.",
    "details": [
      { "current_status": "completed", "requested_status": "running" }
    ]
  }
}
```

### ProviderError (503)
```json
{
  "status": "error",
  "error": {
    "code": "GPU_UNAVAILABLE",
    "message": "GPU worker at 192.168.178.152 is not reachable.",
    "details": [
      { "provider": "ssh_gpu", "host": "192.168.178.152", "last_attempt": "2026-03-29T10:15:00Z" }
    ]
  }
}
```

---

## Implementierungshinweise

### Python Exception Hierarchy

```python
class AppError(Exception):
    """Basis für alle App-Fehler."""
    code: str = "INTERNAL_ERROR"
    http_status: int = 500

class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    http_status = 422

class NotFoundError(AppError):
    code = "NOT_FOUND"
    http_status = 404

class ConflictError(AppError):
    code = "CONFLICT"
    http_status = 409

class ProviderError(AppError):
    code = "PROVIDER_ERROR"
    http_status = 503

class InternalError(AppError):
    code = "INTERNAL_ERROR"
    http_status = 500
```

### FastAPI Exception Handler

```python
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": str(exc),
                "details": getattr(exc, "details", None),
            }
        }
    )
```

---

## Zusammenfassung

- **Ein Format** für alle API-Responses: `{"status": "ok|error", "data": ..., "error": ...}`
- **Drei State Machines** für Workflow, AudioJob, PublishJob mit definierten Übergängen
- **Fünf Fehlerklassen** mit klarer HTTP-Zuordnung
- **Kein Wildwuchs** — neue Endpoints müssen diese Verträge erfüllen
