# Backlog – Agent Smith (Main Keeper)

Schwierigste Aufgaben. Backend-Architektur, komplexe Features, Security.

## Aktive Aufgaben

### 1. Ticket-System im Dashboard (#2) — Priority A
Dashboard-Bereich für Bugs/Features/Improvements. Formular → GitHub Issue → Sync Task.
- Backend: neue DB-Tabelle, GitHub API Integration (Issue erstellen)
- Frontend: Ticket-Formular, Ticket-Liste mit Status
- Bidirektionale Verknüpfung: Dashboard Ticket ↔ GitHub Issue ↔ Task

### 2. Pipeline Job Queue (#3d) — Priority A
Warteschlange für Pipeline-Jobs mit sequentieller Ausführung.
- Queue-Semantik: waiting, running, completed, failed, cancelled
- Concurrency-Limit (default: 1 gleichzeitig)
- Queue-UI im Dashboard mit Reihenfolge + Status
- Integration mit Audio-Gen und Auto-Upload

### 3. Audio-to-Pipeline One-Click Flow (#3a) — Priority A
Audio generieren + Pipeline starten in einem Rutsch.
- Neuer combined Endpoint / Workflow-Orchestrator
- Overnight-Modus ohne manuelle Zwischenschritte
- Auto-Upload Option (opt-in per Run)
- Klare Phase-Anzeige im UI (Audio → Render → QA → Upload)

### 4. Admin Login mit Sessions (#18) — Priority E
Auth-System für alle Admin-Views.
- Session/Cookie-basierte Auth
- Login-Page, Logout, Session-Lifetime
- Alle /admin/* Routes schützen

### 5. GPU-Worker Metrics (#13) — Priority D
GPU Load, VRAM, Temperatur live im Dashboard.
- SSH-basierte Metriken von GPU-VM abfragen
- API-Endpoint + Dashboard-Widget
- Warning-Thresholds

### 6. System Tab Redesign (#15) — Priority D
Version + Metriken aus Homepage in System Tab verschieben.
- System Tab als zentrale Status-Oberfläche
- Server Stats, DB Stats, Version, Protocol Health zusammenführen
