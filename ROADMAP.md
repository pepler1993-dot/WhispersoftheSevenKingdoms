# 🗺️ ROADMAP – Whispers of the Seven Kingdoms
> Stand: 24.03.2026 (aktualisiert von Smith nach Review aller Fortschritte)

---

## Aktuelle Lage in einem Satz

GPU-Worker Hardware ist ready (nvidia-smi ✅, PyTorch ✅). **Audio im Repo:** nur noch **Stable Audio Local**. Doku folgt Diátaxis + Dashboard-Integration. GitHub-Task-Webhooks im alten Sinne gibt es nicht mehr — Koordination über **Tickets** im Dashboard.

---

## Prioritäten ab jetzt

## P0 – GPU-Worker funktionsfähig machen
**Ziel:** **Stable Audio Local** auf dem GPU-Worker zuverlässig betreiben.

### Erledigt ✅
- [x] `nvidia-smi` in GPU-VM sauber zum Laufen gebracht (GTX 1070, 8GB VRAM, CUDA 12.4)
- [x] Nouveau-/Treiber-Konflikte gelöst (Kernel 6.12.74 → 6.12.73 Downgrade)
- [x] PyTorch CUDA 12.1 installiert (`torch-2.5.1+cu121`)
- [x] Python venv unter `/opt/stable-audio-worker/.venv` (oder gleichwertiger Pfad auf der Worker-VM)

### Offen – blockiert durch SSH-Key
- [ ] SSH-Key von LXC 103 erneut auf GPU-VM eintragen (**Kevin, manuell via noVNC**)
- [ ] CUDA Dependencies installieren (nvidia-cublas-cu12, nvidia-cudnn-cu12, etc.)
- [ ] Audio-Libs installieren (soundfile, scipy, einops)
- [ ] stable-audio-tools / stable-audio-open installieren
- [ ] Worker-Script erstellen (Jobs von Pipeline entgegennehmen)
- [ ] Ersten lokalen Audio-Test fahren
- [ ] Erfolg/Misserfolg sauber dokumentieren

### Ergebnis
- Ein lokaler Worker kann Audio generieren oder ist technisch sauber als ungeeignet evaluiert.

---

## P1 – Audio-Strategie festhalten (Feinschliff)
**Ziel:** Den gewählten Pfad dokumentieren und am Worker optimieren — ohne neue parallele Stacks im Repo.

### Offen / iterativ
- [ ] kurze Tracks + Looping als Standard-Produktionslogik in Runbooks festhalten
- [ ] Worker-Parameter (Steps, Clip-Länge) und Erwartungswerte für Laufzeit dokumentieren
- [ ] `GPU_WORKER_*` / `GPU_WORKER_CODE_DIR` in einer zentralen Reference-Seite sammeln

### Ergebnis
- Betrieb und Onboarding sind ohne mündliche Übergabe möglich

---

## P2 – UI-Feinschliff auf Basis echter Nutzung
**Ziel:** Das Dashboard soll nicht nur hübscher, sondern produktiver sein.

### Erledigt ✅
- [x] Top-Level-Navigation verschlankt
- [x] `Operations` Hub eingeführt
- [x] `Overview / Create / Audio Lab / Operations`
- [x] erste Tooltips / Microcopy / Mobile-Verbesserungen
- [x] Create-Seite strukturell besser in Schritte gegliedert
- [x] Server Stats Widget (CPU/RAM/Disk/Load mit Gauge-Ringen)
- [x] Activity Timeline (Pipeline Runs + Audio Jobs)
- [x] Doku-Sektion im Dashboard mit Suchfeld + Quicklinks (24.03)

### Noch offen
- [ ] restliches Inline-CSS aus `pipeline_new.html` rausziehen
- [ ] Asset-/Fehlermeldungen menschlicher formulieren
- [ ] mobile Ansicht gezielt auf echter Nutzung testen
- [ ] letzte UI-Inkonsistenzen glätten
- [ ] Operations um Problemansicht erweitern (`blocked`, `stale`, `failed`, `action needed`)

### Ergebnis
- UI ist nicht nur neu, sondern betriebssicher und konsistent

---

## P3 – Produktlogik verbessern + Shorts
**Ziel:** Weniger doppelte Eingaben, mehr Studio-Flow. Shorts als neuer Output-Kanal.

