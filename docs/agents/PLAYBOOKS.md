# Agent Playbooks

Diese Seite beschreibt Standardabläufe für Agenten im Projekt.

Ziel: wiederholbare Arbeit ohne jedes Mal improvisierten Git-/Sync-/Push-Folkore-Tanz.

---

## Playbook 1 – Kleine Doku-Änderung sauber nach `main`

Geeignet für:
- kleine Korrekturen
- klar isolierte Doku-Verbesserungen
- konfliktarme Updates

### Ablauf
1. Repo-Status prüfen
2. aktuelle Wahrheit lesen (`README.md`, `PROJECT_STATUS.md`, relevante Doku)
3. `git fetch --all --prune`
4. Änderung lokal machen
5. Diff prüfen
6. committen
7. `git pull --rebase origin main`
8. pushen

### Minimalbefehle
```bash
git status
git fetch --all --prune
# Dateien ändern
git add <dateien>
git commit -m "docs: ..."
git pull --rebase origin main
git push origin main
```

### Nicht geeignet, wenn
- dieselben Dateien gerade heiß umkämpft sind
- Upstream auf denselben Dateien schon driftet
- die Änderung größer als ein kleiner sauberer Patch ist

---

## Playbook 2 – Größere Änderung auf eigenem Branch

Geeignet für:
- Refactors
- neue Doku-Bereiche
- UI-/Struktur-Änderungen
- alles mit höherem Konfliktrisiko

### Ablauf
```bash
git fetch --all --prune
git checkout -b docs/<name>-<thema>
# Dateien ändern
git add <dateien>
git commit -m "docs: ..."
git push -u origin docs/<name>-<thema>
```

Danach:
- reviewen lassen
- nicht blind auf `main` drücken
- gezielt mergen oder selektiv übernehmen

---

## Playbook 3 – Ticket im Dashboard übernehmen und abschließen

### Ablauf
1. Ticket im Dashboard öffnen oder neu anlegen
2. Status auf **in_progress**, Owner setzen wenn vorgesehen
3. `git fetch --all --prune` und auf aktuellem `main`/Branch arbeiten
4. kleine Commits, klare Messages
5. vor Push: Rebase/Merge mit `origin/main`
6. PR oder direkter Push nach Teamregel
7. Ticket auf **done** oder **closed**, Kurznotiz wenn nötig

### Faustregel
Wenn die Aufgabe doch nicht fertig wird: Ticket wieder **open** oder jemanden zuweisen — nicht einfach verschwinden lassen.

---

## Playbook 4 – Review eines fremden Agent-Branches

### Ziel
Nicht blind mergen. Erst prüfen, ob der Branch:
- neue Arbeit bringt
- keine neueren Inhalte zurückdreht
- keine falschen Pfade / Altstände wieder reinholt

### Vorgehen
1. Branch gegen `origin/main` diffen
2. Commit-Liste ansehen
3. Dateien mit hohem Risiko prüfen:
   - `README.md`
   - `PROJECT_STATUS.md`
   - zentrale Templates
   - UI-Basisdateien
4. entscheiden:
   - komplett mergebar
   - nur teilweise brauchbar
   - ablehnen / neu aufsetzen

### Wenn gemischt
Dann selektiv übernehmen statt Komplettmerge.

Das ist feiger Heldentum? Nein. Das ist professionelle Schadensbegrenzung.

---

## Playbook 5 – Konflikt beim Rebase oder Pull

### Nicht tun
- panisch weiterklicken
- blind `--force`
- Konflikt mit Bauchgefühl wegwürfeln

### Stattdessen
1. stoppen
2. betroffene Dateien identifizieren
3. prüfen, welche Seite aktueller / richtiger ist
4. Konflikt sauber lösen
5. Diff danach nochmal lesen

Wenn unklar ist, welche Version die Wahrheit ist:
- `PROJECT_STATUS.md`
- aktueller Code
- letzte saubere Commits
- operative Teamentscheidung

---

## Playbook 6 – Doku für instabile Technik schreiben

Wenn ein Bereich noch nicht stabil ist:
- klar als Baustelle markieren
- nicht so schreiben, als sei die Sache produktionsreif
- zwischen "existiert", "wird evaluiert" und "ist Standardpfad" unterscheiden

Gerade hier wichtig für:
- Audio-Worker (Stable Audio Local)
- lokale GPU-Pfade und SSH/Betrieb

---

## Playbook 7 – Vor dem Push letzter Realitätscheck

Vor jedem Push kurz prüfen:
- [ ] im richtigen Repo?
- [ ] auf dem richtigen Branch?
- [ ] keine Secrets im Diff?
- [ ] keine versehentlichen Rollbacks?
- [ ] Doku beschreibt Realität statt Wunschbild?
- [ ] bei Ticket-Arbeit: Status im Dashboard noch korrekt?

Wenn eine Antwort "nein" oder "unklar" ist, erst fixen, dann pushen.
