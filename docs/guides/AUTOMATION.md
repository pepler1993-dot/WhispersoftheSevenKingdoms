# AUTOMATION – aktueller Stand und realistischer Ausbaupfad

## Zweck
Diese Seite beschreibt, **was im Projekt heute schon automatisiert ist**, was nur teilweise automatisiert ist und was noch offen bleibt.

Nicht Visionstheater, sondern realistischer Betriebsstand.

---

## Kurzfassung

Der aktuelle Kernpfad ist bereits weit automatisiert:
- Audio-Datei bereitstellen
- Metadaten laden
- Thumbnail erzeugen oder übernehmen
- Video rendern
- QA / Preflight laufen lassen
- optional YouTube hochladen

Die Schwachstelle ist nicht mehr nur "fehlende Automation", sondern vor allem die **stabile Audio-Erzeugung** als vorgelagerter Schritt.

---

## Was heute bereits automatisiert ist

## 1. Pipeline-Orchestrierung
Zentrale Datei:
- `pipeline/pipeline.py`

Automatisiert:
- Audio-Datei finden
- Metadaten laden
- Statusdatei fortschreiben
- Teilprozesse in sinnvoller Reihenfolge ausführen

---

## 2. Audio-bezogene Verarbeitung
Unter `pipeline/scripts/audio/`:
- Looping kurzer Tracks
- Audio-Postprocessing

Beispiele:
- `loop_audio.py`
- `post_process.py`

---

## 3. Thumbnail-Erzeugung
Unter:
- `pipeline/scripts/thumbnails/generate_thumbnail.py`

Automatisiert:
- Theme-basiertes Thumbnail erzeugen
- vorhandene Thumbnails alternativ übernehmen

---

## 4. Video-Rendering
Unter:
- `pipeline/scripts/video/render.py`
- `pipeline/scripts/video/render_animated.py`

Automatisiert:
- statischer Renderpfad
- optional animierter Renderpfad

---

## 5. Metadaten-Erzeugung
Unter:
- `pipeline/scripts/metadata/metadata_gen.py`

Automatisiert:
- Ableitung von Output-Metadaten für den Publish-Prozess

---

## 6. QA / Preflight
Unter:
- `pipeline/scripts/qa/preflight_metadata_report.py`
- `pipeline/scripts/qa/check-upload-completeness.js`

Automatisiert:
- Metadaten-Preflight
- Vollständigkeitsprüfung für Upload-Bausteine

---

## 7. Optionaler YouTube-Upload
Unter:
- `pipeline/scripts/publish/youtube_upload.py`

Automatisiert:
- Upload über vorbereiteten OAuth-Flow

Voraussetzung:
- gültige Credentials
- lokaler Token / sauberer OAuth-Zustand

---

## 8. Dashboard-gestützte Bedienung
Unter:
- `services/sync/`

Teilweise automatisiert / orchestriert:
- Eingaben erfassen
- Job-Verläufe und Status anzeigen
- Audio-Generator-Workflows begleiten
- Operations / Systemstatus darstellen

---

## Was nur teilweise automatisiert ist

## Audio-Erzeugung
Hier liegt die strategische Baustelle.

Vorhanden oder vorbereitet:
- Kaggle-basierte Audio-Erzeugung
- lokale Worker-/GPU-Richtung
- Stable-Audio-/Provider-Ansätze

Aber:
- das ist noch nicht überall gleich stabil
- nicht jede Doku darf so tun, als sei das schon fertig industrialisiert

---

## Was bewusst noch nicht vollautomatisch sein sollte

Bestimmte Dinge bleiben sinnvollerweise reviewbar oder manuell kontrolliert:
- finale Qualitätsprüfung von Output
- Veröffentlichung als `public`
- strategische Titel-/Beschreibungsauswahl
- Entscheidungen bei instabilen Audio-Pfaden

Vollautomatisierung ohne Review klingt geil, bis man automatisiert Schrott publiziert.

---

## Praktischer Ist-Workflow

### Datei-/Slug-basiert
1. Audio unter `data/upload/songs/`
2. Metadata unter `data/upload/metadata/`
3. optional Thumbnail unter `data/upload/thumbnails/`
4. Pipeline-Run starten
5. Output unter `data/output/youtube/<slug>/` prüfen

### Dashboard-gestützt
1. Haus / Stil / Eingaben im Dashboard
2. Audio-Job oder Pipeline-Job anstoßen
3. Status beobachten
4. Artefakte prüfen
5. optional Upload

---

## Empfohlener Ausbaupfad

### P0
- Audio-Erzeugung stabilisieren
- klaren Standardpfad definieren

### P1
- QA / Reports weiter ausbauen
- Fehlermeldungen und Recovery robuster machen

### P2
- Dashboard und Pipeline enger verzahnen
- weniger manuelle Doppelpflege

### P3
- zusätzliche Publishing-/Analytics-/Ops-Funktionen

---

## Nicht mehr die richtige Denke

Früher war die Frage oft: "Wie automatisieren wir das überhaupt?"

Heute ist die bessere Frage:

**Welcher Teil ist schon stabil automatisiert und welcher Teil braucht noch echte Betriebsreife?**

Das spart viel Bullshit-Planung.
