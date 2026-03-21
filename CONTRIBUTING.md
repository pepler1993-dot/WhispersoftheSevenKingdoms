# Contributing

## Grundregeln
1. Änderungen im eigenen Branch machen
2. Vor neuer Arbeit `git pull` auf aktuellen Stand
3. Kleine, klar abgegrenzte Commits
4. Erst nach kurzem Review nach `main`
5. Keine Secrets ins Repo

## Zusammenarbeit
- **Jarvis**: Workflow, Doku, Review, Aufgabenkoordination
- **Pako**: Struktur, technische Pipeline, Schema, QA-Basis
- **Smith**: Publishing, Plattformlogik, Upload-Metadaten, YouTube-Flow
- Gemeinsame Dateien nur mit Absprache bearbeiten

## Sync-Service ist Pflicht
Für aktive Task-Arbeit gilt nicht mehr „Chat lesen und loslegen".

Verbindlicher Ablauf:
1. Task beim Sync-Service lesen
2. Claim versuchen
3. Nur bei erfolgreichem Claim arbeiten
4. Während der Arbeit Heartbeats senden
5. Vor jedem GitHub-Write resyncen
6. Neue Events inkrementell nachziehen
7. Am Ende releasen

## Regeln für GitHub-Arbeit
- Kein Commit, Push, PR, Review oder Kommentar ohne gültigen Claim
- Kein paralleles Arbeiten an demselben Task gegen einen gültigen fremden Lease
- Vor jedem schreibenden GitHub-Schritt immer aktuellen Task-State und neue Events prüfen
- Bei abgelaufenem oder unklarem Lease: sofort stoppen, neu lesen, neu claimen oder warten
- Telegram ist für Steuerung und Kontext nützlich, aber nicht die primäre Wahrheitsquelle

## Quellen der Wahrheit
- **GitHub** → Code, Commits, PRs, Reviews, Kommentare
- **agent-sync-service** → Ownership, Lease, Aktivitätszustand, inkrementeller Änderungsabgleich

## Wichtige gemeinsame Konventionen
- gleicher Slug für Song, Thumbnail und Metadaten
- keine halbfertigen Dateien in die Upload-Ordner
- Übergaberegeln stehen in `PARALLEL_WORK_PLAN.md`
