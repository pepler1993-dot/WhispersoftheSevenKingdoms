#!/usr/bin/env python3
"""
MusicGen Track Generator – Whispers of the Seven Kingdoms

Generiert Sleep Music Tracks aus Text-Prompts mit Meta's MusicGen.
Clips werden automatisch zusammengefügt und optional hochgeladen.

Usage:
    python generate.py --track winterfell_peaceful_piano
    python generate.py --track winterfell_peaceful_piano --minutes 42 --upload github
    python generate.py --all --upload github
    python generate.py --list
"""

import argparse
import json
import os
import random
import sys
import time

import numpy as np
import scipy.io.wavfile
import yaml

from merge import merge_clips
from upload import upload_track


def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_prompts(prompts_path="prompts.json"):
    with open(prompts_path, "r") as f:
        return json.load(f)


def load_model(config):
    """Lädt das MusicGen Modell auf GPU/CPU."""
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import torch

    model_name = config["model"]["name"]
    device = config["model"]["device"]

    print(f"🔄 Lade Modell: {model_name}...")
    processor = AutoProcessor.from_pretrained(model_name)
    model = MusicgenForConditionalGeneration.from_pretrained(model_name)

    if device == "cuda":
        import torch
        if torch.cuda.is_available():
            model = model.to("cuda")
            print(f"✅ Modell auf GPU geladen")
        else:
            print("⚠️  Keine GPU gefunden, nutze CPU (langsam!)")
            device = "cpu"
    else:
        print(f"✅ Modell auf CPU geladen")

    sample_rate = model.config.audio_encoder.sampling_rate
    return model, processor, device, sample_rate


def generate_clips(model, processor, device, sample_rate, track_info, config):
    """Generiert alle Clips für einen Track."""
    import torch

    gen_config = config["generation"]
    clip_seconds = gen_config["clip_seconds"]
    target_minutes = gen_config["target_minutes"]
    crossfade_sec = gen_config["crossfade_seconds"]

    effective_clip = clip_seconds - crossfade_sec
    num_clips = int(np.ceil((target_minutes * 60) / effective_clip))

    track_name = track_info["name"]
    prompts = track_info["prompts"]
    output_dir = config["output"]["output_dir"]
    clip_dir = os.path.join(output_dir, f"{track_name}_clips")
    os.makedirs(clip_dir, exist_ok=True)

    print(f"\n🎹 Track: {track_name}")
    print(f"⏱️  Ziel: {target_minutes} Min → {num_clips} Clips à {clip_seconds}s")
    print(f"🔁 {len(prompts)} Prompt-Variationen\n")

    start_time = time.time()

    for i in range(num_clips):
        prompt = prompts[i % len(prompts)]
        temp = round(random.uniform(
            gen_config["temperature_min"],
            gen_config["temperature_max"]
        ), 2)
        guidance = round(random.uniform(
            gen_config["guidance_min"],
            gen_config["guidance_max"]
        ), 1)

        print(f"  [{i+1}/{num_clips}] Prompt {(i % len(prompts))+1} | "
              f"temp={temp} cfg={guidance}", end="... ")

        inputs = processor(
            text=[prompt], padding=True, return_tensors="pt"
        ).to(device)
        max_tokens = int(clip_seconds * 50)

        with torch.no_grad():
            audio_values = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temp,
                guidance_scale=guidance,
            )

        audio_data = audio_values[0, 0].cpu().numpy()
        clip_path = os.path.join(clip_dir, f"clip_{i:03d}.wav")
        scipy.io.wavfile.write(clip_path, rate=sample_rate, data=audio_data)

        elapsed = time.time() - start_time
        eta = (elapsed / (i + 1)) * (num_clips - i - 1)
        print(f"✅ ({len(audio_data)/sample_rate:.0f}s) ETA: {eta/60:.0f}min")

    total_min = (time.time() - start_time) / 60
    print(f"\n🎉 {num_clips} Clips generiert in {total_min:.1f} Min")

    return clip_dir


