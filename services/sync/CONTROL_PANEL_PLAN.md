# Control Panel Plan

## Ziel
Aus dem bisherigen Admin-Dashboard des `agent-sync-service` wird die zentrale Verwaltungsstelle für den Content-Workflow.

Nicht nur beobachten, sondern steuern:
- Dateien bereitstellen
- Pipeline konfigurieren
- Pipeline starten
- Laufstatus sehen
- Ergebnis prüfen
- Upload erst nach Preview freigeben

---

## Leitprinzip

**Render und Upload trennen.**

Der größte Fehler wäre, aus der UI direkt einen "mach alles"-Knopf zu bauen, der halbfertigen Content blind nach YouTube schiebt.

Stattdessen:
1. Input bereitstellen
2. Run konfigurieren
3. Render / Vorbereitung starten
4. Preview prüfen
5. Upload bewusst freigeben

---

## Zielarchitektur

### 1. agent-sync-service bleibt die Zentrale
Der Service wird nicht nur Sync-/Task-Server, sondern Orchestrierungszentrale.

Er bekommt zusätzlich:
- Pipeline-Run-Verwaltung
- Upload-/Asset-Verwaltung
- Preview-Zustände
- optional Storage-Connectoren

### 2. Pipeline wird in den Service integriert
Die aktuelle Pipeline bleibt nicht als loses externes Skript-Ding bestehen, sondern wird fachlich an den Service angebunden.

Das heißt nicht zwingend, dass sofort jede Zeile Code in dieses Repo kopiert werden muss.

Sinnvoller mittelfristiger Weg:
- zuerst Service kann lokale Pipeline-Prozesse starten und überwachen
- später Pipeline-Logik sauber als integrierbare Komponente / Worker auslagern

### 3. UI ist Control Panel, nicht nur Dashboard
Neue Aufgabe der UI:
- Inputs annehmen
- Runs erzeugen
- Status und Logs zeigen
- Ergebnisse previewen
- Upload bewusst triggern

---

## Empfohlene Systembausteine

### A. Pipeline Jobs
Neue fachliche Einheit im Service:
**pipeline_job**

Ein Pipeline-Job beschreibt:
- welche Inputs genutzt werden
- welche Parameter gesetzt wurden
- welchen Status der Run hat
- wo Output liegt
- ob Preview fertig ist
- ob Upload freigegeben wurde

Beispielhafte Zustände:
- `created`
- `queued`
- `running`
- `rendered`
- `preview_ready`
- `uploading`
- `uploaded`
- `failed`
- `cancelled`

### B. Asset Registry
Die UI braucht eine Sicht auf verfügbare Dateien.

Deshalb sinnvoll:
**asset registry**
- Audio-Dateien
- Thumbnails
- Metadaten
- erzeugte Videos
- Preview-Artefakte

Nicht nur Dateien auf Platte, sondern mit Metadaten:
- Typ
- Pfad / Storage-URL
- Größe
- Upload-Zeit
- zugehöriger Slug
- Quelle

### C. Pipeline Runner
Ein Runner startet lokal Pipeline-Prozesse und überwacht sie.

Zunächst ausreichend:
- Subprocess-basiert
- stdout/stderr mitschneiden
- Exit-Code speichern
- Status updaten

Später möglich:
- Queue / Worker-Modell
- parallele Jobs
- Remote Runner

### C.1 Live-Logs statt stumpfem Polling
Pipeline-Runs können längere Zeit laufen. Reines Polling für Log-Ausgaben ist funktional, aber UX-seitig unerquicklich.

Empfehlung:
- **SSE (Server-Sent Events)** für Run-Logs
- Endpunkt z. B. `GET /admin/runs/{run_id}/logs/stream`
- Browser kann ohne großen Frontend-Overhead reconnecten

Polling kann als Fallback bleiben, aber Live-Logs sollten das Zielbild sein.

### C.2 Disk-Space Guard
Der Runner muss aktiv Speicherplatz überwachen.

Warum:
- Render-Jobs können große Artefakte erzeugen
- ein voller Datenträger darf nicht erst am Ende auffallen

Empfehlung:
- vor Start: Freiplatz-Prüfung gegen geschätzten Bedarf
- harte Mindestreserve definieren
- während Render: abbrechen, wenn Sicherheitsgrenze unterschritten wird
- Warnung im UI sichtbar machen

### D. Preview Layer
Nach erfolgreichem Render soll die UI direkt zeigen können:
- Thumbnail
- Video
- generierte Metadaten

Wichtig:
**Preview ist ein eigener Zustand vor Upload.**

### E. Upload Gate
Upload zu YouTube nur:
- separat
- bewusst
- nach sichtbarer Preview

