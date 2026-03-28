# Audio Pipeline Sleep Optimization – Whispers of the Seven Kingdoms

## Ziel

Diese Spezifikation beschreibt, wie die bestehende Audio-Pipeline so umgebaut werden soll, dass die Qualität der generierten Tracks deutlich steigt, **mit Fokus auf Einschlafmusik**.

Wichtige Rahmenbedingungen:
- weiter **kostenlos / lokal** nutzbar
- weiterhin auf **Stable Audio Open** als Basismodell
- optimiert für **Sleep / Deep Relaxation / Background Listening**
- Repetition nach **30–60 Minuten** ist akzeptabel
- Ziel ist **nicht** maximale musikalische Abwechslung, sondern **maximale Konsistenz, Ruhe und Schlaftauglichkeit**

---

## Kurzfassung der Hauptprobleme

Die aktuelle Pipeline hat vier Hauptschwächen:

1. **Zu viele Prompt-Ereignisse**
   - Viele Prompts enthalten markante Einzelereignisse wie Horns, Bells, Howls, Thunder, Laughter, Clock Ticks, Footsteps etc.
   - Das macht die Tracks atmosphärisch, aber nicht schlaffreundlich.

2. **Zu stark wechselnde Identität zwischen Clips**
   - Wenn jeder 30s-Clip einen deutlich anderen Charakter hat, kaschiert ein Crossfade nur den Schnitt, aber nicht den Stilbruch.

3. **Zu generisches Post-Processing**
   - Bass-Boost + Höhenreduktion + Reverb + Loudnorm + Limiter macht viele Tracks dumpf, matschig und zu dicht.

4. **Zu wenig echte Unique-Dauer vor dem Lang-Loop**
   - 20 Minuten Material auf 3 Stunden zu strecken ist technisch machbar, klingt aber auf Dauer schnell künstlich oder repetitiv im negativen Sinn.

---

## Neues Grundprinzip

Die Pipeline soll von diesem alten Modell:

> viele kleine Szenen + viele Details + Crossfades + langes Looping

auf dieses neue Modell umgestellt werden:

> wenige stabile Klangwelten + minimale kontrollierte Variation + zurückhaltendes Processing + längere echte Unique-Phase

Für Sleep-Audio gilt:
- weniger Vordergrund
- weniger Überraschung
- weniger Erzählung
- weniger Ereignisse
- mehr Stabilität
- mehr konstante Textur
- mehr gleichmäßige Klangidentität

---

# 1. Sleep-First Audio Design Rules

## 1.1 Erlaubte Elemente

Folgende Elemente sind für Sleep-Audio grundsätzlich geeignet:
- drones
- pads
- sehr einfache 2–4-Noten-Motive
- weiche Streicherflächen
- felt piano sehr sparsam
- sehr dezente Flöten oder Holzbläser
- Wind, Wasser, Feuer, Raumtexturen
- leises Holzknarzen
- sehr langsame Harmoniebewegung
- geringe Event-Dichte
- sehr weiche Attacken

## 1.2 Elemente, die stark reduziert oder verboten werden sollen

Diese Elemente stören Schlaf oder wirken zu narrativ:
- wolf howl
- horn call
- bell strike / bell tower chime
- clock tick
- footsteps
- laughter
- chant-like foreground
- armor resonance / metallic foreground hits
- thunder cracks / lightning strike accents
- bird calls in Vordergrundrolle
- whale calls / dragon growls / animal spotlight events
- battle references
- starke Solomelodien
- auffällige perkussive Impulse
- alles mit Alarm- oder Signalfunktion

## 1.3 Grundregel

Die Welt soll **spürbar**, aber nicht **aufdringlich erzählerisch** sein.

Atmosphäre ja. Szenische Einzelereignisse nein.

---

# 2. Neue Prompt-Architektur

Die bisherige Struktur mit vielen stark unterschiedlichen Variant-Prompts soll ersetzt werden durch ein dreistufiges System.

