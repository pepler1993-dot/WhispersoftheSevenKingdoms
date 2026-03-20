# Proof of Concept – erster minimaler Workflow

Ziel: Einen **kleinsten realen End-to-End-Workflow** definieren, der von einem bereits generierten Song bis zu einem YouTube-fähigen Upload-Paket führt.

Dieser PoC soll bewusst **klein, testbar und reproduzierbar** sein.

---

## 1. Ziel des PoC

Der erste Proof of Concept soll zeigen, dass das Projekt technisch funktioniert, ohne sofort alle Plattformen und Sonderfälle abzudecken.

### Erfolgsdefinition
Ein einzelner Song-Datensatz durchläuft erfolgreich:
1. Input-Erfassung
2. Metadaten-Validierung
3. Video-Erstellung aus Audio + Bild
4. Thumbnail-Erstellung
5. Paketbau für YouTube
6. Preflight-Check

### Noch nicht Teil des ersten PoC
- vollautomatischer echter Upload
- Spotify/SoundCloud
- Multi-Song-Batch-Verarbeitung
- komplexe KI-Textgenerierung
- mehrere Visual-Varianten

---

## 2. Input für den PoC

Benötigt werden:
- **1 fertige Audio-Datei** eines extern generierten Songs
- **1 Cover-/Artwork-Datei**
- **1 Metadaten-Datei** (`song.json`)

### Beispielhafte Eingaben
- `input/songs/whispers-of-winterfell.wav`
- `input/artwork/whispers-of-winterfell.jpg`
- `input/metadata/whispers-of-winterfell.song.json`

---

## 3. Minimales Metadatenmodell für den PoC

Pflichtfelder:
- `slug`
- `title`
- `theme`
- `mood`
- `duration_target`
- `platforms`
- `generator`
- `prompt_summary`
- `source_audio`
- `source_artwork`

### Beispiel
```json
{
  "slug": "whispers-of-winterfell",
  "title": "Whispers of Winterfell",
  "theme": "Winterfell",
  "mood": ["calm", "cold", "melancholic"],
  "duration_target": "02:00:00",
  "platforms": ["youtube"],
  "generator": "tbd",
  "prompt_summary": "slow, ambient, fantasy sleep music inspired by a cold northern castle",
  "source_audio": "input/songs/whispers-of-winterfell.wav",
  "source_artwork": "input/artwork/whispers-of-winterfell.jpg"
}
```

---

## 4. PoC-Ablauf

## Schritt 1 – Input ablegen
Ein generierter Song und ein Artwork werden in definierte Ordner gelegt.

### Ergebnis
Die Dateien liegen in erwarteter Struktur vor.

---

## Schritt 2 – Metadaten validieren
Ein Skript prüft:
- existiert `song.json`?
- sind Pflichtfelder gesetzt?
- existieren Audio- und Bilddatei?
- ist `platforms` sinnvoll befüllt?

### Ergebnis
- `pass` oder `fail`
- Report-Datei

---

## Schritt 3 – Audio technisch prüfen
Ein Skript liest via `ffprobe` aus:
- Dauer
- Codec
- Sample-Rate
- Kanäle

### Ergebnis
Technischer Audio-Report.

---

## Schritt 4 – YouTube-Video rendern
Aus Audio + Artwork wird ein simples Video erzeugt:
- statisches Bild
- Titel optional als Overlay
- Audio läuft über die gesamte Dauer

### Ergebnis
- `output/youtube/<slug>/video.mp4`

---

## Schritt 5 – Thumbnail erzeugen
Aus dem Artwork wird ein Thumbnail erzeugt oder ein Template befüllt.

### Ergebnis
- `output/youtube/<slug>/thumbnail.jpg`

---

## Schritt 6 – Metadaten-Paket bauen
Aus `song.json` und Templates werden erzeugt:
- `description.txt`
- `tags.txt`
- `metadata.json`

### Ergebnis
Vollständiges Upload-Paket.

---

## Schritt 7 – Preflight-Check
Ein finaler Check prüft:
- alle erwarteten Dateien vorhanden
- Dateien nicht leer
- Video und Thumbnail im Zielordner
- Metadaten-Files vorhanden

### Ergebnis
- Freigabebericht für manuellen oder später automatisierten Upload

---

## 5. Erwartete Ausgabe des PoC

Beispiel:

```text
output/youtube/whispers-of-winterfell/
  video.mp4
  thumbnail.jpg
  metadata.json
  description.txt
  tags.txt
  preflight-report.json
```

---

## 6. Aufteilung für die Umsetzung

### Pako
- Ordnerstruktur
- Metadaten-Schema v1
- Validierung / Reports
- Render-/Paket-Workflow-Struktur

### Jarvis
- Beschreibungstemplate
- Titel-/Tag-Regeln
- YouTube-spezifische Textbausteine
- Upload-Checkliste

---

## 7. Warum dieser PoC sinnvoll ist

- klein genug für schnellen Test
- groß genug, um die Pipeline real zu prüfen
- funktioniert schon mit extern generierten Songs
- zwingt zu sauberer Struktur statt Wunschdenken

Kurz: Erst ein funktionierender Einzeller, dann die Raumstation.
