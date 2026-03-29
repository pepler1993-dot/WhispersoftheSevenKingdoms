
# ROADMAP_UNIVERSAL_CONTENT_SAAS_2026-03-28

## Zweck
Diese Roadmap beschreibt den Weg vom aktuellen internen Produktionssystem zum universellen Content-SaaS.
Sie ist so geschrieben, dass drei Agents parallel daran arbeiten können, ohne sich gegenseitig zu blockieren.

## Leitidee
Nicht neu anfangen.
Stattdessen:

1. aktuellen internen Nutzen stabil halten
2. spezialisierte Struktur in generischen Produktkern überführen
3. neue Plattformen und Provider nur auf sauberer Basis hinzufügen
4. SaaS-Härtung erst dann, wenn Kernmodell und Adapter stehen

---

# PHASE 0 – Stabilisieren, sichtbar machen, technische Schulden einfrieren

## Ziel
Der aktuelle Stand wird abgesichert, damit ihr von einer stabilen Basis aus erweitert.

## Dauer
Kurzfristig / zuerst

## Ergebnis
- aktueller Workflow bleibt benutzbar
- Architekturentscheidungen werden dokumentiert
- Sicherheits- und Prozesslücken werden sichtbar
- keine unkontrollierte Feature-Expansion mehr

## Aufgaben

### 0.1 Scope-Freeze festlegen
**Owner:** Smith + Eddi
**Unterstützung:** Jarvis

- schriftlich definieren:
  - was aktuell produktiv genutzt wird
  - was experimentell ist
  - was eingefroren wird
- Tag setzen: `current-internal-tool-baseline`
- PR-/Branch-Regel dokumentieren

**Done wenn:**
- Baseline-Tag existiert
- Freeze-Regeln dokumentiert
- alle Agents kennen die Grenze zwischen „stabil“ und „experimentell“

### 0.2 Architektur-Quick-Audit
**Owner:** Smith
**Unterstützung:** Jarvis

- identifizieren:
  - zentrale Module
  - kritische Kopplungen
  - Stellen mit Dateisystem-Abhängigkeit
  - Stellen mit Plattform-/Provider-Speziallogik
  - Sicherheitskritische Pfade
- Ergebnis als Audit-Dokument ablegen

**Done wenn:**
- Liste der Top-10 technischen Risiken vorhanden
- jedes Risiko hat Schweregrad und Empfehlung

### 0.3 Sicherheits-Minimum herstellen
**Owner:** Smith
**Unterstützung:** Jarvis

- API-Grenzen prüfen
- Auth für sensible Admin-/API-Pfade strikter machen
- Secrets-Handling prüfen
- `.env.example` / Config-Reference erstellen
- Secret-Scan in CI erwägen

**Done wenn:**
- kein sensibler Pfad versehentlich offen
- Secrets-Handling dokumentiert
- klare Regel: niemals Tokens / Secrets committen

### 0.4 Prozess-Standards festziehen
**Owner:** Jarvis
**Unterstützung:** alle

- PR-Template
- ADR-Template
- Issue-/Ticket-Template
- Definition of Done Template
- Release-Checkliste
- Branch-Konvention

**Done wenn:**
- Vorlagen im Repo liegen
- Agents sie tatsächlich nutzen

### 0.5 Test-Minimum einführen
**Owner:** Smith
**Unterstützung:** Jarvis

- Test-Setup wählen
- mindestens Smoke-Tests einführen für:
  - App startet
  - DB init
  - Workflow create/list
  - Audio job create/list
- CI auf Pull Requests ausführen

**Done wenn:**
- jeder PR mindestens Smoke-Tests durchläuft

---

# PHASE 1 – Domain Cut: vom Spezialtool zum generischen Produktkern

## Ziel
Die heutige fachliche Spezialisierung wird schrittweise in ein generisches Modell überführt.

## Ergebnis
Es gibt einen neuen Produktkern, auf dem aktuelle und zukünftige Funktionen aufbauen können.

## Neue Kernobjekte
Diese Objekte sollen eingeführt oder sauber definiert werden:

- Workspace
- User
- Role
- Brand
- ConnectedAccount
- ProviderConfig
- ContentPreset
- ContentRequest
- ContentVariant
- Asset
- AssetBundle
- Workflow
- Job
- PublishTarget
- PublishJob
- PublishResult
- AnalyticsRecord

