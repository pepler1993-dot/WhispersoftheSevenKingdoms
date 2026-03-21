# Aufgaben für Pako

## Deine Issues

### #7 – Video-Rendering Script
**Was:** Ein ffmpeg-basiertes Script in `scripts/video/` das aus Audio + Thumbnail ein YouTube-Video macht.

**Input:**
- MP3 oder WAV (z.B. `upload/songs/winterfell.mp3`)
- Thumbnail JPG/PNG (z.B. `upload/thumbnails/winterfell.jpg`)

**Output:**
- MP4 Video (H.264, AAC Audio, 1080p)

**Technisch:**
```bash
# So simpel kann der Kern sein:
ffmpeg -loop 1 -i thumbnail.jpg -i audio.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -shortest output.mp4
```

**Anforderungen:**
- Python-Wrapper um ffmpeg mit CLI-Interface
- `python render.py --audio song.mp3 --image thumb.jpg --output video.mp4`
- 1080p Output (1920x1080), Bild wird ggf. skaliert/gepadded
- Optional nice-to-have: leichter Ken-Burns-Effekt oder Partikel-Overlay
- Datei kommt nach `scripts/video/render.py`

---

### #10 – Pipeline-Orchestrierung
**Was:** Ein `pipeline.py` das ALLE Schritte verbindet. Der heilige Gral.

**⚠️ Erst starten wenn #7, #8 und #9 fertig sind!**

**Flow:**
1. MusicGen generiert Audio → `publishing/musicgen/generate.py`
2. Thumbnail zuordnen (aus `upload/thumbnails/`)
3. Video rendern → `scripts/video/render.py` (dein #7)
4. Metadaten generieren → `scripts/metadata/metadata_gen.py` (mein #8)
5. QA Preflight → `scripts/qa/preflight-metadata-report.js`
6. YouTube Upload → `scripts/publish/youtube_upload.py` (mein #9)
7. Dateien nach `upload/done/` verschieben
8. Log schreiben

**CLI-Ziel:**
```bash
python pipeline.py --song "Peaceful Winterfell" --mood calm --house stark --minutes 42
```

**Ein Befehl → Song auf YouTube. Das ist das Endziel.**

---

## Wo liegen deine Dateien?
- `scripts/video/render.py` (neu, #7)
- `pipeline.py` im Root oder `scripts/` (neu, #10)

## Sync-Service Protokoll
Nicht vergessen: Task claimen → arbeiten → heartbeats → vor Push resyncen → releasen.
