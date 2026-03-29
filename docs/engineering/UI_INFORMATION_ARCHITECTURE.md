# UI Information Architecture

**Owner:** Pako
**Reviewer:** Smith, Jarvis
**Stand:** 2026-03-29
**Welle:** B11
**Depends:** A03, B01

---

## Zweck

Diese Datei definiert verbindlich, wie UI-Seiten aufgebaut, geschnitten und bewertet werden.
Sie gilt für alle neuen Seiten und als Maßstab für bestehende Seiten.

---

## 1. Kernregel

Jede Seite braucht genau:
- **1 Hauptzweck**
- **1 Hauptaktion**
- **3–5 sofort sichtbare Kerninfos**

Wenn das nicht eindeutig ist, ist die Seite noch nicht sauber geschnitten.

---

## 2. Sichtbarkeitsstufen

| Stufe | Beschreibung | Beispiele |
|---|---|---|
| **A – sofort sichtbar** | Infos für die nächste Entscheidung | Status, Titel, primäre Aktion |
| **B – nach kurzem Scan** | Wichtige Metadaten, sekundäre Aktionen | Konfigurationsdetails, Zeitstempel, Nebenaktionen |
| **C – nur bei Bedarf** | Logs, Rohdaten, Debug, technische Herkunft | Logs, Raw-Config, Error-Traces, Job-IDs |

**Regel:** Debug/Ops/Tech darf nicht denselben visuellen Rang wie Produktentscheidungen haben.

---

## 3. Verbindliche Seitentypen

Jede Seite im Dashboard gehört zu genau einem Typ:

| Typ | Zweck | Hauptaktion |
|---|---|---|
| **Overview / Studio Home** | Aufmerksamkeit steuern, nächste Schritte zeigen | Neuen Run starten |
| **List** | Objekte durchsuchen und filtern | Zu Detail navigieren oder Schnellaktion |
| **Detail** | Einzelnen Lauf/Job vollständig verstehen | Weiterführen (rendern, uploaden, retry) |
| **Create** | Neues Objekt schnell und sicher anlegen | Run starten |
| **Settings** | Konfiguration verwalten | Speichern / Aktualisieren |
| **Ops** | System-Gesundheit und Betriebszustand prüfen | Eingreifen bei Problemen |

Keine Mischseite (z.B. Create + Debug + Settings auf einer Seite) ohne explizite begründete Ausnahme.

---

## 4. Universelle Seitenstruktur

Jede Seite folgt diesem Schichtenmodell (von oben nach unten):

```
┌────────────────────────────────────────┐
│  A. Header                             │  Titel, Status, Hauptaktion
├────────────────────────────────────────┤
│  B. Decision Layer                     │  3–5 wichtigste Entscheidungsinfos
├────────────────────────────────────────┤
│  C. Work Layer                         │  Formular / Objekt / Liste
├────────────────────────────────────────┤
│  D. Support Layer                      │  Verlauf, Metadaten, verwandte Objekte
├────────────────────────────────────────┤
│  E. Debug / Ops Layer                  │  Logs, Raw, Fehler – immer nachgelagert
└────────────────────────────────────────┘
```

---

## 5. Seitentyp: Overview / Studio Home

| Eigenschaft | Wert |
|---|---|
| **Hauptzweck** | Aufmerksamkeit steuern, nächsten Schritt zeigen |
| **Hauptaktion** | Neuen Workflow starten |
| **Sichtbarkeit A** | Needs Attention, laufende Runs, primäre CTA |
| **Sichtbarkeit B** | Kürzlich veröffentlichte Videos, Recent Workflows |
| **Sichtbarkeit C** | Health, Queue, Worker, GPU-Status |

Prioritätsreihenfolge auf der Seite:
1. Header + primäre CTA
2. Needs Attention (blockierte oder fehlgeschlagene Runs)
3. Active Productions (laufende Renders/Uploads)
4. Ready / Recently Published
5. Recent Workflows (Liste)
6. Ops-Bereich klein oder eigene Ops-Seite

