# Risk Register

**Owner:** Jarvis  
**Reviewer:** Smith  
**Stand:** 2026-03-29  
**Welle:** A04

---

## Zweck

Dieses Register priorisiert die aktuell wichtigsten technischen, operativen und sicherheitsrelevanten Risiken des Projekts.
Es dient als gemeinsame Entscheidungsgrundlage vor Gate **A → B**.

---

## Bewertungslogik

### Wahrscheinlichkeit
- **Hoch** = wahrscheinlich oder bereits mehrfach sichtbar
- **Mittel** = realistisch, aber nicht dauerhaft akut
- **Niedrig** = derzeit unwahrscheinlich, aber relevant

### Impact
- **Hoch** = blockiert Kernworkflow, verursacht Daten-/Betriebsrisiko oder Sicherheitsvorfall
- **Mittel** = deutliche Reibung, Mehrarbeit oder Qualitätsverlust
- **Niedrig** = begrenzter Schaden, lokal eingrenzbar

### Priorität
- **P0** = akut / Gate-relevant / sollte sehr früh adressiert werden
- **P1** = wichtig, zeitnah beheben
- **P2** = relevant, aber nachgelagert

---

## Priorisierte Risiken

| ID | Priorität | Kategorie | Risiko | Wahrscheinlichkeit | Impact | Mitigation / Nächster Schritt |
|---|---|---|---|---|---|---|
| R01 | P0 | Security / Operations | **OAuth- und API-Secrets liegen als Dateien auf Servern oder im Arbeitsverzeichnis.** YouTube-OAuth-Dateien (`client_secret.json`, `.youtube_token.json`) und andere Tokens sind dateibasiert und potenziell falsch verteilt, kopiert oder nicht rotiert. | Hoch | Hoch | Secrets-Inventar anlegen, Speicherorte dokumentieren, Dateirechte härten, Rotation-Runbook schreiben, langfristig Secret-Store / klaren Deployment-Pfad definieren. |
| R02 | P0 | Operations | **YouTube-Upload hängt an fragilem lokalem OAuth-Setup.** Refresh-Token kann widerrufen, mit falschem Client erzeugt oder auf falschem Host liegen; Auto- und Manual-Upload fallen dann gleichzeitig aus. | Hoch | Hoch | Upload-Auth-Runbook dokumentieren, einen stabilen OAuth-Client fest definieren, Token-Erneuerung standardisieren, Preflight-Check vor Upload ergänzen. |
| R03 | P0 | Architecture / Runtime | **Subprocess-/Langläufer-Logik hängt direkt am Web-/Sync-Prozess.** Audio, Upload, Pipeline und Polling werden teils direkt aus dem Dashboard-Kontext angestoßen; das erhöht Kopplung, Fehlersensitivität und Recovery-Aufwand. | Mittel | Hoch | Klare Trennung zwischen Web-App, Job-Orchestrierung und Worker-Verantwortung definieren; langfristig Queue-/Worker-Grenzen härten; kurzfristig Vertrags- und Fehlerpfade dokumentieren. |
| R04 | P0 | Infrastructure | **GPU-Worker ist kein stabiler Always-on-Baustein.** VM 104 läuft nur bei Bedarf, RAM ist knapp, und der Kernpfad Audio hängt an einer einzelnen Maschine mit manuellem Betriebsmodus. | Hoch | Hoch | Betriebszustände explizit im UI anzeigen, Start-/Stop-Runbook pflegen, RAM-Upgrade priorisieren, Fallback-Verhalten transparent machen. |
| R05 | P1 | Reliability | **Dateisystem ist zentrale Integrationsschicht.** Songs, Jobs, Output, Metadaten und Tokens hängen stark an Dateinamen, Pfaden und impliziten Konventionen statt an stabilen Objekten/Verträgen. | Hoch | Hoch | Kritische Pfad- und Dateinamenskonventionen dokumentieren, Validierungschecks ausbauen, mittelfristig Asset-/Job-Modell mit klaren IDs definieren. |
| R06 | P1 | Product / Consistency | **Defaults und Preset-Logik driften zwischen Audio Lab, Create-Flow und Backend auseinander.** UI zeigt andere Werte oder Felder als tatsächlich im Backend verwendet werden. | Hoch | Mittel | Single Source of Defaults definieren, serverseitige Validierung und Mapping vereinheitlichen, UI-Regressionen gezielt testen. |
| R07 | P1 | Reliability / UX | **Template-/Frontend-Logik ist fehleranfällig durch verteilte Inline-Skripte und implizite Zustände.** Doppelte Skripte, fehlende Funktionen oder uneinheitliche Feldnamen können Kernflows still brechen. | Mittel | Hoch | Kritische Templates entdoppeln, JS-Helfer konsolidieren, Smoke-Tests für Dashboard/Create-Flow fest einführen. |
| R08 | P1 | Security | **Aktuell fehlt ein klar gehärtetes Auth-/Session-Modell fürs Dashboard.** Interne Admin-Flows und Betriebsfunktionen sind wertvoll, aber Schutzmechanismen sind laut Status/Backlog noch nicht vollständig etabliert. | Mittel | Hoch | Session-/Cookie-basierten Login priorisieren, Bedrohungsmodell für Dashboard formulieren, Exponierung und Reverse-Proxy-Konfiguration prüfen. |
| R09 | P1 | Single Dependency | **Starke Anbieter- und Tool-Abhängigkeit.** YouTube API, Google OAuth, Stable Audio Open, ffmpeg und die lokale GPU-Umgebung sind harte Abhängigkeiten ohne austauschbare Provider-Schicht. | Mittel | Mittel | Abhängigkeiten explizit dokumentieren, Failure Modes je Provider festhalten, mittelfristig Adapter-/Provider-Grenzen definieren. |
| R10 | P1 | Observability | **Fehlerdiagnose ist stark logbasiert und personenabhängig.** Viele Probleme lassen sich nur über Chat-Kontext, Terminal-Ausgaben oder manuelle Repo-Inspektion nachvollziehen. | Hoch | Mittel | Standardisierte Preflight-/Health-Checks und Runbooks ergänzen, Fehlerklassen dokumentieren, zentrale Troubleshooting-Seite pflegen. |
| R11 | P2 | Deployment | **Deployment-Prozess ist personengebunden und teilweise manuell.** Deploy-Verantwortung ist klar benannt, aber Auth, Pull, Restart und Verify sind nicht vollständig idiotensicher automatisiert. | Mittel | Mittel | Deploy-Runbook schärfen, Auth-Pfade stabilisieren, Verify-Checklist und Rollback-Schritte standardisieren. |
| R12 | P2 | Data Integrity | **Metadaten-, Asset- und Upload-Vollständigkeit wird nicht überall hart geprüft.** Fehlende Dateien oder unvollständige Outputs können erst spät im Flow auffallen. | Mittel | Mittel | Preflight-Validierung vor Render/Upload ausbauen, Pflichtartefakte je Workflow explizit prüfen, Fehlermeldungen nutzerorientiert machen. |

