# Test Strategy

**Owner:** Pako
**Reviewer:** Smith
**Stand:** 2026-03-29
**Welle:** B05
**Depends:** A03 (Engineering Standards)

---

## Ausgangslage

Aktuell existieren **keine Tests** im Projekt.
Ziel dieser Strategie ist nicht maximale Coverage, sondern gezielter Schutz der kritischsten Pfade – ohne den laufenden Betrieb zu blockieren.

---

## Testpyramide

```
           ┌──────────────┐
           │    E2E       │  ← wenige, nur Happy Paths des Hauptflusses
           ├──────────────┤
           │ Integration  │  ← DB, Dateisystem, Subprocess-Grenzen
           ├──────────────┤
           │    Unit      │  ← Logik, Transformationen, Helfer  ← Einstieg hier
           └──────────────┘
```

**Priorität:** Unit first. Erst wenn Unit-Tests stabil, Integration. E2E nur für den Hauptpfad.

---

## Prioritäten – was zuerst getestet wird

### Priorität 1 – Sofort (Welle B/C)

| Bereich | Was testen | Warum |
|---|---|---|
| `store.py` (AgentSyncDB) | Workflow CRUD, Status-Übergänge, Migrations | Einzige persistente Wahrheit des Systems |
| `helpers.py` | `slugify()`, `_load_house_templates()` | Werden überall verwendet, kaum Abhängigkeiten |
| `pipeline/scripts/metadata/metadata_gen.py` | Metadaten-Generierung pro Haus | Kritisch für YouTube-Upload |
| `pipeline/scripts/thumbnails/generate_thumbnail.py` | Thumbnails ohne GPU | Keine externen Deps nötig |

### Priorität 2 – Mit Fixtures (Welle B/C, nach B06)

| Bereich | Was testen | Warum |
|---|---|---|
| `audio_jobs.py` | Job-Erstellung, Status-Updates | Verbindet DB mit Worker |
| `routes/pipeline.py` | Create-Flow (POST) mit In-Memory-DB | Hauptpfad der App |
| `routes/shorts.py` | Short-Erstellung, Detail-View | Neuer Workflow |
| `pipeline/pipeline.py` | Orchestrierung (gemockt) | Integrität des Ablaufs |

### Priorität 3 – Später / optional

| Bereich | Was testen |
|---|---|
| YouTube Upload | Nur gegen Mock, kein echter API-Call in Tests |
| GPU Worker | Nur Job-Submission-Format, kein echter Worker-Call |
| E2E Hauptpfad | FastAPI TestClient: New → Render → Upload (gemockt) |

---

## Tooling

| Tool | Zweck |
|---|---|
| `pytest` | Haupt-Testrunner |
| `pytest-cov` | Coverage-Report |
| `pytest-mock` / `unittest.mock` | Mocking von Subprocessen, Dateisystem, GPU-Calls |
| `httpx` + FastAPI `TestClient` | HTTP-Tests der Routes |
| `tmp_path` (pytest builtin) | Temporäre Verzeichnisse für Dateisystem-Tests |

Kein separates Test-Framework. Kein Playwright/Selenium für UI (zu früh).

---

## Verzeichnisstruktur

```
tests/
  unit/
    test_helpers.py
    test_store.py
    test_metadata_gen.py
  integration/
    test_pipeline_routes.py
    test_audio_jobs.py
  fixtures/
    conftest.py          ← gemeinsame Fixtures (DB, Templates, Slugs)
    house_templates.json ← Test-Kopie, kein Prod-Zugriff
```

---

## Fixture-Grundsätze (für B06)

- Tests dürfen **nie** auf Prod-DB oder Prod-Dateipfade zugreifen
- Alle Fixtures sind in `conftest.py` zentralisiert
- DB-Fixtures: immer `tmp_path` + frische `AgentSyncDB`-Instanz
- Dateisystem-Fixtures: minimale Testdaten (kein echtes Audio, keine echten Videos)
- House-Templates: eigene Test-JSON, nicht `data/house_templates.json`

---

## CI-Plan

Kurzfristig (Welle B/C):
- `pytest tests/unit/` läuft lokal ohne externe Deps
- kein CI/CD bis Smoke Checks (B10) definiert sind

Mittelfristig (nach B10):
- GitHub Actions Workflow: `pytest tests/unit/ tests/integration/` bei jedem PR auf `main`
- Coverage-Report als Artefakt (kein Pflicht-Threshold zunächst)

Langfristig (Welle E/F):
- E2E-Tests in Staging-Umgebung
- Coverage-Threshold einführen (Ziel: Kernpfade >80%)

---

## Was explizit nicht getestet wird (jetzt)

- Rendering via ffmpeg (zu langsam, zu viele externe Deps)
- GPU-Worker (kein Testsetup ohne GPU)
- YouTube API (kein Test-Credential-Handling)
- ngrok/Cloudflare-Tunnel

Diese Bereiche werden durch Smoke Checks (B10) und manuelle Verification abgedeckt.

---

## Akzeptanzkriterium

- [ ] `pytest tests/unit/` läuft durch (nach B06 wenn erste Tests angelegt)
- [ ] Coverage für `store.py` und `helpers.py` > 60%
- [ ] Reviewed by Smith
