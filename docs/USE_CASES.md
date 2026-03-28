# Use Cases – Whisper Studio SaaS Platform

**Stand:** 28.03.2026
**Zielgruppe:** UI/UX Tests, Produktentwicklung, QA

---

## Konventionen

| Feld | Bedeutung |
|------|-----------|
| **ID** | Stabile Referenz (UC-XX) |
| **Phase** | Aktuell = bereits gebaut, SaaS = für Launch nötig, Future = spätere Iteration |
| **Akteur** | Creator, Admin, Viewer, System |

---

## Kern-Workflows (Content Production)

### UC-01: Neues Video erstellen (End-to-End)

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator |
| **Ziel** | Longform-Video von Hauswahl bis YouTube-Upload in einem Flow |

**Flow:** Haus wählen → Variante → Länge → Audio-Quelle (generieren oder Bibliothek) → Video erstellen → Automatischer Render → Optional Auto-Upload

**Seiten:** `/admin/pipeline/new` → `/admin/pipeline/run/{id}`

---

### UC-02: Short aus bestehendem Video erstellen

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator |
| **Ziel** | Clip aus fertigem Video als YouTube Short generieren |

**Flow:** Quellvideo wählen → Clip-Start/Dauer konfigurieren → Visual Mode → Render → Upload

**Seiten:** `/admin/shorts` → `/admin/shorts/{id}`

---

### UC-03: Audio im Audio Lab generieren

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator |
| **Ziel** | Standalone Audio-Track erzeugen (ohne Video-Pipeline) |

**Flow:** Titel + Haus/Variante wählen → Prompts prüfen → Dauer/Steps → Job starten → Track in Library

**Seiten:** `/admin/audio` → `/admin/audio/jobs/{id}`

---

### UC-04: Song erstellen und exportieren

| | |
|---|---|
| **Phase** | SaaS (MVP fehlt) |
| **Akteur** | Creator |
| **Ziel** | Fertigen Song (Audio + Metadaten) für Streaming-Plattformen produzieren |

**Flow:** Genre/Stil wählen → Audio generieren → Post-Processing (Preset: ambient/dark/gentle) → Metadaten → Export als MP3/WAV → Optional Distribution (Spotify, Apple Music)

**Seiten:** `/admin/songs` (aktuell Placeholder)

---

## Dashboard & Monitoring

### UC-05: Production Overview prüfen

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator, Admin |
| **Ziel** | Auf einen Blick sehen: Was läuft, was ist fertig, was ist kaputt |

**Flow:** Dashboard öffnen → Tab wählen (Videos/Shorts/Songs) → KPIs scannen → Active Runs sehen → Published Content prüfen → Bei Bedarf in Detail springen

**Seiten:** `/admin`

---

### UC-06: Workflow-Status im Detail verfolgen

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator |
| **Ziel** | Live-Logs, Fortschritt und Ergebnis eines laufenden Workflows sehen |

**Flow:** Workflow in Overview/Liste anklicken → Live-Log verfolgen → Video-Preview → Thumbnail prüfen → Upload auslösen oder Retry

**Seiten:** `/admin/pipeline/run/{id}`, `/admin/shorts/{id}`, `/admin/audio/jobs/{id}`

---

### UC-07: Fehlgeschlagenen Workflow fixen

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator |
| **Ziel** | Fehler erkennen, verstehen und Workflow erneut starten |

**Flow:** Failed-Status in Overview sehen → Detail öffnen → Fehlermeldung lesen → Retry klicken oder Config anpassen → Neuen Run starten

**Erwartung:** Fehlermeldung ist verständlich (nicht nur Traceback), Retry-Button direkt sichtbar

---

## Library & Assets

### UC-08: Library durchsuchen und Assets verwalten

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator |
| **Ziel** | Songs, Thumbnails, Backgrounds finden, anhören, hochladen |

**Flow:** Library öffnen → Filter nach Typ → Audio abspielen → Asset für neuen Workflow auswählen

**Seiten:** `/admin/library`

---

### UC-09: Video-Ergebnis prüfen und freigeben

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator (QA-Rolle) |
| **Ziel** | Fertiges Video + Thumbnail + Metadaten bewerten, dann Upload auslösen |

