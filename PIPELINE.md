# Technische Pipeline – Whispers of the Seven Kingdoms

Ziel: Aus einer Song-Idee ein veröffentlichungsfertiges Audio-/Video-Paket erzeugen und dieses mit möglichst wenig manueller Arbeit auf Plattformen wie YouTube bereitstellen.

---

## 1. Gesamtüberblick

Die Pipeline besteht aus 8 Stufen:

1. **Idee & Planung**
2. **Song-Erstellung**
3. **Audio-Finalisierung**
4. **Visual- und Video-Erstellung**
5. **Metadaten-Erstellung**
6. **Qualitätsprüfung**
7. **Publikationsvorbereitung**
8. **Upload & Veröffentlichung**

Langfristiges Ziel:
Ein fertiger Song landet in einem definierten Input-Ordner, dazu kommen wenige Metadaten – der Rest läuft standardisiert oder automatisiert.

---

## 2. Zielstruktur im Repository

Empfohlene Struktur:

```text
input/
  songs/
  artwork/
  metadata/

work/
  audio/
  video/
  thumbnails/
  publish/

output/
  youtube/
  spotify/
  soundcloud/

templates/
  descriptions/
  thumbnails/
  metadata/

scripts/
  audio/
  video/
  metadata/
  publish/
  qa/

docs/
  platform-guides/
```

