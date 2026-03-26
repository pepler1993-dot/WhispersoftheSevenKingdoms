#!/usr/bin/env python3
"""
Thumbnail-Generator – Whispers of the Seven Kingdoms

Generiert YouTube-Thumbnails (1280x720) automatisch aus Templates.
Bild + Text-Overlay + Branding → fertig.

Usage:
    python generate_thumbnail.py --title "Whispers of Winterfell" --theme winterfell
    python generate_thumbnail.py --title "Lullaby of the Red Keep" --theme castamere --output thumb.jpg
    python generate_thumbnail.py --list-themes

Benötigt: pip install Pillow
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ASSETS_DIR = REPO_ROOT / "data" / "assets"
TEMPLATES_DIR = REPO_ROOT / "docs" / "templates" / "thumbnails"
OUTPUT_DIR = REPO_ROOT / "data" / "output" / "thumbnails"
FONT_DIR = Path(__file__).parent / "fonts"

WIDTH = 1280
HEIGHT = 720

# === THEME-FARBPALETTEN ===
THEMES = {
    "winterfell": {
        "bg_color": (15, 25, 45),          # Dunkles Eisblau
        "gradient_color": (40, 60, 90),     # Heller Blauton
        "text_color": (220, 235, 255),      # Eisweiß
        "accent_color": (130, 180, 220),    # Frostblau
        "subtitle_color": (170, 200, 230),
        "vignette_strength": 0.7,
        "mood": "cold",
        "font_title": "MedievalSharp-Regular.ttf",    # Nordisch/mittelalterlich → Stark
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "king's landing": {
        "bg_color": (45, 25, 10),
        "gradient_color": (80, 50, 20),
        "text_color": (255, 230, 180),
        "accent_color": (220, 170, 80),     # Gold
        "subtitle_color": (200, 180, 140),
        "vignette_strength": 0.6,
        "mood": "warm",
        "font_title": "UnifrakturMaguntia-Book.ttf",  # Blackletter/Royal → Krone
        "font_subtitle": "PlayfairDisplay-Bold.ttf",
    },
    "targaryen": {
        "bg_color": (40, 10, 10),
        "gradient_color": (80, 20, 20),
        "text_color": (255, 220, 200),
        "accent_color": (200, 60, 40),      # Feuerrot
        "subtitle_color": (220, 180, 160),
        "vignette_strength": 0.8,
        "mood": "dark",
        "font_title": "AlmendraDisplay-Regular.ttf",  # Fantasy/Drachen → Targaryen
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "the wall": {
        "bg_color": (10, 15, 25),
        "gradient_color": (30, 40, 55),
        "text_color": (200, 210, 230),
        "accent_color": (100, 140, 180),
        "subtitle_color": (150, 170, 200),
        "vignette_strength": 0.9,
        "mood": "cold",
        "font_title": "IMFellEnglishSC-Regular.ttf",  # Antik/wuchtig → Night's Watch
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "highgarden": {
        "bg_color": (15, 35, 15),
        "gradient_color": (30, 60, 25),
        "text_color": (240, 255, 230),
        "accent_color": (180, 220, 100),    # Grün-Gold
        "subtitle_color": (200, 230, 180),
        "vignette_strength": 0.5,
        "mood": "warm",
        "font_title": "PlayfairDisplay-Bold.ttf",     # Elegant/edel → Tyrell
        "font_subtitle": "PlayfairDisplay-Bold.ttf",
    },
    "dorne": {
        "bg_color": (50, 30, 15),
        "gradient_color": (90, 55, 25),
        "text_color": (255, 235, 200),
        "accent_color": (230, 150, 50),     # Wüstengold
        "subtitle_color": (220, 190, 150),
        "vignette_strength": 0.6,
        "mood": "warm",
        "font_title": "AmaticSC-Bold.ttf",            # Exotisch/handschriftlich → Martell
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "godswood": {
        "bg_color": (20, 30, 15),
        "gradient_color": (40, 55, 30),
        "text_color": (230, 245, 220),
        "accent_color": (180, 50, 40),      # Weirwood-Rot
        "subtitle_color": (200, 220, 190),
        "vignette_strength": 0.7,
        "mood": "mystical",
        "font_title": "UncialAntiqua-Regular.ttf",    # Keltisch/mystisch → Alte Götter
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "castamere": {
        "bg_color": (35, 20, 15),
        "gradient_color": (70, 40, 25),
        "text_color": (255, 225, 180),
        "accent_color": (200, 160, 60),     # Lannister-Gold
        "subtitle_color": (210, 190, 150),
        "vignette_strength": 0.7,
        "mood": "melancholic",
        "font_title": "PirataOne-Regular.ttf",        # Dramatisch/ornamental → Lannister
        "font_subtitle": "PlayfairDisplay-Bold.ttf",
    },
    "default": {
        "bg_color": (20, 20, 35),
        "gradient_color": (45, 40, 65),
        "text_color": (230, 230, 245),
        "accent_color": (160, 140, 200),
        "subtitle_color": (190, 185, 210),
        "vignette_strength": 0.6,
        "mood": "calm",
        "font_title": "CinzelDecorative-Bold.ttf",
        "font_subtitle": "Cinzel-Regular.ttf",
    },
}


def get_theme(name):
    """Findet passendes Theme."""
    name_lower = name.lower()
    for key in THEMES:
        if key in name_lower or name_lower in key:
            return THEMES[key]
    return THEMES["default"]


def create_gradient(width, height, color1, color2):
    """Vertikaler Gradient von color1 (oben) zu color2 (unten)."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def add_vignette(img, strength=0.7):
    """Dunkle Ecken für cinematic Look."""
    vignette = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(vignette)
    cx, cy = img.size[0] // 2, img.size[1] // 2
    max_dist = (cx**2 + cy**2) ** 0.5

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
            ratio = dist / max_dist
            brightness = int(255 * (1 - ratio * strength))
            draw.point((x, y), fill=max(0, brightness))

    # Schneller: resize trick
    small = Image.new("L", (64, 36), 0)
    draw_s = ImageDraw.Draw(small)
    scx, scy = 32, 18
    smax = (scx**2 + scy**2) ** 0.5
    for sy in range(36):
        for sx in range(64):
            dist = ((sx - scx)**2 + (sy - scy)**2) ** 0.5
            ratio = dist / smax
            val = int(255 * (1 - ratio * strength))
            draw_s.point((sx, sy), fill=max(0, val))
    vignette = small.resize(img.size, Image.LANCZOS)

    result = Image.composite(img, Image.new("RGB", img.size, (0, 0, 0)), vignette)
    return result


