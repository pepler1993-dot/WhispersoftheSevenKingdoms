# Audio Strategy

## Zweck
Diese Seite fasst die aktuelle Audio-Strategie des Projekts zusammen.

Sie ersetzt nicht alle Detailreviews, aber sie verdichtet die operative Linie, damit nicht jeder durch vier halbe Entscheidungsdokumente waten muss.

---

## Kurzfassung

Die Audio-Seite ist der aktuell wichtigste technische Hebel.

**Kernaussage:**
- Kaggle ist kein verlässliches strategisches Fundament
- kurze Generierung + Looping ist ein starker praktischer Hebel
- lokaler GPU-Worker ist die bevorzugte langfristige Richtung
- Colab oder ähnliche Übergänge können pragmatisch sinnvoll sein

---

## Warum Audio das Kernproblem ist

Dashboard, Pipeline, Thumbnailing, Rendering und Metadaten sind bereits relativ weit.

Was das Gesamtsystem noch wirklich bremst, ist:
- reproduzierbare Audio-Erzeugung
- stabile Laufzeitumgebung
- Provider-/Infra-Entscheidung mit vertretbaren Kosten

---

## Kaggle – aktuelle Einordnung

Kaggle war attraktiv, weil:
- kostenlos
- GPU-Ressourcen prinzipiell verfügbar
- notebook-naher Workflow

Die operative Erfahrung zeigt aber:
- fehleranfällig
- instabil als Produktionsbasis
- für unseren Stack nicht vertrauenswürdig genug als Fundament

Die Doku sollte deshalb Kaggle nicht mehr als sichere Standardlösung verkaufen.

---

## Kurze Tracks + Looping

Das ist aktuell einer der stärksten Hebel.

Statt direkt sehr lange Rohtracks zu erzeugen:
- kürzere Audio-Stücke erzeugen
- danach in der Pipeline loopen
- crossfaden
- post-processen
- für lange YouTube-Versionen ausbauen

### Warum das stark ist
- weniger Rechenlast
- schnellere Tests
- besser für kostenlose oder begrenzte Ressourcen
- passt gut zum Sleep-Music-Use-Case

---

## Lokaler GPU-Worker

Langfristig die bevorzugte Richtung.

### Vorteile
- volle Kontrolle über Runtime und Versionen
- bessere Debugbarkeit
- kein Plattformroulette
- gute Automatisierbarkeit

### Nachteile
- initialer Setup-Aufwand
- GPU-/Treiber-/Infra-Themen müssen sauber gelöst werden

### Einordnung
Wenn stabile Hardware verfügbar ist, ist das die professionellste Lösung.

---

## Übergangslösungen

Mögliche Übergänge:
- Google Colab
- andere temporäre Notebook-/Cloud-Wege
- notfalls lokale CPU-Tests

Diese Wege sind eher Übergangs- oder Testpfade — nicht automatisch das finale Produktionsmodell.

---

## Architekturprinzip dahinter

Die Audio-Seite sollte **providerfähig** bleiben.

Das bedeutet:
- UI / Dashboard nicht zu hart an einen einzelnen Provider koppeln
- Pipeline nicht davon abhängig machen, wo das Audio herkommt
- Wechsel zwischen Kaggle / Colab / lokalem Worker / API-Provider technisch möglich halten

---

## Aktuelle strategische Linie

### Kurzfristig
- pragmatisch arbeitsfähig bleiben
- kurze Tracks + Looping nutzen
- Übergangsprovider nur als Mittel zum Zweck betrachten

### Mittelfristig
- lokalen GPU-Worker evaluieren / aufbauen
- Audio-Pfad stabilisieren
- klaren Standardpfad definieren

### Langfristig
- Audio als belastbaren Produktionsschritt industrialisieren
- Provider-Wechsel operativ beherrschbar halten

---

## Welche älteren Dokumente dazu relevant sind

Für tiefere Details:
- `../AUDIO_GENERATION_ALTERNATIVES_EVALUATION.md`
- `../AUDIO_GENERATION_ALTERNATIVES_FEEDBACK.md`
- `../AUDIO_GENERATION_ALTERNATIVES_SMITH_FEEDBACK.md`
- `../AUDIO_GENERATION_FEEDBACK_SMITH.md`

Diese Seiten enthalten mehr Rohanalyse und Feedback-Loop. Diese Seite hier ist die verdichtete Fassung.
