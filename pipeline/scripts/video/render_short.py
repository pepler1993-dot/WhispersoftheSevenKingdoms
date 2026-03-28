#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
DEFAULT_AUDIO_BITRATE = '192k'


def parse_args():
    p = argparse.ArgumentParser(description='Render a vertical YouTube Short from longform video/audio via ffmpeg.')
    p.add_argument('--video', required=True, help='Path to input longform video')
    p.add_argument('--audio', required=False, help='Optional fallback audio path')
    p.add_argument('--image', required=False, help='Optional fallback image/background')
    p.add_argument('--output', required=True, help='Path to output mp4 file')
    p.add_argument('--width', type=int, default=VIDEO_WIDTH)
    p.add_argument('--height', type=int, default=VIDEO_HEIGHT)
    p.add_argument('--clip-start', type=float, default=0)
    p.add_argument('--clip-duration', type=float, default=30)
    p.add_argument('--visual-mode', default='static-artwork', choices=['static-artwork', 'blurred-background', 'cinematic-gradient'])
    p.add_argument('--audio-bitrate', default=DEFAULT_AUDIO_BITRATE)
    p.add_argument('--fps', type=int, default=24)
    p.add_argument('--dry-run', action='store_true')
    return p.parse_args()


def fail(msg: str, code: int = 1):
    print(f'ERROR: {msg}', file=sys.stderr)
    raise SystemExit(code)


def ensure_inputs(video: Path, output: Path, image: Path | None = None):
    if not video.is_file():
        fail(f'Video file not found: {video}')
    if image and not image.is_file():
        fail(f'Image file not found: {image}')
    output.parent.mkdir(parents=True, exist_ok=True)


def build_video_filter(width: int, height: int, visual_mode: str) -> str:
    base = (
        f'scale={width}:{height}:force_original_aspect_ratio=increase,'
        f'crop={width}:{height},fps=24'
    )
    if visual_mode == 'blurred-background':
        return (
            f'[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},boxblur=18:2[bg];'
            f'[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];'
            f'[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=24,format=yuv420p'
        )
    if visual_mode == 'cinematic-gradient':
        return base + ',eq=brightness=-0.04:saturation=0.85,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.18:t=fill,format=yuv420p'
    return base + ',format=yuv420p'


def ffmpeg_cmd(video: Path, output: Path, width: int, height: int, fps: int, audio_bitrate: str, clip_start: float, clip_duration: float, visual_mode: str):
    filter_graph = build_video_filter(width, height, visual_mode)
    cmd = ['ffmpeg', '-y']
    if clip_start > 0:
        cmd += ['-ss', str(clip_start)]
    cmd += ['-t', str(clip_duration), '-i', str(video)]
    if visual_mode == 'blurred-background':
        cmd += ['-filter_complex', filter_graph, '-map', '0:v:0', '-map', '0:a:0?']
    else:
        cmd += ['-vf', filter_graph]
    cmd += [
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-r', str(fps),
        '-c:a', 'aac',
        '-b:a', audio_bitrate,
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-shortest',
        str(output),
    ]
    return cmd


def main():
    args = parse_args()
    video = Path(args.video).expanduser().resolve()
    image = Path(args.image).expanduser().resolve() if args.image else None
    output = Path(args.output).expanduser().resolve()

    ensure_inputs(video, output, image)

    if shutil.which('ffmpeg') is None:
        fail('ffmpeg is not installed or not in PATH')

    cmd = ffmpeg_cmd(video, output, args.width, args.height, args.fps, args.audio_bitrate, args.clip_start, args.clip_duration, args.visual_mode)
    print('COMMAND:', ' '.join(str(x) for x in cmd))

    if args.dry_run:
        return

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        fail(f'ffmpeg exited with code {result.returncode}', result.returncode)

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f'[OK] rendered short {output.name} ({size_mb:.1f} MB)', flush=True)


if __name__ == '__main__':
    main()
