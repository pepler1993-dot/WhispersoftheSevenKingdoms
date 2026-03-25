# Dashboard Task Backlog

Stand: 25.03.2026

## Erledigte Aufgaben

- ~~#1 Claims expire unexpectedly~~ → Protocol Health System implementiert (Stale-Sweep, Warnings, API, Ops-Panel, Task-Detail Flags)
- ~~#3 Old Kaggle logic still visible~~ → Kaggle-UI entfernt, Default auf GPU-Worker, Kaggle als Fallback
- ~~#6 Task summaries not meaningful~~ → Issue-Titel als Kurzbeschreibung, detaillierte Beschreibung aus Issue-Body
- ~~#7 Task filters need to be more usable~~ → Dropdown-Filter für Status/Assignee, Live-Filtering, API-Endpoint für Filterwerte
- ~~#17 Slug auto-generate from title~~ → Backend + Frontend, Slug-Feld versteckt

## Offene Aufgaben

### Priority A — critical / blocking

**#2. Ticket-System im Dashboard**
Bugs, Features, Änderungen direkt im Dashboard anlegen → GitHub Issue → Sync Task.

**#3a. Audio-to-Pipeline Workflow zu fragmentiert**
Ein-Klick-Flow: Audio generieren + Pipeline starten + optional Auto-Upload. Overnight-Modus.

**#3b. Audio Job Cancel geht nicht zuverlässig**
Cancel-Flow tracen, für alle Job-States fixen, UI-Feedback bei fehlgeschlagenem Cancel.

**#3c. Thumbnail-Herkunft unklar**
Anzeigen woher das Thumbnail kommt (Library, Upload, Auto-generiert). Vor und nach dem Run sichtbar.

**#3d. Pipeline Job Queue**
Mehrere Jobs in Warteschlange, sequentielle Ausführung, Queue-Status im Dashboard.

### Priority B — dashboard usability

**#4. Docs-Startseite zu dicht**
Übersichtlichere Struktur, klare Einstiegspunkte, besseres Spacing.

**#5. Dashboard-Docs nicht aus User-Perspektive**
Developer-Sprache raus, task-orientierte Nutzerdoku schreiben.

**#8. Mobile Bottom-Navigation instabil**
Active States, Layout-Jumps, Scroll-Verhalten, Tap-Targets fixen.

### Priority C — library and content

**#9. Metadata direkt in Library erstellen**
Formular für Titel, Beschreibung, Tags, Playlist-Metadaten. JSON-Export.

**#10. Songs in Library: Usability**
Direktlink zu Audio Lab, MP3/WAV Upload, In-Dashboard Playback.

**#11. Thumbnail-Editor MVP**
Konzept für Template-basierte Thumbnail-Erstellung im Dashboard.

**#12. Animated Video Assets**
Asset-Klasse für Visuals/Animationen definieren, Pipeline-Integration planen.

### Priority D — monitoring

**#13. GPU-Worker Metrics im Dashboard**
GPU Load, VRAM, Temperatur, Queue-Status sichtbar machen.

**#14. PVE Temperatur im Dashboard**
Sensor-Daten vom Proxmox Host anzeigen, Warning-Thresholds.

**#15. System Tab Redesign**
Version + Server-Metriken von Homepage in System Tab verschieben.

### Priority E — performance, security

**#16. Audio Lab lädt zu langsam**
Health-Checks in Background, Page sofort rendern, lazy Loading.

**#18. Admin Login mit Sessions/Cookies**
Auth für alle Admin-Views, persistente Sessions, Logout.

### Priority F — process

**#19. Pako als UI/UX Tester formalisieren**
Workflow für Testing, Screenshots, Findings definieren.
