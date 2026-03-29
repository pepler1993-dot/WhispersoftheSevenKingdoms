
# AGENT_FEEDBACK_2026-03-28

## Zweck
Diese Datei ist direkt an die drei OpenClaw-Agents gerichtet. Sie soll den aktuellen Stand einordnen, die größten Risiken benennen und eine klare Richtung für die nächste Ausbaustufe vorgeben.

## Ausgangslage
Das aktuelle Repo ist bereits deutlich mehr als ein Skriptset. Es ist heute ein vertikales Produktionssystem für einen sehr klaren Use Case:

**GoT-/Sleep-Music-Workflow**
Haus wählen → Audio generieren → Thumbnail → Video → Metadaten → YouTube / Shorts

Das ist gut. Genau diese Vertikalität hat es erlaubt, schnell echten Nutzen zu bauen.
Aber: Diese Vertikalität wird jetzt zur Grenze, wenn das System Schritt für Schritt zu einem universellen Content-SaaS wachsen soll.

## Was bereits stark ist
1. **Echter Produktkern vorhanden**
   - Dashboard statt nur CLI
   - persistente Workflows
   - Audio-Jobs
   - Tickets
   - Nutzer / Spaces / Settings
   - Deployment-Workflow

2. **Gute operative Denkweise**
   - Logs, Status, Recovery
   - Tickets im Dashboard als Arbeitssteuerung
   - Deployment ist bereits automatisiert
   - Doku wird aktiv gepflegt

3. **Richtiger erster Expansionsschritt wurde begonnen**
   - Shorts sind bereits als eigener Workflow gedacht
   - damit wurde die erste Format-Erweiterung vorbereitet

## Was aktuell noch nicht professionell genug für ein echtes SaaS ist
### 1. Domänenmodell noch zu spezialisiert
Der Kern ist noch zu stark auf folgende Objekte zugeschnitten:
- Song
- Slug
- Thumbnail
- Video
- YouTube
- stable-audio-local

Das ist für den aktuellen Use Case okay, aber kein tragfähiges Endmodell.

### 2. Zu viel Logik hängt am lokalen Dateisystem
Viele Annahmen sind direkt in Ordnern und Pfaden codiert:
- `data/upload/...`
- `data/output/youtube/...`
- `data/work/jobs/...`

Für ein SaaS muss das langfristig ersetzt oder abstrahiert werden.

### 3. Hintergrundarbeit läuft noch zu nah am Web-Prozess
Subprocesses und Threads direkt aus FastAPI-Requests zu starten ist für ein internes Tool tolerierbar, aber nicht robust genug für skalierte Produktivsysteme.

### 4. Provider- und Plattform-Abstraktion fehlt noch
Noch gibt es kein stabiles generisches Modell für:
- mehrere KI-Provider
- mehrere Plattformen
- mehrere Content-Typen
- mehrere Brand-/Workspace-Konfigurationen

### 5. Datenhaltung und Migration sind noch Übergangslösungen
SQLite ist okay für jetzt. Runtime-Migrationen und implizite Schema-Fixes sind aber kein sauberer Langzeitpfad.

### 6. Sicherheits- und Betriebsgrenzen sind noch weich
Vor allem API-Grenzen, Secrets, Background-Jobs, Auditing und Account-Verbindungen müssen deutlich strikter werden, bevor daraus ein echtes SaaS wird.

## Nicht verhandelbare Richtungsentscheidung
**Ab jetzt keine neue Speziallogik direkt auf das alte GoT-/YouTube-/Audio-Modell stapeln.**

Neue Funktionen dürfen nur noch gebaut werden, wenn sie mindestens eine dieser beiden Regeln erfüllen:

### Regel A
Sie verbessern den aktuellen internen Produktions-Workflow direkt und stabil.

### Regel B
Sie verschieben die Architektur sichtbar in Richtung generisches Produktmodell.

Wenn eine Änderung weder A noch B erfüllt, wird sie nicht gebaut.

## Zielbild
Das System soll sich in klaren Stufen entwickeln:

### Heute
Vertikales internes Produktionssystem für Sleep-/Ambient-Content

### Mittlere Phase
Generisches internes Studio für mehrere Content-Typen und Plattformen

### Endzustand
Multi-tenant SaaS für Content-Produktion, Varianten, Publishing und Analyse

## Kernprinzipien für alle Agents
1. **Erst abstrahieren, dann expandieren**
2. **Keine UI ohne klares Backend-Modell**
3. **Keine neue Plattform ohne Adapter-Schicht**
4. **Keine neue Provider-Integration ohne Provider-Registry**
5. **Keine Produktfunktion ohne Ticket, Akzeptanzkriterien und Definition of Done**
6. **Keine stillen Architekturbrüche**
7. **Jede größere Entscheidung bekommt eine ADR**
8. **Kein „magischer“ Pfad oder Status ohne Dokumentation**
9. **Keine Secrets im Repo**
10. **Lieber weniger Features mit sauberem Modell als viele Sonderfälle**

