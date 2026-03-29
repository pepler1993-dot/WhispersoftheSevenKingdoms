# PROJECT_FUTURE_DOCS_AND_WHEN_2026-03-29.md

## Zweck
Dieses Dokument ergänzt den aktuellen Dokumentensatz um die Dinge, die **später noch gebraucht werden**, aber **jetzt noch nicht** als voll ausgearbeitete Dokumente nötig sind.

Es ist bewusst kein neuer Masterplan, sondern eine Orientierung:
- was noch fehlt
- warum es noch fehlt
- wann man sich sinnvoll darum kümmern sollte

---

## Grundregel
Nicht alles sofort dokumentieren.

Ein Dokument sollte erst dann ernsthaft ausgearbeitet werden, wenn:
- das zugrunde liegende Modell halbwegs stabil ist
- die Umsetzung kurz bevorsteht oder gerade beginnt
- das Dokument reale Entscheidungen, Entwicklung oder Betrieb verbessert

---

# 1. Technische Spezifikationen

## Was später noch gebraucht wird
- API-Spezifikationen
- Datenbankschema-/Migrationsspezifikationen
- Status- und Fehlerobjekte
- Adapter-Schnittstellen
- Felddefinitionen für Kernobjekte

## Warum das noch nicht vollständig fehlt
Ihr habt aktuell die strategische Ebene gut abgedeckt, aber die detaillierten technischen Verträge müssen später pro Modul präzise werden.

## Wann sinnvoll
### Starten in
- **Welle B** für Grundverträge
- **Welle C/D** für konkrete Modul-Specs

### Spätestens nötig bei
- echten Kernobjekt-Implementierungen
- API-first Refactors
- Plattform-/Provider-Adaptern
- mehreren parallelen Entwicklern an denselben Modulen

## Konkret später anzulegen
- `API_CONTRACTS.md`
- `DOMAIN_OBJECT_SPECS.md`
- `DB_SCHEMA_AND_MIGRATIONS.md`
- `ADAPTER_INTERFACES.md`

---

# 2. Betriebsdokumente / Runbooks

## Was später noch gebraucht wird
- Incident-Runbooks
- Backup/Restore-Runbook
- Deploy-Runbook
- Staging-/Release-Checklisten
- Support-Playbooks

## Warum das noch nicht vollständig fehlt
Solange ihr intern entwickelt, reichen pragmatische Abläufe oft noch aus.  
Sobald aber echte externe Nutzer oder Design Partner dazukommen, wird fehlende Betriebsdoku teuer.

## Wann sinnvoll
### Starten in
- **Welle B/C** für Deploy-/Smoke-/Rollback-Minimum
- **Welle D/E** für echte Runbooks

### Spätestens nötig bei
- Design Partner Alpha
- Private Beta
- jeder echten Support-/Onboarding-Welle

## Konkret später anzulegen
- `DEPLOY_RUNBOOK.md`
- `INCIDENT_RESPONSE_RUNBOOK.md`
- `BACKUP_RESTORE_RUNBOOK.md`
- `SUPPORT_PLAYBOOK.md`
- `STAGING_RELEASE_CHECKLIST.md`

---

# 3. Security- und Compliance-Dokumente

## Was später noch gebraucht wird
- Secrets-/Credential-Handling
- OAuth-/Connected-Account-Policies
- Data Retention / Deletion
- Audit-Log-Konzept
- Rechte-/Asset-/AI-Disclosure-Regeln

## Warum das noch nicht vollständig fehlt
Das Thema ist schon erkannt, aber noch nicht bis zur späteren Beta-Reife ausgearbeitet.  
Gerade bei verbundenen Accounts, Uploads und generiertem Content wird das später Pflicht.

## Wann sinnvoll
### Starten in
- **Welle A/B** als Audit und Grundregeln
- **Welle C/D** für konkrete Modelle
- **Welle E/F** für Beta-/Launch-Reife

### Spätestens nötig bei
- Connected Accounts
- externer Beta
- mehreren Workspaces/Teams
- öffentlicher Vermarktung

