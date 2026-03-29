# UI INFORMATION ARCHITECTURE GUIDE v5

## Zweck
Finale kompakte UI-Leitdatei für eure Agents.  
Sie definiert:
- wie Dashboard-Seiten aufgebaut werden
- wie zukünftige Funktionen in die UI einsortiert werden
- wie man entscheidet, was sichtbar sein darf

Diese Datei ist absichtlich kompakt und soll zusammen mit euren anderen V5/V6-Dateien nutzbar sein.

---

## 1. Kernregel
Jede Seite braucht:
- **1 Hauptzweck**
- **1 Hauptaktion**
- **3–5 sofort sichtbare Kerninfos**
- Details erst darunter oder separat

Wenn das nicht klar ist, ist die Seite noch nicht sauber geschnitten.

---

## 2. Sichtbarkeitsstufen
### Ebene A – sofort sichtbar
Nur Infos für die nächste Entscheidung

### Ebene B – nach kurzem Scan sichtbar
wichtige Metadaten, sekundäre Aktionen, Statusdetails

### Ebene C – nur bei Bedarf
Logs, Rohdaten, Debug, technische Herkunft, tiefe Konfiguration

**Regel:**  
Debug/Tech darf nicht denselben visuellen Rang wie Produktentscheidungen haben.

---

## 3. Verbindliche Seitentypen
Alle zukünftigen Seiten müssen einem Typ zugeordnet werden:

- **Overview**
- **List**
- **Detail**
- **Create**
- **Settings**
- **Ops**

Keine Mischseite ohne klare Begründung.

---

## 4. Universelle Seitenschablone
Fast jede Seite folgt diesem Aufbau:

### A. Header
- Titel
- kurzer Kontext
- Hauptstatus falls relevant
- 1 Hauptaktion

### B. Decision Layer
- die wichtigsten 3–5 Infos für die nächste Entscheidung

### C. Work Layer
- das eigentliche Formular, Objekt oder die Liste

### D. Support Layer
- Verlauf, Metadaten, Nebeninfos, verwandte Dinge

### E. Debug / Ops Layer
- Logs
- technische Details
- Rohzustände
- nur nachgelagert

---

## 5. Dashboard / Studio Home
### Zweck
**Aufmerksamkeit und nächste Schritte steuern**

### Hauptaktion
Neuen Workflow / neues Video starten

### Pflichtreihenfolge
1. Header + Primary CTA
2. Needs Attention
3. Active Productions
4. Ready / Recently Published
5. Recent Workflows
6. kleiner Ops/Health-Bereich oder separate Ops-Seite

### Was nicht dominieren darf
- Health
- Queue
- GPU/Worker
- rohe Technik
- doppelte Workflow-Darstellung

---

## 6. Create-Seite
### Zweck
**einen neuen Produktionslauf schnell und sicher starten**

### Hauptaktion
Run starten

### Pflichtreihenfolge
1. Preset / House
2. Variant
3. Duration
4. Source Choice
5. Hauptoptionen
6. Review Summary
7. Start

### In Advanced
- tiefe Audio-/Render-Parameter
- Thumbnail-/Background-Details
- Post-Processing
- Spezialoptionen

### Nicht auf der Hauptfläche
- Generator-Live-Logs
- technische Asset-Herkunft
- Rohstatus
- zu viele versteckte Systemkonzepte in sichtbarer UX

---

## 7. Detailseiten
Gilt für Workflow Detail, Publish Detail, Audio Job Detail.

### Aufbau
1. Header: Name, Typ, Status, Hauptaktion
2. Decision Layer: aktuelle Phase, nächster Schritt, letzte relevante Änderung
3. Work Layer: Outputs, Preview, Metadaten, Quick Actions
4. Support Layer: Timeline, Files, sekundäre Infos
5. Debug Layer: Logs, technische Fehler, Rohzustände

### Regel
Detailseiten tragen technische Tiefe.  
Overview- und Create-Seiten nicht.

---

## 8. Listen-Seiten
### Sofort sichtbar
- Name
- Status
- Typ
- letzte Änderung
- 1–2 sinnvolle Metafelder
- Quick Action falls sinnvoll

### Vermeiden
- zu viele Spalten
- jede technische Eigenschaft
- Listen als Ersatz für gute Detailseiten

---

## 9. Settings-Seiten
### Nur zeigen
- logisch gruppierte Konfiguration
- kurze Erklärung
- Defaults / Policies / Accounts
- gefährliche Aktionen separat

### Nicht mischen mit
- operativen Logs
- Workflow-Listen
- Produktionsaktionen

---

## 10. Ops-Seiten
Ops ist für:
- Queue
- Worker
- Health
- Failures
- Releases / Server / Deploy

Ops darf mit dem Produkt verbunden sein, aber nicht denselben Rang wie die Hauptproduktions-UI bekommen.

---

## 11. Regeln für zukünftige Funktionen
### Neue Funktion = neues Objekt
Fragen:
- reicht eine bestehende Detailseite?
- braucht es eine eigene Listenseite?
- braucht es wirklich eine eigene Startseite?

### Neue Funktion = neuer Status
- in bestehende Statuslogik integrieren
- nicht sofort neue Sonderkarten/Sondertabs bauen

### Neue Funktion = neue Plattform
- in Publish-/Workflow-/Account-Modell einordnen
- keine eigene UI-Welt ohne Not

### Neue Funktion = neuer Provider
- eher Settings / Config / Detail
- nicht Dashboard aufblähen

### Neue Funktion = neue Debug-Info
- in Detail oder Ops
- nicht in Overview/Create

---

## 12. UI-Verbote
- keine Seite mit mehreren gleichrangigen Hauptaktionen
- keine Debug-Infos im primären Sichtbereich
- keine neuen Tabs als Müllhalde für unklare Struktur
- keine temporären UI-Sonderlösungen ohne Modellbezug
- keine Health-/Ops-Infos gleichrangig mit Produktentscheidungen
- keine Mischseite aus Overview + Create + Debug + Settings

---

## 13. Review-Fragen für Agents
Vor jeder neuen Seite beantworten:
1. Was ist die Hauptaufgabe?
2. Was ist die Hauptaktion?
3. Was muss sofort sichtbar sein?
4. Was gehört in Support?
5. Was gehört in Debug?
6. Welcher Seitentyp ist das?
7. Wird Produktlogik gezeigt oder nur Technik?
8. Gehört ein Teil davon eigentlich auf eine Detailseite?

---

## 14. Maßstab
Gutes UI heißt hier nicht zuerst “schön”, sondern:
**klar priorisiert, leicht scanbar, modelltreu und ohne unnötige Technik im Hauptfluss.**
