# Regression Checklist

**Owner:** Jarvis  
**Stand:** 2026-03-29  
**Phase:** Stabilitäts-/Bug-Welle

---

## Zweck

Diese Checkliste definiert den minimalen Regression- und Freigabeumfang für den aktuellen Stable-Stand.
Sie ist absichtlich knapp und auf die echten Hauptpfade fokussiert.

---

## 1. Dashboard

- [ ] `/admin` lädt ohne sichtbaren Server-/Template-Fehler
- [ ] primäre Inhalte sind sichtbar und verständlich priorisiert
- [ ] Needs Attention / aktive Runs / aktuelle Workflows sind erreichbar
- [ ] Health-/GPU-Infos sind vorhanden, aber blockieren die Hauptnutzung nicht

## 2. Create-Flow Video

- [ ] Haus-Auswahl funktioniert
- [ ] Varianten-Auswahl funktioniert
- [ ] Titel wird nach Variantenwahl korrekt erzeugt
- [ ] Stimmung / Preset / Defaults werden sauber vorausgefüllt
- [ ] Hintergrund-/Asset-Vorwahl verhält sich plausibel
- [ ] Create POST startet ohne offensichtlichen Contract-Fehler

## 3. Shorts Create

- [ ] `/admin/shorts` lädt
- [ ] Preset-Auswahl befüllt sichtbare Felder vollständig
- [ ] Stimmung bleibt nach Preset-Wahl nicht leer
- [ ] keine offensichtlichen JS-/Console-Fehler im Kernfluss

## 4. Workflow / Status / Progress

- [ ] Workflow-Detailseiten laden
- [ ] Progress-/Status-Anzeige wirkt konsistent
- [ ] keine offensichtlichen Widersprüche zwischen Status, Phase und UI-Anzeige
- [ ] laufende / fehlgeschlagene / fertige Zustände sind unterscheidbar

## 5. Audio / Library / Generation

- [ ] Audio-Library-Auswahl verhält sich nachvollziehbar
- [ ] Audio-Generation startet ohne offensichtlichen UI-/Route-Bruch
- [ ] bekannte Defaults sind konsistent zwischen UI und Backend

## 6. Upload / Publish

- [ ] Upload-Startpfad ist technisch intakt
- [ ] OAuth-/Token-Fehler sind klar diagnostizierbar und nicht irreführend
- [ ] Publish-/Upload-Status wird nachvollziehbar angezeigt

## 7. Smoke / Basis-Checks

- [ ] `GET /healthz` liefert Erfolg
- [ ] `GET /api/health/overview` liefert plausiblen JSON-Status
- [ ] Zugriff auf `/admin` funktioniert
- [ ] Default-DB-Pfad bleibt konsistent (`data/agent_sync.db`)
- [ ] keine offensichtlichen Tracebacks im Hauptpfad

---

## Freigabe für Stable-Stand

Stable ist nur vorbereitbar, wenn:
- [ ] keine offenen P0-Bugs mehr existieren
- [ ] alle betroffenen P1-Bugs geprüft wurden
- [ ] Hauptpfad Dashboard → Create → Workflow → Upload nicht offensichtlich bricht
- [ ] Smoke-Checks grün sind