def generate_track(model, processor, device, sample_rate, track_info, config,
                   target_minutes=None, do_upload=False):
    """Generiert einen kompletten Track: Clips → Merge → Optional Upload."""
    if target_minutes:
        config["generation"]["target_minutes"] = target_minutes

    output_dir = config["output"]["output_dir"]
    track_name = track_info["name"]
    os.makedirs(output_dir, exist_ok=True)

    # 1. Clips generieren
    clip_dir = generate_clips(
        model, processor, device, sample_rate, track_info, config
    )

    # 2. Zusammenfügen
    output_format = config["output"]["format"]
    output_path = os.path.join(output_dir, f"{track_name}.{output_format}")

    merge_clips(
        clip_dir=clip_dir,
        output_path=output_path,
        crossfade_ms=config["generation"]["crossfade_seconds"] * 1000,
        fade_in_ms=config["output"]["fade_in_ms"],
        fade_out_ms=config["output"]["fade_out_ms"],
        output_format=output_format,
        bitrate=config["output"]["bitrate"],
        metadata={
            "artist": config["metadata"]["artist"],
            "album": config["metadata"]["album"],
            "title": track_name.replace("_", " ").title(),
        },
    )

    # 3. Upload
    if do_upload:
        upload_track(output_path, track_name, config)

    return output_path


def list_tracks(prompts_data):
    """Zeigt alle verfügbaren Tracks."""
    print("\n🎵 Verfügbare Tracks:\n")
    for i, track in enumerate(prompts_data["tracks"], 1):
        print(f"  {i}. {track['name']}")
        print(f"     Kategorie: {track['category']} | Haus: {track['house']}")
        print(f"     Prompts: {len(track['prompts'])} Variationen")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="MusicGen Track Generator – Whispers of the Seven Kingdoms"
    )
    parser.add_argument("--track", type=str, help="Track-Name aus prompts.json")
    parser.add_argument("--all", action="store_true", help="Alle Tracks generieren")
    parser.add_argument("--list", action="store_true", help="Verfügbare Tracks anzeigen")
    parser.add_argument("--minutes", type=int, help="Ziel-Länge in Minuten")
    parser.add_argument("--upload", type=str, choices=["github", "nextcloud", "local"],
                        help="Upload-Ziel")
    parser.add_argument("--config", type=str, default="config.yaml",
                        help="Pfad zur Config")
    parser.add_argument("--prompts", type=str, default="prompts.json",
                        help="Pfad zur Prompts-Datei")

    args = parser.parse_args()

    # Pfade relativ zum Script-Verzeichnis
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, args.config)
    prompts_path = os.path.join(script_dir, args.prompts)

    config = load_config(config_path)
    prompts_data = load_prompts(prompts_path)

    if args.list:
        list_tracks(prompts_data)
        return

    if not args.track and not args.all:
        parser.print_help()
        print("\n💡 Nutze --list um verfügbare Tracks zu sehen")
        return

    if args.upload:
        config["upload"]["target"] = args.upload

    # Modell laden (einmal für alle Tracks)
    model, processor, device, sample_rate = load_model(config)

    tracks_to_generate = []
    if args.all:
        tracks_to_generate = prompts_data["tracks"]
    else:
        track_info = next(
            (t for t in prompts_data["tracks"] if t["name"] == args.track), None
        )
        if not track_info:
            print(f"❌ Track '{args.track}' nicht gefunden.")
            print("💡 Nutze --list um verfügbare Tracks zu sehen")
            return
        tracks_to_generate = [track_info]

    print(f"\n🐺 Whispers of the Seven Kingdoms – MusicGen Pipeline")
    print(f"{'='*55}")
    print(f"Tracks: {len(tracks_to_generate)}")
    print(f"Ziel: {args.minutes or config['generation']['target_minutes']} Min/Track")
    print(f"Upload: {config['upload']['target']}")
    print(f"{'='*55}")

    for i, track_info in enumerate(tracks_to_generate, 1):
        print(f"\n[{i}/{len(tracks_to_generate)}] {'='*40}")
        generate_track(
            model, processor, device, sample_rate, track_info, config,
            target_minutes=args.minutes,
            do_upload=bool(args.upload),
        )

    print(f"\n✅ Fertig! {len(tracks_to_generate)} Track(s) generiert.")


if __name__ == "__main__":
    main()
