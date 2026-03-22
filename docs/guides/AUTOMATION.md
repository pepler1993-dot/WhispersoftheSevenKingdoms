# Automatisierungs-Pipeline: Whispers of the Seven Kingdoms

## Ziel
Musik und Thumbnails automatisch in einen Upload-Prozess bringen: Dateianlage reicht – Titel/Beschreibung generieren und Upload auf YouTube starten.

## Proof-of-Concept-Workflow (Schritt-für-Schritt)

1. Ordnerstruktur festlegen:
   - `upload/songs/`
   - `upload/thumbnails/`
   - `upload/done/`
2. Neue Datei (Musik, Thumbnail) wird in den jeweiligen Upload-Ordner gelegt.
3. Automations-Skript erkennt neuen Inhalt, generiert:
   - Titel (z. B. Songname/Datum/GoT-Bezug)
   - Beschreibung (KI-/Template-gestützt)
   - Weist Thumbnail korrekt zu
4. Skript lädt alles via YouTube Data API hoch (API-Key nötig – privat ablegen!)
5. Nach erfolgreichem Upload verschiebt das Skript die Datei nach `upload/done/`.
6. Logfile erzeugen (für Nachvollziehbarkeit).

## Zu erledigen / Aufgaben
- [ ] Beispiel-Ordnerstruktur im Repo anlegen
- [ ] Beispiel-Skript für automatisierten Upload (Python, Bash oder GitHub Action)
- [ ] Mini-Testlauf mit Demo-Song und -Thumbnail
- [ ] Dokumentation/README um API-Hinweise erweitern

## Hinweise
- API-Schlüssel (YouTube etc.) nie im Repo selbst ablegen!
- Ablauf kann für Spotify/SoundCloud später ähnlich ausgebaut werden

---
Das ist die Grundlage für vollautomatisierte Publishing-Pipeline. Weitere Ausbaustufen bitte als Issue oder Task aufnehmen.