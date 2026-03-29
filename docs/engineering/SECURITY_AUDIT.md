# Security / Secrets / Config Audit

**Stand:** 2026-03-29  
**Auditor:** Smith  
**Baseline:** `current-internal-tool-baseline`

## 1. OAuth / Google Credentials

### client_secret.json
- **Zweck:** YouTube Data API v3 OAuth2 Client
- **Speicherort:** Repo-Root auf dem Server (`/opt/whispers/.../client_secret.json`)
- **Gitignore:** ✅ Ja (`client_secret*.json` in .gitignore)
- **Risiko:** 🟡 Mittel – Datei liegt auf dem Server im Projektverzeichnis, aber nicht im Git
- **Empfehlung:** In ein separates Secrets-Verzeichnis außerhalb des Repos verschieben (z.B. `/etc/whispers/secrets/`) und per ENV-Variable referenzieren

### token.json / .youtube_token.json
- **Zweck:** OAuth2 Refresh Token für YouTube-Upload
- **Speicherort:** Repo-Root auf dem Server
- **Gitignore:** ✅ Ja (`.youtube_token.json` in .gitignore)
- **Risiko:** 🟡 Mittel – Token kann ablaufen/revoked werden (aktuelles Problem). Kein automatisches Re-Auth.
- **Empfehlung:** Token-Pfad per ENV konfigurierbar machen. Auto-Refresh-Flow dokumentieren.

## 2. Hardcoded Credentials & Defaults

### JWT Secret
- **Datei:** `services/sync/app/auth.py:20`
- **Code:** `SECRET_KEY = os.environ.get('JWT_SECRET', 'whisper-studio-dev-secret-change-me')`
- **Risiko:** 🔴 Hoch – Default-Secret ist ein bekannter String. Wenn ENV nicht gesetzt, ist Auth unsicher.
- **Empfehlung:** Kein Default-Fallback. Beim Start prüfen ob ENV gesetzt ist, sonst Fehler.

### Admin Default-Passwort
- **Datei:** `services/sync/app/auth.py:90`
- **Code:** `admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')`
- **Risiko:** 🔴 Hoch – Default-Admin-Passwort "admin" ist trivial erratbar
- **Empfehlung:** Kein Default. Erzwinge Passwort-Setzung beim ersten Start oder per ENV.

### GPU Worker IP
- **Datei:** `services/sync/app/stable_audio_gen.py:51`
- **Code:** `GPU_WORKER_HOST = os.environ.get('GPU_WORKER_HOST', '192.168.178.152')`
- **Risiko:** 🟢 Niedrig – Lokale IP, nur im LAN erreichbar. Aber hardcoded.
- **Empfehlung:** Kein Handlungsbedarf, aber bei Infrastruktur-Änderung ENV setzen.

### SSH Zugang GPU Worker
- **BatchMode=yes, StrictHostKeyChecking=no**
- **Risiko:** 🟡 Mittel – Akzeptiert jeden Host-Key. Bei MITM-Angriff im LAN verwundbar.
- **Empfehlung:** Host-Key einmalig pinnen statt `StrictHostKeyChecking=no`.

## 3. .gitignore Abdeckung

| Datei/Pattern | In .gitignore? | Status |
|---|---|---|
| `client_secret*.json` | ✅ | OK |
| `.youtube_token.json` | ✅ | OK |
| `*.db` (SQLite) | ✅ | OK |
| `*.db-shm`, `*.db-wal` | ✅ | OK |
| `.env` | ❌ | **Fehlt!** |
| `token.json` | ❌ | **Fehlt!** (nur `.youtube_token.json`) |
| SSH Keys | N/A | Nicht im Repo |

### Empfehlung:
Folgende Einträge zu `.gitignore` hinzufügen:
```
.env
token.json
*.pem
*.key
```

## 4. Environment Variables (Überblick)

| Variable | Datei | Default | Risiko |
|---|---|---|---|
| `JWT_SECRET` | auth.py | `whisper-studio-dev-secret-change-me` | 🔴 Unsicherer Default |
| `ADMIN_PASSWORD` | auth.py | `admin` | 🔴 Unsicherer Default |
| `GPU_WORKER_HOST` | stable_audio_gen.py | `192.168.178.152` | 🟢 LAN-only |
| `GPU_WORKER_USER` | stable_audio_gen.py | `root` | 🟡 Root-Zugang |
| `GPU_WORKER_SSH_KEY` | stable_audio_gen.py | `''` (default key) | 🟡 Implizit |
| `GPU_WORKER_OUTPUT_DIR` | stable_audio_gen.py | `/mnt/data/output` | 🟢 OK |
| `GPU_WORKER_CODE_DIR` | stable_audio_gen.py | `/opt/stable-audio-worker` | 🟢 OK |
| `DATA_DIR` | config.py | `data` | 🟢 OK |
| `GOOGLE_CLIENT_SECRET` | youtube_upload.py | `client_secret.json` | 🟡 Relative Pfad |
| `SKIP_RECOVERY` | main.py | `''` | 🟢 OK |

## 5. Zusammenfassung & Prioritäten

### 🔴 Sofort fixen (P0):
1. **JWT_SECRET** ohne Default ausliefern – Pflicht-ENV
2. **ADMIN_PASSWORD** ohne Default – Pflicht-ENV oder First-Run-Setup
3. `.env` und `token.json` in `.gitignore` aufnehmen

### 🟡 Zeitnah angehen (P1):
4. OAuth-Secrets aus dem Repo-Verzeichnis in separaten Pfad verschieben
5. SSH `StrictHostKeyChecking=no` durch gepinnten Host-Key ersetzen
6. GPU Worker User von `root` auf dedizierten User umstellen

### 🟢 Nice to have (P2):
7. Secrets-Management (z.B. `.env`-Datei mit `python-dotenv`)
8. Auto-Rotation für OAuth Tokens dokumentieren
9. Rate Limiting für Login-Endpunkt