## Aufgaben

### 1.1 Ziel-Domain modellieren
**Owner:** Smith
**Unterstützung:** Jarvis

- für jedes Objekt definieren:
  - Zweck
  - Felder
  - Beziehungen
  - Lebenszyklus
- altes Modell auf neues Modell abbilden

**Done wenn:**
- Domain-Dokument existiert
- Mapping Alt → Neu ist beschrieben
- keine Kernentität ist unklar

### 1.2 Naming bereinigen
**Owner:** Smith
**Unterstützung:** Pako

- Begriffe vereinheitlichen:
  - workflow
  - job
  - asset
  - preset
  - request
  - run
  - publish
- keine fachlich irreführenden Namen weitertragen

**Done wenn:**
- Glossar existiert
- neue Module nutzen das Glossar konsequent

### 1.3 DB-Zielmodell v2 definieren
**Owner:** Smith
**Unterstützung:** Jarvis

- neues Schema entwerfen
- Migrationsstrategie festlegen
- alte Tabellen nicht hektisch ersetzen, sondern kontrolliert migrieren

**Empfohlene Tabellenfamilien**
- identities: users, workspaces, memberships, roles
- brands: brands, brand_rules
- providers: provider_configs, provider_credentials_refs
- assets: assets, asset_versions, asset_tags
- content: content_requests, content_variants, presets
- workflow: workflows, workflow_steps, jobs, logs
- publish: connected_accounts, publish_jobs, publish_results
- analytics: analytics_records, analytics_rollups

**Done wenn:**
- Schema-Vorschlag reviewt
- Migrationsreihenfolge festgelegt

### 1.4 Current Product entkoppeln
**Owner:** Smith
**Unterstützung:** Pako

- alte GoT-/Sleep-spezifische Logik in eigenes Modul / Namespace ziehen
- generische Core-Logik von produktspezifischer Logik trennen

**Beispielziel**
- `core/` oder `domain/`
- `products/whispers/`
- `platforms/youtube/`
- `providers/stable_audio/`

**Done wenn:**
- neue Core-Module nicht mehr GoT-spezifisch benannt sind
- Speziallogik klar isoliert ist

---

# PHASE 2 – Runtime und Storage professionalisieren

## Ziel
Das System soll nicht mehr primär am lokalen Dateisystem und Webprozess hängen.

## Ergebnis
Hintergrundarbeit, Dateien und Persistenz sind abstrahiert und robuster.

## Aufgaben

### 2.1 Asset-Abstraktion einführen
**Owner:** Smith
**Unterstützung:** Pako

- Asset-Service definieren
- Dateien nicht mehr nur über feste Pfade adressieren
- Asset-Metadaten speichern:
  - owner / workspace
  - type
  - mime
  - source
  - provider
  - created_by
  - tags
  - lineage

**Done wenn:**
- neue Features Assets über IDs statt feste Pfade referenzieren können

### 2.2 Storage-Layer vorbereiten
**Owner:** Smith

- Storage-Interface einführen
- erster Backend-Typ: LocalStorage
- späterer Backend-Typ: ObjectStorage / S3-kompatibel

**Done wenn:**
- Rendering-/Publishing-Code nicht direkt an rohe Ordnerpfade gekoppelt ist

### 2.3 Job-System trennen
**Owner:** Smith
**Unterstützung:** Jarvis

- Hintergrundjobs aus dem Request-Lebenszyklus lösen
- Worker-Konzept definieren
- Queue/Execution-Modell dokumentieren
- Retry-, Timeout-, Cancel-, Recovery-Regeln festlegen

**Done wenn:**
- Webserver startet Jobs nur noch kontrolliert
- Jobzustände sind klar und dokumentiert

### 2.4 Logging und Observability verbessern
**Owner:** Smith
**Unterstützung:** Jarvis

- strukturierte Logs
- Korrelation über workflow_id / job_id / workspace_id
- Fehlerklassen definieren
- Metriken definieren:
  - job duration
  - success rate
  - provider error rate
  - publish error rate

**Done wenn:**
- Probleme ohne Code-Lesen grob nachvollziehbar sind

### 2.5 Migrationsframework einführen
**Owner:** Smith