**Verboten auf Studio Home:**
- Health/GPU als dominantes Element
- Rohe Queue-Länge als Hauptinfo
- Doppelte Workflow-Darstellung
- Debug-Logs auf Hauptfläche

---

## 6. Seitentyp: Create

| Eigenschaft | Wert |
|---|---|
| **Hauptzweck** | Neuen Produktionslauf schnell und sicher starten |
| **Hauptaktion** | Run starten |
| **Sichtbarkeit A** | Preset/House, Variant, Dauer, Quelle, Start-Button |
| **Sichtbarkeit B** | Hauptoptionen, Review Summary |
| **Sichtbarkeit C** | Advanced-Optionen (Audio-Parameter, Rendering, Post-Processing) |

Pflichtfelder in dieser Reihenfolge:
1. Preset / House
2. Variant
3. Dauer
4. Quelle (Audio oder Upload)
5. Hauptoptionen
6. Review Summary
7. Start

**Verboten auf Create:**
- Generator-Live-Logs
- Technische Asset-Herkunft im Hauptfluss
- Rohstatus-Anzeigen
- Zu viele versteckte Systemkonzepte in sichtbarer UX

---

## 7. Seitentyp: Detail

Gilt für: Workflow Detail, Short Detail, Audio Job Detail.

| Eigenschaft | Wert |
|---|---|
| **Hauptzweck** | Einzelnen Lauf vollständig verstehen und weiterführen |
| **Hauptaktion** | Kontextspezifisch (Rendern / Hochladen / Retry / Abbrechen) |
| **Sichtbarkeit A** | Status, nächster Schritt, Hauptaktion |
| **Sichtbarkeit B** | Outputs, Preview, Konfiguration, Quick Actions |
| **Sichtbarkeit C** | Logs, Raw-Config, technische IDs, Error Traces |

Seitenaufbau:
1. Header: Name, Typ, Status-Pill, Hauptaktion
2. Decision Layer: aktuelle Phase, nächster Schritt, letzte relevante Änderung
3. Work Layer: Output-Dateien, Preview (Video/Audio), Metadaten
4. Support Layer: Quelle/Kontext, Timeline, verwandte Objekte
5. Debug Layer: Logs (kollabiert), technische Details (kollabiert)

**Regel:** Detailseiten tragen technische Tiefe. Overview- und Create-Seiten nicht.

---

## 8. Seitentyp: List

| Eigenschaft | Wert |
|---|---|
| **Hauptzweck** | Objekte durchsuchen, filtern, zur Detailseite navigieren |
| **Hauptaktion** | Zu Detail navigieren oder Schnellaktion auslösen |
| **Sichtbarkeit A** | Name, Status, Typ, letzte Änderung |
| **Sichtbarkeit B** | 1–2 relevante Metafelder, Quick Action |
| **Sichtbarkeit C** | Nichts – alle Details gehören auf die Detailseite |

Spaltenregel:
- Max. 5–6 Spalten sichtbar
- Keine technischen IDs in der Hauptliste
- Keine Inline-Logs

---

## 9. Seitentyp: Settings

| Eigenschaft | Wert |
|---|---|
| **Hauptzweck** | Konfiguration verwalten |
| **Hauptaktion** | Speichern / Aktualisieren |
| **Sichtbarkeit A** | Aktuelle Werte der wichtigsten Einstellungen |
| **Sichtbarkeit B** | Defaults, Policies, Accounts |
| **Sichtbarkeit C** | Gefährliche Aktionen (separater Bereich, explizite Bestätigung) |

**Nicht mischen mit:** Workflow-Listen, operativen Logs, Produktionsaktionen.

---

## 10. Seitentyp: Ops

| Eigenschaft | Wert |
|---|---|
| **Hauptzweck** | System-Gesundheit und Betriebszustand überwachen |
| **Hauptaktion** | Eingreifen bei konkretem Problem |
| **Inhalte** | Queue, Worker, Health, Failures, Releases, Server, Deploy |

