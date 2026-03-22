#!/usr/bin/env python3
"""
Animated Video Renderer – Whispers of the Seven Kingdoms
Erzeugt Loop-Videos mit Kamerafahrt + Partikel-Effekten aus einem Hintergrundbild.
"""
import argparse
import math
import random
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("❌ Pillow fehlt: pip install Pillow")
    sys.exit(1)

# Partikel-Presets pro Theme
PARTICLE_PRESETS = {
    "winterfell":   {"type": "snow",     "count": 200, "color": (255, 255, 255)},
    "the-wall":     {"type": "snow",     "count": 300, "color": (200, 220, 255)},
    "kings-landing": {"type": "embers",  "count": 80,  "color": (255, 180, 50)},
    "targaryen":    {"type": "embers",   "count": 150, "color": (255, 100, 30)},
    "highgarden":   {"type": "firefly",  "count": 60,  "color": (200, 255, 100)},
    "dorne":        {"type": "dust",     "count": 50,  "color": (255, 220, 150)},
    "godswood":     {"type": "firefly",  "count": 80,  "color": (150, 255, 150)},
    "castamere":    {"type": "rain",     "count": 250, "color": (180, 200, 220)},
}

DEFAULT_PRESET = {"type": "snow", "count": 100, "color": (255, 255, 255)}


class Particle:
    def __init__(self, w, h, ptype, color):
        self.w, self.h = w, h
        self.ptype = ptype
        self.color = color
        self.reset(initial=True)

    def reset(self, initial=False):
        self.x = random.randint(0, self.w)
        if self.ptype == "rain":
            self.y = random.randint(-self.h, 0) if not initial else random.randint(-self.h, self.h)
            self.speed = random.uniform(8, 15)
            self.drift = random.uniform(-0.5, 0.5)
            self.size = random.randint(1, 2)
            self.length = random.randint(8, 20)
        elif self.ptype == "embers":
            self.y = random.randint(self.h, self.h + 200) if not initial else random.randint(0, self.h)
            self.speed = random.uniform(-2.5, -0.8)  # floats UP
            self.drift = random.uniform(-1.0, 1.0)
            self.size = random.randint(2, 4)
            self.length = 0
        elif self.ptype == "firefly":
            self.y = random.randint(0, self.h) if initial else random.randint(0, self.h)
            self.speed = random.uniform(-0.3, 0.3)
            self.drift = random.uniform(-0.5, 0.5)
            self.size = random.randint(2, 4)
            self.length = 0
            self.phase = random.uniform(0, 2 * math.pi)
        elif self.ptype == "dust":
            self.y = random.randint(0, self.h)
            self.speed = random.uniform(-0.2, 0.2)
            self.drift = random.uniform(0.3, 1.0)
            self.size = random.randint(1, 3)
            self.length = 0
        else:  # snow
            self.y = random.randint(-20, -5) if not initial else random.randint(-self.h, self.h)
            self.speed = random.uniform(1.5, 4.0)
            self.drift = random.uniform(-0.3, 0.3)
            self.size = random.randint(2, 5)
            self.length = 0
        self.alpha = random.randint(120, 220)

    def update(self, frame_i=0):
        self.y += self.speed
        self.x += self.drift + random.uniform(-0.3, 0.3)

        if self.ptype == "firefly":
            # Pulsing glow
            self.alpha = int(120 + 100 * abs(math.sin(self.phase + frame_i * 0.05)))

        # Wrap / respawn
        if self.ptype in ("snow", "rain", "dust"):
            if self.y > self.h + 20:
                self.reset()
        elif self.ptype == "embers":
            if self.y < -20:
                self.reset()
        if self.x < -10: self.x = self.w + 10
        if self.x > self.w + 10: self.x = -10

    def draw(self, draw_ctx):
        c = self.color + (self.alpha,)
        if self.ptype == "rain":
            draw_ctx.line(
                [(self.x, self.y), (self.x + self.drift * 2, self.y + self.length)],
                fill=c, width=self.size
            )
        else:
            draw_ctx.ellipse(
                [self.x - self.size, self.y - self.size,
                 self.x + self.size, self.y + self.size],
                fill=c
            )


def render_animated_video(bg_path, output_path, theme="winterfell",
                          loop_duration=30, audio_path=None, fps=30):
    """Rendert ein animiertes Loop-Video."""
    preset = PARTICLE_PRESETS.get(theme, DEFAULT_PRESET)
    WIDTH, HEIGHT = 1920, 1080
    TOTAL_FRAMES = fps * loop_duration

    # Load & upscale background for pan room
    bg = Image.open(bg_path).resize((2880, 1620), Image.LANCZOS)

    # Init particles
    particles = [
        Particle(WIDTH, HEIGHT, preset["type"], preset["color"])
        for _ in range(preset["count"])
    ]

    # Pipe frames to ffmpeg
    if audio_path:
        loop_file = str(Path(output_path).with_suffix('.loop.mp4'))
    else:
        loop_file = str(output_path)

    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{WIDTH}x{HEIGHT}', '-r', str(fps),
        '-i', 'pipe:0',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '28',
        '-pix_fmt', 'yuv420p', loop_file
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    MAX_PAN_X, MAX_PAN_Y = 960, 200

    for fi in range(TOTAL_FRAMES):
        progress = fi / TOTAL_FRAMES

        # Pendulum pan (seamless loop via sin)
        pan_x = int(MAX_PAN_X * (0.5 + 0.5 * math.sin(2 * math.pi * progress - math.pi / 2)))
        pan_y = int(MAX_PAN_Y * (0.5 + 0.5 * math.sin(2 * math.pi * progress * 0.7)))

        crop = bg.crop((pan_x, pan_y, pan_x + WIDTH, pan_y + HEIGHT))
        frame = crop.convert('RGBA')

        # Draw particles
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for p in particles:
            p.update(fi)
            p.draw(draw)

        frame = Image.alpha_composite(frame, overlay).convert('RGB')
        proc.stdin.write(frame.tobytes())

        if fi % (TOTAL_FRAMES // 5) == 0:
            pct = int(fi / TOTAL_FRAMES * 100)
            print(f"  Rendering: {pct}%")

    proc.stdin.close()
    proc.wait()
    print(f"  Rendering: 100%")

    # If audio provided: loop video to match audio length, mux
    if audio_path:
        print(f"  Muxing with audio...")
        mux_cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1',
            '-i', str(Path(loop_file).resolve()),
            '-i', str(Path(audio_path).resolve()),
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest', '-movflags', '+faststart',
            str(Path(output_path).resolve())
        ]
        subprocess.run(mux_cmd, check=True, capture_output=True)
        Path(loop_file).unlink(missing_ok=True)

    print(f"✅ Video: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Animated Video Renderer")
    parser.add_argument("--bg-image", required=True, help="Hintergrundbild")
    parser.add_argument("--output", required=True, help="Ausgabe MP4")
    parser.add_argument("--theme", default="winterfell", help="Partikel-Theme")
    parser.add_argument("--audio", help="Audio-Datei (MP3)")
    parser.add_argument("--loop-duration", type=int, default=30, help="Loop-Länge in Sekunden")
    parser.add_argument("--fps", type=int, default=24)
    args = parser.parse_args()

    render_animated_video(
        args.bg_image, args.output, args.theme,
        args.loop_duration, args.audio, args.fps
    )


if __name__ == "__main__":
    main()
