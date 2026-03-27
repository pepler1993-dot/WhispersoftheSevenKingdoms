# AGENT SYNC – Zusammenarbeit (Tickets + Git)

## Zweck
Praktische Anleitung für parallele Arbeit: **Git** bleibt die Wahrheit für Code; **Tickets** im Dashboard ersetzen das frühere GitHub-Task-/Webhook-System im Sync-Service.

---

## Zwei Wahrheiten

### 1. Git / GitHub
- Code, Branches, Commits, PRs, Reviews

### 2. Dashboard-Tickets
- wer arbeitet woran
- Priorität, Status, kurze Beschreibung
- siehe `PROJECT_STATUS.md` für teamweite Regeln

Chat/Telegram hilft — ersetzt aber keine der beiden.

---

## Empfohlener Ablauf

1. `PROJECT_STATUS.md` und ggf. `ROADMAP.md` lesen
2. Ticket anlegen oder bestehendes übernehmen (Status **in progress**, Owner setzen)
3. kleine Änderungen, oft committen
4. vor Push: `git fetch`, Rebase/Merge mit aktuellem `main`
5. Ticket bei fachlichem Abschluss auf **done** oder **closed** setzen

---

## Was es nicht mehr gibt

- **Kein** `/api/tasks`-Lifecycle, **kein** Claim/Heartbeat für GitHub-Issues im Sync-Service
- **Kein** `docs/agents/SYNC_SERVICE.md` (entfernt)

Wenn du alte Doku mit „Task claimen“ findest: als veraltet behandeln.

---

## Typische Fehler

- ohne Ticket parallel an derselben Story arbeiten → doppelte Arbeit
- Ticket nicht aktualisieren → niemand sieht Blocker
- große Würfe auf `main` ohne Abstimmung → schwer zu reviewen