### Offen
- [ ] Hauswahl stärker mit Audio-Generierung koppeln
- [ ] Audio-Quelle intelligenter vorbelegen
- [ ] Defaults stärker nutzen, weniger manuelle Felder
- [ ] Create-Flow weiter in Richtung: Stil → Audio → Visuals → Launch
- [ ] **YouTube Shorts Pipeline** evaluieren und planen (Pako erstellt Entwurf)

### Ergebnis
- Weniger Formulararbeit, mehr produktisierte Bedienung
- Shorts als zusätzlicher Content-Kanal

---

## P4 – Datenbank-Robustheit
**Ziel:** DB überlebt Container-/VM-Restarts ohne Datenverlust.

### Erledigt ✅
- [x] DB-Backup-Cron + WAL-Modus + Recovery-Check (Smith, `f299d36`)

### Noch offen
- [ ] DB-Pfad auf persistentes Volume legen (Kevin, wenn GPU-Worker steht)
- [ ] Optional: DB-Export als JSON für manuelles Backup

### Ergebnis
- Kein Datenverlust mehr bei Restarts

---

## P5 – Dokumentation nach Diátaxis Framework
**Ziel:** Professionelle, strukturierte Doku die für Menschen UND Agenten funktioniert.

### Erledigt ✅
- [x] Docs-Struktur im Repo angelegt (tutorials/, guides/, reference/, explanation/, technical/)
- [x] Dashboard-Integration: Doku-Sektion mit Navbar, Suchfeld, Quicklinks
- [x] CHANGELOG.md erstellt (Jarvis)
- [x] Architecture Diagram erstellt (Jarvis)
- [x] Agenten-Doku begonnen (Pako – wie Agents mit dem Projekt arbeiten)
- [x] Audio-Strategie (`docs/explanation/audio-strategy.md`) an Stable Audio Local angeglichen

### Noch offen
- [ ] Tutorial: "Erstes Video von A bis Z"
- [ ] How-to: "GPU-Worker / Stable Audio Local betreiben" (Env-Vars, Pfade, typische Fehler)
- [ ] How-to: "GPU-Worker einrichten"
- [ ] Reference: API-Endpoints Übersicht
- [ ] Reference: DB-Schema + Tabellen
- [ ] Reference: Umgebungsvariablen + Konfiguration
- [ ] Explanation: Pipeline-Architektur
- [ ] Agenten-Doku vervollständigen (Tickets, Git-Workflow, Regeln — ohne altes Task/Webhook-Protokoll)

### Aufgabenverteilung
- **Pako:** Tutorials + How-to Guides + Agenten-Doku + Dashboard-Integration
- **Smith:** Reference + Explanation + Reviews
- **Jarvis:** CHANGELOG, Architecture, Zusammenführung

### Ergebnis
- Jeder neue Agent/Mensch kann das Projekt in 15 Min verstehen

---

## P6 – Betriebsreife / Infrastruktur
**Ziel:** Weniger implizites Wissen, stabile Infrastruktur.

### Erledigt ✅
- [x] PROJECT_STATUS.md Auto-Update Cron (3x täglich, Berliner Winterzeit)
- [x] Backup-Cron alle 6h
- [x] Koordination über **Tickets** im Dashboard (GitHub-Task-Sync entfernt)

### Noch offen
- [ ] SSH-Tunnel stabilisieren (bore als systemd Service ODER Cloudflare Tunnel evaluieren)
- [ ] Versionierung konsequent bei Dashboard-Änderungen durchziehen
- [ ] bore-Tunnel Port-Problem lösen (ändert sich bei jedem Restart)

### Ergebnis
- Neue Agenten oder Menschen können schneller übernehmen

---

## Konkrete nächste Schritte

### Unmittelbar (heute/morgen)
1. **Kevin:** SSH-Key auf GPU-VM eintragen → Smith kann weiter einrichten
2. **Smith:** CUDA Dependencies + stable-audio installieren sobald SSH geht
3. **Pako:** Shorts-Plan finalisieren + Doku weiter ausbauen
4. **Jarvis:** Webhook-Cleanup (Duplikat entfernen) + Doku-Beiträge

### Diese Woche
5. Ersten lokalen Audio-Test auf GPU-VM fahren
6. Audio-Strategie schriftlich festzurren
7. Agenten-Doku fertigstellen

---

## Nordstern

**Haus wählen → Audio stabil erzeugen → visuell rendern → reviewen → veröffentlichen**

Alles, was diesen Kernpfad nicht stabiler macht, ist aktuell zweitrangig.
