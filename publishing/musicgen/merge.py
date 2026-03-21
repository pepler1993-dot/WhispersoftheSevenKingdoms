#!/usr/bin/env python3
"""
Audio Merge – Fügt generierte Clips mit Crossfade zusammen.
"""

import glob
import os

from pydub import AudioSegment


def merge_clips(clip_dir, output_path, crossfade_ms=4000,
                fade_in_ms=3000, fade_out_ms=5000,
                output_format="mp3", bitrate="192k", metadata=None):
    """
    Fügt alle WAV-Clips aus clip_dir mit Crossfade zusammen.
    
    Args:
        clip_dir: Verzeichnis mit clip_*.wav Dateien
        output_path: Ausgabepfad (z.B. output/track.mp3)
        crossfade_ms: Crossfade-Dauer in Millisekunden
        fade_in_ms: Fade-in am Anfang
        fade_out_ms: Fade-out am Ende
        output_format: Ausgabeformat (mp3, wav)
        bitrate: MP3-Bitrate
        metadata: Dict mit artist, album, title
    
    Returns:
        Tuple (output_path, duration_minutes)
    """
    wav_files = sorted(glob.glob(os.path.join(clip_dir, "clip_*.wav")))

    if len(wav_files) < 1:
        raise ValueError(f"Keine Clips gefunden in {clip_dir}")

    print(f"🔗 Füge {len(wav_files)} Clips zusammen...")

    # Erster Clip
    merged = AudioSegment.from_wav(wav_files[0])

    for i, wav_file in enumerate(wav_files[1:], 1):
        clip = AudioSegment.from_wav(wav_file)
        merged = merged.append(clip, crossfade=crossfade_ms)
        if i % 20 == 0:
            print(f"  ... {i}/{len(wav_files)-1} Clips zusammengefügt")

    # Normalisieren
    merged = merged.normalize()

    # Fade-in / Fade-out
    if fade_in_ms > 0:
        merged = merged.fade_in(fade_in_ms)
    if fade_out_ms > 0:
        merged = merged.fade_out(fade_out_ms)

    # Export
    export_params = {"format": output_format}
    if output_format == "mp3":
        export_params["bitrate"] = bitrate
    if metadata:
        export_params["tags"] = metadata

    merged.export(output_path, **export_params)

    duration_min = len(merged) / 1000 / 60
    size_mb = os.path.getsize(output_path) / 1024 / 1024

    print(f"✅ Fertig: {output_path}")
    print(f"⏱️  Länge: {duration_min:.1f} Minuten")
    print(f"💾 Größe: {size_mb:.1f} MB ({output_format.upper()})")

    return output_path, duration_min


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Merge audio clips with crossfade")
    parser.add_argument("clip_dir", help="Verzeichnis mit clip_*.wav Dateien")
    parser.add_argument("-o", "--output", required=True, help="Ausgabepfad")
    parser.add_argument("--crossfade", type=int, default=4000, help="Crossfade in ms")
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav"])
    parser.add_argument("--bitrate", default="192k")

    args = parser.parse_args()

    merge_clips(
        clip_dir=args.clip_dir,
        output_path=args.output,
        crossfade_ms=args.crossfade,
        output_format=args.format,
        bitrate=args.bitrate,
    )
