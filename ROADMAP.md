# 🗺️ ROADMAP – Whispers of the Seven Kingdoms
> Stand: 24.03.2026 (aktualisiert von Smith nach Review aller Fortschritte)

---

## Aktuelle Lage in einem Satz

GPU-Worker Hardware ist ready (nvidia-smi ✅, PyTorch ✅), aber **SSH-Zugang blockiert** die letzten Schritte. Doku wächst parallel stark (Diátaxis + Dashboard-Integration). Webhooks sind gefixt.

---

## Prioritäten ab jetzt

## P0 – GPU-Worker funktionsfähig machen
**Ziel:** Lokale Audio-Generierung als ernsthafte Alternative zu Kaggle zum Laufen bringen.

### Erledigt ✅
- [x] `nvidia-smi` in GPU-VM sauber zum Laufen gebracht (GTX 1070, 8GB VRAM, CUDA 12.4)
- [x] Nouveau-/Treiber-Konflikte gelöst (Kernel 6.12.74 → 6.12.73 Downgrade)
- [x] PyTorch CUDA 12.1 installiert (`torch-2.5.1+cu121`)
- [x] Python venv unter `/opt/musicgen-worker/.venv`

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

## P1 – Audio-Strategie finalisieren
**Ziel:** Nicht mehr zwischen Kaggle, Hoffnung und Nebenpfaden treiben.

### Entscheidungen, die jetzt fallen müssen
- [ ] Kaggle als Produktionspfad verwerfen oder nur als Fallback markieren
- [ ] Stable Audio Open vs. anderer lokaler Stack final bewerten
- [ ] kurze Tracks + Looping als Standard-Produktionslogik festschreiben oder verwerfen
- [ ] Provider-Strategie für `AudioGenerator` dokumentieren

### Ergebnis
- Ein klarer, schriftlich festgehaltener Audio-Pfad für die nächsten Wochen

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
- [x] Audio-Strategie-Feedback dokumentiert (Smith + Jarvis)

### Noch offen
- [ ] Tutorial: "Erstes Video von A bis Z"
- [ ] How-to: "Neuen Audio-Provider implementieren"
- [ ] How-to: "GPU-Worker einrichten"
- [ ] Reference: API-Endpoints Übersicht
- [ ] Reference: DB-Schema + Tabellen
- [ ] Reference: Umgebungsvariablen + Konfiguration
- [ ] Explanation: Pipeline-Architektur
- [ ] Agenten-Doku vervollständigen (Sync Service Protokoll, Push-Workflow, Regeln)

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
- [x] GitHub Webhooks gefixt (Secret-Mismatch behoben, Duplikat-Hook entfernt)
- [x] PROJECT_STATUS.md Auto-Update Cron (3x täglich, Berliner Winterzeit)
- [x] Backup-Cron alle 6h
- [x] Sync Service Pflicht für alle Agents (Issues = Tasks)

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