- formalen DB-Migrationspfad etablieren
- keine ad-hoc Runtime-Schema-Reparaturen mehr für neue Änderungen

**Done wenn:**
- jede Schemaänderung versioniert und reproduzierbar ist

---

# PHASE 3 – Provider-System aufbauen

## Ziel
Mehrere KI-Provider und Modelle sollen technisch sauber auswählbar werden.

## Ergebnis
Es gibt eine generische Provider-Schicht.

## Aufgaben

### 3.1 Provider-Registry definieren
**Owner:** Smith
**Unterstützung:** Jarvis

- Provider-Typen:
  - text
  - image
  - audio
  - video
  - voice
  - transcription
- pro Provider:
  - capabilities
  - auth mode
  - rate limits
  - fallback-Möglichkeiten
  - Kostenmodell

**Done wenn:**
- Registry-Dokument + Interface existieren

### 3.2 ProviderConfig im Produktmodell verankern
**Owner:** Smith
**Unterstützung:** Pako

- pro Workspace / Brand / Workflow konfigurierbar:
  - default provider
  - default model
  - quality tier
  - fallback chain
  - budget cap
  - key source

**Done wenn:**
- Auswahl nicht mehr hardcoded ist

### 3.3 Stable Audio aus Spezialfall lösen
**Owner:** Smith

- Stable Audio bleibt erhalten
- aber als normaler Provider hinter Interface
- provider-spezifische Felder kapseln

**Done wenn:**
- Stable Audio kein Sonderrecht im Kern mehr hat

### 3.4 UI für Provider-Management
**Owner:** Pako
**Unterstützung:** Smith

- Provider-Seite
- Modellwahl
- Quality presets
- Provider-Test
- Fehlermeldungen
- Kostenhinweise

**Done wenn:**
- ein Nutzer Provider bewusst wählen und verstehen kann

### 3.5 Provider-Testmatrix
**Owner:** Jarvis
**Unterstützung:** Smith

- definieren:
  - Health checks
  - Contract tests
  - Fallback tests
  - Fehlerfall-Tests

**Done wenn:**
- Provider-Integrationen nicht mehr blind live gehen

---

# PHASE 4 – Plattform-Adapter aufbauen

## Ziel
Plattformen werden nicht mehr direkt im Produktkern implementiert.

## Ergebnis
Jede Plattform hängt an einer klaren Adapter-Schicht.

## Zielplattformen in Reihenfolge
1. YouTube Longform
2. YouTube Shorts
3. Instagram Reels
4. TikTok
5. optional später weitere

## Aufgaben

### 4.1 Publish-Domain definieren
**Owner:** Smith
**Unterstützung:** Jarvis

- ConnectedAccount
- PublishTarget
- PublishJob
- PublishStatus
- PublishResult
- RetryPolicy

**Done wenn:**
- Publishing fachlich sauber modelliert ist

### 4.2 YouTube-Adapter refactoren
**Owner:** Smith
**Unterstützung:** Pako

- aktuelles YouTube-Upload-System in Adapter kapseln
- Longform und Shorts als Varianten eines Plattformadapters behandeln
- Thumbnails, Visibility, Metadata-Mapping kapseln

**Done wenn:**
- YouTube-Logik nicht mehr verstreut liegt

### 4.3 Connected-Account-Management vorbereiten
**Owner:** Smith
**Unterstützung:** Pako

- Accounts verbinden
- Token-Status anzeigen
- Account pro Workspace / Brand zuordnen
- Health / last verified / scopes sichtbar machen

**Done wenn:**
- Plattformkonten als echte Produktobjekte existieren

### 4.4 Publish UI generalisieren
**Owner:** Pako

- Publish nicht als „YouTube Upload“-Seite, sondern als generischen Publish-Step denken
- plattformspezifische Optionen nur kontextuell anzeigen

**Done wenn:**
- gleiche Grund-UX für mehrere Plattformen funktioniert

### 4.5 Adapter-Verträge dokumentieren
**Owner:** Jarvis

Für jeden Adapter dokumentieren:
- Inputs
- unterstützte Content-Typen
- unterstützte Metadaten
- Statusmodell
- Fehlertypen
- Retries
- bekannte Limits

**Done wenn:**
- neue Plattformen nach demselben Muster integrierbar sind

---

# PHASE 5 – Content-Modell erweitern

