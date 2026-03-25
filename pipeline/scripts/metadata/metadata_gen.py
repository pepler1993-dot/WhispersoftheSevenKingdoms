#!/usr/bin/env python3
"""
Metadaten-Generator – Whispers of the Seven Kingdoms

Generiert YouTube-ready Metadaten aus song.json + Publishing-Templates.

Usage:
    python metadata_gen.py --song whispers-of-winterfell
    python metadata_gen.py --song whispers-of-winterfell --output youtube-meta.json
    python metadata_gen.py --list
"""

import argparse
import json
import os
import sys

# Pfade relativ zum Repo-Root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
METADATA_DIR = os.path.join(REPO_ROOT, "data", "upload", "metadata")
TAG_LIBRARY = os.path.join(REPO_ROOT, "docs", "publishing", "TAG_LIBRARY.md")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "output", "youtube")


# === TITEL-TEMPLATES ===
TITLE_TEMPLATES = {
    "peaceful": [
        "Peaceful {theme} – Gentle Sleep Music, {duration} | Whispers of the Seven Kingdoms",
        "{theme} at Night – Calm Ambient Music for Deep Sleep | Whispers of the Seven Kingdoms",
        "Fall Asleep in {theme} – {duration} Soothing {instrument} Music",
    ],
    "dark": [
        "Dark {theme} – Haunting Ambient for Sleep & Meditation | Whispers of the Seven Kingdoms",
        "{theme} – Dark Ambient Sleep Music, {duration} | Whispers of the Seven Kingdoms",
        "Beyond {theme} – {duration} Deep Dark Ambient for Sleep",
    ],
    "melancholic": [
        "{theme} – Melancholic {instrument} for Deep Sleep | Whispers of the Seven Kingdoms",
        "Bittersweet {theme} – Gentle Sleep Music, {duration}",
        "The Sorrow of {theme} – Calm {instrument}, {duration} Sleep Music",
    ],
    "default": [
        "{theme} – Sleep Music, {duration} | Whispers of the Seven Kingdoms",
        "Peaceful {theme} – {duration} Ambient Music for Sleep",
    ],
}

# === BESCHREIBUNGS-TEMPLATE ===
DESCRIPTION_TEMPLATE = """{hook}

{lore_paragraph}

🎵 What you'll hear:
{content_description}
{timestamps}
━━━━━━━━━━━━━━━━━━━

🐺 Whispers of the Seven Kingdoms
Sleep music inspired by the world of Westeros. Every track is crafted to carry you into deep, peaceful sleep – through the frozen North, the gardens of Highgarden, and the ancient halls of King's Landing.

🎧 More from our realm:
► Full Collection: [link]
► {playlist_name}: [link]

💤 Tips for better sleep:
• Use comfortable headphones or low speakers
• Set a sleep timer so the screen turns off
• Let the music play – no need to watch

{seo_sentence}

━━━━━━━━━━━━━━━━━━━

© Whispers of the Seven Kingdoms

{hashtags}"""

