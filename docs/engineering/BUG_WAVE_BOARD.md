# Bug Wave Board

**Owner:** Jarvis  
**Stand:** 2026-03-29  
**Phase:** Stabilitäts-/Bug-Welle

---

## Zweck

Dieses Board ist die knappe Arbeitsübersicht für die laufende Bug-Welle.

Regeln für diese Welle:
- nur Bugfixes
- keine neuen Features
- keine großen Refactors
- keine parallelen Sonderlösungen
- jeder Bug braucht: **Reproduktion, Ursache, Fix, Verifikation**

---

## Priorisierung

### P0
Blockiert Hauptpfad oder macht das Produkt akut unbenutzbar.

Typische Fälle:
- Dashboard nicht benutzbar
- Create-Flow startet nicht oder sendet kaputte Daten
- Workflow-/Progress-/Status-Pfad bricht
- Upload-/Publish-Pfad funktioniert nicht

### P1
Deutlich spürbarer Fehler im Hauptprodukt, aber kein kompletter Totalausfall.

Typische Fälle:
- unvollständige Vorbelegung
- falsche Titel-/Preset-Logik
- UI priorisiert falsche Informationen
- Seiten sind benutzbar, aber fehlerhaft oder irreführend

### P2
Nicht blockierend, aber sollte für einen sauberen Stable-Stand bereinigt werden.

Typische Fälle:
- Informationsarchitektur / Platzierung
- kleinere UX-/Klarheitsmängel
- sekundäre Bereiche

---

## Aktueller Board-Stand

### Status-Snapshot
- **Offene P0:** 0
- **Offene P1:** 7 (`#156`, `#157`, `#158` + neue P1-Stabilitätspunkte aus Review)
- **Offene P2:** 1 (`#159`)
- **Stable-Gate:** noch **nicht** freigabefähig, weil offene P1-Bugs und Regression noch nicht als gelaufen dokumentiert sind
- **Stable-Criteria:** siehe `docs/engineering/STABLE_CRITERIA.md`

### P0
Aktuell keine offen bestätigten P0-Issues im neuen Bug-Set.

### P1

#### #156 – Dashboard: GPU/Health-Bereich dominiert visuell die Studio-Overview
- **Bereich:** Dashboard / `/admin`
- **Reproduktion:** Studio Home öffnen und Sichtgewicht der Blöcke prüfen
- **Vermutete Ursache:** Ops-/Health-Infos stehen visuell zu nah an primären Produktionsinhalten
- **Fix-Richtung:** Produktionsinhalte klar vor Health/System priorisieren
- **Verifikation:** Studio Home zeigt zuerst Needs Attention / Active Runs / aktuelle Workflows; Health bleibt sekundär

#### #157 – Create-Flow: title_template enthält kein `{variant}` – Titel-Generierung unvollständig
- **Bereich:** Create-Flow Video
- **Reproduktion:** Haus wählen → Variante wählen → automatisch generierten Titel prüfen
- **Vermutete Ursache:** `buildTitleFromPreset()` behandelt fehlendes `{variant}` uneinheitlich
- **Fix-Richtung:** Titelbildung robust machen, ohne doppelte oder fehlende Variant-Namen
- **Verifikation:** Titel ist nach Variantenwahl konsistent und vollständig

#### #158 – Shorts Create Tab: fehlende Stimmung / Presets nicht vollständig befüllt
- **Bereich:** Shorts Create
- **Reproduktion:** `/admin/shorts` → Neuer Short → Preset wählen → abhängige Felder prüfen
- **Vermutete Ursache:** Preset-Auswahl befüllt abhängige Zustände/Felder nicht vollständig
- **Fix-Richtung:** Preset-Verhalten an den stabilen Haupt-Create-Flow angleichen
- **Verifikation:** sichtbare Felder werden konsistent vorausgefüllt, keine leeren Mood-/Preset-Felder

#### P1-A – Auto-Upload-Endstatus nicht sauber finalisiert
- **Owner:** Smith
- **Bereich:** Backend / Orchestrator / Upload
- **Reproduktion:** Create → Render → Auto-Upload → finalen Workflow-Status prüfen
- **Vermutete Ursache:** Upload landet auf `uploaded`, aber Abschluss zu `completed` / `phase=done` wird nicht zuverlässig bis zum Ende nachgezogen
- **Fix-Richtung:** Endstatus im Queue-/Orchestrator-Pfad sauber finalisieren
- **Verifikation:** erfolgreicher Auto-Upload endet sichtbar konsistent im finalen Abschlusszustand