## Ziel
Das System kann mehr als nur einen Sleep-Music-Workflow.

## Ergebnis
Ein generisches Studio-Modell für mehrere Content-Typen.

## Reihenfolge der Content-Typen
1. Longform ambient/sleep video
2. Short from longform
3. Faceless short video from prompt
4. Image + caption post
5. Music + cover + metadata bundle
6. später komplexere Kampagnen / Serien

## Aufgaben

### 5.1 ContentPreset-System bauen
**Owner:** Smith + Pako
**Unterstützung:** Jarvis

Ein Preset beschreibt:
- Content-Typ
- Input-Felder
- Defaults
- Variant-Logik
- empfohlene Provider
- Renderregeln
- Publish-Ziele

**Done wenn:**
- neue Workflows aus Presets statt Spezialformularen entstehen

### 5.2 ContentRequest und Varianten einführen
**Owner:** Smith

- Request = Nutzerabsicht
- Variant = konkrete Ausprägung
- Trennung zwischen Idee und produziertem Output

**Done wenn:**
- Varianten ohne Copy-Paste-Workflows möglich sind

### 5.3 Brand-Kit / Brand-Rules
**Owner:** Pako
**Unterstützung:** Smith

- Logos
- Farben
- Tonalität
- verbotene Begriffe
- CTA-Regeln
- Default-Plattformen
- Default-Provider

**Done wenn:**
- das Produkt nicht nur generiert, sondern markenkonsistent generiert

### 5.4 Asset Bundles / Output Packages
**Owner:** Smith

- ein Content-Request kann mehrere Outputs erzeugen:
  - video
  - thumbnail
  - metadata
  - captions
  - cover
  - preview images

**Done wenn:**
- Output nicht mehr nur in einem YouTube-Ordner gedacht wird

### 5.5 Studio-UX statt Tool-UX
**Owner:** Pako

Create-Flow umbauen in:
1. Ziel wählen
2. Preset wählen
3. Inputs / Brand / Provider bestätigen
4. Varianten erzeugen
5. reviewen
6. rendern
7. publishen

**Done wenn:**
- die Bedienung einem Studio gleicht, nicht einer Scriptoberfläche

---

# PHASE 6 – Analytics und Lernschleife

## Ziel
Das System soll aus Ergebnissen lernen und nicht nur veröffentlichen.

## Ergebnis
Performance wird strukturiert zurückgeführt.

## Aufgaben

### 6.1 Analytics-Domain definieren
**Owner:** Smith
**Unterstützung:** Jarvis

- Plattformdaten normalisieren
- Metriken definieren:
  - views
  - watch time
  - retention
  - CTR
  - saves
  - shares
  - comments
  - publish status
  - cost per asset / variant

**Done wenn:**
- dieselbe Analyse-Logik plattformübergreifend denkbar ist

### 6.2 Performance-Dashboard
**Owner:** Pako

- nach Preset
- nach Plattform
- nach Brand
- nach Provider
- nach Variante
- nach Zeitraum

**Done wenn:**
- Nutzer sehen, was funktioniert und warum

### 6.3 Learning Loop
**Owner:** Smith + Jarvis

- erfolgreiche Muster extrahieren
- Empfehlungen für Presets / Hooks / Provider ableiten
- nicht automatisch live optimieren, bevor die Grundlagen stabil sind

**Done wenn:**
- echte Verbesserungsvorschläge aus Daten entstehen

---

# PHASE 7 – SaaS-Härtung

## Ziel
Aus dem internen Studio wird ein belastbares Multi-User-Produkt.

## Ergebnis
Technisch und prozessual saubere Basis für externe Nutzer.

## Aufgaben

### 7.1 Multi-Tenant sauber durchziehen
**Owner:** Smith

- Workspace-Isolation
- Memberships
- RBAC
- Datenzugriff pro Workspace

**Done wenn:**
- kein Objekt implizit global ist, wenn es eigentlich tenant-gebunden sein sollte

### 7.2 Billing / Usage-Grundlage
**Owner:** Smith
**Unterstützung:** Jarvis

- Usage Events
- Provider-Kosten
- Asset-/Render-Kosten
- Limits / Plans / Quotas

**Done wenn:**
- Kosten technisch nachvollziehbar sind