---

## Detailbewertung

### R01 – Secrets in Dateien / verteilte Secret-Ablage
**Beschreibung**  
Das Projekt nutzt mehrere file-basierte Secrets und Tokens. Ohne klaren Standard für Speicherort, Rechte, Rotation und Verantwortlichkeit steigt das Risiko von Leaks, Fehlkonfigurationen und schwer nachvollziehbaren Ausfällen.

**Warum kritisch**  
Ein Secret- oder Tokenproblem trifft direkt Upload, Deploy oder externe Integrationen.

**Mitigation**  
- Secret-Inventar anlegen
- erlaubte Speicherorte definieren
- Dateirechte prüfen
- Rotation dokumentieren
- keine Secrets ins Repo

### R02 – Fragiles YouTube-OAuth
**Beschreibung**  
Upload hängt an einem lokal erzeugten OAuth-Token, der zum richtigen Client passen muss. Falsche oder widerrufene Tokens führen zu sofortigem Ausfall beider Upload-Wege.

**Warum kritisch**  
Auto-Upload und manueller Upload fallen gemeinsam aus.

**Mitigation**  
- ein autoritativer OAuth-Client
- dokumentierter `--setup`-Prozess
- Upload-Preflight auf Tokenformat und Refresh-Fähigkeit
- klare Ownership für Re-Auth

### R03 – Kopplung von Webprozess und Langläufern
**Beschreibung**  
Wenn Web-App und Job-Ausführung nicht sauber getrennt sind, entstehen fragile Fehlerpfade, Race Conditions und schwer testbare Betriebszustände.

**Warum kritisch**  
Kernflows hängen an mehreren impliziten Seiteneffekten statt an klaren Grenzen.

**Mitigation**  
- Zuständigkeiten Web / Runner / Worker sauber dokumentieren
- Verträge für Start, Status, Fehler und Artefakte definieren
- mittelfristig stärkere Entkopplung über Queue-/Worker-Modell

### R04 – Einzelne GPU-VM als Engpass
**Beschreibung**  
Die Audio-Generation hängt an einer einzelnen VM mit knapper RAM-Situation und nicht-persistentem Betriebsmodus.

