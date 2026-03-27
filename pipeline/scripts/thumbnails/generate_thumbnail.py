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
import re
import sys
import unicodedata
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


WIDTH = 1280
HEIGHT = 720


def find_repo_root(start: Path) -> Path:
    """Versucht die Repo-Wurzel robust zu finden."""
    expected_markers = [
        ("data", "assets"),
        ("docs", "templates", "thumbnails"),
    ]

    for candidate in [start, *start.parents]:
        if all((candidate.joinpath(*marker)).exists() for marker in expected_markers):
            return candidate

    # Fallback auf die bisherige Strukturannahme
    parents = start.parents
    if len(parents) >= 4:
        return parents[3]
    return start


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = find_repo_root(SCRIPT_DIR)
ASSETS_DIR = REPO_ROOT / "data" / "assets"
OUTPUT_DIR = REPO_ROOT / "data" / "output" / "thumbnails"
FONT_DIR = SCRIPT_DIR / "fonts"

# === THEME-FARBPALETTEN ===
THEMES = {
    "winterfell": {
        "bg_color": (15, 25, 45),
        "gradient_color": (40, 60, 90),
        "text_color": (220, 235, 255),
        "accent_color": (130, 180, 220),
        "subtitle_color": (170, 200, 230),
        "vignette_strength": 0.7,
        "mood": "cold",
        "font_title": "MedievalSharp-Regular.ttf",
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "king's landing": {
        "bg_color": (45, 25, 10),
        "gradient_color": (80, 50, 20),
        "text_color": (255, 230, 180),
        "accent_color": (220, 170, 80),
        "subtitle_color": (200, 180, 140),
        "vignette_strength": 0.6,
        "mood": "warm",
        "font_title": "UnifrakturMaguntia-Book.ttf",
        "font_subtitle": "PlayfairDisplay-Bold.ttf",
    },
    "targaryen": {
        "bg_color": (40, 10, 10),
        "gradient_color": (80, 20, 20),
        "text_color": (255, 220, 200),
        "accent_color": (200, 60, 40),
        "subtitle_color": (220, 180, 160),
        "vignette_strength": 0.8,
        "mood": "dark",
        "font_title": "AlmendraDisplay-Regular.ttf",
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
        "font_title": "IMFellEnglishSC-Regular.ttf",
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "highgarden": {
        "bg_color": (15, 35, 15),
        "gradient_color": (30, 60, 25),
        "text_color": (240, 255, 230),
        "accent_color": (180, 220, 100),
        "subtitle_color": (200, 230, 180),
        "vignette_strength": 0.5,
        "mood": "warm",
        "font_title": "PlayfairDisplay-Bold.ttf",
        "font_subtitle": "PlayfairDisplay-Bold.ttf",
    },
    "dorne": {
        "bg_color": (50, 30, 15),
        "gradient_color": (90, 55, 25),
        "text_color": (255, 235, 200),
        "accent_color": (230, 150, 50),
        "subtitle_color": (220, 190, 150),
        "vignette_strength": 0.6,
        "mood": "warm",
        "font_title": "AmaticSC-Bold.ttf",
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "godswood": {
        "bg_color": (20, 30, 15),
        "gradient_color": (40, 55, 30),
        "text_color": (230, 245, 220),
        "accent_color": (180, 50, 40),
        "subtitle_color": (200, 220, 190),
        "vignette_strength": 0.7,
        "mood": "mystical",
        "font_title": "UncialAntiqua-Regular.ttf",
        "font_subtitle": "Cinzel-Regular.ttf",
    },
    "castamere": {
        "bg_color": (35, 20, 15),
        "gradient_color": (70, 40, 25),
        "text_color": (255, 225, 180),
        "accent_color": (200, 160, 60),
        "subtitle_color": (210, 190, 150),
        "vignette_strength": 0.7,
        "mood": "melancholic",
        "font_title": "PirataOne-Regular.ttf",
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

THEME_ALIASES = {
    "kings landing": "king's landing",
    "kingslanding": "king's landing",
    "red keep": "king's landing",
    "theredkeep": "king's landing",
    "wall": "the wall",
    "nights watch": "the wall",
    "nightswatch": "the wall",
}


def normalize_text(value: str) -> str:
    """Normalisiert Text für Matching/Slugging."""
    value = value.strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("’", "'")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


NORMALIZED_THEME_MAP = {normalize_text(name): name for name in THEMES.keys()}


def get_theme_name(name: str) -> str:
    """Findet den passenden Theme-Namen robust über Normalisierung und Aliases."""
    normalized = normalize_text(name or "")

    if not normalized:
        return "default"

    if normalized in THEME_ALIASES:
        return THEME_ALIASES[normalized]

    if normalized in NORMALIZED_THEME_MAP:
        return NORMALIZED_THEME_MAP[normalized]

    for normalized_key, original_key in NORMALIZED_THEME_MAP.items():
        if normalized_key in normalized or normalized in normalized_key:
            return original_key

    return "default"


def get_theme(name: str) -> dict:
    return THEMES[get_theme_name(name)]


def create_gradient(width: int, height: int, color1: tuple[int, int, int], color2: tuple[int, int, int]) -> Image.Image:
    """Vertikaler Gradient von color1 (oben) zu color2 (unten)."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def add_vignette(img: Image.Image, strength: float = 0.7) -> Image.Image:
    """Dunkle Ecken für cinematic Look, performant via low-res Mask."""
    small_w, small_h = 64, 36
    small = Image.new("L", (small_w, small_h), 0)
    draw = ImageDraw.Draw(small)

    cx, cy = small_w / 2, small_h / 2
    max_dist = (cx**2 + cy**2) ** 0.5

    for y in range(small_h):
        for x in range(small_w):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            ratio = min(dist / max_dist, 1.0)
            val = int(255 * (1 - ratio * strength))
            draw.point((x, y), fill=max(0, min(255, val)))

    mask = small.resize(img.size, Image.LANCZOS)
    black = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(img, black, mask)


def get_font(size: int, bold: bool = False, style: str = "title", theme: dict | None = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Lädt thematische Fonts pro Haus/Theme."""
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

    if style == "title":
        fallback_fonts = ["CinzelDecorative-Bold.ttf", "Cinzel-Bold.ttf"]
    elif style == "subtitle":
        fallback_fonts = ["Cinzel-Regular.ttf", "Cinzel-Bold.ttf"]
    else:
        fallback_fonts = ["Cinzel-Bold.ttf", "Cinzel-Regular.ttf"]

    for name in fallback_fonts:
        path = FONT_DIR / name
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except (IOError, OSError):
                pass

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
                try:
                    return ImageFont.truetype(str(path), size)
                except (IOError, OSError):
                    pass

    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except (IOError, OSError):
        return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def split_long_word(word: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Bricht ein einzelnes zu langes Wort sinnvoll in Stücke."""
    parts = []
    current = ""

    for index, char in enumerate(word):
        is_last_char = index == len(word) - 1
        tentative = current + char
        preview = tentative if is_last_char else tentative + "-"

        if current and text_width(draw, preview, font) > max_width:
            parts.append(current + "-")
            current = char
        else:
            current = tentative

    if current:
        parts.append(current)

    return parts


def wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Bricht Text um wenn er zu breit ist, inkl. langer Einzelwörter."""
    words = text.split()
    if not words:
        return []

    lines = []
    current = ""

    for word in words:
        if text_width(draw, word, font) > max_width:
            if current:
                lines.append(current)
                current = ""
            lines.extend(split_long_word(word, font, max_width, draw))
            continue

        test = f"{current} {word}".strip()
        if text_width(draw, test, font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    text: str,
    font,
    fill,
    shadow_color=(0, 0, 0),
    shadow_offset: int = 3,
):
    """Text mit Schatten für bessere Lesbarkeit."""
    x, y = pos

    for dx in range(-shadow_offset, shadow_offset + 1):
        for dy in range(-shadow_offset, shadow_offset + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)

    draw.text(pos, text, font=font, fill=fill)


def slugify(text: str) -> str:
    """Erzeugt sichere Dateinamen."""
    normalized = normalize_text(text)
    slug = normalized.replace(" ", "-")
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "thumbnail"


def resolve_output_path(title: str, output_path: str | None) -> Path:
    """Ermittelt den finalen Output-Pfad und ergänzt bei Bedarf eine sinnvolle Endung."""
    if output_path:
        path = Path(output_path)
        if path.suffix:
            return path
        return path.with_suffix(".jpg")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR / f"{slugify(title)}.jpg"


def save_image(img: Image.Image, output_path: Path) -> None:
    """Speichert das Bild passend zur Dateiendung."""
    suffix = output_path.suffix.lower() or ".jpg"
    output_path = output_path.with_suffix(suffix)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if suffix in {".jpg", ".jpeg"}:
        img.convert("RGB").save(str(output_path), "JPEG", quality=95, optimize=True)
    elif suffix == ".png":
        img.save(str(output_path), "PNG", optimize=True)
    elif suffix == ".webp":
        img.save(str(output_path), "WEBP", quality=95, method=6)
    else:
        fallback_path = output_path.with_suffix(".jpg")
        img.convert("RGB").save(str(fallback_path), "JPEG", quality=95, optimize=True)
        print(f"⚠️ Unbekannte Endung '{suffix}'. Speichere stattdessen als JPEG: {fallback_path}")
        return

    print(f"✅ Thumbnail: {output_path} ({WIDTH}x{HEIGHT})")


def build_background(bg_image: str | None, theme: dict) -> Image.Image:
    """Erzeugt den Hintergrund ausschließlich aus einem echten Bild."""
    if not bg_image:
        raise ValueError("Kein Hintergrundbild angegeben. --bg-image ist erforderlich.")

    bg_path = Path(bg_image)
    if not bg_path.exists() or not bg_path.is_file():
        raise FileNotFoundError(f"Hintergrundbild nicht gefunden: {bg_path}")

    img = Image.open(bg_path).convert("RGB")
    img = ImageOps.fit(img, (WIDTH, HEIGHT), method=Image.LANCZOS, centering=(0.5, 0.5))
    img = img.filter(ImageFilter.GaussianBlur(radius=5))

    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.7)

    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.3)
    return img


def compute_line_heights(draw: ImageDraw.ImageDraw, lines: list[str], font) -> tuple[list[int], int]:
    """Berechnet reale Zeilenhöhen auf Basis der Font-Metriken."""
    heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        heights.append(max(1, bbox[3] - bbox[1]))

    try:
        ascent, descent = font.getmetrics()
        line_spacing = max(8, int((ascent + descent) * 0.18))
    except AttributeError:
        line_spacing = 12

    return heights, line_spacing


def generate_thumbnail(title, theme_name, subtitle="3 Hours Deep Sleep Music", output_path=None, bg_image=None):
    """Generiert ein YouTube-Thumbnail."""
    theme = get_theme(theme_name)

    img = build_background(bg_image, theme)
    img = add_vignette(img, theme["vignette_strength"])
    draw = ImageDraw.Draw(img)

    logo_path = ASSETS_DIR / "whispers-of-the-seven-kingdoms-logo.jpg"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = 80
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            img.paste(logo, (WIDTH - logo_size - 30, 30), logo)
        except Exception:
            pass

    title_font = get_font(80, bold=True, style="title", theme=theme)
    subtitle_font = get_font(32, bold=False, style="subtitle", theme=theme)
    brand_font = get_font(22, bold=False, style="brand", theme=theme)

    max_text_width = WIDTH - 160
    title_lines = wrap_text(title.upper(), title_font, max_text_width, draw)
    if not title_lines:
        title_lines = ["UNTITLED"]

    title_heights, title_spacing = compute_line_heights(draw, title_lines, title_font)
    title_block_height = sum(title_heights) + title_spacing * max(0, len(title_lines) - 1)

    subtitle_text = f"♫ {subtitle} ♫"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

    brand_text = "Whispers of the Seven Kingdoms"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_height = brand_bbox[3] - brand_bbox[1]

    accent_gap_top = 16
    accent_gap_bottom = 20
    subtitle_gap_bottom = 45
    bottom_brand_margin = 42

    total_text_height = (
        title_block_height
        + accent_gap_top
        + 4
        + accent_gap_bottom
        + subtitle_height
        + subtitle_gap_bottom
        + brand_height
    )

    start_y = max(40, (HEIGHT - total_text_height) // 2)

    current_y = start_y
    for line, line_height in zip(title_lines, title_heights):
        line_width = text_width(draw, line, title_font)
        x = (WIDTH - line_width) // 2
        draw_text_with_shadow(draw, (x, current_y), line, title_font, theme["text_color"])
        current_y += line_height + title_spacing

    current_y -= title_spacing if len(title_lines) > 1 else 0
    line_y = current_y + accent_gap_top
    accent_width = min(400, max_text_width // 2)
    draw.rectangle(
        [
            (WIDTH // 2 - accent_width // 2, line_y),
            (WIDTH // 2 + accent_width // 2, line_y + 3),
        ],
        fill=theme["accent_color"],
    )

    subtitle_width = text_width(draw, subtitle_text, subtitle_font)
    sub_y = line_y + accent_gap_bottom
    draw_text_with_shadow(
        draw,
        ((WIDTH - subtitle_width) // 2, sub_y),
        subtitle_text,
        subtitle_font,
        theme["subtitle_color"],
        shadow_offset=2,
    )

    brand_width = text_width(draw, brand_text, brand_font)
    brand_y = min(HEIGHT - bottom_brand_margin, sub_y + subtitle_height + subtitle_gap_bottom)
    draw_text_with_shadow(
        draw,
        ((WIDTH - brand_width) // 2, brand_y),
        brand_text,
        brand_font,
        theme["accent_color"],
        shadow_offset=1,
    )

    final_output_path = resolve_output_path(title, output_path)
    save_image(img, final_output_path)
    return str(final_output_path)


def list_themes():
    print("\n🎨 Verfügbare Themes:\n")
    for name, theme in THEMES.items():
        if name == "default":
            continue
        print(f"  {name:<20} Mood: {theme['mood']}")
    print(f"\n  {'default':<20} Fallback für unbekannte Themes")


def main():
    parser = argparse.ArgumentParser(description="Thumbnail-Generator – Whispers of the Seven Kingdoms")
    parser.add_argument("--title", type=str, help="Video-Titel für Thumbnail")
    parser.add_argument("--theme", type=str, default="default", help="Theme/Location (winterfell, targaryen, etc.)")
    parser.add_argument("--subtitle", type=str, default="3 Hours Deep Sleep Music", help="Untertitel")
    parser.add_argument("--output", type=str, help="Output-Pfad (default: output/thumbnails/) ")
    parser.add_argument("--bg-image", type=str, help="Pflicht: Hintergrundbild")
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

    try:
        generate_thumbnail(args.title, args.theme, args.subtitle, args.output, args.bg_image)
    except (ValueError, FileNotFoundError) as exc:
        print(f"❌ {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