## Konkret später anzulegen
- `SECURITY_BASELINE.md`
- `CONNECTED_ACCOUNT_SECURITY.md`
- `DATA_RETENTION_AND_DELETION.md`
- `ASSET_RIGHTS_AND_AI_DISCLOSURE.md`
- `AUDIT_LOG_POLICY.md`

---

# 4. Design-System / UI-Pattern-Dokumente

## Was später noch gebraucht wird
- Komponentenregeln
- Spacing-/Typografie-Standards
- Tabellen-/Form-/Status-Patterns
- Empty-/Error-/Loading-State-Regeln
- einheitliche CTA-/Badge-/Statuslogik

## Warum das noch nicht vollständig fehlt
Ihr habt jetzt eine gute Informationsarchitektur-Regeldatei.  
Was noch fehlt, ist die Ebene darunter: wie einzelne UI-Bausteine konsistent umgesetzt werden.

## Wann sinnvoll
### Starten in
- **Welle D**, sobald Dashboard/Create/Detail aktiv refactored werden

### Spätestens nötig bei
- mehreren parallelen UI-Änderungen
- wachsender Komponentenanzahl
- UI-Drift zwischen mehreren Agents

## Konkret später anzulegen
- `DESIGN_SYSTEM_RULES.md`
- `FORM_PATTERNS.md`
- `STATUS_BADGE_AND_STATE_PATTERNS.md`
- `EMPTY_ERROR_LOADING_PATTERNS.md`

---

# 5. Produktspezifikationen

## Was später noch gebraucht wird
- Onboarding-Flow im Detail
- Rollen-/Rechtemodell im Detail
- Billing-/Usage-Spezifikation
- Analytics-Event-Schema
- Connected-Account-Lifecycle
- Workspace-/Tenant-Regeln im Detail

## Warum das noch nicht vollständig fehlt
Diese Themen hängen stark von eurem tatsächlichen Produktkern und eurer ersten Marktstrategie ab.  
Zu früh zu detaillieren führt oft zu toter Doku.

## Wann sinnvoll
### Starten in
- **Welle C/D** für Core-nahe Spezifikationen
- **Welle E/F** für Markt-/Beta-nahe Spezifikationen

### Spätestens nötig bei
- Pricing-Test
- Private Beta
- Team-/Workspace-Features
- echter Nutzungsmessung und Abrechnung

## Konkret später anzulegen
- `ONBOARDING_FLOW_SPEC.md`
- `RBAC_AND_PERMISSIONS.md`
- `USAGE_AND_BILLING_SPEC.md`
- `ANALYTICS_EVENT_SCHEMA.md`
- `CONNECTED_ACCOUNT_LIFECYCLE.md`
- `WORKSPACE_ISOLATION_SPEC.md`

---

# 6. Empfehlung nach Wellen

## Jetzt / sofort nicht extra ausarbeiten
Nicht jetzt voll ausarbeiten:
- vollständiges Design System
- detaillierte Billing-Spec
- voll ausgearbeitete Support-Playbooks
- tiefe Compliance-Dokumentation für alle Eventualitäten
- komplette API-Spec für alles

## In Welle A/B anfangen
- Security-Baseline
- Grundverträge
- Migrationslogik
- Release-/Rollback-Minimum

## In Welle C/D ausarbeiten
- Kernobjekt-Spezifikationen
- Adapter-/API-Specs
- UI-Pattern-Regeln
- erste echte Runbooks

## In Welle E/F ausarbeiten
- Billing/Usage-Spec
- Analytics-Event-Schema
- Connected-Account-Lifecycle
- Support-Playbooks
- Beta-/Launch-nahe Compliance- und Betriebsdokumente

---

# 7. Kurzfassung
Der aktuelle Dokumentensatz ist **für Steuerung und Richtung** ausreichend.

Später fehlen vor allem noch diese vier Ebenen:
1. **technische Detail-Specs**
2. **Betriebs-/Runbooks**
3. **Security-/Compliance-Dokumente**
4. **produktnahe Spezifikationen und UI-Pattern-Regeln**

## Maßstab
Diese Dinge sollen **nicht jetzt alle sofort geschrieben werden**, sondern **phasenweise dann, wenn sie echte Umsetzung, Stabilität oder Launch-Reife verbessern**.
