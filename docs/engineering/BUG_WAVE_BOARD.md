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
- **Offene P1:** 3 (`#156`, `#157`, `#158`)
- **Offene P2:** 1 (`#159`)
- **Stable-Gate:** noch **nicht** freigabefähig, weil offene P1-Bugs und Regression noch nicht als gelaufen dokumentiert sind

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
- **P1:** noch offen (`#156`, `#157`, `#158`)
- **P2:** offen, aber nicht automatisch blockierend (`#159`)
- **Regression:** noch nicht als komplett gelaufen dokumentiert

### Aktuelle Aussage
**Noch kein Stable-Freigabe-Stand.**

Blocker im Moment:
1. offene P1-Bugs im sichtbaren Hauptprodukt
2. keine abgeschlossene Regression-Dokumentation für Dashboard / Create / Shorts / Workflow / Upload
