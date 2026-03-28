# ⚙️ Whisper Studio → SaaS Content Engine – Konzept

## Kernidee

Whisper Studio wird eine konfigurierbare Content-Produktionsplattform. Jeder User/Team bekommt einen **Space** mit eigenen **Presets**, **Content Types** und **Team Members**.

---

## Status: Was bereits gebaut ist

### ✅ Phase 1 – Settings & Konfiguration (v3.3.0)
- Settings-Seite mit Tabs: General, Providers, Pipelines, Presets, Team
- Presets: vollständiges CRUD im UI (Create, Edit, Delete, Varianten-Editor)
- Provider-Config (GPU-Host, Audio-Modell, YouTube) aus DB statt config.yaml
- Presets aus JSON in DB migriert, Live-Verdrahtung in der Pipeline

### ✅ Phase 2 – Content Types (v3.3.0–v3.4.0)
- 5 Content Types definiert: Long-Form Video, Short, Audio Only, Thumbnail Pack, Livestream Loop
- Toggle-Switches zum Aktivieren/Deaktivieren pro Type
- Sidebar: Collapsible Create-Folder mit Video, Shorts, Songs
- Jeder Type hat eigene optimierte UI-Seite

### ✅ Phase 3 – Auth & Team (v3.4.0)
- JWT-Auth mit bcrypt Passwörtern, Login-Seite
- Session-Cookies (72h, httponly)
- Team-Management: User CRUD mit Rollen (Admin/Editor/Viewer)
- Profil-Seite: Anzeigename + Passwort ändern
- DB-Tabellen für Users + Spaces angelegt
- Default Admin bei Erststart

### ✅ Phase 3c – Unified Workflow Architecture (28.03.2026)
- `pipeline_runs` + `workflows` zu einer einzigen `workflows` Tabelle zusammengeführt
- Jeder Content-Typ (video/short/song/audio_lab) ist ein Workflow mit `type` Feld
- Workflow-Phasen: audio → render → upload → done
- Automatische DB-Migration von altem Schema
- Dashboard als SaaS Command Center mit Tab-Navigation pro Content-Type
- KPI-Stats, Active Productions, Recently Published Grid
- User/Logout oben rechts im Content-Bereich

### ⏸️ Phase 3b – Space-Isolation (geparkt)
> Bewusst geparkt – erst relevant mit externen Usern.
- Runs, Jobs, Presets, Settings pro Space trennen (space_id Filter auf allen Queries)
- Space-Switcher im UI
- Einladungslinks für neue Spaces

---

## 🔴 Phase 3d – UI/UX Production-Ready (NÄCHSTER SCHRITT)

**Ziel:** UI sieht aus wie ein echtes SaaS-Produkt — nicht wie ein Dev-Tool.

### Konsistenz & Polish
- [ ] Alle Seiten folgen denselben Design Principles (DESIGN_PRINCIPLES.md)
- [ ] Einheitliches Card-Design überall (gleiche Radii, Shadows, Hover-Effekte)
- [ ] Konsistente Statusfarben auf allen Seiten (Status-Farbsystem aus Design Principles)
- [ ] Keine doppelten/widersprüchlichen Badges (Type vs Status Farben)
- [ ] Section Headers einheitlich (mit oder ohne Deko — entscheiden und durchziehen)
- [ ] Sidebar: Logo responsive auf allen Bildschirmgrößen
- [ ] Mobile: alle Seiten sauber responsive getestet

### Create-Flows
- [ ] Video Create: Progressive Disclosure (Step-Cards statt langes Formular)
- [ ] Shorts Create: gleicher Standard
- [ ] Songs Create: MVP Seite fertig bauen
- [ ] Preset-basierte Defaults überall ("Zero Config to Launch")

### Workflow-Detailseiten
- [ ] Video Run Detail: sauberes Layout, Live-Log, Status-Anzeige
- [ ] Short Detail: gleicher Standard
- [ ] Audio Job Detail: gleicher Standard
- [ ] Einheitlicher "Workflow Detail" Style für alle Typen

### Fehlerzustände
- [ ] Fehler prominent anzeigen (nicht in normaler Liste verstecken)
- [ ] Retry-Buttons direkt sichtbar
- [ ] Leere Zustände ("Noch keine Videos") mit Call-to-Action

### Status-Labels aufräumen
- [ ] `waiting_for_audio` → im UI als "Running" anzeigen (nicht als eigener Status)
- [ ] `uploading` → im UI als "Running" anzeigen
- [ ] Nur 5 UI-Status: Running, Queued, Ready, Published, Failed

---

## Roadmap: Was noch fehlt für ein professionelles SaaS

### Phase 4 – Onboarding & Self-Service

**Ziel:** Neue User können sich selbst registrieren und sofort starten.