Ops ist vom Produkt getrennt oder klar in einen eigenen Bereich verschoben.
Ops-Inhalte bekommen **nicht** denselben Rang wie Produktions-UI.

---

## 11. Statusdarstellung

Status-Pills/Badges folgen dieser Logik:

| Status-Gruppe | Beispiele | Visueller Stil |
|---|---|---|
| **Aktiv** | running, queued, uploading | Pulsierender Indikator, blau |
| **Fertig** | rendered, uploaded | Grün |
| **Fehler** | failed, error, cancelled | Rot / Orange |
| **Entwurf** | created | Neutral / grau |

Regeln:
- Statustexte sind immer verständlich ohne technische Vorkenntnisse
- Kein raw `status`-Feld direkt zeigen ohne Display-Mapping
- Fehlerzustände zeigen immer einen nächsten Schritt

---

## 12. Regeln für neue Features

### Neue Funktion = neues Objekt
- Reicht eine bestehende Detailseite? → Dort einbauen
- Braucht es eine eigene Listenseite? → Nur wenn eigenständiger Objekttyp
- Braucht es eine eigene Startseite? → Nur wenn zentraler neuer Workflow

### Neue Funktion = neuer Status
- In bestehende Statuslogik integrieren
- Keine neuen Sonderkarten oder Sondertabs ohne Modellbezug

### Neue Funktion = neue Plattform
- In Publish-/Workflow-/Account-Modell einordnen
- Keine eigene UI-Welt ohne Not

### Neue Funktion = neue Debug-Info
- In Detail (C) oder Ops
- Nicht in Overview oder Create

---

## 13. UI-Verbote

- Keine Seite mit mehreren gleichrangigen Hauptaktionen
- Keine Debug-Infos im primären Sichtbereich (Ebene A)
- Keine neuen Tabs als Sammelbecken für unklare Struktur
- Keine temporären UI-Sonderlösungen ohne Modellbezug
- Keine Health-/Ops-Infos gleichrangig mit Produktentscheidungen
- Keine Mischseite aus Overview + Create + Debug + Settings
- Keine rohen technischen IDs auf Ebene A oder B
- Kein raw `status`-Feld ohne Display-Mapping

---

## 14. Review-Checkliste für neue UI-Seiten

Vor jeder neuen Seite (oder größerem Umbau):

- [ ] Was ist die Hauptaufgabe dieser Seite?
- [ ] Was ist die eine Hauptaktion?
- [ ] Was muss sofort sichtbar sein (Ebene A)?
- [ ] Was gehört in Support (Ebene B/C)?
- [ ] Was gehört in Debug (Ebene C)?
- [ ] Welcher Seitentyp ist das?
- [ ] Wird Produktlogik gezeigt oder nur Technik?
- [ ] Gehört ein Teil davon auf eine Detailseite?
- [ ] Ist der Status verständlich ohne Fachkenntnisse?
- [ ] Gibt es bei Fehler immer einen nächsten Schritt?

---

## 15. Maßstab

Gutes UI bedeutet hier nicht zuerst „schön", sondern:

> **Klar priorisiert, leicht scanbar, modelltreu und ohne unnötige Technik im Hauptfluss.**

---

## Appendix: Mapping auf den aktuellen Stand (Stand 2026-03-29)

Dieses Mapping zeigt, wie die realen Seiten des Dashboards den Seitentypen entsprechen.
Es dient als Brücke zwischen dem Zielmodell und dem aktuellen Produktionsstand.

### `/admin` – Studio Home / Overview

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Overview / Studio Home |
| **Route** | `GET /admin` |
| **Hauptzweck** | Laufende und zuletzt erstellte Workflows anzeigen, neuen Run starten |
| **Hauptaktion** | Neuen Workflow erstellen (`/admin/pipeline/new`) |
| **Sichtbarkeit A** | Laufende Workflows, letzte Runs, primäre CTA |
| **Sichtbarkeit C** | Server-Stats, Release-Info |
| **Abweichungen vom Ziel** | GPU/Health kann auf Hauptfläche dominant sein → mittelfristig in Ops verschieben |