### Bedeutung
- **input/** → Rohmaterial vom Team
- **work/** → Zwischenstände, Render, temporäre Artefakte
- **output/** → finale exportierte Pakete pro Plattform
- **templates/** → Vorlagen für Beschreibungen, Titel, Metadaten, Thumbnails
- **scripts/** → Automatisierung
- **docs/** → Dokumentation und Plattformregeln

---

## 3. Pipeline im Detail

## 3.1 Idee & Planung

### Ziel
Eine lose Song-Idee in ein klar definiertes Produktionsobjekt verwandeln.

### Input
- Thema (z. B. Winterfell, House Stark, The Wall, Daenerys, King's Landing)
- Stimmung (ruhig, düster, warm, mystisch, melancholisch)
- Format (reines Audio / YouTube-Video / Shorts-Teaser)
- Zielplattformen

### Output
Eine strukturierte Projektdatei, z. B. JSON oder YAML:

```json
{
  "title": "Whispers of Winterfell",
  "theme": "House Stark",
  "mood": ["calm", "cold", "melancholic"],
  "duration_target": "02:30:00",
  "platforms": ["youtube"],
  "tags": ["sleep music", "fantasy ambience", "game of thrones inspired"]
}
```

### Technische Arbeitspakete
- Standard für Song-Metadaten definieren
- Vorlage für Song-Briefing erstellen
- Namensschema definieren
- Pflichtfelder festlegen

---

## 3.2 Song-Erstellung

### Ziel
Das eigentliche Audio erzeugen oder sammeln.

### Mögliche Varianten
- manuell komponiert
- mit DAW produziert
- mit KI-Musiktool erzeugt
- Kombination aus Loops, Instrumenten, Ambience und Voice-Elementen

### Input
- Song-Briefing
- Audioquellen / Stems / Midis / Render

### Output
- Rohmix oder erste Master-Datei
- optionale Einzelspuren / Stems

### Technische Arbeitspakete
- Standard-Eingangsformate definieren (`wav`, `flac`, ggf. `mp3` nur als Ausnahme)
- Konvention für Dateinamen definieren
- Input-Ordner für neue Songs festlegen
- Optional: Validierungsskript für Dateiformate und Pflichtdateien

---

## 3.3 Audio-Finalisierung

### Ziel
Das Audio für Veröffentlichung und Weiterverarbeitung stabilisieren.

### Schritte
- Lautstärke prüfen
- Clipping prüfen
- Intro/Outro prüfen
- Export in Ziel-Formate
- Loop-Tauglichkeit prüfen, falls relevant

### Output
- Master-Audio (`wav`)
- Plattformversion (`mp3`, optional `aac`)
- technische Metadaten (Dauer, Bitrate, Sample-Rate)

### Technische Arbeitspakete
- Audio-QA-Checkliste definieren
- Exportprofile definieren
- Skript für technische Audio-Analyse vorbereiten
- Dateinamen-Regeln für finale Exporte festlegen

### Sinnvolle Prüfungen
- Sample-Rate
- Lautheit/LUFS
- Peak-Level
- Dateilänge
- Stereo/Mono
- defekte oder leere Dateien

---

## 3.4 Visual- und Video-Erstellung

### Ziel
Aus Audio + Artwork ein veröffentlichbares Video erzeugen.

### Mögliche Assets
- Cover-Art
- animierter Hintergrund
- leichter Partikel-/Nebel-Effekt
- statisches Bild mit Audio
- Thumbnail

### Output
- YouTube-Video-Datei
- Thumbnail-Datei
- optionale Kurzclips für Social Media

### Technische Arbeitspakete
- Thumbnail-Spezifikation definieren
- Video-Template definieren
- ffmpeg-basierte Render-Pipeline planen
- optional Motion-Template-Struktur festlegen
- Intro/Outro-Regeln definieren

### Automatisierungsidee
Mit einem Skript:
- Audio-Datei einlesen
- Hintergrundbild auswählen
- Titel-Overlay generieren
- Video rendern
- Thumbnail exportieren

---

## 3.5 Metadaten-Erstellung

### Ziel
Alle Texte und Plattformdaten automatisch oder halbautomatisch erzeugen.

### Benötigte Metadaten
- Titel
- Beschreibung
- Tags/Keywords
- Kapitelmarken (optional)
- Playlist-Zuordnung
- Plattform-spezifische Kurztexte
- Veröffentlichungsdatum / Scheduling

### Output
Beispielsweise als JSON:

```json
{
  "title": "Whispers of Winterfell | Game of Thrones Inspired Sleep Music",
  "description": "Drift into the cold silence of the North with this Game of Thrones inspired sleep track...",
  "tags": ["sleep music", "fantasy sleep", "winterfell ambience"],
  "youtube": {
    "privacy": "private",
    "playlist": "Sleep Music"
  }
}
```

### Technische Arbeitspakete
- Metadaten-Schema definieren
- Beschreibungsvorlagen schreiben
- Titelregeln festlegen
- Tag-Bibliothek pflegen
- Playlist-Mapping dokumentieren

---

## 3.6 Qualitätsprüfung

### Ziel
Vor Upload verhindern, dass Müll automatisiert live geht.

### Prüfbereiche
- Sind alle Pflichtdateien vorhanden?
- Stimmen Dateinamen und Struktur?
- Ist Audio abspielbar?
- Ist Video renderbar und vollständig?
- Ist Thumbnail vorhanden?
- Sind Titel/Beschreibung nicht leer?
- Sind Plattformfelder gültig?

### Technische Arbeitspakete
- QA-Checkliste dokumentieren
- Preflight-Skript bauen
- Fehlerklassen definieren:
  - blockierend
  - Warnung
  - Info

### Ergebnis
Eine Freigabe-Datei oder ein Report, z. B.:

```json
{
  "status": "pass",
  "warnings": [],
  "errors": []
}
```

---

## 3.7 Publikationsvorbereitung

### Ziel
Plattformfähige Upload-Pakete bauen.

### Output pro Plattform

#### YouTube
- Video-Datei
- Thumbnail
- Titel
- Beschreibung
- Tags
- Playlist-Ziel
- Sichtbarkeit / Terminierung

#### Spotify / SoundCloud
- Audio-Datei
- Cover-Art
- Titel
- Beschreibung
- Genre / Tags
- Veröffentlichungsdaten

### Technische Arbeitspakete
- Plattformprofile definieren
- Export-Mapping pro Plattform dokumentieren
- Ordnerstruktur für fertige Upload-Pakete definieren

---

## 3.8 Upload & Veröffentlichung

### Ziel
Den finalen Upload reproduzierbar und möglichst automatisiert durchführen.

### YouTube
Mögliche Wege:
- manuell im Browser
- per offizieller YouTube API
- halbautomatisch: Metadaten generieren, Upload manuell

### SoundCloud / Spotify
- prüfen, welche APIs oder Distributionswege praktikabel sind
- ggf. Drittanbieter/Distributor nötig

### Technische Arbeitspakete
- YouTube-Upload-Strategie festlegen
- API-Zugang / OAuth sauber dokumentieren
- Secrets-Management definieren
- Retry-Strategie und Fehlerlogging festlegen
- Upload-Logs speichern

### Wichtig
Automatisierte Uploads brauchen saubere Authentifizierung. Tokens oder Zugangsdaten gehören **nicht** ins Repo.

---

## 4. Technische Arbeitspakete nach Bereichen

## A. Datenmodell & Struktur
- [ ] Verzeichnisstruktur anlegen
- [ ] Metadaten-Schema definieren (`song.json` oder `song.yaml`)
- [ ] Namenskonventionen dokumentieren
- [ ] Pflichtdateien je Song definieren

## B. Audio-Pipeline
- [ ] Audio-Eingabeformate festlegen
- [ ] QA-Kriterien für Audio dokumentieren
- [ ] Exportprofile definieren
- [ ] Skript für Audio-Validierung planen

## C. Video-Pipeline
- [ ] Standard für Hintergrundgrafiken definieren
- [ ] Thumbnail-Spezifikation dokumentieren
- [ ] Video-Rendering mit `ffmpeg` konzipieren
- [ ] Template für lange YouTube-Videos festlegen
- [ ] Optional: Shorts-/Teaser-Template definieren

## D. Metadaten-Automation
- [ ] Titel-Template entwerfen
- [ ] Beschreibungsvorlagen erstellen
- [ ] Tag-System definieren
- [ ] Playlist-Zuordnung dokumentieren
- [ ] Scheduling-Felder festlegen

## E. QA & Freigabe
- [ ] Preflight-Check definieren
- [ ] Fehler-Report-Format definieren
- [ ] Manuelle Reviewpunkte dokumentieren
- [ ] Freigabeschritt vor Upload festlegen

## F. Publishing
- [ ] Zielplattformen priorisieren
- [ ] YouTube zuerst konkretisieren
- [ ] OAuth/API-Ansatz dokumentieren
- [ ] Upload-Logik spezifizieren
- [ ] Secrets außerhalb des Repos verwalten

## G. Projektorganisation
- [ ] Rollen im Team festhalten
- [ ] Branch-Strategie konsequent nutzen
- [ ] PR-Review-Routine etablieren
- [ ] Dokumentation regelmäßig aktualisieren

---

## 5. Empfohlene Reihenfolge für die Umsetzung

### Phase 1 – Fundament
1. Repository-Struktur anlegen
2. Metadaten-Schema definieren
3. Pflichtdateien und Naming festlegen
4. YouTube als erste Zielplattform priorisieren

### Phase 2 – Produktionspipeline
5. Audio-QA standardisieren
6. Thumbnail- und Video-Template definieren
7. Render-Skript für Video-Prototyp bauen
8. Beschreibung/Titel automatisch generieren

### Phase 3 – Uploadpipeline
9. Upload-Paketstruktur definieren
10. YouTube-Upload manuell reproduzierbar machen
11. Danach API-/OAuth-Automatisierung ergänzen
12. Logging und Fehlerbehandlung einbauen

### Phase 4 – Erweiterung
13. Spotify/SoundCloud prüfen
14. Shorts/Teaser ergänzen
15. Feedbackschleife und Performance-Auswertung einbauen

---

## 6. Minimale erste Version (MVP)

Damit das Projekt nicht in Architektur-Pornografie versinkt, hier eine realistische erste Version:

### MVP-Workflow
1. Song als fertige `wav`/`mp3` in `input/songs/` legen
2. Cover-Bild in `input/artwork/` legen
3. `song.json` mit Titel, Beschreibung, Tags ausfüllen
4. Skript rendert daraus ein simples YouTube-Video
5. Skript erzeugt Thumbnail und Upload-Paket
6. Upload zunächst manuell oder halbautomatisch

### Vorteil
- schnell testbar
- wenig moving parts
- gute Basis für spätere Vollautomatisierung

---

## 7. Offene Entscheidungen

Diese Punkte müssen noch vom Team entschieden werden:
- Welche Tools erzeugen die Songs?
- Werden Songs rein manuell oder teilweise KI-basiert erstellt?
- Welche Videooptik soll Standard werden?
- Erst nur YouTube oder direkt Multi-Plattform?
- Vollautomatischer Upload oder zunächst manuell mit vorbereiteten Assets?
- Welches Secrets-Management wird genutzt?

---

## 8. Empfehlung

Sinnvolle nächste konkrete Schritte:
1. **YouTube als erste Zielplattform festlegen**
2. **ein `song.json`-Schema definieren**
3. **eine feste Ordnerstruktur anlegen**
4. **einen ersten ffmpeg-Prototyp für Audio+Bild→Video bauen**
5. **erst danach Upload-Automatisierung anfassen**

Sonst baut ihr euch zuerst einen Raumhafen und merkt danach, dass noch nicht mal ein Fahrrad existiert.

---

## 9. Weiterführende Automatisierung

Für eine schrittweise Analyse der konkreten Automatisierung pro Einzelschritt siehe:
- `AUTOMATION.md`

Dort ist pro Pipeline-Stufe dokumentiert:
- was voll automatisierbar ist
- was nur halbautomatisch sinnvoll ist
- was man bewusst manuell prüfen sollte
- welche Skripte und Tools sich anbieten
- welche Reihenfolge für den Ausbau realistisch ist