**Flow:** Run-Detail öffnen → Video abspielen → Thumbnail checken → Metadaten prüfen → Upload Button

**Seiten:** `/admin/pipeline/run/{id}`

---

## Team & Settings

### UC-10: Presets verwalten

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Admin |
| **Ziel** | Haus-Templates und Varianten erstellen, bearbeiten, löschen |

**Flow:** Settings → Presets Tab → Preset auswählen → Varianten bearbeiten → Prompts, Backgrounds, Thumbnails konfigurieren

**Seiten:** `/admin/settings`

---

### UC-11: Team-Mitglieder verwalten

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Admin |
| **Ziel** | User anlegen, Rollen zuweisen (Admin/Editor/Viewer) |

**Flow:** Settings → Team Tab → User einladen → Rolle zuweisen → User kann sich einloggen

**Seiten:** `/admin/settings` (Team Tab)

---

### UC-12: Provider-Einstellungen konfigurieren

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Admin |
| **Ziel** | GPU-Worker, YouTube-API, Audio-Modell konfigurieren |

**Flow:** Settings → Providers Tab → GPU Host/Modell setzen → YouTube Credentials → Speichern

**Seiten:** `/admin/settings` (Providers Tab)

---

## Tickets & Ops

### UC-13: Bug oder Feature-Wunsch melden

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Creator, Admin |
| **Ziel** | Feedback strukturiert erfassen |

**Flow:** Tickets → Neues Ticket → Typ (Bug/Feature/Task) → Beschreibung → Absenden

**Seiten:** `/admin/tickets/new`, `/admin/tickets`

---

### UC-14: System-Health und Server-Status prüfen

| | |
|---|---|
| **Phase** | Aktuell |
| **Akteur** | Admin |
| **Ziel** | CPU, RAM, Disk, GPU-Status, Service-Health auf einen Blick |

**Flow:** Operations öffnen → Server-Stats sehen → GPU-Worker Status → DB-Backup auslösen

**Seiten:** `/admin/ops`

---

## SaaS-spezifische Use Cases (noch zu bauen)

### UC-20: Erstmalige Registrierung und Onboarding

| | |
|---|---|
| **Phase** | SaaS (Phase 4) |
| **Akteur** | Neuer User |
| **Ziel** | Account erstellen und sofort produktiv sein |

**Flow:** Landing Page → Sign Up → Email verifizieren → Onboarding-Wizard (Space-Name, ersten Preset wählen, GPU verbinden oder Managed nutzen) → Erstes Video erstellen

**Erwartung:** Innerhalb von 5 Minuten nach Registrierung das erste Video gestartet

---

### UC-21: Space erstellen und konfigurieren

| | |
|---|---|
| **Phase** | SaaS (Phase 3b) |
| **Akteur** | Admin |
| **Ziel** | Eigenen isolierten Workspace mit eigenem Branding |

**Flow:** Space-Switcher → Neuer Space → Name + Branding → Presets importieren oder neu erstellen → Team einladen

**Erwartung:** Vollständige Datenisolation zwischen Spaces

---

### UC-22: Subscription verwalten und Billing

| | |
|---|---|
| **Phase** | SaaS (Phase 5) |
| **Akteur** | Admin |
| **Ziel** | Plan wählen, Zahlungsmethode hinterlegen, Usage sehen |

**Flow:** Settings → Billing → Plan auswählen (Free/Creator/Studio/Enterprise) → Stripe Checkout → Usage Dashboard sehen → Rechnungen herunterladen

**Erwartung:** Transparente Kosten, keine versteckten Limits

---

### UC-23: Content auf mehrere Plattformen veröffentlichen

| | |
|---|---|
| **Phase** | SaaS (Phase 7) |
| **Akteur** | Creator |
| **Ziel** | Ein Video/Song gleichzeitig auf YouTube, TikTok, Spotify pushen |

**Flow:** Workflow abgeschlossen → Publish-Dialog → Plattformen auswählen (YouTube ✅, TikTok ✅, Instagram ✅) → Plattform-spezifische Anpassungen → Publish All

**Erwartung:** Ein Klick für Multi-Platform, plattformspezifische Formate automatisch

---

### UC-24: Content-Kalender und Scheduling

