# User Stories & Use Cases – Whispers of the Seven Kingdoms

Stand: 25.03.2026 | Erstversion basierend auf aktuellem Dashboard + bisherigem Feedback

## Rollen

| Rolle | Wer | Fokus |
|-------|-----|-------|
| **Produzent** | Eddi, Kevin, Iwan | Videos erstellen, Songs generieren, Kanal managen |
| **Reviewer** | Eddi | QA, Feedback, Freigabe vor Upload |
| **Zuschauer** | YouTube-Publikum | Konsumiert die Inhalte |

---

## Core Workflows (Prio A)

### UC-01: Neues Video von A bis Z erstellen
**Als** Produzent  
**will ich** ein Video komplett erstellen (Song → Video → Thumbnail → Upload)  
**damit** ich möglichst wenig manuelle Schritte habe.

**Aktueller Flow:**
1. `/admin/pipeline/new` → Haus wählen
2. Audio: "Neu generieren" auswählen ODER bestehenden Song aus Library nehmen
3. "Video erstellen" drücken
4. Wenn generiert: System erstellt Song → rendert Video → (optional) Upload
5. Wenn Library: Pipeline rendert direkt → (optional) Upload

**Erwartung:** Ein Klick, dann läuft alles automatisch durch. Status sehe ich auf der Workflow-Seite.

---

### UC-02: Song im Audio Lab generieren
**Als** Produzent  
**will ich** einzelne Songs generieren und vorhören  
**damit** ich Qualität prüfen kann bevor ein Video daraus wird.

**Aktueller Flow:**
1. `/admin/audio` → Haus/Prompt wählen, Parameter einstellen
2. "Generieren" drücken
3. Job läuft (Stable Audio auf GPU oder Kaggle)
4. Fertiger Song landet automatisch in der Library

**Erwartung:** Ich kann den Song direkt im Browser abspielen und dann entscheiden ob er gut genug ist.

---

### UC-03: Video-Ergebnis prüfen und freigeben
**Als** Reviewer  
**will ich** das fertige Video + Thumbnail + Metadaten sehen  
**damit** ich entscheiden kann ob es hochgeladen werden soll.

**Aktueller Flow:**
1. `/admin/pipeline/run/{id}` → Output-Dateien sehen
2. Video abspielen / Thumbnail anschauen
3. Manuell "Upload" klicken wenn OK

**Erwartung:** Vorschau direkt im Dashboard, keine Downloads nötig.

---

### UC-04: Library verwalten
**Als** Produzent  
**will ich** alle Songs, Thumbnails und Metadaten an einem Ort sehen  
**damit** ich den Überblick über mein Material habe.

**Aktueller Flow:**
1. `/admin/library` → Songs, Thumbnails durchblättern
2. Dateien hochladen oder aus Audio Lab generierte Tracks nutzen

**Erwartung:** Abspielen, löschen, umbenennen — alles im Dashboard.

---

## Operations & Monitoring (Prio B)

### UC-05: Projektstatus auf einen Blick
**Als** Produzent  
**will ich** auf der Startseite sofort sehen was läuft, was fertig ist, was Probleme hat  
**damit** ich nicht durch 5 Seiten klicken muss.

**Dashboard** (`/admin`) zeigt: letzter Run, aktive Jobs, Server-Status.

---

### UC-06: Bugs und Feature-Wünsche melden
**Als** Produzent  
**will ich** direkt im Dashboard ein Ticket erstellen  
**damit** ich nicht zu GitHub wechseln muss.

**Flow:** `/admin/tickets/new` → Formular ausfüllen → Ticket wird erstellt (später: auto GitHub Issue).

---

### UC-07: Pipeline-Queue überwachen
**Als** Produzent  
**will ich** sehen welche Jobs in der Warteschlange sind  
**damit** ich weiß wann mein Video dran ist.

**Flow:** `/admin/pipeline` → Queue-Banner zeigt running/waiting.

---

## Content Management (Prio C)

### UC-08: Shorts erstellen
**Als** Produzent  
**will ich** Kurzvideos (Shorts/Reels) aus bestehendem Material schneiden  
**damit** ich den Kanal auch mit kurzen Clips bespielen kann.

**Status:** Seite existiert (`/admin/shorts`), Feature noch in Entwicklung.

---

### UC-09: Dokumentation lesen
**Als** Produzent  
**will ich** nachschlagen wie Features funktionieren  
**damit** ich das Dashboard selbstständig nutzen kann.

**Flow:** `/admin/docs` → Themenübersicht → Einzelseite.

---

## Anti-Patterns (was NICHT passieren soll)

- ❌ User muss mehrere Seiten besuchen um ein Video zu erstellen
- ❌ Technische Logs/Fehler ohne Erklärung
- ❌ Buttons die nichts tun oder Seiten die 500 zurückgeben
- ❌ Features die nur Entwickler verstehen
- ❌ Manuelles Eingreifen wo Automatisierung möglich ist

---

## Offene Fragen (für nächstes Team-Gespräch)

- [ ] Wie oft wollt ihr Videos veröffentlichen? (Täglich, wöchentlich?)
- [ ] Soll der Upload immer manuell freigegeben werden oder gibt es "Auto-Publish"?
- [ ] Welche Seiten benutzt ihr nie / was ist überflüssig?
- [ ] Braucht ihr Mobile-Zugang (Handy) oder nur Desktop?
- [ ] Soll es Benachrichtigungen geben (Telegram, Email) wenn ein Video fertig ist?
