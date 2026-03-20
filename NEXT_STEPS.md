# Konkrete nächste Schritte nach Feedback

Dieses Dokument übersetzt vorhandenes Feedback und Projektentscheidungen in konkrete Folgeaufgaben.

---

## 1. Aus dem Feedback abgeleitete Aufgaben

### A. Aufgaben feiner unterteilen
Problem:
- Die bisherigen Aufgaben sind noch relativ grob.

Konkrete Folgeaufgabe:
- Aufgaben künftig pro Phase, pro Artefakt und später pro Song aufteilen.
- Zusätzlich sollten Aufgaben einen klaren Owner bekommen.

### B. API-Zugänge und Testdaten vorbereiten
Problem:
- Upload-Automatisierung bleibt theoretisch, solange keine konkrete Auth-/Teststrategie dokumentiert ist.

Konkrete Folgeaufgabe:
- Private/API-bezogene Anforderungen separat dokumentieren.
- Testdatensatz für einen ersten Proof of Concept definieren.

### C. Zuständigkeiten sichtbar halten
Problem:
- Rollen wurden definiert, müssen aber laufend im Repo aktuell gehalten werden.

Konkrete Folgeaufgabe:
- Neue Arbeitspakete immer mit Owner dokumentieren.
- Parallelplan bei Rollenänderungen aktualisieren.

### D. Beispiel-Workflow ergänzen
Problem:
- Der Zielzustand ist dokumentiert, aber der erste kleinste echte Workflow fehlt noch.

Konkrete Folgeaufgabe:
- einen minimalen, ausführbaren PoC-Workflow definieren und danach technisch umsetzen.

---

## 2. Entscheidungen daraus

1. Das Projekt plant **KI für Song-Erzeugung** ein.
2. Die Kernpipeline bleibt **tool-agnostisch**.
3. Der erste PoC soll **einen generierten Song** als Input akzeptieren.
4. Zuständigkeiten und Entscheidungen müssen weiterhin im Repo dokumentiert und gepusht werden.

---

## 3. Direkt anschließende Arbeitspakete

### Pako
- [ ] Repo-Zielstruktur anlegen
- [ ] `song.json`/Metadaten-Schema v1 entwerfen
- [ ] Generator-bezogene Felder im Schema vorsehen
- [ ] PoC-Workflow-Datei definieren

### Jarvis
- [ ] YouTube-Metadaten-Templates für den PoC vorbereiten
- [ ] Upload-Checkliste für den PoC schreiben
- [ ] Content-Felder auf das Schema abstimmen

---

## 4. Was danach passieren sollte

1. Schema v1 mergen
2. PoC-Datensatz definieren
3. Repo-Struktur anlegen
4. erster minimaler Workflow umsetzen
5. erst dann echte API-/Upload-Automatisierung angehen
