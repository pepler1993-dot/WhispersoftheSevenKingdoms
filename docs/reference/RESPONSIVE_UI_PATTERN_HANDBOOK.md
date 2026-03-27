# Responsive UI Pattern Handbook

Ziel: **Whisper Studio soll auf jedem Gerät sauber aussehen** — nicht nur "funktionieren", sondern visuell klar, effizient und konsistent bleiben.

Dieses Dokument ist das verbindliche Handbuch für responsive UI/UX im Projekt. Es orientiert sich an den aktuellen Stärken von **Overview** und **Create**, zieht aber daraus ein systematisches Muster statt Einzelfixes.

---

## 1. Produktziel

Whisper Studio ist kein klassisches CRUD-Backoffice, sondern ein **operatives Content-Studio**.
Die Oberfläche muss deshalb gleichzeitig können:

- **schnell scanbar** sein
- **viel Information** auf großen Screens effizient nutzen
- **mobil bedienbar** bleiben
- **komplexe Workflows** ohne Überforderung zeigen
- **visuell ruhig** bleiben trotz vieler Status, Karten, Aktionen und Panels

Die Kernregel:

> Die UI passt sich nicht nur an die Breite an — sie passt auch **Informationsdichte, Hierarchie, Interaktionsmuster, Schriftgrößen und Komponentenverhalten** an.

---

## 2. Grundprinzipien

### 2.1 Breite ist ein Feature, kein Problem
Große Screens dürfen nicht wie aufgeblasene Tablet-Layouts wirken.
Wenn viel Platz da ist, muss Whisper Studio:

- mehr Spalten nutzen
- größere Karten-Cluster bilden
- Sektionen parallel statt untereinander zeigen
- operative Information dichter, aber weiter klar lesbar darstellen

### 2.2 Mobile zuerst in Klarheit, Desktop zuerst in Dichte
Mobil heißt:

- Fokus
- kurze vertikale Pfade
- große Touch-Ziele
- klare Reihenfolge

Desktop heißt:

- parallele Informationsflächen
- weniger Scrollen
- bessere Vergleichbarkeit
- schnellere Orientierung

### 2.3 Komponenten skalieren, nicht nur Container
Responsive Verhalten darf nicht nur am Seiten-Wrapper hängen.
Sich anpassen müssen immer auch:

- Karten
- Stat-Module
- Buttons
- Tabs
- Typografie
- Badges
- Listen
- Formulargruppen
- Headline-Hierarchien
- Abstände

### 2.4 Jede Seite braucht einen klaren Primärmodus
Jede Seite muss einen dominanten Modus haben:

- **Overview** = beobachten und springen
- **Create** = konfigurieren und starten
- **Audio Lab** = generieren und Jobs verfolgen
- **Operations** = Zustand prüfen und Probleme finden

Responsive Änderungen dürfen diesen Primärmodus nicht verwässern.

### 2.5 Weniger Elemente, bessere Elemente
Wenn eine Karte oder Liste schwach ist, werden nicht mehr Labels ergänzt.
Stattdessen wird gefragt:

- Ist das Element überhaupt nötig?
- Ist die Information relevant?
- Kann dieselbe Information kompakter und besser gruppiert werden?

---

## 3. Responsive Zielbild nach Breakpoints

Nicht nur CSS-Breakpoints, sondern **Layout-Modi**.

### 3.1 XS / kleine Phones (`< 400px`)
Ziel:

- nur eine Hauptspalte
- große Touch-Flächen
- minimierte Sekundärinfos
- keine doppelte Navigation sichtbar

Regeln:

- nur 1 Spalte
- Stats maximal 2 pro Zeile
- Buttons full width, wenn nebeneinander zu eng
- Tabs horizontal scrollbar oder kompakt umbrechend
- Karteninfos maximal 2–3 Zeilen
- keine dekorativen Elemente mit hohem Platzverbrauch

### 3.2 Mobile (`400px – 767px`)
Ziel:

- klare Einspalten-Führung
- Panels untereinander
- Aktionen direkt sichtbar

Regeln:

- Main Content 1 Spalte
- aktive Jobs/Run-Karten 1 Spalte
- Formulare untereinander
- Sections mit knappen Überschriften
- sekundäre Metadaten kleiner und gedimmt

### 3.3 Tablet / Small Laptop (`768px – 1279px`)
Ziel:

- erste Parallelisierung
- bessere Übersicht ohne Überladung

Regeln:

- Stats 3–4 Spalten
- Overview-Module 2 Spalten, wenn sinnvoll
- Karten-Grids `minmax(...)` statt harte Spaltenzahlen
- Primäre CTAs bleiben prominent
- Sekundärbereiche dürfen einklappen oder tiefer rutschen

