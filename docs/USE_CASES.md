# Use Cases – Whispers of the Seven Kingdoms (Detaildokument)

**Stand:** 27.03.2026  
**Bezug:** Erweitert die Kurzform in `[USER_STORIES.md](USER_STORIES.md)`.  
**Zielgruppe:** Produktionsteam (Produzent, Reviewer), Entwicklung, Onboarding.

---

## Konventionen


| Feld          | Bedeutung                                                         |
| ------------- | ----------------------------------------------------------------- |
| **ID**        | Stabile Referenz (UC-XX)                                          |
| **Priorität** | A = Kern-Workflow, B = Betrieb, C = später / experimentell        |
| **Akteur**    | Primärer auslösender Benutzer                                     |
| **System**    | Dashboard (`services/sync`), Pipeline (`pipeline/`), Audio-Worker |


**Abkürzungen:** „Library“ = zentrale Mediensammlung im Dashboard; „Preset“ = Eintrag in `services/sync/data/house_templates.json`.

---

## UC-01: Neues Video von A bis Z erstellen


|               |                                                                                                                        |
| ------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Priorität** | A                                                                                                                      |
| **Akteur**    | Produzent                                                                                                              |
| **Ziel**      | Ein Longform-Sleep-Video (Audio → Loop-Video → Thumbnail → optional YouTube) mit minimalem manuellen Aufwand erzeugen. |


### Kurzbeschreibung

Der Produzent wählt Stil (Haus), konkrete **Variante**, **Länge** und Audio-Quelle; Metadaten und Briefings werden aus dem Haus-Preset befüllt. Nach Start läuft die Kette automatisch (inkl. Audio-Generierung falls nötig).

### Vorbedingungen

- Dashboard erreichbar; bei Generierung: Audio-Worker (Stable Audio) betriebsbereit.
- Für gewählte Variante existieren Einträge in `variant_prompts` und `background_prompts` im JSON-Preset.
- Optional: gewünschte Hintergrunddatei liegt unter `pipeline/data/assets/backgrounds/` (sonst Server-Fallback über `bg_key`).

### Hauptszenario

1. Akteur öffnet `**/admin/pipeline/new`** (z. B. über Dashboard „Neues Video“).
2. Akteur wählt ein **Haus** (Karte).
3. System zeigt **Varianten**; Akteur wählt **eine Variante** (Pflicht für Audio-Prompts).
4. System setzt u. a. Theme, `notes` (Varianten-Key), Thumbnail-Brief (variantenbezogen), **Video-Hintergrund** nach Preset (`bg_key` + passende Dateiendung), Titel nach `title_template` inkl. Variantenname und Dauerplatzhalter.
5. Akteur wählt **Länge** (1 / 3 / 5 / 8 Stunden); Loop-Stunden und Titel-Dauer-Text werden angepasst.
6. Konfigurationsbereich erscheint; Stimmung/Titel sind vorbefüllt, **technischer Slug** wird intern **nur aus dem Video-Titel** abgeleitet (nicht als eigenes UI-Feld sichtbar).
7. Akteur wählt **Audio-Quelle**:
  - **Neu generieren:** verstecktes Feld enthält ausschließlich **Varianten-Prompts**; „Video erstellen“ startet Workflow mit Audio-Job, dann Pipeline.
  - **Aus Bibliothek:** vorhandener Track mit passendem Dateinamen (Slug aus Titel) muss existieren, sonst Hinweis/Fehlerpfad.
8. Akteur kann **Video-Hintergrund** im gleichen Schritt wie zuvor sichtbar anpassen oder „Automatisch aus Preset“ belassen (Server löst leere Auswahl über Haus + Variante auf).
9. Akteur startet mit **„Video erstellen“** (Submit).
10. System legt Metadaten an, startet Run bzw. Workflow; Akteur verfolgt Status auf Workflow-/Run-Seite.

### Alternativverläufe

