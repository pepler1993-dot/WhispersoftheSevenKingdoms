# AGENT SYNC – Zusammenarbeit zwischen Agenten

## Zweck
Diese Seite beschreibt die Zusammenarbeit rund um den Sync-Service und die Übergabe zwischen Agenten.

Nicht als vollständige API-Referenz — dafür gibt es andere Dokus — sondern als **praktische Team-Anleitung**.

---

## Grundidee

Der Sync-Service ist die Koordinationsschicht zwischen parallel arbeitenden Agenten.

Er soll verhindern, dass:
- zwei Agenten denselben Task gleichzeitig zerlegen
- Besitzverhältnisse unklar sind
- Releases und Abschlüsse verwechselt werden
- jemand nur nach Chatlage arbeitet

---

## Drei Wahrheiten im Projekt

### 1. GitHub / Git
Wahrheit für:
- Code
- Commits
- Branches
- PRs
- Reviews

### 2. Sync-Service
Wahrheit für:
- Ownership
- Lease-Zustand
- Task-Aktivität
- Task-Events

### 3. `PROJECT_STATUS.md`
Wahrheit für:
- operative Lage
- Prioritäten
- Infrastruktur-/Projektstand

Telegram/Chat ist hilfreich, aber nicht alleinige Wahrheit.

---

## Verbindlicher Minimalablauf

1. Task lesen
2. claimen
3. arbeiten
4. heartbeat senden, wenn nötig
5. vor GitHub-Write resyncen
6. am Ende `release` oder `complete`

---

## Bedeutungen, die Agenten nicht verwechseln dürfen

### `claim`
Ich übernehme den Task aktiv.

### `heartbeat`
Ich arbeite noch daran, Lease bitte gültig halten.

### `release`
Ich gebe den Task wieder frei, **aber er ist nicht automatisch fertig**.

### `complete`
Die Aufgabe ist fachlich abgeschlossen.

---

## Wann Sync-Service Pflicht ist

Pflicht bzw. stark empfohlen bei:
- echter Task-Arbeit mit mehreren Agenten
- GitHub-bezogenen Aufgaben
- Reviews / Ownership-Fragen
- Übergaben

Für winzige, völlig isolierte Mini-Doku-Fixes kann man pragmatischer sein — aber sobald Überschneidung droht, gilt Koordination vor Ego.

---

## Typische Agentenfehler

### Fehler 1 – nur auf Chatbasis loslegen
Dann arbeiten zwei Leute an verschiedenen Realitäten vorbei.

### Fehler 2 – claim vergessen
Dann gehört der Task gefühlt allen und real niemandem.

### Fehler 3 – `release` statt `complete` oder umgekehrt
Dann kippt die operative Lage.

### Fehler 4 – vor Push nicht resyncen
Dann entsteht GitHub-Müll gegen den aktuellen Stand.

---

## Praktische Empfehlung für dieses Projekt

Wenn du an einem echten Workstream sitzt:
- `PROJECT_STATUS.md` lesen
- Task-Lage prüfen
- claimen
- klein arbeiten
- vor jedem Schreibschritt neu synchronisieren
- sauber releasen oder completen

Das ist billiger als hinterher Branch-Leichen zu sortieren.
