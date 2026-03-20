# Automatisierungsüberlegungen – Whispers of the Seven Kingdoms

Ziel dieses Dokuments: Für **jeden einzelnen Schritt** der Produktions- und Veröffentlichungsstrecke festhalten,
- **was automatisierbar ist**
- **was besser manuell geprüft bleibt**
- **welche Inputs/Outputs gebraucht werden**
- **welche Tools oder Skriptarten sinnvoll wären**
- **wo typische Risiken liegen**

Die Grundregel ist simpel:
**Alles, was standardisierbar und prüfbar ist, kann man automatisieren. Alles, was Geschmack, Kreativität oder Plattformrisiko trägt, braucht mindestens einen Kontrollpunkt.**

---

## 1. Idee & Planung

### Aufgabe
Aus einer losen Idee wird ein klar beschriebenes Produktionsobjekt.

### Manuelle Bestandteile
- Thema auswählen
- Stimmung festlegen
- Zielgruppe / Plattform bestimmen
- kreative Richtung entscheiden

### Automatisierbare Bestandteile
- aus einer Ideenliste automatisch Vorschläge ziehen
- Titel-Varianten generieren
- Standard-Tags und Themen-Kombinationen vorschlagen
- Briefing-Datei aus Template erzeugen

### Konkrete Automatisierung
Ein Skript könnte aus Parametern wie:
- Haus / Ort / Figur
- Stimmung
- Länge
- Zielplattform

automatisch eine `song.json` erzeugen.

### Beispiel
Input:
- Thema: `Winterfell`
- Stimmung: `ruhig, kalt, melancholisch`
- Ziel: `YouTube`

Output:
```json
{
  "slug": "whispers-of-winterfell",
  "title_working": "Whispers of Winterfell",
  "theme": "Winterfell",
  "mood": ["calm", "cold", "melancholic"],
  "duration_target": "02:00:00",
  "platforms": ["youtube"]
}
```

### Geeignete Tools
- JSON/YAML-Templates
- Node.js- oder Python-Skript zur Projektinitialisierung

### Risiken
- automatisch generierte Titel können generisch oder peinlich klingen
- zu viel KI-Text am Anfang erzeugt mehr Mittelmaß als Richtung

### Empfehlung
- **halbautomatisch**: Template automatisch erzeugen, kreative Richtung manuell festlegen

---

## 2. Song-Erstellung / Komposition

### Aufgabe
Das eigentliche Audio wird komponiert, erzeugt oder zusammengestellt.

### Manuelle Bestandteile
- Komposition
- Arrangement
- Sound-Auswahl
- musikalische Dramaturgie
- Qualitätsgefühl

### Automatisierbare Bestandteile
- Projektordner anlegen
- Dateistruktur erzeugen
- Standard-Render exportieren
- Dateibenennung erzwingen
- Stems sammeln und prüfen

### Konkrete Automatisierung
Wenn Song-Erstellung manuell oder mit externem Tool passiert, kann das Repo trotzdem automatisiert vorbereiten:
- neuen Song-Ordner anlegen
- Metadaten-Datei initialisieren
- erwartete Dateien definieren
- Import-Check laufen lassen

### Mögliche Levels der Automation

#### Level 1 – nur Verwaltung automatisieren
- Song wird manuell produziert
- Skripte kümmern sich nur um Struktur, Benennung und Verarbeitung

#### Level 2 – teilautomatisierte Erzeugung
- vorhandene Musikgeneratoren liefern Rohmaterial
- Skripte verarbeiten Ergebnisdateien weiter

#### Level 3 – vollautomatische Generierung
- Prompt → Musiktool → Render → Metadaten → Video → Upload

### Realistische Einschätzung
- **Level 1** ist sofort machbar
- **Level 2** ist machbar, wenn ihr klar definierte Generatoren habt
- **Level 3** ist theoretisch sexy, praktisch oft Qualitätslotterie mit Fantasy-Fassade

### Empfehlung
- Start mit **Level 1**
- später optional Generatoren integrieren

---

## 3. Import & Dateivalidierung

### Aufgabe
Fertige oder halb fertige Audiodateien landen im Projekt und müssen geprüft werden.

### Automatisierbar
- Dateiendung prüfen
- Dateigröße prüfen
- Audio-Dauer auslesen
- Sample-Rate / Kanäle / Bitrate prüfen
- Pflichtdateien prüfen
- Dateinamen gegen Schema prüfen