**Warum kritisch**  
Der Hauptwert des Produkts ist die Audio-Pipeline; wenn diese Maschine nicht verfügbar ist, fällt ein Kernpfad aus.

**Mitigation**  
- Betriebsstatus prominent anzeigen
- Start-/Stop-/Recovery-Prozess dokumentieren
- RAM-Upgrade priorisieren
- Fallbacks ehrlich markieren

### R05 – Dateisystem als implizite API
**Beschreibung**  
Pfade, Slugs und Dateinamen transportieren fachliche Bedeutung. Schon kleine Inkonsistenzen können zu „Datei nicht gefunden“, falschen Assets oder stillen Zuordnungsfehlern führen.

**Mitigation**  
- Pfad- und Naming-Konventionen dokumentieren
- Validierung zentralisieren
- langfristig Asset-/Workflow-Objekte mit stabilen IDs einführen

### R06 – Default-Drift zwischen UI und Backend
**Beschreibung**  
Mehrere Oberflächen und Backend-Routen nutzen dieselben Parameter, aber nicht immer dieselbe Quelle oder denselben Vertrag.

**Mitigation**  
- eine kanonische Default-Definition
- serverseitige Normalisierung
- Regressionstests für Audio Lab + Create-Flow

### R07 – Fragile Template- und JS-Logik
**Beschreibung**  
Inline-Skripte, deduplizierte Logik und implizite DOM-Abhängigkeiten erhöhen das Risiko von Frontend-Defekten im Hauptworkflow.

**Mitigation**  
- Helper-Funktionen konsolidieren
- kritische Templates bereinigen
- Browser-Smoke-Tests für Kernseiten etablieren

### R08 – Unvollständige Dashboard-Härtung
**Beschreibung**  
Das Dashboard bündelt Betriebs- und Admin-Funktionen. Ohne klar gehärtete Authentifizierung, Session-Handling und Exponierungskontrolle ist das Sicherheitsrisiko überproportional hoch.

**Mitigation**  
- Admin-Login priorisieren
- Reverse-Proxy/Exposure prüfen
- Auth-/Session-Entscheidung dokumentieren

### R09 – Harte externe Abhängigkeiten
**Beschreibung**  
Mehrere Kernfähigkeiten hängen an externen APIs oder spezifischer lokaler Runtime. Ausfälle oder Vertragsänderungen wirken direkt auf das Produkt.

**Mitigation**  
- Dependency-Register pflegen
- Failure Modes dokumentieren
- mittelfristig Provider-Abstraktionen definieren

### R10 – Geringe Standardisierung der Fehlersuche
**Beschreibung**  
Troubleshooting läuft derzeit stark über Chat, Ad-hoc-Kommandos und individuelles Wissen.

**Mitigation**  
- Preflight-/Health-Checks standardisieren
- Troubleshooting-Guides ergänzen
- bekannte Fehlerbilder dokumentieren

### R11 – Personengebundener Deploy
**Beschreibung**  
Auch wenn Verantwortlichkeiten klar sind, hängt der reale Deploy stark an Wissen einzelner Personen und funktionierender lokaler Auth.

**Mitigation**  
- Deploy-Runbook und Verify-Schritte schärfen
- Auth-Pfade vereinheitlichen
- Rollback explizit dokumentieren

### R12 – Späte Validierung unvollständiger Artefakte
**Beschreibung**  
Manche Vollständigkeitsfehler werden erst spät sichtbar, etwa beim Upload oder Rendern.

**Mitigation**  
- Preflight vor jedem teuren Schritt
- Pflichtartefakte explizit prüfen
- verständliche Fehlermeldungen erzeugen

---

## Empfohlene Sofortmaßnahmen

1. **Secrets- und OAuth-Härtung zuerst** (`R01`, `R02`)  
   Ohne stabile Auth sind Upload und externe Integrationen nicht zuverlässig.

2. **GPU-/Betriebsstabilität absichern** (`R04`)  
   Hauptpfad der Audio-Erzeugung operativ absichern, bevor weitere Feature-Flächen wachsen.

3. **Verträge und Defaults konsolidieren** (`R05`, `R06`, `R07`)  
   Verhindert, dass UI und Backend weiter auseinanderlaufen.

4. **Dashboard-Zugriff und Deploy-Wissen härten** (`R08`, `R11`)  
   Reduziert Sicherheits- und Bus-Faktor-Risiken.

---

## Nicht-Ziel dieser Datei

Dieses Register ersetzt keine ADRs, keine konkrete Migrationsplanung und kein Incident-Runbook.  
Es ist eine priorisierte Risikosicht, aus der Folgearbeiten und Schutzmaßnahmen abgeleitet werden sollen.
