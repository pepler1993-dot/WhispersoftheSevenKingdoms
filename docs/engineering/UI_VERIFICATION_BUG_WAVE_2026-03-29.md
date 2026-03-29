# UI Verification – Bug Wave – 2026-03-29

**Owner:** Pako
**Zweck:** Knappe Verifikation der UI-/Flow-Fixes für die Bug-Welle.
**Status:** Stable noch nicht freigegeben – dieses Dokument ist nur der UI-Teil der Verifikation.

---

## 1. Create-Flow – Titel / Variant Handling (#157)

### Repro alt
- Haus wählen
- Variante wählen
- automatisch generierten Titel prüfen
- Risiko: Variantenname wurde inkonsistent oder unvollständig in den Titel übernommen

### Aktuelles Verhalten
- Fix `47a209e` ist auf `main`
- aktueller Stand wirkt im Template plausibel korrigiert
- kein offener Widerspruch im Create-Flow-Template sichtbar

### Ergebnis
- **P1-Fix im Repo vorhanden**
- **keine neue P0-Regression sichtbar**
- endgültige Freigabe braucht echten manuellen Screen-Check im Browser

---

## 2. Create-Flow – Mood / Stimmung nach Haus- und Variantenwahl

### Repro alt
- Haus wählen
- Variante wählen
- Mood-/Stimmungs-Tags konnten leer oder veraltet sein

### UI-Ursache
- `buildMoodTags()` wurde nach Variantenwahl nicht erneut gesetzt

### Fix
- Mood wird nach Hauswahl gesetzt
- Mood wird nach Variantenwahl erneut mit `house.mood` als Default gesetzt

### Ergebnis
- **Fix auf main**
- **P0 frei**

---

## 3. Create-Flow – Audio-Statusziel im DOM

### Repro alt
- Create-Flow öffnen
- Audioquelle wechseln / Library-Audio wählen
- JS schrieb auf `#status-audio`, aber das Element existierte nicht

### UI-Ursache
- fehlendes DOM-Target

### Fix
- `3a4027e`
- `id="status-audio"` im Audio-Statusblock wieder ergänzt

### Ergebnis
- JS-Hook ist wieder gültig
- Statusfeedback kann wieder sichtbar gesetzt werden
- **P0 frei**

---

## 4. Create-Flow – Library-Modus ohne Audio-Auswahl

### Repro alt
- Audioquelle auf **Bibliothek** stellen
- keinen Track wählen
- Submit auslösen
- Risiko: stilles Weiterlaufen / stiller Fallback

### UI-Ursache
- Frontend blockte den Submit in diesem Zustand nicht

### Fix
- `0565140`
- harter Submit-Guard im Frontend:
  - wenn `audio_source === 'library'`
  - und kein `selected_audio_track`
  - dann Abbruch mit klarer Fehlermeldung

### Ergebnis
- kein stilles Weiterlaufen mehr auf UI-Seite
- **P1 deutlich verbessert**
- Backend-Verifikation bleibt zusätzlich relevant

---

## 5. Shorts-Create – Config Prefill aus Source-Video

### Repro alt
- Shorts → Neuer Short
- Haus wählen → Variante wählen → Source-Video wählen
- nur Quelle/Titel/Slug wurden gesetzt
- Config-Felder blieben auf starren Defaults

### UI-Ursache
- `uploaded_videos` enthielt kein `config`
- Template übernahm beim Klick keine Config-Werte

### Fix
- `8eb1159`
- `shorts.py`: `config` wird an `uploaded_videos` durchgereicht
- `shorts.html`: beim Video-Klick werden jetzt befüllt:
  - `clip_start_seconds`
  - `clip_duration_seconds`
  - `visual_mode`
  - `visibility`

### Ergebnis
- echter Flow-Fix
- **P1 verbessert**
- Issue bleibt offen, falls unter „Preset nicht vollständig befüllt“ noch weitere UX-Punkte gemeint sind

---

## 6. Thumbnail-Library auf Create-Seite

### Prüfung
- `admin_pipeline_new()` lädt `library_thumbnails` aus `data/output/thumbnails`
- im Repo liegen dort reale Bilddateien

### Ergebnis
- **kein offensichtlicher Pfadbruch**
- aktuell kein P0/P1-Blocker sichtbar
- Hinweis: im Ordner liegen auch `.mp4`-Dateien, die aber wegen Endungsfilter nicht in die Thumbnail-Library gelangen

---

## 7. Dashboard-Priorisierung (#156)

### Prüfung
- Template-Struktur geprüft
- kein technischer P0-Blocker im Script sichtbar
- Thema bleibt ein Priorisierungs-/Informationsarchitekturpunkt

### Ergebnis
- aktuell **P1**, nicht P0
- braucht echten Screen-Check, nicht nur statische Template-Lesung

---

## UI-Zwischenfazit

### P0
- aktuell **frei**

### P1 mit echtem Fortschritt
- Titel-/Variant-Handling verbessert
- Shorts-Config-Prefill verbessert
- Library-Modus im Create-Flow gehärtet

### Noch nicht ausreichend für Stable
- Browser-basierte manuelle End-to-End-Verifikation fehlt noch teilweise
- Regression-/Stable-Gate-Doku muss zentral vollständig sein
