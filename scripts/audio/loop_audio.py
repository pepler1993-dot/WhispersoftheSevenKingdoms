#!/usr/bin/env python3
"""
Loop Audio – Whispers of the Seven Kingdoms

Nimmt eine Audio-Datei (z.B. 20 Min) und loopt sie auf eine Ziel-Dauer
mit nahtlosem Crossfade zwischen den Wiederholungen.

Usage:
    python loop_audio.py --input song-20min.wav --output song-3h.mp3 --target-hours 3
    python loop_audio.py --input song.wav --output song-looped.mp3 --target-hours 3 --crossfade 8
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def get_duration(audio_path):
    """Audio-Dauer in Sekunden ermitteln."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def loop_audio(input_path, output_path, target_hours=3, crossfade_seconds=5):
    """Audio loopen mit Crossfade auf Ziel-Dauer."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"❌ Input nicht gefunden: {input_path}")
        sys.exit(1)

    duration = get_duration(input_path)
    target_seconds = target_hours * 3600
    # Effektive Dauer pro Loop (minus Crossfade-Überlappung)
    effective_duration = duration - crossfade_seconds
    repeats = int(target_seconds / effective_duration) + 1

    print(f"📎 Input: {input_path} ({duration:.0f}s = {duration/60:.1f} Min)")
    print(f"🎯 Ziel: {target_hours}h ({target_seconds}s)")
    print(f"🔁 Wiederholungen: {repeats} mit {crossfade_seconds}s Crossfade")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if repeats <= 1:
        # Keine Wiederholung nötig
        subprocess.run(["ffmpeg", "-y", "-i", str(input_path),
                       "-t", str(target_seconds),
                       "-c:a", "libmp3lame", "-b:a", "192k",
                       str(output_path)], check=True)
    else:
        # Concat-Liste erstellen
        concat_list = output_path.parent / "_concat_list.txt"
        with open(concat_list, "w") as f:
            for _ in range(repeats):
                f.write(f"file '{input_path.resolve()}'\n")

        # Schritt 1: Aneinanderreihen
        temp_concat = output_path.parent / "_temp_concat.wav"
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy", str(temp_concat)
        ], check=True, capture_output=True)

        # Schritt 2: Crossfade an den Übergängen + auf Ziel-Dauer schneiden
        # Fade-in am Anfang, Fade-out am Ende für sauberen Start/Stop
        subprocess.run([
            "ffmpeg", "-y", "-i", str(temp_concat),
            "-t", str(target_seconds),
            "-af", f"afade=t=in:d={crossfade_seconds},afade=t=out:st={target_seconds - crossfade_seconds}:d={crossfade_seconds}",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(output_path)
        ], check=True)

        # Cleanup
        concat_list.unlink(missing_ok=True)
        temp_concat.unlink(missing_ok=True)

    final_duration = get_duration(output_path)
    print(f"✅ Output: {output_path} ({final_duration:.0f}s = {final_duration/60:.1f} Min)")


def main():
    parser = argparse.ArgumentParser(description="Loop Audio mit Crossfade")
    parser.add_argument("--input", required=True, help="Input Audio (WAV/MP3)")
    parser.add_argument("--output", required=True, help="Output Audio (MP3)")
    parser.add_argument("--target-hours", type=float, default=3, help="Ziel-Dauer in Stunden (default: 3)")
    parser.add_argument("--crossfade", type=int, default=5, help="Crossfade in Sekunden (default: 5)")

    args = parser.parse_args()
    loop_audio(args.input, args.output, args.target_hours, args.crossfade)


if __name__ == "__main__":
    main()