## 2.1 Ebene A – House Base DNA

Diese Ebene definiert den Kernklang eines Hauses.

Beispiel Stark:
- dark medieval fantasy sleep ambient
- 58–62 BPM
- low cello drones
- soft choir pad
- cold wind texture
- sparse felt piano motif
- long hall reverb
- warm low mids
- soft highs
- no vocals
- no sharp percussion
- no sudden dynamic jumps

Diese DNA bleibt für einen ganzen Trackblock stabil.

## 2.2 Ebene B – Variant Scene Layer

Die Variant färbt nur den Raum leicht um, verändert aber nicht die musikalische Identität.

Beispiel Stark:
- winterfell → hearth, snow, stone hall
- godswood → wood, leaves, stream, forest air
- the_crypts → stone chamber, low resonance, drip
- beyond_winterfell → open wind, tundra, sparse wilderness
- the_long_night → deep blizzard, near-static frozen texture

## 2.3 Ebene C – Clip Modifier

Pro Clip werden nur kleine Variationen erlaubt:
- more drone, less melody
- slightly more wind
- no piano in this clip
- thicker choir pad
- darker tone, less top end
- almost static texture
- slightly thinner arrangement

Wichtig:
- **Keine komplett neuen Szenen pro Clip**
- **Keine harte Round-Robin-Dramaturgie**
- **Keine völlig andere Instrumentierung pro Clip**

---

# 3. Neue house_templates-Struktur (Audio v2)

Die bestehenden `variant_prompts` sollten mittelfristig durch eine strukturiertere Audio-Sektion ergänzt oder ersetzt werden.

Beispiel:

```json
{
  "audio_design": {
    "base_prompt": "...",
    "negative_prompt": "...",
    "clip_roles": [
      "foundation",
      "texture",
      "motif",
      "breathing_space"
    ],
    "safe_events": [
      "wind",
      "water",
      "fire",
      "soft wood creak"
    ],
    "forbidden_events": [
      "howl",
      "horn",
      "bell strike",
      "laughter",
      "thunder crack",
      "footsteps",
      "clock tick"
    ],
    "mix_profile": {
      "brightness": "low",
      "movement": "very_low",
      "dynamic_range": "narrow",
      "foreground_density": "very_low"
    },
    "clip_blueprints": [
      {
        "role": "foundation",
        "modifier": "mostly drone, no discernible melody, stable tone"
      },
      {
        "role": "texture",
        "modifier": "slightly more wind and room texture, no focal sound"
      },
      {
        "role": "motif",
        "modifier": "tiny 3-note felt piano motif, very sparse, buried in mix"
      },
      {
        "role": "breathing_space",
        "modifier": "thinner arrangement, less low end, almost static"
      }
    ]
  }
}
```

---

# 4. Generation Pipeline v2

## 4.1 Clip-Länge erhöhen

Aktuell:
- Default 30s

Empfehlung:
- auf **44–46s** erhöhen

Grund:
- Stable Audio Open unterstützt bis zu ca. 47 Sekunden
- längere Clips reduzieren die Zahl der Übergänge
- weniger Übergänge = weniger hörbare Stilbrüche

## 4.2 Prompt-Stabilität pro Block

Pro 20-Minuten-Block:
- **eine stabile Klang-DNA**
- nur kleine Modifikatoren pro Clip

Nicht mehr:
- jeder Clip als eigene Mini-Szene mit neuer Instrumentierung und neuen Ereignissen

## 4.3 Rollenverteilung pro Block

Empfohlene Verteilung:
- 50% foundation
- 25% texture
- 15% breathing_space
- 10% motif

Erklärung:
- **foundation** = stabile Bettdecke
- **texture** = leichte Oberflächenbewegung
- **breathing_space** = Entdichtung
- **motif** = sehr sparsame musikalische Wiedererkennbarkeit

## 4.4 Inference Tests

