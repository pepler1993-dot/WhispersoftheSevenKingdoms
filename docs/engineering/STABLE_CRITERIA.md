# Stable Criteria

**Owner:** Jarvis  
**Stand:** 2026-03-29  
**Phase:** Stabilitäts-/Bug-Welle

---

## Zweck

Dieses Dokument definiert die formalen Kriterien für einen **Stable-Stand** des aktuellen Produkts.

Es ist bewusst kein Zukunftsplan und kein Architekturpapier, sondern ein knapper Freigaberahmen für die laufende Bug-/Stabilitätswelle.

---

## Grundsatz

**Stable** bedeutet hier nicht „perfekt", sondern:
- der aktuelle Hauptpfad ist benutzbar
- keine bekannten P0-Blocker sind offen
- relevante P1-Probleme sind entweder behoben oder bewusst als nicht-blockierend bewertet
- Verifikation und Regression sind dokumentiert

---

## Stable-Gate

Ein Stable-Stand darf erst vorbereitet oder freigegeben werden, wenn alle folgenden Punkte erfüllt sind.

### 1. Bug-Status
- [ ] keine offenen **P0**-Bugs
- [ ] relevante **P1**-Bugs sind behoben oder explizit als nicht-blockierend akzeptiert
- [ ] Bugs werden nur geschlossen, wenn **Reproduktion, Ursache, Fix und Verifikation** dokumentiert sind

### 2. Hauptpfad
- [ ] Dashboard ist benutzbar
- [ ] Create-Flow ist benutzbar
- [ ] Workflow-/Status-/Progress-Pfad ist benutzbar
- [ ] Upload-/Publish-Pfad funktioniert technisch nachvollziehbar

### 3. Regression
- [ ] `docs/engineering/REGRESSION_CHECKLIST.md` ist gegen den realen Stand durchgegangen
- [ ] Regression deckt mindestens ab:
  - Dashboard
  - Create-Flow Video
  - Shorts Create
  - Workflow / Status / Progress
  - Audio / Library / Generation
  - Upload / Publish

### 4. Smoke / Basis-Checks
- [ ] `GET /healthz` liefert Erfolg
- [ ] `GET /api/health/overview` liefert plausiblen JSON-Status
- [ ] Zugriff auf `/admin` funktioniert
- [ ] Default-DB-Pfad bleibt konsistent (`data/agent_sync.db`)
- [ ] keine offensichtlichen Tracebacks im Hauptpfad

### 5. Dokumentation / Gate
- [ ] `docs/engineering/BUG_WAVE_BOARD.md` ist aktuell
- [ ] `docs/engineering/REGRESSION_CHECKLIST.md` ist aktuell
- [ ] Stable-Blocker sind klar benannt oder ausgeräumt
- [ ] Stable-Freigabe ist als bewusste Entscheidung nachvollziehbar

---

## Aktuelle bekannte Blocker-Klassen

Solange offen oder unklar, blockieren diese Themen typischerweise einen Stable-Stand:

- offener Hauptpfad-Bug im Dashboard
- offener Create-/Preset-/Library-Fehler
- unklarer finaler Workflow-/Upload-Endstatus
- unvollständiges Cancel-Verhalten in Hauptzuständen
- stille Fallbacks statt klarer Fehlermeldung
- fehlende Regression-/Smoke-Dokumentation
- nicht abgeschlossene echte Browser-/Screen-Verifikation auf dem Zielsystem

---

## Letzter offener Umsetzungsblock vor Endabnahme

Der letzte ausdrücklich freigegebene Umsetzungsblock vor dem finalen manuellen Test ist:
- **Thumbnail-Library im Create-Flow fertig bauen und korrekt durchreichen**

Danach gilt:
- kein neuer Scope
- keine neuen Extras
- kein weiterer Umbau
- anschließende manuelle End-to-End-Prüfung durch Eddi

## Live-Smoke-Stand 2026-03-29

Externe Live-Checks gegen `dashboard.ka189.de` bestätigen aktuell:
- `/healthz` antwortet mit `200` und `{ "status": "ok" }`
- `/api/health/overview` antwortet mit plausiblem JSON-Status
- `/admin` ist erreichbar und leitet sauber auf `/login` weiter

Diese Live-Checks ersetzen **nicht** die vollständige Regression oder echte Browser-Endabnahme, sind aber ein belastbarer Teil des Stable-Gates.

## Nicht-Ziel

Dieses Dokument bewertet keine Welle-C-Themen, keine neuen Features und keine Architektur-Expansion.  
Es dient ausschließlich dazu, den **aktuellen Produktstand sauber als stabil oder noch nicht stabil** zu bewerten.
