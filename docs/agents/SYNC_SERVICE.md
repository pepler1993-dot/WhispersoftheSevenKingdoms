# Sync Service for Agents

## Zweck
Diese Seite erklärt die Nutzung des **Agent Sync Service** aus Sicht eines arbeitenden Agenten.

Nicht Server-Deployment, sondern: **wie benutze ich das Ding sinnvoll, ohne anderen Agenten ins Knie zu schießen?**

---

## Was der Sync-Service ist

Der Dienst unter `services/sync/` ist ein Koordinations-Layer.

Er hilft Agenten dabei:
- Tasks zu lesen
- Besitz auf Tasks zu claimen
- Heartbeats zu senden
- Tasks sauber zu releasen oder zu completen
- GitHub-bezogene Ereignisse nachvollziehbar zu halten

Er ist **kein Magier**, der Konflikte automatisch heilt.

---

## Wichtigste Zustände

Gültige `phase`-Werte:
- `working`
- `blocked`
- `released`
- `done`
- `archived`
- `stale`

Wichtig:
- `release` bedeutet **Besitz aufgeben, Aufgabe bleibt offen**
- `complete` bedeutet **fachlich abgeschlossen**

Das darf ein Agent nicht verwechseln.

---

## Minimaler Arbeitsablauf für Agenten

1. Task lesen
2. claimen
3. daran arbeiten
4. Heartbeats senden, wenn die Arbeit länger läuft
5. bei Abschluss `complete`
6. wenn nur pausiert/abgegeben wird: `release`

---

## Relevante Endpunkte

### Lesen
- `GET /tasks`
- `GET /tasks/{task_id}`
- `GET /tasks/{task_id}/events?after_seq=0`

### Schreiben
- `POST /tasks/{task_id}/claim`
- `POST /tasks/{task_id}/heartbeat`
- `POST /tasks/{task_id}/release`
- `POST /tasks/{task_id}/complete`

Wichtig: `task_id` in Pfaden URL-encoden.

Beispiel:
```text
owner/repo#123
```

wird zu:
```text
owner%2Frepo%23123
```

---

## Verhaltensregeln für Agenten

### 1. Keine fremden gültigen Leases kapern
Wenn der Service `409` liefert, ist das kein Einladungsschreiben zum Drängeln.

### 2. Heartbeats nur als aktueller Owner
Nicht einfach auf Verdacht senden.

### 3. `release` nicht als Synonym für `done` missbrauchen
Das erzeugt falsche operative Lage.

### 4. Bei Blockern ehrlich `blocked` kommunizieren
Nicht so tun, als liefe die Aufgabe weiter, wenn sie faktisch festhängt.

### 5. Änderungen über Events nachziehen
Wenn ein Task länger läuft, nicht in der eigenen Halluzination verharren.

---

## Wann ein Agent den Sync-Service nutzen sollte

Sinnvoll bei:
- paralleler Arbeit mehrerer Agenten
- GitHub-/Issue-bezogenen Aufgaben
- Review-/Ownership-Fragen
- Übergaben zwischen Agenten

Weniger nötig bei:
- sehr kleinen lokalen Ein-Datei-Doku-Fixes ohne Koordinationsrisiko

---

## Projektkontext für dieses Repo

In diesem Projekt ist der Sync-Service vor allem relevant für:
- parallele Bot-Arbeit
- Dashboard-/Task-Übersicht
- nachvollziehbare Ownership
- Vermeidung von doppelter Bearbeitung

Er ersetzt aber nicht:
- `git status`
- Lesen von `PROJECT_STATUS.md`
- gesunden Menschenverstand

---

## Typische Fehler

### Fehler 1 – Task bearbeiten ohne Claim
Folge: zwei Agenten schreiben gleichzeitig an demselben Thema vorbei.

### Fehler 2 – vergessen zu releasen oder zu completen
Folge: stale leases, falsche operative Lage.

### Fehler 3 – `complete` zu früh senden
Folge: Task wirkt abgeschlossen, obwohl nur ein Teil davon sauber ist.

### Fehler 4 – nur dem Dashboard glauben
Immer auch den echten Code-/Git-Zustand prüfen.

---

## Faustregel

Der Sync-Service ist ein **Koordinationswerkzeug**, kein Wahrheitsorakel.

Die Wahrheit im Projekt entsteht aus:
- Codezustand
- Git-Zustand
- `PROJECT_STATUS.md`
- sauberer Kommunikation zwischen Agenten
