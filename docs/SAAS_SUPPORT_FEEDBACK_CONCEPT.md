# SaaS-Konzept: Feedback, Support und Feature Requests

**Stand:** 28.03.2026
**Ziel:** Definieren, wie der heutige interne Ticket-Bereich später als sinnvolle SaaS-Funktion weiterentwickelt werden kann.

---

## Ausgangslage

Der aktuelle Bereich **Tickets** ist vor allem ein internes Entwicklungs- und Ops-Werkzeug.
Für ein späteres SaaS-Produkt sollte dieser Bereich **nicht** als rohe interne Ticketansicht für Kunden sichtbar bleiben.

Stattdessen sollte er in klar verständliche, nutzerzentrierte Bereiche aufgeteilt werden.

---

## Zielbild für SaaS

Aus dem heutigen internen Ticket-System können später drei saubere SaaS-Bausteine entstehen:

1. **Feedback / Bug melden**
2. **Support / Help Center**
3. **Feature Requests**

Diese drei Bereiche haben unterschiedliche Nutzerziele und sollten im Produkt auch unterschiedlich dargestellt werden.

---

## 1. Feedback / Bug melden

### Ziel
Nutzer sollen schnell Probleme oder Unklarheiten melden können, ohne technische Vorarbeit leisten zu müssen.

### Typische User-Fragen
- "Hier stimmt etwas nicht"
- "Der Upload hat komisch reagiert"
- "Die Seite sieht kaputt aus"
- "Ich glaube da ist ein Fehler"

### UX-Prinzip
So wenig Hürde wie möglich.

### Empfohlene Eingabefelder
- Kategorie
  - Bug
  - UI/UX Problem
  - Falsches Ergebnis
  - Upload/Rendering Problem
- kurze Beschreibung
- erwartetes Verhalten
- tatsächliches Verhalten
- optional Screenshot hochladen
- optional Link zur betroffenen Seite / Run / Asset

### Wichtige Automationen
Das System sollte möglichst viel automatisch anhängen:
- aktuelle URL
- betroffener Workflow / Run / Job
- Browser / Gerät
- Zeitstempel
- User / Space
- letzter Fehlerstatus wenn vorhanden

### Was der User sehen sollte
- Bestätigung, dass das Feedback angekommen ist
- klare Referenznummer
- Status wie:
  - eingegangen
  - in Prüfung
  - gelöst

### Nicht zeigen
- interne Entwicklerlabels
- rohe Debug-Felder
- technische IDs ohne Erklärung

---

## 2. Support / Help Center

### Ziel
Nutzer sollen Hilfe bekommen, ohne direkt ein technisches Ticket schreiben zu müssen.

### Typische User-Fragen
- "Wie erstelle ich meinen ersten Run?"
- "Wie funktioniert Auto-Upload?"
- "Warum ist mein Run fehlgeschlagen?"
- "Wo ändere ich Presets oder Provider?"

### Bestandteile

#### a) Hilfe-Center
- kurze Anleitungen
- FAQ
- Schritt-für-Schritt Guides
- Troubleshooting für häufige Fehler

#### b) Kontext-Hilfe direkt im Produkt
- kleine Hilfelinks an kritischen Stellen
- "Was bedeutet dieser Status?"
- "Warum sehe ich das?"
- "Was soll ich als Nächstes tun?"

#### c) Support-Kontakt
- Kontaktformular
- optional Chat / Messenger / E-Mail
- optional Priorität je nach Plan

### Gute SaaS-Erwartung
Support ist nicht nur ein Formular, sondern ein **Hilfe-System**.

### Was der User sehen sollte
- Suchfeld: "Wobei brauchst du Hilfe?"
- Top-Hilfethemen
- Kontaktoption wenn Selbsthilfe nicht reicht

---

## 3. Feature Requests

### Ziel
Nutzer sollen produktive Ideen einreichen können, ohne dass daraus sofort rohe interne Tickets werden.