### Konkrete Automatisierung
Ein `validate-song`-Skript kann beim Einlegen neuer Dateien automatisch prüfen:
- gibt es `song.json`?
- gibt es mindestens eine Haupt-Audiodatei?
- ist die Datei nicht leer oder kaputt?
- passt die Länge ungefähr zum Ziel?

### Geeignete Tools
- `ffprobe`
- Node.js oder Python
- JSON-Schema-Validierung

### Empfehlung
- **voll automatisieren**
- diese Stufe sollte nicht manuell passieren, sonst stolpert man irgendwann über eine Nullbyte-Datei und tut überrascht

---

## 4. Audio-QA / technische Finalisierung

### Aufgabe
Das Audio technisch für Veröffentlichung vorbereiten.

### Automatisierbar
- Peak-Analyse
- Lautheitsmessung
- Silence-Detection am Anfang/Ende
- Dauerprüfung
- Export in definierte Formate
- technische Reports erzeugen

### Teilautomatisierbar
- Loop-Tauglichkeit grob prüfen
- Clipping erkennen
- Lautstärke-Range bewerten

### Nicht voll automatisierbar
- musikalische Qualität
- nervige Frequenzen
- emotionale Wirkung
- ob das Stück langweilig ist

### Konkrete Automatisierung
Ein Skript kann:
1. Quell-Audio einlesen
2. technische Werte mit `ffmpeg`/`ffprobe` ermitteln
3. Export nach `wav` und `mp3` ausführen
4. QA-Bericht schreiben

### Empfehlung
- **technische QA automatisieren**
- **künstlerische QA manuell prüfen**

---

## 5. Artwork / Visual-Erstellung

### Aufgabe
Passende Visuals, Cover und Thumbnails erzeugen.

### Manuelle Bestandteile
- Stilwahl
- Bildauswahl
- visuelle Richtung
- finale ästhetische Freigabe

### Automatisierbare Bestandteile
- Overlay mit Titel erzeugen
- Schriftart und Position standardisieren
- Format und Auflösung prüfen
- mehrere Thumbnail-Varianten aus Template rendern
- aus Artwork automatisch Video-Hintergrund erzeugen

### Konkrete Automatisierung
Skript-Eingaben:
- Basisbild
- Titel
- Stil-Template

Skript-Ausgaben:
- Thumbnail 1280x720
- Video-Background in Zielauflösung
- optional Social-Crop-Versionen

### Geeignete Tools
- ImageMagick
- ffmpeg
- Canvas / Sharp / Pillow

### Risiken
- vollautomatische Thumbnails sehen schnell nach KI-Friedhof aus
- Textumbrüche und Lesbarkeit können kaputtgehen

### Empfehlung
- **Template-basierte Automatisierung**, aber finale Sichtprüfung manuell

---

## 6. Video-Erstellung

### Aufgabe
Audio und Visuals zu einem YouTube-Video zusammenführen.

### Automatisierbar
- statisches Bild + Audio zu Video rendern
- Titel-/Branding-Overlay einblenden
- Intro/Outro einfügen
- passende Dateinamen erzeugen
- Export in definierte Parameter

### Konkrete Automatisierung
Klassischer MVP:
- Input: `master.wav`, `cover.jpg`, `song.json`
- Prozess: `ffmpeg` baut daraus ein 1080p-Video
- Output: `output/youtube/<slug>.mp4`

### Erweiterte Automatisierung
- animierter Zoom/Pan auf statischem Bild
- Partikel-/Nebeleffekt überlagern
- Kapitelgrafiken erzeugen
- mehrere Renderpresets

### Empfehlung
- **voll automatisierbar**, wenn das Videoformat standardisiert ist
- YouTube-Langvideos mit Ambient-Musik sind dafür ideal

---

## 7. Metadaten-Erstellung

### Aufgabe
Titel, Beschreibung, Tags und Plattformtexte erzeugen.

### Automatisierbar
- Titel aus Regeln zusammensetzen
- Beschreibungen aus Templates erzeugen
- Hashtags/Tags aus Thema ableiten
- Playlist-Zuordnung automatisch wählen
- Kapitelmarken vorbereiten

### Teilautomatisierbar
- Beschreibungstexte verfeinern
- mehrere Titelvarianten erzeugen

### Nicht blind automatisieren
- übertriebenes Marketing-Geschwurbel
- rechtlich heikle Formulierungen
- markenrechtlich dumme Begriffe

