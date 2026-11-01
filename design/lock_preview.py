#!/usr/bin/env python3
"""Holo Black lock-screen preview and Plymouth wordmark.

Renders two files from the theme's own artwork:

    preview-unlock.png   1920x1080 lock-screen concept
    unlock.png           800x188 Omarchy wordmark in lavender, for Plymouth

The wordmark is the Omarchy logo, taken from a stock theme, from any theme
already installed, or from --wordmark, as an alpha mask and recoloured, so the
glyphs stay the project's own.

    python3 design/lock_preview.py
    python3 design/lock_preview.py --wordmark ~/some/unlock.png
    python3 design/lock_preview.py --wordmark unlock.png --out /tmp/preview
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

LAVENDER = (184, 184, 255)
INK = (5, 8, 15)
TEXT = (220, 221, 247)

HERE = Path(__file__).resolve().parent
THEME = HERE.parent
OMARCHY = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))


def find_wordmark(override: str | None) -> Path:
    """The Omarchy wordmark to recolour.

    An explicit path wins; otherwise any stock theme's copy, then this theme's
    own `unlock.png`, so the script still runs where Omarchy is not installed.
    """
    if override:
        path = Path(override)
        if not path.is_file():
            raise SystemExit(f"No such wordmark: {path}")
        return path

    for candidate in [*sorted((OMARCHY / "themes").glob("*/unlock.png")), THEME / "unlock.png"]:
        if candidate.is_file():
            return candidate

    raise SystemExit("No wordmark found; pass --wordmark /path/to/unlock.png")


def wordmark(width: int, source_path: Path) -> Image.Image:
    source = Image.open(source_path).convert("RGBA")
    tinted = Image.new("RGBA", source.size, LAVENDER + (0,))
    tinted.putalpha(source.getchannel("A"))
    height = round(width * source.height / source.width)
    if (width, height) == source.size:
        return tinted  # already at this size: keep the glyph edges untouched
    return tinted.resize((width, height), Image.Resampling.LANCZOS)


def radial_mask(size: tuple[int, int], strength: float) -> Image.Image:
    width, height = size
    mask = Image.new("L", (width // 8, height // 8))
    pixels = mask.load()
    cx, cy = width / 16, height / 16
    limit = (width ** 2 + height ** 2) ** 0.5 / 16
    for y in range(height // 8):
        for x in range(width // 8):
            distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / limit
            value = max(0.0, 1.0 - distance) ** 1.4
            pixels[x, y] = round(255 * (1 - (1 - value) * strength))
    return mask.resize(size, Image.Resampling.BICUBIC)


def lock_icon(draw: ImageDraw.ImageDraw, x: float, y: float, size: float, colour: tuple[int, int, int]) -> None:
    body_w = size
    body_h = size * 0.78
    radius = size * 0.18
    draw.rounded_rectangle(
        [x, y + size * 0.36, x + body_w, y + size * 0.36 + body_h],
        radius=radius,
        fill=colour + (235,),
    )
    shackle_w = size * 0.58
    draw.arc(
        [x + (body_w - shackle_w) / 2, y, x + (body_w + shackle_w) / 2, y + size * 0.72],
        start=180,
        end=360,
        fill=colour + (235,),
        width=max(2, round(size * 0.11)),
    )
    # Keyhole
    hole_r = size * 0.09
    cx = x + body_w / 2
    cy = y + size * 0.36 + body_h * 0.42
    draw.ellipse([cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r], fill=INK + (255,))
    draw.rectangle([cx - hole_r * 0.42, cy, cx + hole_r * 0.42, cy + body_h * 0.30], fill=INK + (255,))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate the Holo Black lock preview and Plymouth wordmark.")
    parser.add_argument("--wordmark", help="path to an Omarchy wordmark PNG "
                        "(default: a stock theme's, else this theme's own)")
    parser.add_argument("--out", default=str(THEME), help="output directory (default: the theme)")
    args = parser.parse_args()
    source_path = find_wordmark(args.wordmark)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Lock-screen concept ────────────────────────────────────────────────
    background = Image.open(THEME / "backgrounds" / "01-signal-hex.webp").convert("RGB")
    background = background.resize((1920, 1080), Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(2.4))
    background = ImageChops.multiply(background, Image.new("RGB", background.size, (120, 120, 132)))

    shade = radial_mask(background.size, 0.55)
    background = Image.composite(background, Image.new("RGB", background.size, (3, 5, 10)), shade)

    canvas = background.convert("RGBA")

    mark = wordmark(700, source_path)
    mark_x = (1920 - mark.width) // 2
    mark_y = 300
    canvas.alpha_composite(mark, (mark_x, mark_y))

    # Password field, centred under the wordmark, at the lock theme's scale.
    field_w, field_h = 300, 54
    field_x = (1920 - field_w) // 2
    field_y = 560
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        [field_x, field_y, field_x + field_w, field_y + field_h],
        radius=4,
        fill=INK + (150,),
        outline=LAVENDER + (150,),
        width=2,
    )
    lock_icon(draw, field_x - 42, field_y + 8, 24, TEXT)

    # Four masked characters, as the shell draws them.
    dot_y = field_y + field_h / 2
    for index in range(4):
        cx = field_x + 26 + index * 20
        draw.ellipse([cx - 4, dot_y - 4, cx + 4, dot_y + 4], fill=TEXT + (235,))

    canvas.alpha_composite(overlay)
    canvas.convert("RGB").save(out_dir / "preview-unlock.png", optimize=True)
    print(f"wrote {out_dir / 'preview-unlock.png'}")

    # ── Plymouth wordmark ──────────────────────────────────────────────────
    mark = wordmark(800, source_path)
    mark.save(out_dir / "unlock.png", optimize=True)
    print(f"wrote {out_dir / 'unlock.png'}")


if __name__ == "__main__":
    main()