#### P1-B – Cancel unvollständig für Zwischenzustände
- **Owner:** Smith + Pako (manuelle Repros)
- **Bereich:** Backend / Workflow-Steuerung / UI-Verhalten
- **Reproduktion:** Cancel für `queued`, `waiting_for_audio`, `running`, `uploading` testen
- **Vermutete Ursache:** Cancel behandelt aktuell nur Teilmengen der Runtime-Zustände zuverlässig
- **Fix-Richtung:** Cancel-Verhalten für alle relevanten Hauptpfad-Zustände vereinheitlichen
- **Verifikation:** Cancel stoppt sichtbar und konsistent in allen vier Zuständen ohne hängenden Mischzustand

#### P1-C – Library-Modus hat möglicherweise stillen Fallback
- **Owner:** Smith + Pako (UI-/Flow-Verifikation)
- **Bereich:** Create-Flow / Audio-Library / Contract
- **Reproduktion:** `audio_source=library` ohne explizit gewählten Track testen
- **Vermutete Ursache:** alter slug-basierter Fallback greift still statt harter eindeutiger Auswahl
- **Fix-Richtung:** Verhalten hart machen; ohne Auswahl kein versteckter Fallback
- **Verifikation:** ohne expliziten Library-Track gibt es keinen stillen Ersatzpfad; UI/Fehlermeldung ist klar

#### P1-D – Upload-Asset RAM-Verhalten robust machen
- **Owner:** Smith
- **Bereich:** Upload / Publish / Robustheit
- **Reproduktion:** Upload-Asset-Pfad auf große Dateien prüfen
- **Vermutete Ursache:** Datei wird vor Größenprüfung vollständig in den Speicher gelesen
- **Fix-Richtung:** Größen-/Upload-Handling robust machen, ohne Voll-Load als Vorbedingung
- **Verifikation:** große Upload-Artefakte werden ohne unnötigen Full-Memory-Load geprüft/verarbeitet

#### P1-E – Thumbnail-Library auf Create-Seite ggf. falscher Pfad
- **Owner:** Pako
- **Bereich:** UI / Create / Asset-Library
- **Reproduktion:** Create-Seite öffnen und Thumbnail-Library-Befüllung prüfen
- **Vermutete Ursache:** Pfad in `admin_pipeline_new()` zeigt evtl. nicht auf den echten Thumbnail-Output-Ordner
- **Fix-Richtung:** Pfad und Library-Befüllung an realen Output-Stand angleichen
- **Verifikation:** Library listet die erwarteten Thumbnail-Assets korrekt

### P2

#### #159 – Version/Metrics auf `/admin/system` gehört in Ops-Bereich
- **Bereich:** System / Ops / IA
- **Reproduktion:** `/admin/system` und `/admin/ops` gegen gewünschte Rollenverteilung prüfen
- **Vermutete Ursache:** operative Infos liegen noch im falschen UI-Kontext
- **Fix-Richtung:** Version/Metrics in passenden Ops-Kontext verschieben oder klar als Ops blocken
- **Verifikation:** operative Informationen liegen nicht mehr irreführend im falschen Bereich

---

## Fokusbereiche dieser Welle

- Dashboard
- Create-Flow
- Audio-Library / Audio-Generation
- Workflow Progress / Status
- Upload / Publish

---

## Exit-Kriterien

Die Bug-Welle ist erst fertig, wenn:

- keine offenen P0-Bugs mehr da sind
- Dashboard benutzbar ist
- Create-Flow benutzbar ist
- Hauptpfad durchläuft
- Upload-/Publish-Pfad funktioniert
- Smoke-Checks grün sind
- ein Stable-Tag gesetzt werden kann

---

## Stable-Freigabe-Regel

Eine Freigabe für einen Stable-Stand darf nur vorbereitet werden, wenn:
- P0 = 0 offen
- P1 entweder behoben oder bewusst als nicht-blockierend akzeptiert
- Regression-Checkliste einmal sauber gegen den realen Stand gelaufen ist

## Aktuelle Stable-Bewertung

### Stand jetzt
- **P0:** frei
- **P1:** noch offen (`#156`, `#157`, `#158` + P1-A bis P1-E aus aktuellem Review)
- **P2:** offen, aber nicht automatisch blockierend (`#159`)
- **Regression:** noch nicht als komplett gelaufen dokumentiert

### Aktuelle Aussage
**Noch kein Stable-Freigabe-Stand.**

Blocker im Moment:
1. offene P1-Bugs im sichtbaren Hauptprodukt und im Hauptpfad-Backend
2. neue Review-P1s zu Auto-Upload-Endstatus, Cancel, Library-Fallback, Upload-Robustheit und Thumbnail-Library sind noch offen
3. keine abgeschlossene Regression-Dokumentation für Dashboard / Create / Shorts / Workflow / Upload
