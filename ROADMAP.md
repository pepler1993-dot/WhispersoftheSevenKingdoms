# 🗺️ ROADMAP – Whispers of the Seven Kingdoms
> Stand: 23.03.2026 (aktualisiert nach Pair-Thinking von Pako + Smith)

---

## Aktuelle Lage in einem Satz

Die **UI ist deutlich reifer**, aber der **kritische nächste Hebel** ist jetzt nicht mehr Design, sondern der **lokale GPU-Worker** als stabiler Audio-Pfad.

---

## Prioritäten ab jetzt

## P0 – GPU-Worker funktionsfähig machen
**Ziel:** Lokale Audio-Generierung als ernsthafte Alternative zu Kaggle zum Laufen bringen.

### Offen
- [ ] `nvidia-smi` in VM 104 sauber zum Laufen bringen
- [ ] Nouveau-/Treiber-Konflikte final auflösen
- [ ] Python-Umgebung im Worker aufsetzen
- [ ] Modellentscheidung für lokalen Worker finalisieren
- [ ] ersten lokalen Audio-Test fahren
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

### Schon erledigt
- [x] Top-Level-Navigation verschlankt
- [x] `Operations` Hub eingeführt
- [x] `Overview / Create / Audio Lab / Operations`
- [x] erste Tooltips / Microcopy / Mobile-Verbesserungen
- [x] Create-Seite strukturell besser in Schritte gegliedert

### Noch offen
- [ ] restliches Inline-CSS aus `pipeline_new.html` rausziehen
- [ ] Asset-/Fehlermeldungen menschlicher formulieren
- [ ] mobile Ansicht gezielt auf echter Nutzung testen
- [ ] letzte UI-Inkonsistenzen glätten
- [ ] Operations um Problemansicht erweitern (`blocked`, `stale`, `failed`, `action needed`)

### Ergebnis
- UI ist nicht nur neu, sondern betriebssicher und konsistent

---

## P3 – Produktlogik verbessern
**Ziel:** Weniger doppelte Eingaben, mehr Studio-Flow.

### Offen
- [ ] Hauswahl stärker mit Audio-Generierung koppeln
- [ ] Audio-Quelle intelligenter vorbelegen
- [ ] Defaults stärker nutzen, weniger manuelle Felder
- [ ] Create-Flow weiter in Richtung
  1. Stil
  2. Audio
  3. Visuals
  4. Launch

### Ergebnis
- Weniger Formulararbeit, mehr produktisierte Bedienung

---

## P4 – Datenbank-Robustheit
**Ziel:** DB überlebt Container-/VM-Restarts ohne Datenverlust.

### Problem
- SQLite DB liegt aktuell nur im Container-Dateisystem
- Bei LXC Restart / Neuinstallation → alles weg (Jobs, Events, Runs)

### Maßnahmen
- [ ] DB-Pfad auf persistentes Volume legen (Proxmox mount point oder bind mount)
- [ ] Automatisches DB-Backup (cron → tägliches Kopieren auf hdd-backup)
- [ ] DB-Recovery-Check beim Service-Start (Integritätscheck + WAL-Modus)
- [ ] Optional: DB-Export als JSON für manuelles Backup

### Verantwortlich
- **Smith:** DB-Backup-Cron + WAL-Modus + Recovery-Check implementieren
- **Kevin:** Persistentes Volume auf Proxmox einrichten

### Ergebnis
- Kein Datenverlust mehr bei Restarts

---

## P5 – Dokumentation nach Diátaxis Framework
**Ziel:** Professionelle, strukturierte Doku die für Menschen UND Agenten funktioniert.

### Diátaxis Quadranten
1. **Tutorials** – Schritt-für-Schritt Einstieg ("Dein erstes Video erstellen")
2. **How-to Guides** – Aufgabenorientiert ("Neuen Audio-Provider hinzufügen")
3. **Reference** – Technische Referenz (API, DB-Schema, Architektur)
4. **Explanation** – Hintergründe ("Warum kurze Tracks + Looping?")

### Aufgabenverteilung
- **Pako:** Tutorials + How-to Guides (er kennt die Architektur am besten)
  - [ ] Tutorial: "Erstes Video von A bis Z"
  - [ ] How-to: "Neuen Audio-Provider implementieren"
  - [ ] How-to: "Dashboard lokal aufsetzen"
  - [ ] How-to: "GPU-Worker einrichten"
- **Smith:** Reference + Explanation
  - [ ] Reference: API-Endpoints Übersicht
  - [ ] Reference: DB-Schema + Tabellen
  - [ ] Reference: Umgebungsvariablen + Konfiguration
  - [ ] Explanation: Audio-Strategie (Warum Stable Audio Open?)
  - [ ] Explanation: Pipeline-Architektur
- **Jarvis:** Zusammenführung + Navigation (`docs/index.md`)
  - [ ] Docs-Index mit Quadranten-Navigation
  - [ ] Cross-Links zwischen den Quadranten

### Ergebnis
- Jeder neue Agent/Mensch kann das Projekt in 15 Min verstehen

---

## P6 – Betriebsreife / Sonstiges
**Ziel:** Weniger implizites Wissen, weniger Agenten-Amnesie.

### Offen
- [ ] `PROJECT_STATUS.md` aktuell halten
- [ ] Versionierung konsequent bei Dashboard-Änderungen durchziehen
- [ ] Fehlerbehandlung für Assets / Jobs / Uploads weiter verbessern
- [ ] SSH-Tunnel stabilisieren (Cloudflare Tunnel evaluieren)

### Ergebnis
- Neue Agenten oder Menschen können schneller übernehmen

---

## Konkrete nächste Schritte (empfohlen)

### Unmittelbar als Team
1. **GPU-Worker fixen** bis `nvidia-smi` läuft
2. **lokalen Mini-Test** mit dem finalistischen Modell-Stack machen
3. **Audio-Strategie schriftlich festzurren**
4. Danach erst weitere größere UI-/Produktlogik-Runden

### Für die Audio-Seite
- Wenn lokaler Worker läuft: darauf fokussieren
- Wenn lokaler Worker scheitert: Colab als Übergangspfad ernsthaft evaluieren
- Kaggle nur noch als Test-/Fallback-Pfad betrachten, nicht als Glaubenssystem

---

## Nicht mehr Hauptpriorität
Diese Punkte sind wichtig, aber nicht mehr P0:
- noch schickeres Styling
- weitere Dashboard-Spielereien
- neue Growth-/Marketing-Features
- Shorts / Streaming / Reddit / SEO-Ausbau

Erst muss die Audio-Erzeugung auf stabile Beine.

---

## Entscheidungsnotiz

### Aktuelles Pair-Thinking-Fazit
- **Pako:** UI ist jetzt nicht mehr die Hauptbaustelle
- **Smith:** Struktur stimmt, UI ist auf gutem Weg, Technikpfad muss jetzt liefern
- **Gemeinsame Empfehlung:**
  - lokaler GPU-Worker zuerst
  - Audio-Strategie dann finalisieren
  - UI danach mit echtem Nutzungsfeedback weiter polieren

---

## Nordstern

**Haus wählen → Audio stabil erzeugen → visuell rendern → reviewen → veröffentlichen**

Alles, was diesen Kernpfad nicht stabiler macht, ist aktuell zweitrangig.
