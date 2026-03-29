# Deploy Verification / Smoke Checks

**Owner:** Smith  
**Stand:** 2026-03-29  
**Welle:** B10  
**Issue:** #146  
**Typ:** Engineering  
**Bereich:** Operations

---

## Zweck

Dieses Dokument beschreibt den Smoke-Test-Prozess zur Verifizierung eines
erfolgreichen Deployments. Smoke Tests sind schnelle, nicht-destruktive Checks,
die sicherstellen, dass die Kernkomponenten des Systems nach einem Deploy
funktionsfähig sind.

---

## Wann ausführen?

- **Nach jedem Deploy** auf Produktion
- **Nach Server-Neustarts**
- **Nach Infrastruktur-Änderungen** (DB-Migration, Config-Update, Paket-Updates)
- **Als Teil der CI-Pipeline** (optional, gegen Staging)
- **Manuell** bei Verdacht auf Probleme

---

## Smoke Test Script

### Speicherort

```
scripts/smoke_test.sh
```

### Ausführung

```bash
# Standard (localhost:8000, Standard-DB-Pfad)
./scripts/smoke_test.sh

# Custom URL und DB-Pfad
./scripts/smoke_test.sh http://my-server:8000 /path/to/agent_sync.db
```

### Parameter

| Parameter | Default | Beschreibung |
|---|---|---|
| `BASE_URL` | `http://localhost:8000` | Server-Adresse |
| `DB_PATH` | `services/sync/data/agent_sync.db` | Pfad zur SQLite-Datenbank |

### Exit Codes

| Code | Bedeutung |
|---|---|
| `0` | Alle Checks bestanden |
| `1+` | Anzahl fehlgeschlagener Checks |

---

## Was wird geprüft?

### 1. Server Connectivity
- **Was:** HTTP-Request an die Root-URL
- **Erwartet:** Beliebiger HTTP-Response (nicht Connection Refused)
- **Fehlerfall:** Server läuft nicht, falscher Port, Firewall

### 2. Health Endpoints
- **Was:** GET `/healthz` (Liveness) + GET `/api/health/overview` (Details)
- **Erwartet:** `/healthz` → HTTP 200; `/api/health/overview` → gültiges JSON mit GPU-Status, Queue, Uploads
- **Fehlerfall:** App nicht gestartet, Route fehlt, Exception in Health-Check
- **Hinweis:** Es gibt kein `/api/health` – die echten Routes sind `/healthz` und `/api/health/overview`

### 3. Database
- **Was:** Prüft Existenz, Lesbarkeit und Integrität der SQLite-DB
- **Erwartet:** Datei existiert unter `services/sync/data/agent_sync.db`, ist lesbar, SQLite kann sie öffnen
- **Fehlerfall:** DB fehlt, Berechtigungen falsch, Datei korrupt

### 4. Static Files
- **Was:** GET `/static/` Verzeichnis
- **Erwartet:** HTTP-Response (nicht 404)
- **Fehlerfall:** Static Mount fehlt, Dateien nicht deployed

### 5. Dashboard
- **Was:** GET `/admin`
- **Erwartet:** HTTP 200 oder 302/303 (Redirect zu Login bei aktivem Auth)
- **Fehlerfall:** Template-Fehler, Import-Fehler, DB-Problem
- **Hinweis:** Die Dashboard-Route ist `/admin`, nicht `/admin/dashboard`

---

## Beispiel-Output

```
═══════════════════════════════════════════
  Smoke Test — Deploy Verification
  Target: http://localhost:8000
═══════════════════════════════════════════

▸ Server Connectivity
  ✓ Server responds (HTTP 200)

▸ Health Endpoint
  ✓ GET /healthz responds with 200
  ✓ GET /api/health/overview reachable
  ✓ Health overview returns valid JSON

▸ Database
  ✓ DB file exists (services/sync/data/agent_sync.db)
  ✓ DB file is readable
  ✓ DB is valid SQLite

▸ Static Files
  ✓ Static files served (HTTP 200)

▸ Dashboard
  ✓ GET /admin responds with 200

═══════════════════════════════════════════
  ALL PASSED  (9/9 checks)
═══════════════════════════════════════════
```

---

## Integration in Deploy-Workflow

### Manuelles Deploy

```bash
# 1. Deploy durchführen
git pull origin main
pip install -r requirements.txt

# 2. Server starten/neustarten
systemctl restart whispers

# 3. Warten bis Server ready
sleep 5

# 4. Smoke Test
./scripts/smoke_test.sh

# 5. Bei Fehler: Rollback
if [ $? -ne 0 ]; then
  echo "SMOKE TEST FAILED — rolling back"
  git checkout HEAD~1
  systemctl restart whispers
fi
```

### Automatisiert (CI/Staging)

```yaml
# Beispiel: GitHub Actions
- name: Run smoke tests
  run: ./scripts/smoke_test.sh http://localhost:8000
  timeout-minutes: 2
```

---

## Erweiterungsmöglichkeiten (Zukunft)

- **GPU Worker Erreichbarkeit:** SSH-Ping an GPU-VM
- **YouTube OAuth Token:** Token-Validität prüfen
- **Disk Space:** Freier Speicher auf dem Server
- **DB Schema Version:** Erwartete Tabellen/Spalten vorhanden
- **Queue Health:** Keine stuck Jobs (älter als X Stunden)
- **Response Time:** Health-Endpoint antwortet unter X ms