# === LORE-DATENBANK ===
LORE = {
    "winterfell": {
        "hook": "Drift into the frozen halls of Winterfell with hours of gentle sleep music.",
        "lore": "The snow falls silently over the ancient castle of House Stark. Inside, the great hearth crackles softly as the direwolves rest by the fire. Tonight, Winterfell is at peace – and so are you.",
        "playlist": "The North – House Stark",
        "house": "stark",
    },
    "king's landing": {
        "hook": "Let the warm night air of King's Landing carry you into deep, peaceful sleep.",
        "lore": "The torches flicker softly in the Red Keep as the city below grows quiet. Through the open windows, a gentle breeze carries the distant sound of waves. The Iron Throne sits empty tonight – and the realm is at rest.",
        "playlist": "King's Landing & The Crown",
        "house": "lannister",
    },
    "targaryen": {
        "hook": "Feel the ancient power of Dragonstone as ethereal music guides you to sleep.",
        "lore": "On the shores of Dragonstone, the waves crash gently against volcanic rock. The Targaryen banners hang still in the moonlight. Old Valyria may be gone, but its magic lives on – in every note, in every breath of wind.",
        "playlist": "Fire & Blood – House Targaryen",
        "house": "targaryen",
    },
    "the wall": {
        "hook": "Journey to the edge of the world with dark ambient music from beyond the Wall.",
        "lore": "Seven hundred feet of ice stretch into the darkness. The Night's Watch keeps its silent vigil as cold winds howl from the north. Beyond the Wall, the world is vast, frozen, and unknowable – the perfect backdrop for deep sleep.",
        "playlist": "The North – House Stark",
        "house": "nights_watch",
    },
    "highgarden": {
        "hook": "Wander through the sunlit gardens of Highgarden with gentle, warm sleep music.",
        "lore": "The roses of House Tyrell bloom in every color as warm sunlight filters through ancient arbors. Birds sing softly, and a gentle breeze carries the scent of flowers across the Reach. In Highgarden, everything is peaceful.",
        "playlist": "The South – Highgarden, Dorne & Beyond",
        "house": "tyrell",
    },
    "dorne": {
        "hook": "Escape to the warm desert nights of Dorne with exotic ambient sleep music.",
        "lore": "Under a canopy of stars, the Water Gardens shimmer in the moonlight. The warm desert breeze carries the soft sound of fountains and distant oud melodies. In Dorne, the night is gentle and the sleep is deep.",
        "playlist": "The South – Highgarden, Dorne & Beyond",
        "house": "martell",
    },
    "godswood": {
        "hook": "Find peace beneath the ancient weirwood trees with meditative ambient music.",
        "lore": "The heart tree stands ancient and still, its red leaves whispering secrets older than memory. A gentle stream winds through moss-covered roots. In the Godswood, time slows down – and so does your mind.",
        "playlist": "The North – House Stark",
        "house": "stark",
    },
    "castamere": {
        "hook": "A gentle rendition of the most haunting melody in Westeros – for deep, peaceful sleep.",
        "lore": "The rains weep softly over the ruins of Castamere. But tonight, the famous melody is not a warning – it's a lullaby. Slow, gentle piano carries the bittersweet beauty of the Lannisters' song into the quiet of the night.",
        "playlist": "King's Landing & The Crown",
        "house": "lannister",
    },
}

# === CORE TAGS ===
CORE_TAGS = [
    "sleep music", "deep sleep music", "relaxing music", "ambient music",
    "meditation music", "game of thrones", "game of thrones ambient",
    "game of thrones sleep music", "westeros", "whispers of the seven kingdoms",
    "fantasy sleep music", "peaceful music",
]

# === HOUSE TAGS ===
HOUSE_TAGS = {
    "stark": ["winterfell", "house stark", "the north", "winterfell ambient music"],
    "lannister": ["king's landing", "house lannister", "rains of castamere", "red keep"],
    "targaryen": ["house targaryen", "dragonstone", "house of the dragon", "dragon ambient"],
    "nights_watch": ["the wall", "night's watch", "castle black", "beyond the wall"],
    "tyrell": ["highgarden", "house tyrell", "the reach"],
    "martell": ["dorne", "house martell", "water gardens"],
}

# === MOOD TAGS ===
MOOD_TAGS = {
    "calm": ["calm music", "soothing music", "gentle music", "peaceful ambient"],
    "cold": ["winter ambient", "snow ambient", "frozen ambient", "cold night music"],
    "melancholic": ["melancholic piano", "sad piano sleep", "bittersweet music"],
    "dark": ["dark ambient", "dark ambient music", "haunting ambient"],
    "warm": ["warm ambient", "gentle harp", "soft strings"],
    "mystical": ["mystical ambient", "ethereal music", "ancient ambient"],
    "exotic": ["middle eastern ambient", "exotic music", "oud music"],
}

# === INSTRUMENT MAPPING ===
INSTRUMENT_MAP = {
    "calm": "Piano",
    "cold": "Piano & Ambient",
    "melancholic": "Piano",
    "dark": "Ambient",
    "warm": "Harp & Strings",
    "mystical": "Ambient",
    "exotic": "Oud & Strings",
}


def _extract_title_str(song_meta):
    """Extract a plain title string, handling dict-style titles."""
    title = song_meta.get("title", song_meta.get("slug", ""))
    if isinstance(title, dict):
        primary = title.get("primary", "")
        return primary.split("\u2013")[0].split("--")[0].split("|")[0].strip()
    return title


def _extract_theme(song_meta):
    """Extract theme, falling back to title string."""
    theme = song_meta.get("theme")
    if isinstance(theme, str):
        return theme
    return _extract_title_str(song_meta)


def find_lore(theme):
    """Findet passenden Lore-Eintrag fuer ein Thema."""
    theme_lower = theme.lower()
    for key, lore in LORE.items():
        if key in theme_lower or theme_lower in key:
            return lore
    return None