def get_font(size, bold=False, style="title", theme=None):
    """Lädt thematische Fonts pro Haus/Theme."""
    # Per-theme font selection
    if theme and style == "title" and "font_title" in theme:
        path = FONT_DIR / theme["font_title"]
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except (IOError, OSError):
                pass
    if theme and style == "subtitle" and "font_subtitle" in theme:
        path = FONT_DIR / theme["font_subtitle"]
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except (IOError, OSError):
                pass

    # Fallback: Cinzel
    if style == "title":
        fantasy_fonts = ["CinzelDecorative-Bold.ttf", "Cinzel-Bold.ttf"]
    elif style == "subtitle":
        fantasy_fonts = ["Cinzel-Regular.ttf", "Cinzel-Bold.ttf"]
    else:
        fantasy_fonts = ["Cinzel-Bold.ttf"]

    for name in fantasy_fonts:
        path = FONT_DIR / name
        if path.exists():
            return ImageFont.truetype(str(path), size)

    # System fallback
    font_names = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arial.ttf",
        "FreeSans.ttf",
    ]
    system_paths = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/freefont/",
        "/usr/share/fonts/",
    ]
    for sp in system_paths:
        for name in font_names:
            path = Path(sp) / name
            if path.exists():
                return ImageFont.truetype(str(path), size)

    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except (IOError, OSError):
        return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Bricht Text um wenn er zu breit ist."""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    return lines


def draw_text_with_shadow(draw, pos, text, font, fill, shadow_color=(0, 0, 0), shadow_offset=3):
    """Text mit Schatten für bessere Lesbarkeit."""
    x, y = pos
    # Shadow
    for dx in range(-shadow_offset, shadow_offset + 1):
        for dy in range(-shadow_offset, shadow_offset + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=shadow_color + (120,))
    # Main text
    draw.text(pos, text, font=font, fill=fill)


def generate_thumbnail(title, theme_name, subtitle="3 Hours Deep Sleep Music", output_path=None, bg_image=None):
    """Generiert ein YouTube-Thumbnail."""
    theme = get_theme(theme_name)

    # 1. Hintergrund
    if bg_image and Path(bg_image).exists():
        img = Image.open(bg_image).convert("RGB")
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        # Light blur for dreamy background effect
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        # Slight darken for text readability, keep image visible
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)
        # Boost saturation slightly to keep the mood
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)
    else:
        img = create_gradient(WIDTH, HEIGHT, theme["bg_color"], theme["gradient_color"])

    # 2. Vignette
    img = add_vignette(img, theme["vignette_strength"])

    # 3. Zeichnen
    draw = ImageDraw.Draw(img)

    # Channel-Logo einbetten (wenn vorhanden)
    logo_path = ASSETS_DIR / "whispers-of-the-seven-kingdoms-logo.jpg"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = 80
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            img.paste(logo, (WIDTH - logo_size - 30, 30), logo if logo.mode == "RGBA" else None)
        except Exception:
            pass

    # 4. Text-Layout (Theme-spezifische Fonts)
    title_font = get_font(80, bold=True, style="title", theme=theme)
    subtitle_font = get_font(32, bold=False, style="subtitle", theme=theme)
    brand_font = get_font(22, bold=False, style="brand", theme=theme)

    # Titel (zentriert, mit Umbruch)
    max_text_width = WIDTH - 160
    title_lines = wrap_text(title.upper(), title_font, max_text_width, draw)

    # Berechne Gesamthöhe für Zentrierung
    line_height = 85
    total_text_height = len(title_lines) * line_height + 60 + 45  # +subtitle+brand
    start_y = (HEIGHT - total_text_height) // 2

    # Titel zeichnen
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        y = start_y + i * line_height
        draw_text_with_shadow(draw, (x, y), line, title_font, theme["text_color"])

    # Akzent-Linie unter Titel
    line_y = start_y + len(title_lines) * line_height + 10
    accent_width = min(400, max_text_width // 2)
    draw.rectangle(
        [(WIDTH // 2 - accent_width // 2, line_y),
         (WIDTH // 2 + accent_width // 2, line_y + 3)],
        fill=theme["accent_color"]
    )

    # Subtitle
    subtitle_text = f"♫ {subtitle} ♫"
    bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    sub_width = bbox[2] - bbox[0]
    sub_y = line_y + 20
    draw_text_with_shadow(draw, ((WIDTH - sub_width) // 2, sub_y), subtitle_text,
                          subtitle_font, theme["subtitle_color"], shadow_offset=2)

    # Brand unten
    brand_text = "Whispers of the Seven Kingdoms"
    bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_width = bbox[2] - bbox[0]
    draw_text_with_shadow(draw, ((WIDTH - brand_width) // 2, HEIGHT - 50), brand_text,
                          brand_font, theme["accent_color"], shadow_offset=1)

    # 5. Speichern
    if not output_path:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        slug = title.lower().replace(" ", "-").replace("'", "")
        output_path = OUTPUT_DIR / f"{slug}.jpg"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "JPEG", quality=95)
    print(f"✅ Thumbnail: {output_path} ({WIDTH}x{HEIGHT})")
    return str(output_path)


def list_themes():
    print("\n🎨 Verfügbare Themes:\n")
    for name, t in THEMES.items():
        if name == "default":
            continue
        print(f"  {name:<20} Mood: {t['mood']}")
    print(f"\n  {'default':<20} Fallback für unbekannte Themes")


def main():
    parser = argparse.ArgumentParser(description="Thumbnail-Generator – Whispers of the Seven Kingdoms")
    parser.add_argument("--title", type=str, help="Video-Titel für Thumbnail")
    parser.add_argument("--theme", type=str, default="default", help="Theme/Location (winterfell, targaryen, etc.)")
    parser.add_argument("--subtitle", type=str, default="3 Hours Deep Sleep Music", help="Untertitel")
    parser.add_argument("--output", type=str, help="Output-Pfad (default: output/thumbnails/)")
    parser.add_argument("--bg-image", type=str, help="Optionales Hintergrundbild")
    parser.add_argument("--list-themes", action="store_true", help="Alle Themes anzeigen")

    args = parser.parse_args()

    if args.list_themes:
        list_themes()
        return

    if not args.title:
        parser.print_help()
        return

    if not HAS_PILLOW:
        print("❌ Pillow fehlt. Installiere mit: pip install Pillow")
        sys.exit(1)

    generate_thumbnail(args.title, args.theme, args.subtitle, args.output, args.bg_image)


if __name__ == "__main__":
    main()