### Konkrete Automatisierung
Regelbasiertes System:
- wenn `theme = Winterfell`
- und `mood = calm, cold`
- dann Bausteine für Titel, Tags und Beschreibung auswählen

### Empfehlung
- **erst regelbasiert**, nicht direkt generative Text-Orgie
- Templates schlagen Halluzinationsprosa deutlich öfter

---

## 8. Paketierung für Plattformen

### Aufgabe
Alle nötigen Dateien und Texte pro Plattform sauber bündeln.

### Automatisierbar
- Upload-Paketordner anlegen
- Dateien in Plattformstruktur kopieren
- Manifest-Datei erzeugen
- Checksummen / Vollständigkeitsprüfung

### Beispiel
`output/youtube/whispers-of-winterfell/`
- `video.mp4`
- `thumbnail.jpg`
- `metadata.json`
- `description.txt`
- `tags.txt`

### Empfehlung
- **voll automatisieren**
- Menschen sollten keine Dateien von Hand zusammensammeln wie lose Schrauben im Teppich

---

## 9. QA vor Veröffentlichung

### Aufgabe
Letzte Prüfung vor Upload.

### Automatisierbar
- Vollständigkeit aller Assets prüfen
- Dateiformate prüfen
- Metadatenfelder validieren
- Upload-Manifest validieren
- Thumbnail-Format prüfen
- Video-Länge und Codec prüfen

### Teilautomatisierbar
- einfache Textregeln prüfen
- Dubletten erkennen
- verbotene Begriffe markieren

### Manuell sinnvoll
- Thumbnail einmal ansehen
- Titel lesen
- Beschreibung gegen peinliche Ausrutscher prüfen
- Gesamteindruck kontrollieren

### Empfehlung
- **Preflight vollautomatisch**
- **letzte Freigabe manuell**

---

## 10. Upload zu YouTube

### Aufgabe
Das fertige Paket auf YouTube hochladen.

### Mögliche Automatisierungsstufen

#### Stufe A – manuell
- Video und Texte sind fertig vorbereitet
- Upload erfolgt händisch im Browser

#### Stufe B – halbautomatisch
- Skript öffnet Upload-Seite oder bereitet alle Assets vor
- Mensch klickt final

#### Stufe C – API-basiert
- Upload per YouTube API
- Titel, Beschreibung, Tags, Sichtbarkeit, Thumbnail und Playlist werden automatisch gesetzt

### Was konkret automatisierbar ist
- Upload-Datei auswählen
- Metadaten setzen
- Thumbnail hochladen
- Playlist zuweisen
- Veröffentlichungszeit setzen
- Ergebnis-URL speichern

### Was schwierig ist
- OAuth sauber einrichten
- Token-Handling
- API-Quotas
- Fehlerfälle beim Upload

### Empfehlung
- **zuerst Stufe A oder B**
- **erst danach API-Automation**

Warum?
Weil ihr sonst Stunden in Authentifizierung versenkt, bevor euer einfacher Video-Render überhaupt zuverlässig läuft. Klassischer Technikfetisch mit null Nutzen.

---

## 11. Upload zu SoundCloud / Spotify

### Aufgabe
Audio auf weitere Plattformen bringen.

### Automatisierbarkeit
- Dateipaket erzeugen
- Plattform-spezifische Metadaten vorbereiten
- Cover prüfen
- Veröffentlichungsliste erzeugen

### Einschränkungen
- Spotify läuft oft nicht direkt per simplen Upload, sondern über Distributor
- APIs und Freigaben sind plattformabhängig
- Workflow kann juristisch und organisatorisch komplexer sein als technisch

### Empfehlung
- zuerst **nur YouTube** produktionsreif machen
- dann SoundCloud prüfen
- Spotify erst, wenn klar ist, über welchen Distributor oder Prozess ihr gehen wollt

---

## 12. Logging, Monitoring und Nachverfolgung

### Aufgabe
Sichtbar machen, was wann passiert ist.

### Automatisierbar
- Run-Logs schreiben
- Fehlerberichte speichern
- Upload-URLs dokumentieren
- Veröffentlichungsstatus tracken
- einfache Historie pro Song führen

### Beispielstatus
```json
{
  "slug": "whispers-of-winterfell",
  "audioValidated": true,
  "videoRendered": true,
  "qaPassed": true,
  "youtubeUploaded": false
}
```

### Empfehlung
- von Anfang an einbauen
- ohne Logs ist jede Automatisierung nur Magie mit späterem Nervenzusammenbruch