- **A1 – Nur Pipeline, Audio schon da:** Schritt 7 Bibliothek, Datei `upload/songs/<slug>.{mp3,wav,ogg}` existiert → kein Audio-Job, direkter Pipeline-Run.
- **A2 – Hintergrund nicht in Dropdown:** Select bleibt leer; Server setzt Datei aus Preset-`bg_key`, sofern Datei im Assets-Ordner existiert.
- **A3 – Erweiterte Einstellungen:** Minuten, Loop, Crossfade, Musik-Brief, Thumbnail-Szene, Upload-Flags manuell feinjustierbar.

### Nachbedingungen

- Erfolg: Run/Workflow angelegt; nach Abschluss liegen erwartbare Outputs unter den üblichen Pipeline-Pfaden; optional Auto-Upload wenn gesetzt.
- Fehler: HTTP-Fehlerseite oder Redirect mit `error`-Query; kein inkonsistenter halbfertiger Zustand ohne erkennbare Meldung (Zielbild).

### Akzeptanzkriterien

- Ohne Variantenwahl sind **keine** Haus-weiten Fallback-Prompts verfügbar; Generierung ohne Variante wird zuverlässig verhindert (Client + Server).
- Titeländerung aktualisiert internen Slug konsistent; Nutzer sieht kein separates Slug-Feld.
- Preset-Daten (Musik-Brief, Thumbnail, Hintergrund) sind mit Variante konsistent, sofern JSON vollständig ist.

### UI- / Routen-Referenz

- Create: `/admin/pipeline/new`
- Start: `POST /admin/pipeline/start`
- Logs/Runs: `/admin/pipeline/logs`, `/admin/pipeline/run/{id}`, `/admin/workflow/{id}`

---

## UC-02: Song im Audio Lab generieren


|               |                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------- |
| **Priorität** | A                                                                                             |
| **Akteur**    | Produzent                                                                                     |
| **Ziel**      | Einzelnen Track erzeugen, Qualität prüfen, ohne sofort die gesamte Video-Pipeline zu starten. |


### Kurzbeschreibung

Separates Formular lädt **nur Varianten-Prompts** aus den Haus-Templates; Titel bestimmt den Slug für Dateinamen/Job.

### Vorbedingungen

- `/admin/audio` erreichbar; Generator-Health ok (`/admin/audio/health`).

### Hauptszenario

1. Akteur öffnet `**/admin/audio`** (Audio Lab).
2. Akteur trägt **Titel** ein; Slug wird im Hintergrund aus Titel abgeleitet.
3. Akteur wählt **Haus · Variante** aus Dropdown; Prompt-Textarea füllt sich mit den **variant_prompts**-Zeilen.
4. Akteur passt optional Dauer, Clip-Länge, Steps an.
5. Akteur startet **„Audio-Job anlegen“**.
6. System erstellt Job; Akteur beobachtet Status auf Job-Detailseite; fertiger Track erscheint in der Library (sofern Worker erfolgreich).

### Alternativverläufe

- **A1 – Eigener Prompt:** Dropdown „eigener Prompt“, freier Text im Textarea (kein Preset-Zwang auf dieser Seite).

### Nachbedingungen

- Job in DB/History; bei Erfolg nutzbarer Track für UC-01 (Bibliothek + passender Slug aus späterem Video-Titel).

### Akzeptanzkriterien

- Kein veraltetes „nur Haus“-Preset ohne Variante in der UI.
- Fehlende/leere Prompts blockieren Job mit verständlicher Meldung.

### UI- / Routen-Referenz

- `/admin/audio`, `POST /admin/audio/generate`, `/admin/audio/jobs/{job_id}`

---

## UC-03: Video-Ergebnis prüfen und freigeben


|               |                                                                                          |
| ------------- | ---------------------------------------------------------------------------------------- |
| **Priorität** | A                                                                                        |
| **Akteur**    | Reviewer (oder Produzent in QA-Rolle)                                                    |
| **Ziel**      | Fertiges Video, Thumbnail und Metadaten im Browser bewerten und Upload gezielt auslösen. |