Kein automatischer Upload direkt nach Render als Default.

---

## Storage-Architektur

### Grundsatz
GitHub ist **nicht** der Ort für große Runtime-Artefakte.

GitHub bleibt für:
- Code
- kleine Referenzdateien
- Doku
- Konfiguration

Nicht für:
- große Audios
- fertige Videos
- Preview-Artefakte in Masse

### Option 1: rein lokal
Der Service arbeitet mit lokalen Verzeichnissen.

Vorteile:
- einfach
- schnell
- wenig moving parts

Nachteile:
- an eine Maschine gebunden
- schlechter für Team-Zugriff

### Option 2: Nextcloud/WebDAV als Asset-Storage
Das ist grundsätzlich sinnvoll, **aber nicht als erste harte Pflicht für alles**.

Sinnvoller Einsatz:
- Input-Ablage
- gemeinsame Asset-Bibliothek
- optional Output-Spiegelung

Weniger sinnvoll als alleinige erste Lösung, wenn:
- der Service für jeden kleinen Zugriff über WebDAV hantieren muss
- Pipeline-Läufe dadurch unnötig langsamer / fragiler werden

### Meine Empfehlung
**Hybrid-Modell:**
- lokale Arbeitsverzeichnisse für aktive Runs
- optionaler Nextcloud/WebDAV Connector für Import/Export

Also:
1. Inputs optional aus Nextcloud holen
2. lokal arbeiten/rendern
3. Ergebnis optional nach Nextcloud zurückspiegeln

Warum das besser ist:
- Render bleibt lokal performant
- Team kann trotzdem Assets zentral austauschen
- weniger Abhängigkeit vom Netz während des Runs

---

## Empfohlene UI-Bereiche

### 1. Dashboard
Zeigt nicht nur Tasks, sondern auch Pipeline-Betrieb:
- letzte Runs
- laufende Jobs
- fehlgeschlagene Jobs
- Preview-ready Jobs
- Upload-ready Jobs

### 2. Assets
Für hochgeladene / bekannte Dateien:
- Audio
- Thumbnail
- Metadaten
- Video

Aktionen:
- hochladen
- ansehen
- einem neuen Run zuordnen

### 3. Pipeline Runs
Hier startet und verwaltet man Runs.

Formularfelder:
- slug
- Titel
- Minuten
- loop-hours
- public/private
- animated ja/nein
- skip-upload ja/nein
- Asset-Auswahl oder Upload

### 3.1 Run Presets
Für wiederkehrende Workflows sollten Presets speicherbar sein.

Beispiele:
- `Winterfell Standard`
- `3h Ambient Private`
- `Preview Only`

Nutzen:
- weniger Fehlbedienung
- schnellere Runs
- konsistentere Parameter

### 4. Run Detail
Zeigt:
- Konfiguration
- Status
- Logs
- erzeugte Dateien
- Preview
- Upload-Freigabe

### 5. Preview
Eigener Fokusbereich:
- Video direkt anschauen
- Thumbnail sehen
- Metadaten prüfen
- Upload freigeben oder zurückweisen

### 6. System / Storage
Zeigt:
- lokales Storage-Verzeichnis
- Nextcloud/WebDAV-Status
- freie Kapazität (wenn verfügbar)
- letzte Fehler bei Import/Export

---

## Integration der bestehenden Pipeline

## Phase 0 – Bestandsaufnahme
Vor Umbau klären:
- welche Skripte gibt es aktuell genau
- welche Inputs erwartet die Pipeline
- welche Outputs entstehen
- wie wird YouTube-Upload aktuell aufgerufen
- welche Teile sind rein lokal, welche hängen an Tokens/Secrets
- vollständige CLI-Schnittstelle der Pipeline dokumentieren
- Laufzeit- und Speicherbedarf grob pro Modus erfassen

### Pipeline-Kopplung: keine Copy-Paste-Integration
Die Pipeline sollte mittelfristig **nicht** hart in dieses Repo kopiert werden.

Empfehlung:
- Service orchestriert die Pipeline
- Pipeline bleibt in ihrem eigenen Repo die fachliche Wahrheit
- technische Kopplung zunächst über klaren lokalen Aufruf
- optional später als Submodule oder sauber versionierte Abhängigkeit anbinden

Wichtig:
Der Service soll die Pipeline steuern, nicht heimlich ein zweites divergierendes Pipeline-Repo in sich tragen.

## Phase 1 – Service startet Pipeline lokal
Der agent-service bekommt Endpunkte / interne Funktionen für:
- Job erzeugen
- Job starten
- Jobstatus lesen
- Logs speichern