Nicht blind auf Standardwerten bleiben.

Testmatrix anlegen für:
- 30s vs 46s
- 50 Steps vs 60 Steps vs 70 Steps
- alte Round-Robin-Prompts vs neue Base-DNA + Modifier
- altes Post-Processing vs reduziertes Post-Processing

Bewertungskriterien:
- Konsistenz
- Müdigkeits-/Schlaf-Faktor
- hörbare Übergänge
- Mumpf / Härte
- gefühlte Wiederholung nach 20 Minuten

---

# 5. Unique-Dauer vor Lang-Loop erhöhen

## Aktueller Zustand
- ca. 20 Minuten generiert
- auf 3 Stunden geloopt

## Neuer Zielzustand
Mindestens:
- **3 Blöcke à 20 Minuten** erzeugen
- daraus **60 Minuten Unique-Material** bauen
- erst danach auf 3 Stunden verlängern

Alternativ:
- 4 Blöcke à 15 Minuten

Vorteil:
- Repetition wird viel später wahrgenommen
- die Langform wirkt natürlicher
- selbst bei Sleep-Audio ist 60 Minuten Unique-Material deutlich stärker als 20 Minuten

---

# 6. Stitching verbessern

## 6.1 Nicht nur linear in Eingabereihenfolge stitchen

Aktuell werden Clips im Wesentlichen technisch verkettet.

Neu:
- Clips nach **klanglicher Ähnlichkeit** sortieren
- keine stark unterschiedlichen Clips direkt nebeneinander

## 6.2 Empfohlene technische Analyse pro Clip

Vor dem Stitching Metriken berechnen:
- RMS / perceived loudness
- spectral centroid
- low-end energy
- tail-noise level
- intro-noise level
- transient roughness
- optional: simple similarity score tail(A) vs intro(B)

## 6.3 Stitching-Logik

Ziel:
- dunkler Clip → dunkler Clip
- luftiger Clip → luftiger Clip
- dichter Clip → etwas dichterer Clip
- breathing-space nicht direkt auf stark motivischen Clip

So entstehen weniger abrupte Übergänge.

---

# 7. Crossfade-Regeln

## 7.1 Crossfades zwischen generierten Clips

Aktuell:
- 4s exponentieller Crossfade

Empfehlung:
- **2.5–3.5s** als Standard testen

Grund:
- lange Crossfades machen heterogene Clips oft nur matschiger
- kürzere, sauber platzierte Crossfades funktionieren bei Sleep-Material meist besser

## 7.2 Crossfades im Longform-Loop

Aktuell:
- 8s tri

Empfehlung:
- bei sehr dronigen Tracks: **6–10s**
- bei motivischeren Tracks: **4–6s**

Wichtig:
- Loop-Schnitt nur an Stellen mit geringer Event-Dichte
- keine klaren melodischen Phrasen hart in den Loop-Schnitt setzen

## 7.3 Nicht nur A mit A loopen

Statt einen einzigen Block mit sich selbst zu kreuzen:
- A → B → C → A → B → C
- oder A → B → C → C → B → A

Das wirkt organischer als permanentes Selbstcrossfading desselben 20-Minuten-Stücks.

---

# 8. Post-Processing neu aufsetzen

## 8.1 Problem der aktuellen Kette

Aktuell sinngemäß:
- EQ mit Bass-Boost
- Höhenreduktion
- Reverb (`aecho`)
- Loudnorm
- Limiter

Risiken:
- zu viel Low-End
- Tiefmitten-Mumpf
- zu wenig Luft
- Hall-Suppe
- zu dichter, dumpfer Gesamteindruck

## 8.2 Zielklang für Sleep-Audio

Der Zielklang soll sein:
- weich
- ruhig
- leicht dunkel
- nicht dumpf
- nicht boomy
- nicht zu diffus
- nicht zu laut

## 8.3 Neue Standardkette

