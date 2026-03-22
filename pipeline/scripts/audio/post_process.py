#!/usr/bin/env python3
"""
Audio Post-Processing – Whispers of the Seven Kingdoms

Verbessert die Audioqualität durch:
- Normalisierung (loudnorm)
- Sanfter Reverb (aecho) für räumlicheren Sound
- Bass-Boost / Wärme (equalizer)
- Limiter gegen Clipping

Usage:
    python post_process.py --input raw.mp3 --output processed.mp3
    python post_process.py --input raw.mp3 --output processed.mp3 --preset ambient
    python post_process.py --input raw.mp3 --output processed.mp3 --no-reverb
"""

import argparse
import subprocess
import sys
from pathlib import Path


# Presets für verschiedene Stimmungen
PRESETS = {
    "ambient": {
        "desc": "Warm, spacious ambient – ideal für Sleep Music",
        "eq": "equalizer=f=80:t=q:w=1.2:g=3,equalizer=f=200:t=q:w=1:g=2,equalizer=f=2000:t=q:w=0.8:g=-3,equalizer=f=4000:t=q:w=1:g=-4,equalizer=f=8000:t=q:w=1:g=-6,equalizer=f=12000:t=q:w=1:g=-8",
        "reverb": "aecho=0.8:0.7:60|90:0.3|0.2",
        "loudnorm": "loudnorm=I=-16:TP=-1.5:LRA=11",
    },
    "dark": {
        "desc": "Dunkel, tief – für Dark Ambient",
        "eq": "equalizer=f=60:t=q:w=1:g=4,equalizer=f=150:t=q:w=1:g=3,equalizer=f=4000:t=q:w=1:g=-4,equalizer=f=10000:t=q:w=1:g=-5",
        "reverb": "aecho=0.8:0.6:80|120:0.35|0.25",
        "loudnorm": "loudnorm=I=-18:TP=-1.5:LRA=11",
    },
    "gentle": {
        "desc": "Leicht, sanft – für friedliche Stücke",
        "eq": "equalizer=f=100:t=q:w=1:g=2,equalizer=f=500:t=q:w=1:g=1,equalizer=f=2000:t=q:w=1:g=-1,equalizer=f=6000:t=q:w=1:g=-2",
        "reverb": "aecho=0.8:0.8:40|70:0.25|0.15",
        "loudnorm": "loudnorm=I=-16:TP=-1.5:LRA=11",
    },
    "raw": {
        "desc": "Nur Normalisierung, kein EQ/Reverb",
        "eq": "",
        "reverb": "",
        "loudnorm": "loudnorm=I=-16:TP=-1.5:LRA=11",
    },
}


def post_process(input_path, output_path, preset="ambient", no_reverb=False, no_eq=False):
    """Audio post-processing mit ffmpeg."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"[ERROR] Input nicht gefunden: {input_path}")
        sys.exit(1)

    cfg = PRESETS.get(preset, PRESETS["ambient"])
    print(f"[PRESET] {preset} -- {cfg['desc']}")

    # Filter-Chain aufbauen
    filters = []

    # 1. EQ für Wärme
    if cfg["eq"] and not no_eq:
        filters.append(cfg["eq"])
        print(f"  [EQ] Bass-Boost + Hoehen-Reduktion")

    # 2. Reverb für Räumlichkeit
    if cfg["reverb"] and not no_reverb:
        filters.append(cfg["reverb"])
        print(f"  [REVERB] Raeumlicher Klang")

    # 3. Loudnorm immer
    filters.append(cfg["loudnorm"])
    print(f"  [NORM] Konsistente Lautstaerke")

    # 4. Limiter gegen Clipping
    filters.append("alimiter=limit=0.95:attack=5:release=50")
    print(f"  [LIMITER] Anti-Clipping")

    filter_chain = ",".join(filters)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", filter_chain,
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(output_path)
    ]

    print(f"  [PROCESSING]...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    if result.returncode != 0:
        print(f"[ERROR] ffmpeg Fehler:\n{result.stderr[-500:]}")
        sys.exit(1)

    # Größenvergleich
    in_size = input_path.stat().st_size / (1024 * 1024)
    out_size = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Output: {output_path}")
    print(f"   {in_size:.1f} MB -> {out_size:.1f} MB", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Audio Post-Processing")
    parser.add_argument("--input", required=True, help="Input Audio (MP3/WAV)")
    parser.add_argument("--output", required=True, help="Output Audio (MP3)")
    parser.add_argument("--preset", default="ambient",
                       choices=list(PRESETS.keys()),
                       help="Processing-Preset (default: ambient)")
    parser.add_argument("--no-reverb", action="store_true", help="Reverb überspringen")
    parser.add_argument("--no-eq", action="store_true", help="EQ überspringen")

    args = parser.parse_args()
    post_process(args.input, args.output, args.preset, args.no_reverb, args.no_eq)


if __name__ == "__main__":
    main()
