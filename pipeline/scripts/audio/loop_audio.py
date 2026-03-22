#!/usr/bin/env python3
"""
Loop Audio – Whispers of the Seven Kingdoms

Nimmt eine Audio-Datei und loopt sie auf eine Ziel-Dauer
mit echtem Crossfade zwischen jeder Wiederholung.

Usage:
    python loop_audio.py --input song.mp3 --output song-3h.mp3 --target-hours 3
    python loop_audio.py --input song.wav --output song-looped.mp3 --target-hours 3 --crossfade 8
"""

import argparse
import subprocess
import sys
from pathlib import Path


def get_duration(audio_path):
    """Audio-Dauer in Sekunden ermitteln."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def loop_audio(input_path, output_path, target_hours=3, crossfade_seconds=8):
    """Audio loopen mit echtem Crossfade zwischen jeder Wiederholung."""
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
        subprocess.run(["ffmpeg", "-y", "-i", str(input_path),
                       "-t", str(target_seconds),
                       "-c:a", "libmp3lame", "-b:a", "192k",
                       str(output_path)], check=True)
    else:
        # Echter Crossfade: iterativ zwei Dateien crossfaden
        # Schritt 1: Erste Kopie als Basis
        temp_dir = output_path.parent / "_loop_temp"
        temp_dir.mkdir(exist_ok=True)

        current = temp_dir / "loop_0.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(input_path),
            "-acodec", "pcm_s16le", "-ar", "44100", str(current)
        ], check=True, capture_output=True)

        # Schritt 2: Iterativ crossfaden
        for i in range(1, repeats):
            next_out = temp_dir / f"loop_{i}.wav"
            print(f"  🔀 Crossfade {i}/{repeats-1}...")

            # acrossfade: crossfadet Ende von current mit Anfang von input
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(current),
                "-i", str(input_path),
                "-filter_complex",
                f"acrossfade=d={crossfade_seconds}:c1=tri:c2=tri",
                "-acodec", "pcm_s16le", "-ar", "44100",
                str(next_out)
            ], check=True, capture_output=True)

            # Alte Temp-Datei löschen um Disk zu sparen
            current.unlink(missing_ok=True)
            current = next_out

        # Schritt 3: Auf Ziel-Dauer schneiden + als MP3 exportieren
        print(f"  ✂️  Schneiden auf {target_hours}h + MP3 Export...")
        subprocess.run([
            "ffmpeg", "-y", "-i", str(current),
            "-t", str(target_seconds),
            "-af", f"afade=t=in:d=3,afade=t=out:st={target_seconds - 5}:d=5",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(output_path)
        ], check=True)

        # Cleanup
        current.unlink(missing_ok=True)
        temp_dir.rmdir()

    final_duration = get_duration(output_path)
    print(f"✅ Output: {output_path} ({final_duration:.0f}s = {final_duration/60:.1f} Min)")


def main():
    parser = argparse.ArgumentParser(description="Loop Audio mit Crossfade")
    parser.add_argument("--input", required=True, help="Input Audio (WAV/MP3)")
    parser.add_argument("--output", required=True, help="Output Audio (MP3)")
    parser.add_argument("--target-hours", type=float, default=3, help="Ziel-Dauer in Stunden (default: 3)")
    parser.add_argument("--crossfade", type=int, default=8, help="Crossfade in Sekunden (default: 8)")

    args = parser.parse_args()
    loop_audio(args.input, args.output, args.target_hours, args.crossfade)


if __name__ == "__main__":
    main()