### Vorbedingungen

- Pipeline-Run abgeschlossen oder zumindest relevante Outputs vorhanden.

### Hauptszenario

1. Akteur öffnet `**/admin/pipeline/run/{run_id}`** (oder verlinkt vom Dashboard).
2. Akteur spielt **Video** ab und prüft **Thumbnail** und angezeigte **Metadaten**.
3. Wenn in Ordnung: Akteur löst **Upload** aus (sofern nicht schon automatisch erfolgt).

### Alternativverläufe

- **A1 – Auto-Upload war aktiv:** Schritt 3 entfällt; Review prüft nur noch YouTube-Ergebnis extern.

### Nachbedingungen

- Entscheidung dokumentiert bzw. Upload durchgeführt; bei manuellem Upload keine doppelten Uploads ohne Absicherung (Systemverhalten laut Implementierung).

### Akzeptanzkriterien

- Vorschau ohne zwingenden Download des gesamten Pakets für die reine Sichtprüfung.
- Klare Anzeige von Slug/Titel/Status zum Abgleich mit Checklisten.

### UI- / Routen-Referenz

- `/admin/pipeline/run/{id}`, ggf. Upload-Trigger aus Run-UI

---

## UC-04: Library verwalten


|               |                                                                                            |
| ------------- | ------------------------------------------------------------------------------------------ |
| **Priorität** | A                                                                                          |
| **Akteur**    | Produzent                                                                                  |
| **Ziel**      | Songs, Thumbnails und verwandte Assets überblicken, hochladen und für die Pipeline nutzen. |


### Vorbedingungen

- Berechtigung für Admin-Bereich; Speicherpfade verfügbar.

### Hauptszenario

1. Akteur öffnet `**/admin/library`**.
2. Akteur listet/filtert **Audio** / **Thumbnails** / **Backgrounds** (je nach Implementierung der Seite).
3. Akteur lädt Dateien hoch oder nutzt generierte Tracks.
4. Akteur prüft Wiedergabe/Qualität in der UI wo vorhanden.

### Alternativverläufe

- **A1 – Umbenennen/Löschen:** gemäß Dashboard-Funktionen; Konsistenz mit Slug aus UC-01 beachten.

### Akzeptanzkriterien

- Keine „toten“ Aktionen; große Uploads ohne Browser-Absturz (Streaming/Chunking wo implementiert).

### UI- / Routen-Referenz

- `/admin/library`

---

## UC-05: Projektstatus auf einen Blick


|               |                                                                               |
| ------------- | ----------------------------------------------------------------------------- |
| **Priorität** | B                                                                             |
| **Akteur**    | Produzent                                                                     |
| **Ziel**      | Laufende und kürzlich abgeschlossene Aktivitäten ohne Seitenwechsel erfassen. |


### Hauptszenario

1. Akteur öffnet `**/admin`** (Dashboard).
2. Sieht Kacheln/Kurzinfos zu letztem Run, Jobs, Serverhinweisen.

### Akzeptanzkriterien

- Kein leeres Dashboard ohne Erklärung bei leerer DB; Links zu relevanten Detailseiten.

### UI- / Routen-Referenz

- `/admin` (`dashboard.html`)

---

## UC-06: Bugs und Feature-Wünsche melden


|               |                                                                      |
| ------------- | -------------------------------------------------------------------- |
| **Priorität** | B                                                                    |
| **Akteur**    | Produzent                                                            |
| **Ziel**      | Feedback strukturiert erfassen, ohne sofort GitHub öffnen zu müssen. |


### Hauptszenario

1. Akteur öffnet `**/admin/tickets/new`**.
2. Füllt Formular (Titel, Beschreibung, ggf. Typ).
3. Sendet ab; Ticket wird gespeichert (Roadmap: optional GitHub-Issue).

### Akzeptanzkriterien

- Validierung und Erfolgs-/Fehlermeldung verständlich; keine stillen Fehler.