Empfohlene Reihenfolge:
1. sanfter Highpass bei **25–30 Hz**
2. optional kleine Absenkung bei **180–320 Hz**, falls Mumpf entsteht
3. optional leichte Absenkung bei **2.5–4.5 kHz**, falls Härten auftreten
4. nur sehr dezenter Reverb, **nur wenn der Rohclip zu trocken ist**
5. milde Loudness-Normalisierung
6. Limiter nur als Schutz, nicht als Klangmacher

## 8.4 Dinge, die standardmäßig entfernt oder reduziert werden sollten

- pauschaler +3 dB Bass-Boost bei 80 Hz
- pauschaler starker Höhen-Cut ab 4 kHz
- `aecho` als Standardraum für alles
- zu aggressive LUFS-Normalisierung
- Limiter als finaler Lautmacher

## 8.5 Grundregel

Für Sleep-Audio ist **weniger Bearbeitung oft besser als mehr Bearbeitung**.

---

# 9. House-spezifische Leitlinien

## 9.1 Häuser, die stark von Drones und Near-Static Texture profitieren

Diese Houses sollten eher minimalistisch bleiben:
- Stark
- The Wall
- Greyjoy
- Targaryen

Empfehlung:
- Melodie stark begrenzen
- Fokus auf Raum, Wind, Resonanz, Drones, langsame Pads

## 9.2 Häuser, die etwas musikalischer sein dürfen

Diese Houses dürfen etwas mehr harmonische Bewegung haben:
- Lannister
- Tyrell
- Tully
- Arryn
- Martell

Aber trotzdem:
- keine virtuosen Soli
- keine ornamental überladenen Flötenlinien
- keine dominanten Glocken- oder Signalereignisse

## 9.3 Baratheon als Sonderfall

Baratheon ist aktuell oft zu dramatisch.

Problematische Elemente:
- thunder
- lightning
- horn
- war drum heartbeat
- battlefield remnants

Empfehlung:
Baratheon intern in Sleep-Submodes unterteilen:
- `storm_outside_safe`
- `hall_inside_safe`
- `coastal_drift_safe`

Also weniger Drama, mehr gleichmäßiges Wetterbett.

---

# 10. Prompt-Beispiele für Audio v2

## 10.1 Stark – Winterfell

```text
dark medieval fantasy sleep ambient, 60 BPM, low cello drone, very soft felt piano motif used sparingly, distant choir pad buried in the mix, cold wind texture, long hall reverb, soft highs, warm low mids, minimal movement, deeply calming, no vocals, no sharp transients, no percussion, no bells, no animal calls, no sudden dynamic changes
```

## 10.2 Lannister – Casterly Rock

```text
warm royal sleep ambient, 58 BPM, soft harp harmonics, warm string pad, candlelit stone hall atmosphere, very gentle harmonic movement, luxurious but restrained, stable mix, soft top end, no vocals, no percussion, no bell strikes, no solo flourishes, no dramatic swells
```

## 10.3 The Wall – Beyond the Wall

```text
extreme frozen dark sleep ambient, barely perceptible pulse, deep sub drone, distant wind sheet, crystalline high texture very low in the mix, vast empty space, ancient frozen stillness, almost no melodic content, no horns, no impacts, no sharp ice cracks, no sudden movement, no hope, no rhythm
```

## 10.4 Martell – Desert Night

```text
warm desert night sleep ambient, 54 BPM, deep warm drone, very soft oud harmonics used sparsely, desert wind texture, distant fountain resonance, stable low movement, intimate and expansive, no vocals, no percussion, no market chatter, no bells, no dramatic ornamentation
```

---

# 11. Regeln für bestehende house presets

## 11.1 Bestehende Prompts nicht 1:1 weiterverwenden

Viele aktuelle Prompts sind atmosphärisch stark, aber zu ereignisreich.

Sie sollen nicht direkt gelöscht werden, aber in zwei Gruppen aufgeteilt werden:

