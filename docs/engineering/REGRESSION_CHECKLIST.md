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
- [ ] Auto-Upload endet sichtbar sauber im finalen Abschlusszustand
- [ ] Cancel wurde für `queued`, `waiting_for_audio`, `running` und `uploading` geprüft

## 5. Audio / Library / Generation

- [ ] Audio-Library-Auswahl verhält sich nachvollziehbar
- [ ] bei Library-Modus ohne explizite Auswahl passiert kein stiller Fallback
- [ ] Audio-Generation startet ohne offensichtlichen UI-/Route-Bruch
- [ ] bekannte Defaults sind konsistent zwischen UI und Backend
- [ ] Thumbnail-Library auf der Create-Seite ist korrekt befüllt

## 6. Upload / Publish

- [ ] Upload-Startpfad ist technisch intakt
- [ ] OAuth-/Token-Fehler sind klar diagnostizierbar und nicht irreführend
- [ ] Publish-/Upload-Status wird nachvollziehbar angezeigt
- [ ] Upload-/Asset-Handling verhält sich robust auch bei größeren Dateien

## 7. Smoke / Basis-Checks

- [x] `GET /healthz` liefert Erfolg
- [x] `GET /api/health/overview` liefert plausiblen JSON-Status
- [x] Zugriff auf `/admin` funktioniert (live Redirect auf `/login` verifiziert)
- [ ] Default-DB-Pfad bleibt konsistent (`data/agent_sync.db`)
- [ ] keine offensichtlichen Tracebacks im Hauptpfad

### Live-Snapshot 2026-03-29
- `https://dashboard.ka189.de/healthz` → `200` / `{ "status": "ok" }`
- `https://dashboard.ka189.de/api/health/overview` → `200` / plausibler JSON-Status
- `https://dashboard.ka189.de/admin` → Redirect auf `/login` / Login-Seite erreichbar

---

## Freigabe für Stable-Stand

Stable ist nur vorbereitbar, wenn:
- [ ] keine offenen P0-Bugs mehr existieren
- [ ] alle betroffenen P1-Bugs geprüft wurden
- [ ] Hauptpfad Dashboard → Create → Workflow → Upload nicht offensichtlich bricht
- [ ] Smoke-Checks grün sind

Siehe auch: `docs/engineering/STABLE_CRITERIA.md`

## Aktueller Freigabe-Status

Stand jetzt:
- [x] keine offenen P0-Bugs bekannt
- [ ] P1-Bugs vollständig abgearbeitet
- [x] Reproduktion, Ursache, Fix und Verifikation für neue Review-P1s dokumentiert
- [ ] Hauptpfad als regressionsgeprüft dokumentiert
- [ ] Smoke-Checks grün dokumentiert

### Repo-Review-Stand
- `47a209e` adressiert `#157` plausibel
- `8eb1159` verbessert Shorts-Prefill sichtbar
- `3a4027e` stellt Audio-Status-Ziel im Create-Flow wieder her
- `0565140` blockiert Submit im Library-Modus ohne Track-Auswahl
- `86d2d84` und `e9eb661` adressieren die Backend-P1s plausibel
- `docs/engineering/P1_VERIFICATION_SMITH.md` dokumentiert die Backend-Verifikation
- `docs/engineering/UI_VERIFICATION_BUG_WAVE_2026-03-29.md` dokumentiert die UI-Verifikation

### Gate-Aussage
Trotz dokumentierter Verifikation ist der Stable-Stand **noch nicht freigegeben**, solange Regression/Smoke nicht vollständig grün dokumentiert sind und die restlichen UI-Screen-Checks nicht final durch sind.