Implementation pragmatisch:
- lokales Prozess-Starten via subprocess
- Prozess-ID / Startzeit / Status speichern
- stdout/stderr in Datei und/oder DB schreiben

## Phase 2 – Pipeline Input/Output standardisieren
Definierte Arbeitsordner pro Run, z. B.:
- `work/runs/<run_id>/input`
- `work/runs/<run_id>/output`
- `work/runs/<run_id>/logs`

Damit wird aus Chaos eine reproduzierbare Run-Struktur.

## Phase 3 – Preview-first Flow
Nach Render:
- Preview erzeugen
- Run bekommt Status `preview_ready`
- UI zeigt Ergebnis
- erst danach Upload-Action

## Phase 4 – Upload entkoppeln
Upload wird separater Schritt:
- `render`
- `preview`
- `upload`

Das ist wichtig für Qualitätssicherung.

## Phase 5 – Optionaler Nextcloud Connector
Erst wenn lokaler Flow sauber läuft.

Dann:
- Import von Input-Dateien aus WebDAV
- optional Export von Ergebnisdateien zu WebDAV
- optional zentrale Asset-Bibliothek

---

## Datenmodell – empfohlene neue Einheiten

### pipeline_runs
Felder grob:
- `run_id`
- `slug`
- `title`
- `status`
- `created_at`
- `started_at`
- `finished_at`
- `config_json`
- `input_assets_json`
- `output_assets_json`
- `preview_ready`
- `upload_status`
- `error_message`

### pipeline_run_logs
- `id`
- `run_id`
- `stream` (`stdout` / `stderr` / system)
- `message`
- `created_at`

### assets
- `asset_id`
- `kind` (`audio`, `thumbnail`, `metadata`, `video`, `preview`)
- `slug`
- `storage_type` (`local`, `webdav`)
- `path`
- `size_bytes`
- `created_at`
- `source`
- `meta_json`

### storage_connectors (optional später)
- `connector_id`
- `kind` (`webdav`)
- `name`
- `base_url`
- `enabled`
- `config_json`

### pipeline_presets
- `preset_id`
- `name`
- `description`
- `config_json`
- `created_at`
- `updated_at`

---

## API / interne Funktionen – Zielbild

### Admin UI Endpunkte
- `GET /admin`
- `GET /admin/assets`
- `GET /admin/runs`
- `GET /admin/runs/{run_id}`
- `GET /admin/preview/{run_id}`
- `GET /admin/system`

### Aktionen
- `POST /admin/assets/upload`
- `POST /admin/runs`
- `POST /admin/runs/{run_id}/start`
- `POST /admin/runs/{run_id}/upload`
- `POST /admin/runs/{run_id}/cancel`

### Optional später
- `POST /admin/storage/webdav/import`
- `POST /admin/storage/webdav/export`
- `GET /admin/runs/{run_id}/logs/stream` (SSE)

---

## Sicherheits-/Betriebsaspekte

### 1. Upload nicht blind machen
Preview-Phase verpflichtend oder zumindest Default.

### 2. Secrets sauber behandeln
YouTube-Tokens / WebDAV-Creds nicht in UI offenlegen.

Zusätzlich sinnvoll:
- Token-Status in der UI anzeigen (`gültig`, `fehlt`, `abgelaufen`)
- optional Refresh-/Reauth-Flow vorbereiten
- Token-Werte selbst niemals im Frontend anzeigen

### 3. Dateigrößen begrenzen
UI-Uploads brauchen Limits.

### 4. Arbeitsverzeichnisse sauber halten
Pro Run isolierte Pfade.

### 5. Logs speichern
Wenn ein Run scheitert, muss klar sein warum.

### 6. Cleanup-Strategie
Große Artefakte dürfen nicht unendlich liegen bleiben.

Empfehlung:
- konfigurierbare Retention
- nach erfolgreichem Upload große Zwischenartefakte aufräumen
- Thumbnail / Metadaten optional länger behalten
- Cleanup sichtbar im Systembereich machen

### 7. Minimaler Zugriffsschutz
Spätestens wenn aus der UI Uploads oder Pipeline-Starts möglich sind, reicht ein offenes Dashboard nicht mehr.

Für Phase 1 ausreichend:
- HTTP Basic Auth

Später möglich:
- Session-/User-Modell
- feinere Rollen

---

## Konkrete Empfehlung zur Umsetzung

### Version 1 – lokal, ohne Nextcloud-Zwang
Bauen:
- Asset Upload UI
- Run-Konfiguration
- lokaler Pipeline-Start
- Run-Status + Logs
- Preview-Seite
- Upload separat auslösen