### 7.3 Compliance / Policy Layer
**Owner:** Jarvis
**Unterstützung:** Smith

- AI-Disclosure-Felder
- Content lineage
- Lizenzstatus pro Asset
- Terms / retention / deletion
- Abuse-/Risk-Flags

**Done wenn:**
- Produkt nicht nur technisch, sondern betrieblich tragfähig wird

### 7.4 Support- und Ops-Runbooks
**Owner:** Jarvis

- Incident Response
- deploy rollback
- provider outage
- publish failure
- token refresh failure
- storage outage
- DB recovery

**Done wenn:**
- Betrieb nicht nur von implizitem Wissen abhängt

### 7.5 Produktions-Infrastruktur ausbauen
**Owner:** Smith

Später:
- Postgres
- Object Storage
- Worker-Queue
- Secrets Management
- Monitoring
- Alerting
- Rate limiting

**Done wenn:**
- externes Nutzerwachstum technisch verkraftbar wird

---

# PHASE 8 – Controlled External Beta

## Ziel
Erste externe Nutzer auf begrenztem Scope.

## Ergebnis
Validierung des Produktwerts ohne chaotische Überdehnung.

## Voraussetzungen
- Kernmodell steht
- YouTube sauber abstrahiert
- mindestens ein weiterer Plattformadapter in brauchbarer Form
- Provider-System funktioniert
- Workspace-/Account-/Publish-Grundlagen stehen
- Support-Runbooks vorhanden

## Beta-Scope
- wenige Nutzer
- wenige Presets
- wenige Plattformen
- klare Limits
- enger Support-Kanal

## Done wenn
- ihr echte Nutzungsdaten und echte Friktionen bekommt
- ohne dass die Codebasis wieder in Speziallogik zerfällt

---

# PARALLELE ARBEITSAUFTEILUNG FÜR 3 AGENTS

## Smith
Hauptverantwortung:
- Architektur
- Domain
- DB
- Storage
- Worker
- Provider
- Plattformadapter
- Security
- Deploy

## Pako
Hauptverantwortung:
- Produktlogik
- Dashboard-/Studio-Flows
- Settings/Provider/Publish UX
- Brand-/Preset-/Variant-UX
- Formulare, Übersicht, Navigation

## Jarvis
Hauptverantwortung:
- Roadmaps
- ADRs
- How-tos
- Testpläne
- Akzeptanzkriterien
- Runbooks
- Release Notes
- Konsistenz zwischen Zielbild und Umsetzung

---

# EMPFOHLENE REIHENFOLGE DER TICKETS

## Reihenfolge A – zuerst
1. Phase 0 komplett
2. Phase 1.1 bis 1.4
3. Phase 2.1 bis 2.5
4. Phase 3.1 bis 3.4
5. Phase 4.1 bis 4.3

## Reihenfolge B – danach
6. YouTube-Adapter sauber abschließen
7. Preset-/Request-/Variant-Modell
8. Brand-System
9. Studio-UX
10. Analytics-Grundlagen

## Reihenfolge C – erst spät
11. zusätzlicher Plattformadapter
12. Billing / SaaS-Härtung
13. Controlled Beta

---

# WICHTIGE STOPP-REGELN

## Nicht tun vor Phase 1/2
- keine Instagram-/TikTok-Integration direkt in die alte Struktur
- kein zweiter oder dritter KI-Provider als Spezialfall
- keine „universelle“ UI ohne neues Domainmodell
- keine großflächige Kosmetik, solange Kernlogik unklar bleibt

## Nur tun, wenn nötig
- Bugfixes für den aktuellen internen Workflow
- kleine UX-Verbesserungen
- Doku- und Stabilitätsarbeit

---

# DEFINITION OF DONE FÜR JEDE PHASE
Jede Phase ist erst fertig, wenn:

1. Code gemerged
2. Doku aktualisiert
3. Akzeptanzkriterien erfüllt
4. Migrations- / Betriebsfolgen dokumentiert
5. Review durch zweiten Agent erfolgt
6. kein impliziter Sonderfall entstanden ist

---

# NORDSTERN
Das Ziel ist nicht „mehr Features“.

Das Ziel ist:
**ein sauberes Content Operating System, das neue Plattformen, neue Provider und neue Content-Typen aufnehmen kann, ohne jedes Mal die Architektur zu verbiegen.**