---

### `/admin/pipeline/new` – Create Flow

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Create |
| **Route** | `GET /admin/pipeline/new` |
| **Hauptzweck** | Neuen Video-Workflow anlegen |
| **Hauptaktion** | Pipeline starten (`POST /admin/pipeline/start`) |
| **Sichtbarkeit A** | House-Auswahl, Variant, Dauer, Source |
| **Sichtbarkeit C** | Advanced Audio-/Render-Parameter |
| **Abweichungen vom Ziel** | Stimmungsfelder werden teilweise nicht vorausgefüllt (bekannter Bug) |

---

### `/admin/pipeline/run/{workflow_id}` – Workflow Detail

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Detail |
| **Route** | `GET /admin/pipeline/run/{workflow_id}` |
| **Hauptzweck** | Einzelnen Workflow-Run vollständig verstehen und weiterführen |
| **Hauptaktion** | Upload starten (wenn Status `rendered`) |
| **Sichtbarkeit A** | Status-Pill, Hauptaktion |
| **Sichtbarkeit B** | Outputs, Preview, Konfiguration |
| **Sichtbarkeit C** | Logs (kollabiert) |

---

### `/admin/audio/jobs/{job_id}` – Audio Job Detail

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Detail |
| **Route** | `GET /admin/audio/jobs/{job_id}` |
| **Hauptzweck** | Einzelnen Audio-Job verstehen, weiterführen oder retry |
| **Hauptaktion** | Retry (bei Fehler) oder In Video verwenden (bei Erfolg) |
| **Sichtbarkeit A** | Status, Hauptaktion, Ergebnis |
| **Sichtbarkeit C** | Logs, technische Details |

---

### `/admin/shorts/{workflow_id}` – Short Detail

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Detail |
| **Route** | `GET /admin/shorts/{workflow_id}` |
| **Hauptzweck** | Short-Workflow verstehen, rendern, hochladen |
| **Hauptaktion** | Rendern oder Upload (zustandsabhängig) |
| **Sichtbarkeit A** | Status, Clip-Quelle, Hauptaktion |
| **Sichtbarkeit B** | Video-Preview, Thumbnail, Output-Dateien |
| **Sichtbarkeit C** | Logs |

---

### `/admin/pipeline` – Workflow List

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | List |
| **Route** | `GET /admin/pipeline` |
| **Hauptzweck** | Alle Video-Workflows durchsuchen |
| **Hauptaktion** | Zu Detail navigieren |

---

### `/admin/audio/jobs` – Audio Job List

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | List |
| **Route** | `GET /admin/audio/jobs` |
| **Hauptzweck** | Alle Audio-Jobs durchsuchen |
| **Hauptaktion** | Zu Detail navigieren |

---

### `/admin/ops` und `/admin/system` – Ops

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Ops |
| **Routen** | `GET /admin/ops`, `GET /admin/system` |
| **Hauptzweck** | System-Health, Queue, Worker, Server-Stats |
| **Abweichungen** | `/admin/system` enthält noch Version/Metrics die mittelfristig hierher wandern sollen |

---

### `/admin/settings` – Settings

| Eigenschaft | Aktueller Stand |
|---|---|
| **Seitentyp** | Settings |
| **Hauptzweck** | Presets, Provider-Config, User-Einstellungen |

---

### Bekannte Abweichungen vom Zielmodell

| Problem | Betroffene Seite | Priorität |
|---|---|---|
| Stimmungsfelder bei Create nicht vorausgefüllt | `/admin/pipeline/new` | Hoch (aktiver Bug) |
| GPU/Health auf Studio Home dominant | `/admin` | Mittel |
| Version/Metrics auf Settings statt Ops | `/admin/system` | Niedrig |