def generate_title(song_meta, duration_str="8 Hours"):
    """Generiert Titel-Varianten."""
    mood = song_meta.get("mood", ["calm"])[0]
    theme = _extract_theme(song_meta)
    instrument = INSTRUMENT_MAP.get(mood, "Ambient")

    templates = TITLE_TEMPLATES.get(mood, TITLE_TEMPLATES["default"])
    titles = []
    for t in templates:
        title = t.format(
            theme=theme,
            duration=duration_str,
            instrument=instrument,
        )
        titles.append(title)
    return titles


def generate_description(song_meta):
    """Generiert YouTube-Beschreibung."""
    theme = _extract_theme(song_meta)
    mood = song_meta.get("mood", ["calm"])[0]
    lore = find_lore(theme)

    if lore:
        hook = lore["hook"]
        lore_paragraph = lore["lore"]
        playlist_name = lore["playlist"]
    else:
        hook = f"Hours of peaceful sleep music inspired by {theme} from the world of Westeros."
        lore_paragraph = f"Let the sounds of {theme} carry you into deep, restful sleep. Close your eyes and let the Seven Kingdoms embrace you."
        playlist_name = "Full Collection"

    # Content description from music_brief
    music_brief = song_meta.get("music_brief", {})
    influences = music_brief.get("influences", [])
    if influences:
        content_desc = f"A blend of {', '.join(influences[:3])} – designed for deep sleep, meditation, and quiet study."
    else:
        instrument = INSTRUMENT_MAP.get(mood, "ambient sounds")
        content_desc = f"Soft {instrument.lower()} melodies woven with gentle ambient sounds. Designed for deep sleep, meditation, and quiet study."

    # Timestamps (if available)
    timestamps_path = os.path.join(REPO_ROOT, "data", "upload", "songs", f"{song_meta.get('slug', '')}_timestamps.json")
    if os.path.exists(timestamps_path):
        with open(timestamps_path, encoding="utf-8") as f:
            timestamps = json.load(f)
        ts_block = "\n⏱️ Timestamps:\n" + "\n".join(f"{ts['time']} – {ts['label']}" for ts in timestamps)
    else:
        ts_block = ""

    # SEO sentence
    seo_sentence = (
        f"Relaxing {theme.lower()} sleep music inspired by Game of Thrones, "
        f"featuring peaceful {INSTRUMENT_MAP.get(mood, 'ambient').lower()} sounds "
        f"perfect for deep sleep, meditation, and study in the world of Westeros."
    )

    # Hashtags
    house = lore["house"] if lore else "westeros"
    house_tag = theme.replace(" ", "").replace("'", "")
    hashtags = f"#SleepMusic #GameOfThrones #{house_tag} #Ambient #DeepSleep #Westeros"

    description = DESCRIPTION_TEMPLATE.format(
        hook=hook,
        lore_paragraph=lore_paragraph,
        content_description=content_desc,
        timestamps=ts_block,
        playlist_name=playlist_name,
        seo_sentence=seo_sentence,
        hashtags=hashtags,
    )

    return description


def generate_tags(song_meta):
    """Generiert YouTube-Tags (Upload-Formular)."""
    tags = list(CORE_TAGS)

    # House-spezifische Tags
    lore = find_lore(_extract_theme(song_meta))
    if lore:
        house = lore["house"]
        tags.extend(HOUSE_TAGS.get(house, []))

    # Mood-Tags
    for mood in song_meta.get("mood", []):
        tags.extend(MOOD_TAGS.get(mood, []))

    # Song-spezifische Tags aus Schema
    if "tags" in song_meta:
        tags.extend(song_meta["tags"])

    # Deduplizieren, Reihenfolge beibehalten
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_tags.append(tag)

    return unique_tags[:25]  # YouTube empfiehlt max 25


def generate_playlist(song_meta):
    """Bestimmt passende Playlists (Cross-Pollination: min 3, max 6)."""
    playlists = ["Game of Thrones Sleep Music – Full Collection"]

    lore = find_lore(_extract_theme(song_meta))
    if lore:
        playlists.append(lore["playlist"])

    moods = song_meta.get("mood", [])
    if any(m in moods for m in ["calm", "peaceful", "warm"]):
        playlists.append("Peaceful & Calm – Gentle Sleep Music from Westeros")
    if any(m in moods for m in ["dark", "haunting", "mysterious"]):
        playlists.append("Dark & Mysterious – Haunting Ambient")
    if any(m in moods for m in ["calm", "peaceful"]):
        playlists.append("Study & Focus – Westeros Background Music")
    if any(m in moods for m in ["mystical", "meditative"]):
        playlists.append("Meditation & Relaxation – Westeros Mindfulness")

    # Ensure minimum 3 playlists
    if len(playlists) < 3:
        fallbacks = [
            "8 Hours Deep Sleep – Westeros Edition",
            "Peaceful & Calm – Gentle Sleep Music from Westeros",
            "Study & Focus – Westeros Background Music",
        ]
        for fb in fallbacks:
            if fb not in playlists:
                playlists.append(fb)
            if len(playlists) >= 3:
                break

    # Deduplicate, cap at 6
    seen = set()
    unique = []
    for p in playlists:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique[:6]