- [ ] **Registrierung** – Sign-up Seite (Email + Passwort)
- [ ] **Email-Verifizierung** – Bestätigungsmail bei Registrierung
- [ ] **Passwort vergessen** – Reset-Flow per Email
- [ ] **Onboarding-Wizard** – Schritt-für-Schritt Setup beim ersten Login
- [ ] **Template Gallery** – Vorgefertigte Preset-Pakete (Lo-Fi, Nature, Gaming, Meditation...)
- [ ] **OAuth Login** – Google / GitHub als Alternative

### Phase 5 – Billing & Monetarisierung

**Ziel:** Recurring Revenue über Usage-basiertes Pricing.

- [ ] **Stripe Integration** – Checkout, Subscriptions, Webhooks
- [ ] **Pricing Tiers:**

| Tier | Preis | Inkludiert |
|---|---|---|
| Free | 0€ | 3 Videos/Monat, 1 User, Wasserzeichen |
| Creator | 19€/Monat | 30 Videos, 3 User, kein Wasserzeichen |
| Studio | 49€/Monat | Unlimited Videos, 10 User, Priority GPU |
| Enterprise | Custom | Dedicated GPU, SLA, Custom Branding |

- [ ] **Usage Tracking** – GPU-Minuten, Storage (GB), Uploads pro Space
- [ ] **Usage Dashboard** – Verbrauch visualisieren, Limits anzeigen
- [ ] **Trial Period** – 14 Tage Creator-Features kostenlos

### Phase 6 – Managed GPU & Infrastructure
- [ ] **GPU Job Queue** – Multi-Tenant Job-Scheduler
- [ ] **Auto-Scaling** – GPU-VMs on-demand starten/stoppen
- [ ] **Provider-Abstraction** – Hetzner, RunPod, Lambda Labs als Backends
- [ ] **Bring-Your-Own-GPU** – User können eigene GPU-Worker verbinden

### Phase 7 – Distribution & Publishing
- [ ] **YouTube Auto-Upload** ✅ (existiert)
- [ ] **Spotify/Apple Music** – DistroKid oder eigene Distribution
- [ ] **TikTok Upload API** – Shorts direkt auf TikTok
- [ ] **Scheduling** – Content Calendar
- [ ] **Analytics Dashboard** – Views, Watch Time, Revenue

### Phase 8 – AI & Automation
- [ ] **AI Title Generator** – SEO-optimierte Titel
- [ ] **AI Thumbnail Generator** – Stable Diffusion im Flow
- [ ] **Batch Production** – 10 Videos in einem Klick
- [ ] **Content Calendar AI** – Optimaler Upload-Zeitplan

### Phase 9 – Enterprise & White-Label
- [ ] **White-Label** – Eigenes Branding, eigene Domain
- [ ] **REST API** – Externe Integrationen
- [ ] **SSO** – SAML/OIDC
- [ ] **Audit Log** – Wer hat was wann gemacht

---

## Public-Facing (Landing Page & Marketing)

- [ ] **Landing Page** – whisperstudio.io / Content Engine Pitch
- [ ] **Pricing Page** – Klare Tier-Übersicht
- [ ] **Demo Video** – 60s Product Demo
- [ ] **Blog / Content Marketing** – SEO
- [ ] **Docs Site** – Public API Docs, Guides

---

## ⚠️ Bekannte Workarounds (vor Production fixen!)

- **Auth nur auf GET-Requests** – POST/API-Calls sind aktuell ohne Login möglich. Vor Production: API-Keys oder Service-Tokens einführen.

## Technische Schulden & Infra

Bevor SaaS-Launch:

- [ ] **API-Token-Auth** – Alle POST-Endpoints absichern (🔴 Prio 1)
- [ ] **Tests** – Unit + Integration Tests für Auth, Pipeline, Settings
- [ ] **CI/CD** – Automated Tests in GitHub Actions vor Deploy
- [ ] **Monitoring** – Sentry oder ähnliches für Error Tracking
- [ ] **Logging** – Structured Logging (JSON), zentralisiert
- [ ] **Rate Limiting** – API + Login Brute-Force Protection
- [ ] **Docker** – Containerized Deployment
- [ ] **DB Migration** – Schema-Versionierung (Alembic o.ä.)

---

## Priorität für die nächsten Wochen

1. **UI/UX Production-Ready** (Phase 3d) — alle Seiten SaaS-tauglich
2. **API absichern** — Token-Auth für POST-Endpoints
3. **Songs-Seite** MVP (Standalone Audio → Export)
4. **Landing Page** als Visitenkarte
5. **Domain** — dashboard.ka189.de via Cloudflare finalisieren
6. **Tests** — mindestens Auth + Workflow + Migration
7. **Stripe** wenn Landing Page steht
