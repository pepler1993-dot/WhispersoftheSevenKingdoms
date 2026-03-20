# Start Ready – Freigabe für den ersten Parallel-Sprint

Dieses Dokument übersetzt die Readiness-Analyse in einen direkten Startplan.

---

## 1. Startstatus

### Freigabe
**Freigegeben für den ersten Parallel-Sprint – mit klar begrenztem Scope.**

Das Projekt ist jetzt ausreichend vorbereitet, damit **Pako** und **Jarvis** parallel loslegen können.

Es gilt aber:
- keine gleichzeitigen Strukturumbauten an denselben Dateien
- erste Sprintziele klein und klar halten
- Entscheidungen weiter dokumentieren und pushen

---

## 2. Sprint-Ziel

Der erste Sprint soll die Voraussetzungen schaffen, damit der PoC technisch tatsächlich begonnen werden kann.

### Sprint-Ergebnis
Am Ende des ersten Sprints soll vorhanden sein:
- Zielordnerstruktur im Repo
- erster Metadaten-/Schema-Entwurf
- erste Content-/Publishing-Templates
- klarer Ausgangspunkt für den PoC

---

## 3. Aufgaben im ersten Sprint

## Pako
### Branch 1
- `feature/pako-repo-structure`

### Ziel
- Repo-Zielstruktur anlegen
- technische Bereiche vorbereiten (`input/`, `work/`, `output/`, `scripts/`, `templates/`, `docs/`, `schemas/`)
- technische Platzhalter dort sinnvoll setzen, wo sie dem Team Orientierung geben

### Branch 2
- `feature/pako-song-schema`

### Ziel
- `song.json` Schema Draft v1
- Beispiel-Metadatei
- Generator-bezogene Felder für extern erzeugte Songs

---

## Jarvis
### Branch 1
- `feature/jarvis-content-templates`

### Ziel
- YouTube-Beschreibungsvorlage
- Titelmuster
- Tag-/Keyword-Regeln
- Upload-Checkliste für den PoC

### Branch 2
- `feature/jarvis-metadata-rules`

### Ziel
- Content-Felder an Pakos Schema anpassen
- Beispieltexte für PoC-Song ableiten
- Playlist-/Plattform-Mapping an das Schema koppeln

---

## 4. Merge-Plan für den ersten Sprint

### Merge 1
- Pako merged `feature/pako-repo-structure`

### Merge 2
- Jarvis zieht frisches `main` und merged `feature/jarvis-content-templates`

### Merge 3
- Pako merged `feature/pako-song-schema`

### Merge 4
- Jarvis passt darauf `feature/jarvis-metadata-rules` an und merged danach

---

## 5. Pflicht vor jedem Merge

Vor jedem Merge festhalten in `AGENT_SYNC.md`:
- was geändert wurde
- welche Dateien betroffen sind
- was der andere Agent jetzt wissen muss
- ob danach ein Rebase/Merge auf den eigenen Branch nötig ist

---

## 6. Noch offene Entscheidungen, die früh im Sprint geklärt werden sollen

- endgültige Bestätigung von TypeScript
- ESM oder CommonJS
- Validierungsansatz
- erster Generator/Testinput für PoC

Diese Punkte sollen **früh**, aber nicht blockierend geklärt werden.

---

## 7. Definition of Success

Der erste Sprint ist erfolgreich, wenn:
- beide Agenten auf getrennten, klaren Branches gearbeitet haben
- die ersten Merges ohne unnötige Konflikte gelaufen sind
- Repo-Struktur + Schema-Entwurf + Content-Templates vorhanden sind
- der PoC danach real implementierbar ist

Kurz:
Wenn nach dem Sprint nicht mehr nur Dokumente existieren, sondern ein echter Bauplatz.
