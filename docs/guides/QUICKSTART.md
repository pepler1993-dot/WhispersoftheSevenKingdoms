# QUICKSTART – Whispers of the Seven Kingdoms

**Ziel:** In 5 Minuten einen fertigen Song auf YouTube haben (sofern API Keys vorhanden).

---

## Was du brauchst

- Python 3.10+
- Hugging Face Token (HF_TOKEN) für MusicGen
- YouTube OAuth2 Credentials (`credentials.json`)
- FFmpeg installiert
- Repository geklont: `git clone https://github.com/pepler1993-dot/WhispersoftheSevenKingdoms.git`

---

## 1. Environment vorbereiten

```bash
cd WhispersoftheSevenKingdoms
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r publishing/musicgen/requirements.txt
pip install pillow  # für Thumbnails
```

FFmpeg check: `ffmpeg -version` muss funktionieren.

---

## 2. Tokens setzen

```bash
export HF_TOKEN="hf_..."
# YouTube credentials.json ins Repo-Root legen (oder Pfad angeben)
```

---

## 3. Song-Idee definieren

Erstelle `input/metadata/my-song.json` basierend auf `templates/metadata/example.song.json`.

Mindestfelder:

```json
{
  "title": "Whispers of Winterfell",
  "theme": "winterfell",
  "mood": "calm",
  "duration_target": "08:00:00",
  "platforms": ["youtube"],
  "tags": ["sleep music", "winterfell ambient", "game of thrones"]
}
```

---

## 4. Pipeline durchlaufen (Einzeiliger Befehl folgt – bis dahin manuelle Schritte)

### 4.1 Musik generieren

```bash
python publishing/musicgen/generate.py --prompt "Winterfell peaceful piano and wind, Game of Thrones style" --duration 480
# Output: publishing/musicgen/output/*.wav
```

### 4.2 Metadaten generieren

```bash
python scripts/metadata/metadata_gen.py --input input/metadata/my-song.json --output upload/metadata/
```

### 4.3 Thumbnail erzeugen

```bash
python scripts/thumbnails/generate_thumbnail.py --title "Whispers of Winterfell" --theme winterfell
# Output: output/thumbnails/whispers-of-winterfell.jpg
```

### 4.4 Video rendern

```bash
python scripts/video/render.py \
  --audio publishing/musicgen/output/track.wav \
  --image output/thumbnails/whispers-of-winterfell.jpg \
  --output output/youtube/whispers-of-winterfell.mp4
```

### 4.5 Upload (optional, wenn YouTube konfiguriert)

```bash
python scripts/publish/youtube_upload.py \
  --video output/youtube/whispers-of-winterfell.mp4 \
  --metadata upload/metadata/my-song.json
```

---

## 5. Fertig

Video liegt in `output/youtube/`. Bei Upload erscheint es auf dem Kanal.

---

## Fehler & Hilfe

- **FFmpeg nicht gefunden**: `sudo apt-get install ffmpeg` (Linux) oder Homebrew (macOS)
- **MusicGen timeout**: Token prüfen, ggf. Colab verwenden
- **YouTube Upload fehlschlägt**: `credentials.json` prüfen, OAuth2 Consent Screen in Google Cloud Console
- **Weitere Infos**: siehe `README.md`, `PIPELINE.md`, `CONTRIBUTING.md`

---

## Für Fortgeschrittene

- Orchestrierungsskript: `scripts/orchestrate.py` (in Arbeit – #10)
- Batch-Verarbeitung: mehrere `song.json` in `input/metadata/` ablegen und Skript laufen lassen
- Proxmox GPU: siehe Issue #22