### Typische User-Wünsche
- "Ich brauche bessere Fortschrittsanzeigen"
- "Ich will Multi-Upload für Plattformen"
- "Ich will Vorlagen speichern"
- "Ich will Kalender/Scheduling"

### UX-Prinzip
Wünsche strukturiert erfassen, aber nicht wie ein Bug behandeln.

### Empfohlene Eingabefelder
- Titel
- Problem / Bedarf
- gewünschte Lösung
- warum das wichtig ist
- optional Kategorie
  - Workflow
  - Publishing
  - Library
  - Analytics
  - Team / Collaboration
  - API / Automation

### Mögliche SaaS-Erweiterung
- Voting / Upvotes
- Status:
  - gesammelt
  - geplant
  - in Arbeit
  - veröffentlicht
- Release-Hinweis, wenn Wunsch umgesetzt wurde

### Vorteil
Feature Requests werden so zu einem geordneten Produkt-Feedback-Kanal statt zu verstreuten Support-Nachrichten.

---

## Empfohlene Produktstruktur

Statt eines Menüpunkts **Tickets** könnte es später so aussehen:

### Option A: Ein Bereich „Hilfe & Feedback"
Unterpunkte:
- Hilfe-Center
- Problem melden
- Feature vorschlagen

### Option B: Zwei getrennte Bereiche
- **Help Center**
- **Feedback**

### Option C: Planabhängig
- Free/Creator: Hilfe-Center + Feedback-Form
- Studio/Enterprise: zusätzlich Support-Priorität / direkter Kontakt

---

## Interne Abbildung im System

Nach außen sieht der Nutzer nur die sauberen SaaS-Einstiege.
Intern können alle Eingänge weiterhin in ein gemeinsames Bearbeitungssystem laufen.

Beispiel:
- Bug melden → internes Ticket vom Typ `bug`
- Support-Anfrage → internes Ticket vom Typ `support`
- Feature Request → internes Ticket vom Typ `feature`

Das interne System darf komplex sein.
Die externe UX darf es nicht sein.

---

## Statusmodell für Nutzer

Empfohlenes einfaches Statusmodell:
- **Eingegangen**
- **In Prüfung**
- **Geplant**
- **Gelöst**
- **Veröffentlicht**

Nicht empfohlen für externe Nutzer:
- `triage`
- `blocked`
- `in_progress_backend`
- `awaiting_repro`
- andere interne Arbeitslabels

---

## Wichtige UX-Prinzipien

### 1. Kein internes Jira/GitHub-Gefühl für Kunden
Der Nutzer will Hilfe oder Feedback geben, nicht Entwicklerprozesse lernen.

### 2. Kontext automatisch sammeln
Je weniger der Nutzer manuell erklären muss, desto besser.

### 3. Fehler = Handlung
Wenn der Nutzer wegen eines Problems hier landet, muss klar sein:
- was schief lief
- was er tun kann
- ob das Team schon genug Infos hat

### 4. Schöne Bestätigung nach Absenden
Nicht einfach nur "erstellt", sondern:
- danke
- Referenznummer
- nächster Schritt
- geschätzte Reaktion falls relevant

### 5. Rückkanal wichtig
Wenn etwas gelöst oder veröffentlicht wurde, sollte der Nutzer das wiederfinden können.

---

## Mögliche spätere Erweiterungen

- In-App Changelog mit Bezug auf umgesetzte Feature Requests
- Vote-System für Wünsche
- KI-gestützte Hilfesuche
- automatische Vorschläge aus Fehlermeldungen
- kontextbasierte Hilfe je Seite / Workflow / Status
- Enterprise Support Inbox

---

## Empfehlung

Kurzfristig:
- internen Ticket-Bereich intern lassen
- nicht als finale SaaS-Lösung betrachten

Mittelfristig:
- daraus **Help Center + Feedback + Feature Requests** entwickeln
- externe UX sauber vom internen Bearbeitungssystem trennen

Langfristig:
- Support und Produktfeedback als echten Teil des SaaS-Erlebnisses ausbauen
- inklusive Status, Rückmeldung, Self-Service und sichtbarer Produktentwicklung