def generate_metadata(song_meta, duration_str="8 Hours"):
    """Generiert komplettes YouTube-Metadaten-Paket."""
    titles = generate_title(song_meta, duration_str)
    description = generate_description(song_meta)
    tags = generate_tags(song_meta)
    playlists = generate_playlist(song_meta)

    # Endscreen recommendation
    lore = find_lore(_extract_theme(song_meta))
    moods = song_meta.get("mood", [])
    if any(m in moods for m in ["dark", "haunting"]):
        endscreen_playlist = "Dark & Mysterious – Haunting Ambient"
    elif any(m in moods for m in ["mystical", "meditative"]):
        endscreen_playlist = "Meditation & Relaxation – Westeros Mindfulness"
    elif lore:
        endscreen_playlist = lore["playlist"]
    else:
        endscreen_playlist = "Game of Thrones Sleep Music – Full Collection"

    return {
        "slug": song_meta["slug"],
        "titles": {
            "primary": titles[0],
            "ab_variants": titles[1:],
        },
        "description": description,
        "tags": tags,
        "playlists": playlists,
        "endscreen": {
            "recommended_playlist": endscreen_playlist,
            "strategy": "Next video from same playlist (autoplay) + playlist link",
        },
        "privacy": "private",
        "category": "10",
        "language": "en",
    }


def load_song_meta(slug):
    """Laedt song.json aus upload/metadata/."""
    path = os.path.join(METADATA_DIR, f"{slug}.json")
    if not os.path.exists(path):
        print(f"[ERROR] Nicht gefunden: {path}")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_songs():
    """Zeigt alle verfuegbaren Songs."""
    print("\n[SONGS] Verfuegbare Songs:\n")
    if not os.path.exists(METADATA_DIR):
        print("  (keine)")
        return
    for f in sorted(os.listdir(METADATA_DIR)):
        if f.endswith(".json"):
            slug = f.replace(".json", "")
            with open(os.path.join(METADATA_DIR, f), encoding="utf-8") as fh:
                meta = json.load(fh)
            print(f"  {slug}")
            print(f"    Titel: {meta.get('title', '?')}")
            print(f"    Theme: {meta.get('theme', '?')}")
            print(f"    Mood:  {', '.join(meta.get('mood', []))}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Metadaten-Generator – Whispers of the Seven Kingdoms"
    )
    parser.add_argument("--song", type=str, help="Song-Slug aus upload/metadata/")
    parser.add_argument("--list", action="store_true", help="Verfügbare Songs anzeigen")
    parser.add_argument("--output", type=str, help="Output JSON Pfad")
    parser.add_argument("--duration", type=str, default="8 Hours",
                        help="Dauer für Titel (z.B. '3 Hours', '8 Hours')")
    parser.add_argument("--preview", action="store_true",
                        help="Nur Vorschau, nicht speichern")

    args = parser.parse_args()

    if args.list:
        list_songs()
        return

    if not args.song:
        parser.print_help()
        return

    song_meta = load_song_meta(args.song)
    if not song_meta:
        sys.exit(1)

    metadata = generate_metadata(song_meta, args.duration)

    if args.preview:
        print(f"\n[PREVIEW] {metadata['titles']['primary']}\n")
        print("--- BESCHREIBUNG ---")
        print(metadata["description"][:500] + "...")
        print(f"\n--- TAGS ({len(metadata['tags'])}) ---")
        print(", ".join(metadata["tags"][:10]) + "...")
        print(f"\n--- PLAYLISTS ---")
        for p in metadata["playlists"]:
            print(f"  > {p}")
        return

    # Output speichern
    if args.output:
        output_path = args.output
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{args.song}.youtube.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[OK] Metadaten generiert: {output_path}")
    print(f"[TITLE] {metadata['titles']['primary']}")
    print(f"[TAGS] {len(metadata['tags'])}")
    print(f"[PLAYLISTS] {len(metadata['playlists'])}")


if __name__ == "__main__":
    main()