### 3.4 Desktop (`1280px – 1599px`)
Ziel:

- echtes Arbeitslayout
- weniger Scrollen
- parallele Sicht auf relevante Module

Regeln:

- Overview in 2–3 Spalten
- aktive Bereiche als Grid, nicht als vertikale Liste
- Panels sollen breite Screens sichtbar nutzen
- Content-Breite nicht künstlich klein halten

### 3.5 Wide / Ultra-wide (`>= 1600px`)
Ziel:

- hohe Informationsdichte ohne Leere
- keine unkontrollierten XXL-Zeilen

Regeln:

- breite Flächen in mehrere Module aufteilen
- lieber zusätzliche Spalten als überlange Karten
- Textblöcke nicht unendlich breit laufen lassen
- Überblicksmodule dürfen als Dashboard-Raster erscheinen
- Forms ggf. in Multi-Column-Abschnitte teilen

---

## 4. Layout-System

## 4.1 Seitencontainer
Globale Container dürfen **nicht unnötig hart begrenzen**.

Regel:

- globale Content-Bereiche: `width: 100%`
- `max-width` nur dort, wo es fachlich sinnvoll ist
- keine pauschale Desktop-Verengung für alle Seiten

Erlaubte Ausnahme:

- textlastige Doku-/Longform-Seiten
- schmale Formular-Dialoge
- dedizierte Leseflächen

Nicht erlaubt:

- produktive Studio-Seiten künstlich auf Blog-Breite begrenzen

## 4.2 Grid-Ebenen
Jede komplexe Seite soll maximal 3 klare Layout-Ebenen haben:

1. **Top Summary**
   - Stats
   - Hero/Status
   - Primäre Aktionen
2. **Main Work Area**
   - Hauptmodule / Kernlisten / Kernformulare
3. **Secondary Modules**
   - Shorts, Logs, Hinweise, Diagnostik, Kontext

## 4.3 Responsive Grid Patterns
Verbindliche Muster:

### Pattern A: Auto-fit card grid
Für Kartenlisten mit gleicher Priorität.

```css
grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
```

Nutzen:
- skaliert sauber
- kein starres Breakpoint-Gefrickel
- nutzt Breite automatisch

### Pattern B: Primary + secondary dashboard split
Für Seiten wie Overview / Operations.

```css
grid-template-columns: minmax(0, 1.2fr) minmax(0, 1.2fr) minmax(280px, 0.9fr);
```

Nutzen:
- zwei starke Hauptbereiche
- ein schmalerer Kontext-/Nebenbereich

### Pattern C: Single-column collapse
Unter Tablet:

```css
grid-template-columns: 1fr;
```

Pflicht:
- niemals Layout-Reste halbkaputt lassen
- komplette, saubere Einspalten-Logik

---

## 5. Komponentenregeln

## 5.1 Karten
Karten sind das Standardmuster für Whisper Studio.

Jede Karte braucht:

- klaren Titel
- Status oder visuelle Einordnung
- maximal 2–5 relevante Infos
- große klickbare Fläche
- klare Hover-/Touch-Reaktion

Karten dürfen nicht:

- Rohdatenwüsten sein
- zu viele Badges tragen
- Slugs zeigen, wenn Nutzer sie nicht brauchen
- mehrere konkurrierende Primärinformationen enthalten

Responsive Regeln:

- Desktop: kompakter, aber dichter
- Mobile: mehr vertikaler Raum, weniger Meta-Infos
- gleiche Karte darf je nach Breakpoint weniger Details zeigen

## 5.2 Stat Cards
Stat Cards sind für Überblick, nicht Diagnose.

Immer zeigen:

- Zahl
- Label
- eventuell Statusfarbe

Nie zeigen:

- längere Erklärtexte
- technische IDs
- unnötige Dekoration

Responsive Regeln:

- XS: 2 pro Zeile
- Mobile: 2–3 pro Zeile
- Desktop: auto-fit

## 5.3 Buttons
Buttons müssen auf jeder Größe sauber funktionieren.

Regeln:

- Primär-CTA immer klar erkennbar
- Sekundär-Buttons visuell schwächer
- Danger klar getrennt
- auf kleinen Screens lieber full width als gequetscht

Mindestanforderungen:

- klare Padding-Skalierung
- konsistente Icon/Text-Abstände
- kein abgeschnittener Text

## 5.4 Tabs
Tabs sind Standard für Bereichswechsel auf derselben Ebene.

Nutzen für:

- Neues Video / Übersicht
- Audio Lab / Jobs / Logs
- zukünftige Settings-Bereiche