### Version 2 – bessere Betriebsfähigkeit
Dann ergänzen:
- Run-Historie
- Fehleransicht
- Lösch-/Cleanup-Mechanik
- bessere Filter / Suche
- Live-Logs via SSE
- Token-Statusanzeige
- Disk-Space Guard
- Presets

### Version 3 – optional Nextcloud/WebDAV
Dann erst:
- Connector einbauen
- Inputs importieren
- Outputs spiegeln

---

## Meine klare Architekturmeinung

**Nextcloud kann sinnvoll sein, aber nicht als Herzstück des ersten lauffähigen Systems.**

Erst muss der lokale End-to-End-Flow sauber stehen:
- Upload / Input
- Run
- Preview
- Upload

Dann kann man Nextcloud als Storage-Erweiterung andocken.

Sonst baut ihr euch zu früh wieder eine zusätzliche Fehlerquelle rein.

---

## Empfohlene Umsetzungsreihenfolge

1. Datenmodell für `pipeline_runs` + `assets`
2. lokale Run-Verzeichnisse standardisieren
3. Upload UI für Audio/Thumbnail/Metadata
4. Run-Konfigurationsseite
5. Starten + Log-Erfassung
6. Preview-Seite
7. separater Upload-Trigger
8. erst danach optional WebDAV / Nextcloud

---

## Agent Onboarding / Einstieg für neue Agents

Der Plan soll so aufgebaut sein, dass ein neu dazukommender Agent nicht erst Chat-Verläufe archäologisch ausgraben muss.

### Ziel
Ein neuer Agent soll in kurzer Zeit verstehen:
- was der Service heute schon kann
- was die Zielarchitektur ist
- was zuerst gebaut werden soll
- welche Grenzen und Entscheidungen schon feststehen

### Empfohlene Onboarding-Bausteine

#### 1. Executive Summary direkt am Anfang
Der Plan sollte ganz oben eine ultrakurze Zusammenfassung tragen:
- Was ist das Ziel?
- Was ist Version 1?
- Was ist bewusst noch nicht Teil von Version 1?

#### 2. Current State Abschnitt
Neuer Pflichtabschnitt im Plan bzw. in begleitender Doku:
- was ist bereits implementiert
- welche Endpunkte/UI-Seiten existieren schon
- welche Persistenz gibt es bereits
- was ist nur geplant, aber noch nicht gebaut

#### 3. Decisions / Non-Goals klar markieren
Ein neuer Agent muss sofort sehen:
- Upload und Render bleiben getrennt
- GitHub ist nicht der Storage für große Artefakte
- Nextcloud/WebDAV optional, nicht Kern von V1
- Dashboard startet read-only, dann Control Panel
- Pipeline soll orchestriert, nicht blind kopiert werden

#### 4. Next Steps mit Priorität
Nicht nur Ideenliste, sondern klare Reihenfolge:
1. Datenmodell für Runs + Assets
2. Upload/UI
3. lokaler Run-Start
4. Logs / Status
5. Preview
6. Upload-Freigabe
7. optional WebDAV

#### 5. Glossar / Begriffe
Kurze Begriffsklärung, damit neue Agents dieselben Worte gleich verstehen:
- `pipeline_run`
- `asset`
- `preview_ready`
- `upload gate`
- `storage connector`
- `preset`

#### 6. Bekannte Risiken / Stolperfallen
Kurz und ehrlich dokumentieren:
- große Render-Artefakte können Speicher fressen
- Token/Secrets sind sensibel
- Preview vor Upload ist Pflichtdenken, nicht Nice-to-have
- lokale Pfade und externe Pipeline-Kopplung müssen sauber definiert werden

#### 7. Referenz auf operative Dateien
Ein neuer Agent soll wissen, wo er weiterlesen muss:
- `README.md`
- `CONTROL_PANEL_PLAN.md`
- Admin-UI-Stand im Repo
- relevante Store-/API-Dateien

### Empfehlung
Zusätzlich zum Architekturplan sollte mittelfristig eine kleine Datei entstehen wie:
- `AGENT_BRIEFING.md`
oder
- `CURRENT_STATE.md`

Die ist kürzer als der große Plan und dient als schneller Einstieg.

## Definition of Done für Version 1

Fertig ist die erste echte Verwaltungszentrale, wenn man über die UI:
- Audio/Thumbnail/Metadata hochladen kann
- einen Run konfigurieren kann
- den Run starten kann
- Status und Logs sehen kann
- das erzeugte Video previewen kann
- den Upload anschließend bewusst auslösen kann

Dann ist das Dashboard keine reine Beobachtungsfläche mehr, sondern eine echte Zentrale.