| | |
|---|---|
| **Phase** | SaaS (Phase 7) |
| **Akteur** | Creator |
| **Ziel** | Content im Voraus planen und automatisch veröffentlichen |

**Flow:** Calendar öffnen → Datum/Uhrzeit wählen → Workflow zuweisen → System veröffentlicht automatisch zum Zeitpunkt

**Erwartung:** Kalenderansicht, Drag & Drop, Zeitzone-aware

---

### UC-25: Analytics und Performance einsehen

| | |
|---|---|
| **Phase** | SaaS (Phase 7) |
| **Akteur** | Creator, Admin |
| **Ziel** | Views, Watch Time, Revenue pro Video/Song/Channel sehen |

**Flow:** Analytics öffnen → Zeitraum wählen → Pro Content oder pro Channel filtern → Trends erkennen

**Erwartung:** Daten direkt von YouTube/Spotify APIs, nicht manuell

---

### UC-26: GPU-Provider verbinden (Bring Your Own GPU)

| | |
|---|---|
| **Phase** | SaaS (Phase 6) |
| **Akteur** | Admin |
| **Ziel** | Eigene GPU-Hardware für Audio-Generierung nutzen |

**Flow:** Settings → Providers → GPU hinzufügen → SSH-Key/Host konfigurieren → Health Check → Worker aktiv

**Erwartung:** Fallback auf Managed GPU wenn eigene offline

---

### UC-27: Batch-Produktion starten

| | |
|---|---|
| **Phase** | SaaS (Phase 8) |
| **Akteur** | Creator |
| **Ziel** | Mehrere Videos/Songs auf einmal erstellen |

**Flow:** Preset/Haus wählen → "Alle Varianten" → Bulk-Config (Länge, Auto-Upload) → 8 Videos auf einmal starten

**Erwartung:** Queue-Management, Progress für alle gleichzeitig sichtbar

---

### UC-28: API-Integration für externe Tools

| | |
|---|---|
| **Phase** | SaaS (Phase 9) |
| **Akteur** | Developer (externer User) |
| **Ziel** | Workflows programmatisch starten und Status abfragen |

**Flow:** Settings → API Keys → Key erstellen → REST API Docs lesen → Workflow per API starten → Webhook bei Completion

**Erwartung:** Vollständige REST API, API Key Auth, Webhook Notifications

---

### UC-29: White-Label für Agentur-Kunden

| | |
|---|---|
| **Phase** | SaaS (Phase 9) |
| **Akteur** | Agentur-Admin |
| **Ziel** | Eigenes Branding, eigene Domain, Kunden-Management |

**Flow:** Enterprise Settings → Domain verbinden → Logo/Farben anpassen → Sub-Spaces für Kunden erstellen

**Erwartung:** Endkunde sieht nur Agentur-Branding, nicht Whisper Studio

---

## Querschnitt-Anforderungen (alle Use Cases)

### UX-Prinzipien
- **5-Sekunden-Test:** User versteht sofort wo er ist und was er tun kann
- **Progressive Disclosure:** Komplexität nur wenn nötig
- **Zero-Config Default:** Presets füllen alles vor, User kann überschreiben
- **Fehler = Handlung:** Jeder Fehler zeigt was der User tun soll
- **Output first:** Fertige Inhalte prominenter als Prozess-Details

### Status-System (UI)
Nur 5 sichtbare Status für den User:
- 🟢 **Running** (inkl. waiting_for_audio, uploading)
- 🟡 **Queued**
- 🟠 **Ready** (rendered, bereit zum Upload)
- 🔵 **Published** (uploaded)
- 🔴 **Failed** (error, cancelled)

### Anti-Patterns
- Keine technischen Fehlermeldungen ohne Kontext
- Keine toten UI-Elemente oder leere Seiten ohne CTA
- Keine Tabellen-Listen (immer Cards)
- Kein GoT-spezifisches Branding in der Produktstruktur
- Keine doppelten/widersprüchlichen Status-Badges

---

## Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 27.03.2026 | Erstversion UC-01 bis UC-09 |
| 28.03.2026 | Komplett überarbeitet für SaaS. UC-01 bis UC-29. Querschnitt-Anforderungen, Status-System, Anti-Patterns hinzugefügt. |