---

## 13. Secrets & Authentifizierung

### Aufgabe
Zugangsdaten sicher verwalten.

### Automatisierbar
- Umgebungsvariablen einlesen
- Secrets aus lokalem Secret-Store laden
- Konfigurationsdateien per `.env.example` dokumentieren

### Nicht tun
- Tokens ins Repo schreiben
- echte Secrets in Markdown-Dokumente kippen
- Zugangsdaten im Team-Readme verewigen

### Empfehlung
- `.env` lokal, nicht versioniert
- Secret-Manager wenn möglich
- klare Dokumentation, **aber ohne echte Werte**

---

## 14. Review & Teamarbeit

### Aufgabe
Mit mehreren Agenten/Menschen koordiniert arbeiten.

### Automatisierbar
- Branch-Namenskonventionen prüfen
- Pull-Request-Checklist generieren
- Dateistruktur prüfen
- automatisierte QA in CI laufen lassen

### Manuell nötig
- fachliche Review
- Stil-/Qualitätsentscheidung
- Abnahme bei größeren Änderungen

### Empfehlung
- CI für Struktur + QA
- Menschen/Agenten für Inhalt + Freigabe

---

## 15. Konkrete Automatisierungsarchitektur (empfohlen)

## Stufe 1 – sofort umsetzbar
Ziel: reproduzierbare Produktion ohne API-Zauberei.

Bausteine:
1. `init-song` → legt Song-Ordner + Metadaten an
2. `validate-song` → prüft Input-Dateien
3. `render-video` → baut aus Audio + Bild ein Video
4. `build-package` → erstellt YouTube-Paket
5. `preflight-check` → prüft Vollständigkeit

**Ergebnis:**
Ein Mensch lädt am Ende nur noch hoch.

---

## Stufe 2 – sinnvoller Ausbau
Ziel: mehr Metadaten und visuelle Assets automatisch.

Bausteine:
1. `generate-metadata` → Titel/Beschreibung/Tags aus Templates
2. `render-thumbnail` → Thumbnail automatisch erzeugen
3. `build-teaser` → Kurzclip für Socials
4. `track-status` → Statusdatei pro Song

---

## Stufe 3 – erweiterte Automation
Ziel: Upload und Publishing weitgehend automatisieren.

Bausteine:
1. `upload-youtube`
2. `set-thumbnail`
3. `assign-playlist`
4. `schedule-publish`
5. `save-publish-report`

### Voraussetzung
- OAuth / API steht stabil
- Paketstruktur ist zuverlässig
- QA funktioniert reproduzierbar

---

## 16. Empfehlung für die Praxis

### Was ihr sofort automatisieren solltet
- Projektinitialisierung
- Dateivalidierung
- Audio-Export-Prüfung
- Video-Render
- Thumbnail-Render
- Metadaten-Templates
- Paketbau
- Preflight-Checks

### Was ihr erst später automatisieren solltet
- vollautomatische Titel-/Beschreibungsgenerierung mit KI
- Multi-Plattform-Veröffentlichung
- API-Uploads
- Performance-/Analytics-Auswertung

### Was bewusst manuell bleiben sollte
- kreative Abnahme des Songs
- finale Sichtprüfung von Thumbnail und Beschreibung
- Freigabe vor Veröffentlichung

---

## 17. Idealer Zielworkflow

1. Neuer Song wird mit `init-song` angelegt
2. Audio und Artwork werden in Input-Ordner gelegt
3. `validate-song` prüft die Dateien
4. `generate-metadata` erzeugt Titel/Beschreibung/Tags
5. `render-thumbnail` baut Vorschaubild
6. `render-video` erzeugt YouTube-Video
7. `build-package` sammelt alles für die Plattform
8. `preflight-check` gibt grünes oder rotes Licht
9. Mensch prüft kurz
10. `upload-youtube` lädt hoch oder der Upload erfolgt manuell
11. `track-status` schreibt das Ergebnis weg

---

## 18. Fazit

Die Pipeline ist **gut automatisierbar**, wenn ihr sie nicht mit dem schwersten Teil beginnt.

Der sinnvolle Weg ist:
1. **Dateien und Metadaten standardisieren**
2. **Render- und Paketprozesse automatisieren**
3. **QA absichern**
4. **erst dann Upload automatisieren**

Kurzfassung:
Nicht zuerst den Raketenstart bauen, wenn ihr noch nicht mal den Treibstoffkanister beschriftet habt.