## Konkretes Feedback pro Agent-Rolle

### Smith – Architektur / Backend / Infra / Reviews
Fokus:
- Domänenmodell generalisieren
- Job-System härten
- Plattform- und Provider-Abstraktion definieren
- Persistenz und Migrationspfad professionalisieren
- Sicherheitsgrenzen enger ziehen

Erwartung:
- Du bist Hauptverantwortlicher für den Architektur-Schnitt
- Keine weiteren großen Features ohne technisches Zielbild
- Du reviewst alles, was Domain-, DB-, Worker- oder Deploy-Logik berührt

Nicht tun:
- Noch mehr Spezialstatus oder Spezialtabellen auf das alte Modell patchen
- Plattformlogik direkt in UI-Routen verteilen
- neue Runtime-Migrationen improvisieren, wenn ein formaler Migrationspfad nötig ist

### Pako – Produktlogik / UX / Bedienfluss
Fokus:
- Workflow vereinfachen
- Studio-Denke statt Einzeltool-Denke
- generische Create-Flows vorbereiten
- Brand-/Preset-/Variant-UX sauber strukturieren

Erwartung:
- Die UI darf nicht mehr nur „Whispers Dashboard“ denken
- Jede neue Seite soll so entworfen werden, dass später weitere Content-Typen und Plattformen passen
- Weniger Spezialformulare, mehr modulare Flows

Nicht tun:
- UI direkt an rohe DB-/Dateisystemannahmen koppeln
- plattformspezifische Optionen ungeordnet in globale Formulare kippen
- visuelle Politur vor Modellklarheit priorisieren

### Jarvis – Doku / QA / Planung / Review-Unterstützung
Fokus:
- Doku als Betriebs- und Onboarding-System
- ADRs, Runbooks, Migrationspläne, Release-Notizen
- Testpläne und Akzeptanzkriterien
- Konsistenz-Checks zwischen Zielbild, Roadmap und implementiertem Code

Erwartung:
- Jede Phase braucht klare „Done“-Kriterien
- Architekturänderungen müssen schriftlich nachvollziehbar sein
- Doku ist nicht Schmuck, sondern Steuerungssystem

Nicht tun:
- Altdoku mit neuer Terminologie vermischen
- Features als „fertig“ dokumentieren, wenn kein Test- oder Abnahmestand vorliegt

## Sofortige Leitplanken
Diese Punkte gelten ab sofort:

### Architektur
- Neue Plattformlogik nur in Adapter-Schichten
- Neue KI-Provider nur über Registry/Provider-Interface
- Neue Content-Typen nur über generisches Content-Modell
- keine weitere Core-Logik direkt an `slug`-Ordnerstrukturen hängen

### Prozess
- Jede größere Änderung hat Ticket + Branch + PR + Review
- Commits klein und rückbaubar halten
- PRs müssen fachlich begrenzt sein
- jede Architekturentscheidung > 1 Tag Aufwand bekommt ADR

### Qualität
- Für neue Kernmodule immer:
  - minimaler Test
  - Logging
  - Fehlerpfad
  - Doku-Update
  - Migrationshinweis falls nötig

### Sicherheit
- API-Zugriffe härten
- Secrets nur via Env / Secret Store
- verbundene Konten später verschlüsselt speichern
- Rollen- und Rechtekonzept nicht weiter aufschieben

## Prioritätenreihenfolge
1. **Aktuellen internen Workflow stabil halten**
2. **Architektur für generisches Produktmodell vorbereiten**
3. **YouTube-Use-Case in saubere Adapter-/Job-/Asset-Struktur überführen**
4. **Erst danach weitere Plattformen und Provider**
5. **SaaS-Härtung erst nach Architektur-Schnitt**

## Definition von Erfolg in den nächsten Wochen
Erfolg ist **nicht**, möglichst viele neue Buttons zu bauen.

Erfolg ist:
- das aktuelle System bleibt benutzbar
- die Kernobjekte werden sauberer
- der Weg zu mehreren Plattformen wird technisch klar
- Provider und Publishing werden abstrahierbar
- die Codebasis wird weniger speziell, nicht spezieller

## Klare Anweisung
Ab jetzt wird das Projekt in **zwei Ebenen** gedacht:

### Ebene 1 – Current Product
Interner Produktions-Workflow für eure aktuellen Videos

### Ebene 2 – Product Core
Die generische Plattform, aus der später das SaaS entsteht

Jeder Task muss explizit sagen, ob er Ebene 1 oder Ebene 2 verbessert.

Wenn nicht klar ist, zu welcher Ebene der Task gehört, ist der Task noch nicht sauber genug definiert.