Regeln:

- visuell klar aktiv/inaktiv
- mobil scrollbar oder umbrechend
- nicht zu viele Tabs pro Ebene
- keine Mischung aus Tabs und konkurrierenden Buttons für denselben Kontext

## 5.5 Formulare
Forms müssen auf Desktop dichter, auf Mobile linearer werden.

Regeln:

- Desktop: Gruppen und sinnvolle 2er-/3er-Raster
- Mobile: strikt untereinander
- Labels kurz und eindeutig
- Hilfetexte nur, wenn nötig
- Standardwerte sichtbar, aber nicht laut

Für Create besonders wichtig:

- keine unnötige Reihenfolge-Komplexität
- Abschnitte klar voneinander trennen
- primärer Flow zuerst, Expertenoptionen später

---

## 6. Typografie-System

Responsive Typografie darf nicht statisch sein.

## 6.1 Headline-Hierarchie
- `h1`: Seitenidentität
- `h2`: Bereichsebene
- `h3`: Untergruppe / Karten-Substruktur

Regeln:

- große Screens: mehr Luft und stärkere Hierarchie
- kleine Screens: kompakter, aber weiterhin klar unterscheidbar

## 6.2 Fließtext / Meta / Labels
Drei funktionale Ebenen:

1. **Primary text**
   - Titel, Kernzahlen, Hauptinfos
2. **Secondary text**
   - Untertitel, Datumsinfos, Zusatzkontext
3. **Utility text**
   - Labels, Badges, Mini-Metadaten

Pflicht:
- Meta-Texte nie gleich laut wie Hauptinfos
- kleine Texte nur dort, wo sie wirklich sekundär sind
- Buttons und Inputs nicht zu klein machen

## 6.3 Responsive Schriftregeln
- große Displays: Schrift leicht größer oder luftiger
- mobile Displays: kompakter, aber nicht winzig
- keine Seite soll auf Mobile „Desktop in klein“ sein

---

## 7. Spacing-System

Die Seite wirkt nur dann hochwertig, wenn Abstände systematisch sind.

Verbindliche Ebenen:

- **8px**: Mikro-Abstand
- **12px**: kleine Gruppierung
- **16px**: Standard-Abstand
- **24px**: Bereichsabstand
- **32px**: große Trennung
- **48px**: selten, nur für große heroartige Flächen

Regeln:

- enge Infos = 8–12px
- Karten-/Panel-Inhalt = 12–20px
- Sektionen = 24–32px
- kein wild gemischtes Spacing pro Seite

---

## 8. Responsive Verhaltensregeln pro Kernseite

## 8.1 Overview
Overview ist ein **Operations-Dashboard**.

Soll auf großen Screens:

- mehrere Module parallel zeigen
- aktive Bereiche sichtbar priorisieren
- letzte Runs/Jobs/Shorts nebeneinander zeigen
- keine toten Leerräume lassen

Soll mobil:

- Stats oben
- aktive Jobs direkt danach
- restliche Module untereinander

## 8.2 Create
Create ist ein **Flow**, kein Dashboard.

Soll auf großen Screens:

- Konfigurationsgruppen nebeneinander zeigen, wenn sinnvoll
- aber nie den Flow zerstören

Soll mobil:

- strikt linear sein
- immer nur die nächste sinnvolle Entscheidung betonen

## 8.3 Audio Lab
Audio Lab ist eine Mischseite aus:

- Konfiguration
- Startpunkt
- Job-Verfolgung

Soll auf großen Screens:

- optionalen Kontext (Haus/Variante) klar oben zeigen
- Jobbereiche getrennt von Formularbereichen halten
- Logs und neue Jobs nicht im gleichen visuellen Raum vermischen

## 8.4 Operations
Operations darf dichter sein als Studio-Seiten.

Hier ist mehr technische Information okay, aber:

- trotzdem responsiv
- trotzdem klar gruppiert
- keine unkontrollierten Tabellenwüsten auf kleineren Geräten

---

## 9. Anti-Patterns

Diese Dinge sollen künftig aktiv vermieden werden:

### 9.1 Globales Breitenproblem mit Einzelfixes lösen
Nicht nur den Outer Container anfassen und hoffen, dass damit alles gut wird.

### 9.2 Leere Desktopflächen durch Mobile-Denken
Wenn ein Desktop groß ist, müssen Module anders angeordnet werden.

### 9.3 Zu viele irrelevante Infos in Karten
Wenn Nutzer den Slug nicht brauchen, kommt er weg.

### 9.4 Listen, wo Karten sinnvoller wären
Für aktuelle/letzte Inhalte sind Karten oft besser scanbar als Listen.