### A. Sleep-Safe
Direkt für Einschlafmusik geeignet

### B. Cinematic / Active Listening
Für spätere andere Modi geeignet:
- ambiance
- study
- fantasy atmosphere
- soundtrack-like listening

## 11.2 Neues Tagging-System für Prompt-Bausteine

Empfehlung:
- `sleep_safe: true/false`
- `foreground_density: very_low/low/medium`
- `event_density: very_low/low/medium`
- `melodic_focus: none/sparse/moderate`
- `risk_flags: [horn, bell, howl, thunder, footsteps, laughter, chant]`

So kann die Pipeline automatisch sichere Prompts bevorzugen.

---

# 12. Looping-Strategie für 3 Stunden

## Ziel
Die Langfassung soll nach einiger Zeit repetitiv werden dürfen, aber nicht künstlich auffallen.

## Empfehlung
- 60 Minuten Unique-Material erzeugen
- daraus 3 Stunden bauen
- Segment-Reihenfolge variieren
- nur ähnliche Teile direkt crossfaden

Beispiel:
- Block A: foundation-heavy
- Block B: slightly more texture
- Block C: slightly more breathing-space

Dann:
- A → B → C → A → B → C

oder:
- A → B → C → B → A → C

---

# 13. Empfohlene Prioritäten für die Umsetzung

## Priorität 1
1. alle foreground events aus Sleep-Prompts entfernen oder stark reduzieren
2. Base-Prompt + Modifier-System einführen
3. Clip-Länge auf 44–46s erhöhen

## Priorität 2
4. 60 Minuten Unique-Material statt 20 Minuten erzeugen
5. Post-Processing deutlich entschärfen
6. Sleep-Safe Prompt-Tagging einführen

## Priorität 3
7. ähnlichkeitsbasiertes Stitching implementieren
8. House-spezifische Audio-v2-Struktur ausrollen
9. Loop-Arrangement intelligent statt stumpf bauen

---

# 14. Konkrete Umsetzungsschritte für Agents

## Agent Task 1 – Prompt Refactor
- alle House-Varianten analysieren
- Sleep-unsafe Elemente markieren
- neue `base_prompt`, `negative_prompt`, `clip_blueprints` definieren
- alte `variant_prompts` optional als cinematic fallback archivieren

## Agent Task 2 – Generation Update
- Default-Clip-Länge von 30s auf 44–46s erhöhen
- Base-DNA + Modifier pro Block nutzen
- Rollenverteilung foundation / texture / motif / breathing-space einführen

## Agent Task 3 – Stitching Update
- Analysemetriken pro Clip erfassen
- ähnliche Clips bevorzugt aneinanderreihen
- Crossfade-Länge dynamisch nach Dichte / Ähnlichkeit wählen

## Agent Task 4 – Post-Processing Update
- Presets neu abstimmen
- Bass-Boost standardmäßig entfernen
- Höhen nicht pauschal absenken
- Reverb stark reduzieren
- Loudness entspannter fahren

## Agent Task 5 – Longform Assembly
- mehrere 20-Minuten-Blöcke erzeugen
- mindestens 60 Minuten Unique-Material bauen
- Segment-Reihenfolge für 3h intelligent arrangieren

## Agent Task 6 – Evaluation
- A/B-Tests mit alten und neuen Pipelines durchführen
- Blind-Bewertung nach Schlaf-Faktor, Konsistenz, Übergängen, Mumpf, Wiederholung
- beste Kombination als neue Default-Pipeline setzen

---

# 15. Endziel

Die neue Pipeline soll Tracks erzeugen, die:
- ruhiger sind
- homogener sind
- weniger künstlich zusammengesetzt wirken
- besser einschlaffähig sind
- trotz Stable Audio Open deutlich hochwertiger wahrgenommen werden

Das Hauptziel ist **nicht maximale musikalische Komplexität**, sondern:

> maximale Ruhe, maximale Kohärenz, minimale Störung.