### UI- / Routen-Referenz

- `/admin/tickets/new`, Tickets-Liste falls vorhanden

---

## UC-07: Pipeline-Queue überwachen


|               |                                                |
| ------------- | ---------------------------------------------- |
| **Priorität** | B                                              |
| **Akteur**    | Produzent                                      |
| **Ziel**      | Wissen, ob und was gerade rendert oder wartet. |


### Hauptszenario

1. Akteur öffnet `**/admin/pipeline`** oder Pipeline-Logs.
2. Liest Queue-/Statusanzeige (running, waiting, Fehler).

### Akzeptanzkriterien

- Konsistente Begriffe mit Run-Detailseiten; bei Stau erkennbare Ursache oder nächster Schritt.

### UI- / Routen-Referenz

- `/admin/pipeline`, `/admin/pipeline/logs`

---

## UC-08: Shorts erstellen


|               |                                                |
| ------------- | ---------------------------------------------- |
| **Priorität** | C                                              |
| **Akteur**    | Produzent                                      |
| **Ziel**      | Kurzformate aus vorhandenem Material erzeugen. |


### Vorbedingungen

- Feature gemäß Produktstand (Seite kann existieren, Funktionalität teils in Entwicklung).

### Hauptszenario (Soll)

1. Akteur öffnet `**/admin/shorts`**.
2. Wählt Quellmaterial und Schnittparameter.
3. Erzeugt Short; prüft Vorschau; veröffentlicht oder übergibt an Upload-Flow.

### Akzeptanzkriterien (Zielbild)

- Parallele Nutzung ohne Longform-Pipeline zu blockieren; klare Trennung der Outputs.

### UI- / Routen-Referenz

- `/admin/shorts`

---

## UC-09: Dokumentation lesen


|               |                                         |
| ------------- | --------------------------------------- |
| **Priorität** | C (Onboarding relevant)                 |
| **Akteur**    | Produzent, neues Teammitglied           |
| **Ziel**      | Selbsthilfe bei Bedienung und Abläufen. |


### Hauptszenario

1. Akteur öffnet `**/admin/docs`**.
2. Navigiert Themen → liest Seiten; optional Suche nutzen.

### Akzeptanzkriterien

- Verlinkung aus Dashboard; aktuelle Pfade und Begriffe (z. B. Varianten-Presets) in Doku nachziehen, wenn sich der Flow ändert.

### UI- / Routen-Referenz

- `/admin/docs`

---

## Querschnitt: Preset-Daten (`house_templates.json`)

Für **UC-01** und Teile von **UC-02** relevant:


| Konzept  | JSON-Felder (typisch)                                                                                      |
| -------- | ---------------------------------------------------------------------------------------------------------- |
| Haus     | Top-Level-Key (`stark`, …), `display_name`, `title_template`, `defaults`, `music_brief`, `thumbnail_brief` |
| Variante | `variants`, `variant_prompts`, `background_prompts` (`bg_key`, `prompt`, optional `thumbnail_brief`)       |


**Wichtig:** Audio-Prompts existieren **nur** auf Varianten-Ebene (`variant_prompts`); es gibt keine separaten hausweiten `prompts`-Listen mehr.

---

## Abgleich mit Produktregeln (Anti-Patterns)

Aus `[USER_STORIES.md](USER_STORIES.md)` – weiterhin gültig als nicht-funktionale Anforderungen:

- Kein unnötiges Springen zwischen vielen Seiten für den Standard-Video-Flow.
- Keine rein technischen Fehlermeldungen ohne Kontext.
- Keine toten UI-Elemente.
- Automatisierung wo sinnvoll (Presets, Slug aus Titel, Hintergrund aus Variante).

---

## Änderungshistorie (Dokument)


| Datum      | Änderung                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------- |
| 27.03.2026 | Erstversion als Detaildokument; UC-01/UC-02 an aktuellen Create-Flow und JSON-Struktur angepasst. |


