# Aufgaben für Jarvis

## Dein Issue

### #11 – Doku-Update
**Was:** Die Projektdokumentation auf den aktuellen Stand bringen.

---

### 1. AUFGABEN.md aktualisieren

Folgendes ist jetzt **erledigt** (abhaken oder als done markieren):
- [x] Publishing-/Upload-Definition für YouTube → Templates sind fertig
- [x] Repo-Struktur und Schema v1 → existiert

Folgendes ist **neu dazugekommen** (in die ToDo-Liste):
- [ ] Video-Rendering Script bauen (Pako, Issue #7)
- [ ] Metadaten-Generator bauen (Smith, Issue #8)
- [ ] YouTube Upload Script bauen (Smith, Issue #9)
- [ ] Pipeline-Orchestrierung bauen (Pako, Issue #10)
- [ ] Erster End-to-End Testlauf (alle)

---

### 2. README.md updaten

Folgendes sollte erwähnt werden:
- **Publishing-Toolkit** unter `publishing/` (Templates, Tag-Library, Playlist-Strategie)
- **MusicGen-Pipeline** unter `publishing/musicgen/` (CLI-Tool für Song-Generierung)
- **Agent-Sync-Service** für Koordination (siehe AGENT_SYNC.md)
- **3-Bot-Team:** Pako (Tech/Pipeline), Smith (Publishing/API), Jarvis (Doku)

---

### 3. PIPELINE.md abgleichen

Aktueller Stand pro Pipeline-Stufe:

| Stufe | Status |
|---|---|
| 1. Idee & Planung | ✅ Schema + Briefing-Vorlage existiert |
| 2. Song-Erstellung | ✅ MusicGen-Pipeline fertig |
| 3. Audio-Finalisierung | ✅ merge.py mit Crossfade |
| 4. Video-Erstellung | ❌ Script fehlt (Pako #7) |
| 5. Metadaten | 🔶 Templates da, Generator fehlt (Smith #8) |
| 6. QA | ✅ Preflight + Validierung existiert |
| 7. Publikationsvorbereitung | 🔶 Teilweise (Templates) |
| 8. Upload | ❌ YouTube-Script fehlt (Smith #9) |

Bitte diesen Stand in PIPELINE.md einarbeiten.

---

### 4. CONTRIBUTING.md aktualisieren

Sync-Service Workflow einbauen:
1. Issue erstellen auf GitHub
2. Warten bis Sync-Service Task erstellt
3. Task claimen: `POST /tasks/{id}/claim`
4. Arbeiten + Heartbeats senden
5. Vor jedem Push resyncen
6. PR erstellen
7. Task releasen: `POST /tasks/{id}/release`

Details stehen in AGENT_SYNC.md.

---

## Wo liegen deine Dateien?
- `AUFGABEN.md` (bearbeiten)
- `README.md` (bearbeiten)
- `PIPELINE.md` (bearbeiten)
- `CONTRIBUTING.md` (bearbeiten)

## Sync-Service Protokoll
Task #11 claimen → arbeiten → vor Push resyncen → PR erstellen → releasen.

## Tipp
Lies dir vor dem Start die existierenden Dateien durch. Nicht überschreiben, nur ergänzen/aktualisieren.
