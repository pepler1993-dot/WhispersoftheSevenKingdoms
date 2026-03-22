# 🎵 MusicGen Pipeline – Whispers of the Seven Kingdoms

Automatische Sleep Music Generierung mit Meta's MusicGen.

## Setup

```bash
# GPU erforderlich (Colab, Cloud-GPU oder lokal)
pip install -r requirements.txt
apt-get install ffmpeg  # für MP3-Konvertierung
```

## Usage

```bash
# Verfügbare Tracks anzeigen
python generate.py --list

# Einen Track generieren (42 Min, lokaler Download)
python generate.py --track winterfell_peaceful_piano

# Track generieren und zu GitHub pushen
GITHUB_TOKEN=ghp_xxx python generate.py --track winterfell_peaceful_piano --upload github

# Alle Tracks generieren (Batch)
GITHUB_TOKEN=ghp_xxx python generate.py --all --upload github

# Eigene Dauer setzen
python generate.py --track winterfell_peaceful_piano --minutes 60
```

## Dateien

| Datei | Beschreibung |
|---|---|
| `generate.py` | Hauptscript: Prompt → Clips → Merge → Upload |
| `merge.py` | Fügt Clips mit Crossfade zusammen |
| `upload.py` | GitHub/Nextcloud Upload |
| `prompts.json` | Alle GoT-Prompts (editierbar) |
| `config.yaml` | Settings (Dauer, Modell, Upload) |
| `requirements.txt` | Python-Abhängigkeiten |

## Neue Tracks hinzufügen

Einfach in `prompts.json` einen neuen Eintrag anlegen:

```json
{
    "name": "braavos_mysterious",
    "category": "dark",
    "house": "faceless_men",
    "prompts": [
        "mysterious ambient, venetian canals, soft waves, exotic and dark, no vocals",
        "haunting flute, water city, foggy night, mysterious calm, no vocals"
    ]
}
```

Dann: `python generate.py --track braavos_mysterious`

## Konfiguration

Alle Settings in `config.yaml`:
- **Modell:** small/medium/melody
- **Dauer:** Ziel-Minuten, Clip-Länge, Crossfade
- **Upload:** GitHub oder Nextcloud + Credentials
- **Output:** Format, Bitrate, Fades
