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

### ⏸️ Phase 3b – Space-Isolation (geparkt)
> Bewusst geparkt – erst relevant mit externen Usern.
- Runs, Jobs, Presets, Settings pro Space trennen (space_id Filter auf allen Queries)
- Space-Switcher im UI
- Einladungslinks für neue Spaces

---

## Roadmap: Was noch fehlt für ein professionelles SaaS

### Phase 4 – Onboarding & Self-Service

**Ziel:** Neue User können sich selbst registrieren und sofort starten.

- [ ] **Registrierung** – Sign-up Seite (Email + Passwort)
- [ ] **Email-Verifizierung** – Bestätigungsmail bei Registrierung
- [ ] **Passwort vergessen** – Reset-Flow per Email
- [ ] **Onboarding-Wizard** – Schritt-für-Schritt Setup beim ersten Login:
  1. Space-Name + Branding wählen
  2. Ersten Preset erstellen oder Template importieren
  3. GPU-Provider verbinden (oder Managed nutzen)
  4. Erstes Video/Audio erstellen
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
- [ ] **Overage Handling** – Soft-Limits mit Upgrade-Prompts
- [ ] **Invoices** – Automatische Rechnungen via Stripe
- [ ] **Trial Period** – 14 Tage Creator-Features kostenlos

### Phase 6 – Managed GPU & Infrastructure

**Ziel:** User brauchen keine eigene GPU – wir stellen die Compute bereit.

- [ ] **GPU Job Queue** – Multi-Tenant Job-Scheduler
- [ ] **Auto-Scaling** – GPU-VMs on-demand starten/stoppen
- [ ] **Provider-Abstraction** – Hetzner, RunPod, Lambda Labs, AWS als Backends
- [ ] **Cost Tracking** – GPU-Kosten pro Space/Job erfassen
- [ ] **Fair Scheduling** – Priority Queue basierend auf Tier
- [ ] **Bring-Your-Own-GPU** – User können eigene GPU-Worker verbinden

### Phase 7 – Distribution & Publishing

**Ziel:** Multi-Plattform Publishing aus einem Flow.

- [ ] **YouTube Auto-Upload** ✅ (existiert)
- [ ] **Spotify/Apple Music** – DistroKid oder eigene Distribution für Audio
- [ ] **TikTok Upload API** – Shorts direkt auf TikTok pushen
- [ ] **Instagram Reels** – Shorts cross-posten
- [ ] **Scheduling** – Content Calendar: Wann wird was veröffentlicht
- [ ] **Analytics Dashboard** – Views, Watch Time, Revenue pro Video/Song
- [ ] **A/B Testing** – Verschiedene Thumbnails/Titel testen

### Phase 8 – AI & Automation

**Ziel:** Content-Produktion weiter automatisieren.

- [ ] **AI Title Generator** – Optimierte Titel basierend auf Niche + SEO
- [ ] **AI Thumbnail Generator** – Stable Diffusion direkt im Flow
- [ ] **Auto-Tagging** – YouTube Tags automatisch aus Content ableiten
- [ ] **Trend Detection** – Was performt gerade gut in der Niche?
- [ ] **Batch Production** – "Erstelle 10 Videos für alle Varianten" in einem Klick
- [ ] **Content Calendar AI** – Optimaler Upload-Zeitplan basierend auf Analytics
- [ ] **Voice-over Integration** – ElevenLabs/TTS für Intros/Outros

### Phase 9 – Enterprise & White-Label

**Ziel:** B2B-Kunden und Agenturen.

- [ ] **White-Label** – Eigenes Branding, eigene Domain
- [ ] **API** – REST API für externe Integrationen
- [ ] **Webhooks** – Notifications bei Job-Completion, Upload etc.
- [ ] **SSO** – SAML/OIDC für Enterprise-Kunden
- [ ] **Audit Log** – Wer hat was wann gemacht
- [ ] **SLA & Support Tiers** – Premium Support für Enterprise

---

## Public-Facing (Landing Page & Marketing)

- [ ] **Landing Page** – whisperstudio.io / Content Engine Pitch
- [ ] **Pricing Page** – Klare Tier-Übersicht
- [ ] **Demo Video** – 60s Product Demo
- [ ] **Blog / Content Marketing** – SEO für "AI video generator", "sleep music automation"
- [ ] **Discord Community** – Support + Feature Requests
- [ ] **Docs Site** – Public API Docs, Guides, Tutorials
- [ ] **Changelog** – Öffentlich, automatisch aus Git-Tags

---

## ⚠️ Bekannte Workarounds (vor Production fixen!)

- **Auth nur auf GET-Requests** – POST/API-Calls sind aktuell ohne Login möglich, damit Agents (Jarvis etc.) Tickets anlegen und Jobs starten können. Vor Production: API-Keys oder Service-Tokens für Agents einführen, dann alle Routen absichern.

## Technische Schulden & Infra

Bevor SaaS-Launch:

- [ ] **Tests** – Unit + Integration Tests für Auth, Pipeline, Settings
- [ ] **CI/CD** – Automated Tests in GitHub Actions vor Deploy
- [ ] **Monitoring** – Sentry oder ähnliches für Error Tracking
- [ ] **Logging** – Structured Logging (JSON), zentralisiert
- [ ] **Backups** – Automatische DB-Backups (existiert teilweise)
- [ ] **Rate Limiting** – API + Login Brute-Force Protection
- [ ] **HTTPS** – TLS überall (Cloudflare Tunnel erledigt das aktuell)
- [ ] **CORS** – Korrekte CORS-Config für API
- [ ] **Secrets Management** – JWT Secret, API Keys nicht in Code/Env
- [ ] **Docker** – Containerized Deployment
- [ ] **DB Migration** – Schema-Versionierung (Alembic oder manuell)

---

## Priorität für die nächsten Wochen

1. **Shorts-Flow** produktionsreif machen (läuft)
2. **Songs-Seite** MVP (Standalone Audio → Export)
3. **Space-Isolation** wenn erster externer User kommt
4. **Landing Page** als Visitenkarte
5. **Stripe** wenn Landing Page steht
