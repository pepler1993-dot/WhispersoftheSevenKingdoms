# 🎨 Whisper Studio – UI/UX Design Principles

## 1. Dark-First, Cinematic
Durchgehend dunkles Farbschema (`color-scheme: dark`). Panels mit subtilen Borders (`rgba(255,255,255,0.06-0.08)`) auf dunklem Hintergrund. Farbakzente nur gezielt über Gradient-Toplines (grün/blau für System, lila/pink für GPU, gold für Aktionen).

## 2. Progressive Disclosure
Komplexität wird schrittweise aufgedeckt: Haus wählen → Variante → Dauer → Config. Erweiterte Einstellungen in `<details>` versteckt. Der User sieht nur, was er gerade braucht.

## 3. Card-Based Layout
Alles sind Panels/Cards mit einheitlichem Radius (`12-14px`), 1px Border, leichtem Padding. Gauges, Stats, Tickets, Config – alles in Karten. Grid-basiert, responsiv (`auto-fit`, `minmax`).

## 4. Interaction = Visuelles Feedback
Selected States mit Glow + Border-Color-Shift (Haus-Farbe). Hover mit `translateY(-2px)` + Box-Shadow. Toggle-Buttons mit aktiver Gold-Tint. Nie ein Klick ohne sichtbare Reaktion.

## 5. Emoji als funktionale Icons
Emojis für Status-Indikatoren (🎬 🎵 ✅ 🐛), Kategorien und Quick-Stats. Lucide-Icons nur in der Navigation. Keine Icon-Overload – max 1 Emoji pro Element.

## 6. Minimale Text-Hierarchie
`Inter` als einzige Font. Titel `0.95rem/700`, Sub `0.7-0.72rem/muted`, Werte `1.3rem/800`. Keine großen Headlines – alles kompakt und scanbar.

## 7. Mobile-First Responsive
Grids brechen sauber um (4→2→1 Spalten). Bottom-Nav auf Mobile. Touch-Targets ausreichend groß. Sidebar verschwindet, Mobile-Header erscheint.

## 8. Status-Farbsystem
Konsistent:
- **Grün** = Erfolg / Online
- **Blau** = In Arbeit
- **Gold/Amber** = Offen / Warnung
- **Rot** = Fehler / Kritisch
- **Grau** = Geschlossen / Inaktiv

Immer als Dot + Badge-Combo.

## 9. Guided Workflow statt Formular-Wüste
Create-Flow ist kein langes Formular, sondern geführte Steps mit `step-card` Sections. Jeder Schritt hat eigene Überschrift. Scroll-Animations (`fadeSlide`) geben Orientierung.

## 10. Preset-Driven Defaults
Presets füllen alles vor – Titel, Mood, Audio, Thumbnail. Der User kann überschreiben, muss aber nicht. „Zero-Config to Launch" als Ziel.