### 9.5 Gleiche Komponente auf allen Breakpoints identisch behandeln
Responsive Design ist Anpassung, nicht Schrumpfung.

---

## 10. Konkreter Umsetzungsplan

## Phase 1 — Foundations
Ziel: responsive Basis vereinheitlichen.

1. globales Layout-Audit aller Studio-Seiten
2. zentrale Tokens für:
   - Container
   - Grid
   - Spacing
   - Typografie
   - Button-Größen
3. harte `max-width`-Bremsen dokumentieren und nur dort erlauben, wo fachlich sinnvoll
4. wiederverwendbare Grid-Patterns definieren

Ergebnis:
- keine zufälligen Breitenentscheidungen mehr
- gleiche Breakpoint-Logik über alle Kernseiten

## Phase 2 — Core Studio Pages
Ziel: wichtigste Nutzerflächen konsistent machen.

Seiten:
- Overview
- Create
- Audio Lab
- Pipeline Übersicht
- Pipeline Run Detail

Für jede Seite:
1. Primärmodus definieren
2. Desktop-Layout definieren
3. Tablet-Layout definieren
4. Mobile-Layout definieren
5. Komponentenregeln festhalten

## Phase 3 — Component Library im Projektstil
Ziel: Muster statt Einzel-CSS.

Bausteine:
- Summary Card
- Status Card
- Metric Card
- Active Job Card
- Asset Card
- Filter Chips
- Tab Bars
- Responsive Panel Header
- Dense Table Wrapper
- Split Form Sections

Ergebnis:
- neue Seiten werden schneller konsistent
- weniger visuelle Drift

## Phase 4 — Responsive QA System
Ziel: nicht wieder in Einzelfehler zurückfallen.

Pflicht-Viewport-Set für Reviews:
- 390 × 844
- 768 × 1024
- 1366 × 768
- 1536 × 960
- 1920 × 1080
- 2560 × 1440

Für jede relevante UI-Änderung prüfen:
- wirkt die Seite ausgewogen?
- gibt es Leerräume ohne Funktion?
- brechen Texte/Buttons um?
- bleiben Klickflächen gut?
- stimmen Reihenfolge und Priorität auf Mobile?

---

## 11. Konkrete technische Regeln für dieses Repo

### 11.1 Global
- `.content` darf Studio-Seiten nicht künstlich deckeln
- Seitenmodule müssen Breite selbst sinnvoll nutzen

### 11.2 Dashboard
- aktive Bereiche immer Grid-basiert
- Hauptmodule auf Desktop parallel
- Kartenlisten mit `auto-fit/minmax`

### 11.3 Forms
- Formularblöcke nie mit starren Desktop-Maßen bauen
- auf Mobile immer sauber auf 1 Spalte kollabieren

### 11.4 Buttons und Actions
- Header-Actions umbrechbar
- auf kleinen Screens notfalls full width
- Primäraktion immer zuerst sichtbar

### 11.5 Typography
- keine zu kleinen Metatexte unter 0.68rem in produktiven Kernflows
- keine riesigen H1s ohne Gegensteuerung auf Mobile

---

## 12. Definition of Done für responsive Whisper-Studio-UI

Ein Feature gilt erst dann als visuell fertig, wenn:

- es auf Mobile, Tablet, Laptop und großem Desktop geprüft wurde
- keine sinnlosen Leerflächen dominieren
- Karten, Buttons, Schrift und Panels mit skalieren
- die Informationshierarchie auf allen Größen klar bleibt
- keine irrelevanten technischen Infos angezeigt werden
- die Oberfläche auf großen Screens **reicher**, nicht nur **breiter** wird

---

## 13. Nächste direkte Aufgaben

1. **Responsive Audit** für Overview, Create, Audio Lab, Pipeline Runs, Ops
2. zentrale **Layout-Utilities** in `admin.css` definieren
3. Dashboard-Komponenten in wiederverwendbare Muster überführen
4. Audio Lab anhand dieses Handbuchs umbauen
5. Sichtprüfung auf allen Zielgrößen als feste Checkliste etablieren

---

## Kurzfassung

Whisper Studio soll responsive sein auf drei Ebenen:

1. **Container** passen sich an
2. **Layouts** ordnen sich neu
3. **Komponenten** verändern Dichte, Größe und Verhalten

Nicht ausreichend ist:

- nur Breite zu erhöhen
- nur Breakpoints einzubauen
- nur Mobile-Fallbacks zu haben

Richtig ist:

- jede Seite als System aus Informationsdichte, Priorität, Grid und Interaktion zu denken
- und dieses System über das ganze Produkt konsistent anzuwenden
