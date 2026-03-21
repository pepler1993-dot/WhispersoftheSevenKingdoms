#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
DEFAULT_AUDIO_BITRATE = '192k'


def parse_args():
    p = argparse.ArgumentParser(description='Render a YouTube-ready MP4 from audio + image via ffmpeg.')
    p.add_argument('--audio', required=True, help='Path to input audio file (mp3/wav/ogg/...)')
    p.add_argument('--image', required=True, help='Path to thumbnail/background image (jpg/png/webp/...)')
    p.add_argument('--output', required=True, help='Path to output mp4 file')
    p.add_argument('--width', type=int, default=VIDEO_WIDTH)
    p.add_argument('--height', type=int, default=VIDEO_HEIGHT)
    p.add_argument('--audio-bitrate', default=DEFAULT_AUDIO_BITRATE)
    p.add_argument('--fps', type=int, default=30)
    p.add_argument('--dry-run', action='store_true', help='Print ffmpeg command without running it')
    return p.parse_args()


def fail(msg: str, code: int = 1):
    print(f'ERROR: {msg}', file=sys.stderr)
    raise SystemExit(code)


def ensure_inputs(audio: Path, image: Path, output: Path):
    if not audio.is_file():
        fail(f'Audio file not found: {audio}')
    if not image.is_file():
        fail(f'Image file not found: {image}')
    output.parent.mkdir(parents=True, exist_ok=True)


def ffmpeg_cmd(audio: Path, image: Path, output: Path, width: int, height: int, fps: int, audio_bitrate: str):
    filter_graph = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
    )
    return [
        'ffmpeg', '-y',
        '-loop', '1',
        '-framerate', str(fps),
        '-i', str(image),
        '-i', str(audio),
        '-vf', filter_graph,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', audio_bitrate,
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-movflags', '+faststart',
        str(output),
    ]


def main():
    args = parse_args()
    audio = Path(args.audio).expanduser().resolve()
    image = Path(args.image).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()

    ensure_inputs(audio, image, output)

    if shutil.which('ffmpeg') is None:
        fail('ffmpeg is not installed or not in PATH')

    cmd = ffmpeg_cmd(audio, image, output, args.width, args.height, args.fps, args.audio_bitrate)
    print('COMMAND:', ' '.join(str(x) for x in cmd))

    if args.dry_run:
        return

    result = subprocess.run(cmd)
    if result.returncode != 0:
        fail(f'ffmpeg exited with code {result.returncode}', result.returncode)

    print(f'OK: rendered {output}')


if __name__ == '__main__':
    main()
