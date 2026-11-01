#!/usr/bin/env python3
"""Holo Black wallpaper generator.

Draws the wallpapers from the theme's five anchors, so the set can be rebuilt
or retuned without touching an image editor:

    #0A0F1E ink        #2A2F45 slate      #B8B8FF lavender
    #FF4FD8 magenta    #2EF9B6 mint

Mint is deliberately absent: in this theme it means "success", and a wallpaper
is decoration. The grain is seeded per wallpaper, so a run reproduces the
committed set exactly. Run from anywhere:

    python3 design/wallpapers.py                   # all four, 2560x1440 WebP
    python3 design/wallpapers.py --size 3840x2160  # larger set
    python3 design/wallpapers.py --format png      # PNG instead of WebP
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

INK = (10, 15, 30)
INK_DEEP = (5, 8, 15)
INK_BAR = (7, 11, 22)
SLATE = (42, 47, 69)
LAVENDER = (184, 184, 255)
MAGENTA = (255, 79, 216)
WHITE = (220, 221, 247)

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "backgrounds"

SS = 2  # supersample factor for crisp hairlines


def vertical_gradient(width: int, height: int, stops: list[tuple[float, tuple[int, int, int]]]) -> Image.Image:
    """A smooth vertical gradient from a list of (position 0..1, colour)."""
    column = Image.new("RGB", (1, height))
    pixels = column.load()
    stops = sorted(stops, key=lambda stop: stop[0])
    for y in range(height):
        t = y / max(1, height - 1)
        for index in range(len(stops) - 1):
            p0, c0 = stops[index]
            p1, c1 = stops[index + 1]
            if p0 <= t <= p1:
                local = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                pixels[0, y] = tuple(round(a + (b - a) * local) for a, b in zip(c0, c1))
                break
        else:
            pixels[0, y] = stops[-1][1]
    return column.resize((width, height), Image.Resampling.BILINEAR)


def radial_mask(size: tuple[int, int], centre: tuple[float, float], radius: float, power: float = 2.0,
                scale: int = 8) -> Image.Image:
    """A soft radial falloff, computed small and upscaled."""
    width, height = size
    small = (max(2, width // scale), max(2, height // scale))
    mask = Image.new("L", small)
    pixels = mask.load()
    cx, cy = centre[0] / scale, centre[1] / scale
    r = radius / scale
    for y in range(small[1]):
        for x in range(small[0]):
            d = math.hypot(x - cx, y - cy) / r
            value = max(0.0, 1.0 - d) ** power if d < 1 else 0.0
            pixels[x, y] = round(255 * value)
    return mask.resize(size, Image.Resampling.BICUBIC)


def glow(size: tuple[int, int], centre: tuple[float, float], radius: float, colour: tuple[int, int, int],
         strength: float = 1.0, power: float = 2.0, blur: int = 24) -> Image.Image:
    """An additive coloured light: screen-blend the result onto a base."""
    mask = radial_mask(size, centre, radius, power).filter(ImageFilter.GaussianBlur(blur))
    if strength != 1.0:
        mask = mask.point(lambda v: round(v * strength))
    layer = Image.new("RGB", size, (0, 0, 0))
    layer.paste(Image.new("RGB", size, colour), (0, 0), mask)
    return layer


def hex_points(cx: float, cy: float, radius: float, rotation: float = 0.0) -> list[tuple[float, float]]:
    """Pointy-top hexagon vertices."""
    return [
        (cx + radius * math.cos(math.radians(60 * index - 90 + rotation)),
         cy + radius * math.sin(math.radians(60 * index - 90 + rotation)))
        for index in range(6)
    ]


def hex_lattice(width: int, height: int, radius: float, rotation: float = 0.0) -> list[tuple[float, float, float]]:
    """Centres of a pointy-top hexagonal tiling covering the canvas."""
    step_x = math.sqrt(3) * radius
    step_y = 1.5 * radius
    centres = []
    row = 0
    y = -radius
    while y < height + radius:
        offset = step_x / 2 if row % 2 else 0
        x = -radius + offset
        while x < width + radius:
            centres.append((x, y, radius))
            x += step_x
        y += step_y
        row += 1
    return centres


def grain(image: Image.Image, amount: float = 0.35, sigma: float = 22, seed: int = 0) -> Image.Image:
    """Deterministic film grain.

    `Image.effect_noise` cannot be seeded, and unseeded noise means the committed
    wallpapers could never be rebuilt. Instead two seeded uniform layers are
    averaged into a gaussian-like bell and rescaled to `sigma`.
    """
    width, height = image.size
    layers = [
        Image.frombytes("L", (width, height), random.Random(seed + index).randbytes(width * height))
        for index in range(2)
    ]
    noise = Image.blend(layers[0], layers[1], 0.5)
    # Two averaged uniforms carry a standard deviation of about 52; scale to sigma.
    noise = noise.point(lambda v: max(0, min(255, round(128 + (v - 128) * sigma / 52))))
    return Image.blend(image, ImageChops.overlay(image, noise.convert("RGB")), amount)


def scanlines(size: tuple[int, int], alpha: int = 10, spacing: int = 4) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for y in range(0, size[1], spacing):
        draw.line([(0, y), (size[0], y)], fill=(0, 0, 0, alpha))
    return layer


def vignette(image: Image.Image, strength: float = 0.55) -> Image.Image:
    width, height = image.size
    mask = radial_mask((width, height), (width / 2, height / 2), math.hypot(width, height) * 0.62, power=1.6)
    dark = mask.point(lambda v: round(255 - (255 - v) * strength))
    shade = Image.merge("RGB", (dark, dark, dark))
    return ImageChops.multiply(image, shade)


def finish(image: Image.Image) -> Image.Image:
    return image.filter(ImageFilter.GaussianBlur(0.4))


# ── Wallpaper 1: Holo Lattice ───────────────────────────────────────────────

def holo_lattice(size: tuple[int, int]) -> Image.Image:
    out_width, out_height = size
    width, height = out_width * SS, out_height * SS
    sw, sh = width, height
    canvas = (sw, sh)

    base = vertical_gradient(width, height, [
        (0.0, (6, 9, 18)),
        (0.45, INK),
        (1.0, (12, 18, 38)),
    ])
    base = ImageChops.screen(base, glow(canvas, (width * 0.76, height * 0.30), width * 0.52, LAVENDER, 0.42, 2.4))
    base = ImageChops.screen(base, glow(canvas, (width * 0.18, height * 0.86), width * 0.42, MAGENTA, 0.20, 2.8))
    base = ImageChops.screen(base, glow(canvas, (width * 0.52, height * 0.52), width * 0.36, (24, 32, 64), 0.55, 2.0))

    lattice = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(lattice)
    focus = (sw * 0.76, sh * 0.30)
    radius = 62 * SS

    for cx, cy, r in hex_lattice(sw, sh, radius):
        distance = math.hypot(cx - focus[0], cy - focus[1]) / (sw * 0.55)
        lift = max(0.0, 1.0 - distance)
        points = hex_points(cx, cy, r)
        colour = (
            round(SLATE[0] + (LAVENDER[0] - SLATE[0]) * lift),
            round(SLATE[1] + (LAVENDER[1] - SLATE[1]) * lift),
            round(SLATE[2] + (LAVENDER[2] - SLATE[2]) * lift),
        )
        alpha = round(28 + 92 * lift ** 2)
        draw.polygon(points, outline=colour + (alpha,), width=max(1, SS))

    # A few hexagons near the light are filled, like lit cells of the lattice.
    lit = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    lit_draw = ImageDraw.Draw(lit)
    for cx, cy, r in hex_lattice(sw, sh, radius):
        distance = math.hypot(cx - focus[0], cy - focus[1])
        if distance > radius * 4.2:
            continue
        strength = max(0.0, 1.0 - distance / (radius * 4.2))
        points = hex_points(cx - radius * 0.12, cy - radius * 0.12, r * 0.94)
        lit_draw.polygon(points, fill=LAVENDER + (round(36 * strength),))
        lit_draw.polygon(points, outline=LAVENDER + (round(150 * strength),), width=max(1, SS))
    lit = lit.filter(ImageFilter.GaussianBlur(1.5 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), lit).convert("RGB")

    base = Image.alpha_composite(base.convert("RGBA"), lattice).convert("RGB")

    # One ascending data trace: a thin lavender circuit leaving the lit cluster.
    trace = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    trace_draw = ImageDraw.Draw(trace)
    points = []
    x, y = sw * 0.76, sh * 0.30
    for index in range(9):
        points.append((x, y))
        x += radius * 1.4 if index % 2 == 0 else -radius * 0.4
        y -= radius * 0.85
    trace_draw.line(points, fill=LAVENDER + (86,), width=max(1, SS))
    for x, y in points[::2]:
        trace_draw.regular_polygon((x, y, 3.2 * SS / 2), 4, fill=LAVENDER + (140,))
    trace = trace.filter(ImageFilter.GaussianBlur(0.6 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), trace).convert("RGB")

    base = base.resize((out_width, out_height), Image.Resampling.LANCZOS)
    base = grain(base, 0.28, seed=2)
    base = Image.alpha_composite(base.convert("RGBA"), scanlines(size, 8, 4)).convert("RGB")
    return vignette(base, 0.38)


# ── Wallpaper 2: Noir Hex ───────────────────────────────────────────────────

def noir_hex(size: tuple[int, int]) -> Image.Image:
    out_width, out_height = size
    width, height = out_width * SS, out_height * SS
    sw, sh = width, height
    canvas = (sw, sh)

    base = vertical_gradient(width, height, [
        (0.0, (4, 6, 12)),
        (0.5, (8, 12, 24)),
        (0.78, (6, 9, 18)),
        (1.0, (3, 4, 9)),
    ])
    base = ImageChops.screen(base, glow(canvas, (width * 0.62, height * 0.42), width * 0.40, (22, 28, 58), 0.55, 2.2))
    base = ImageChops.screen(base, glow(canvas, (width * 0.40, height * 0.60), width * 0.26, LAVENDER, 0.16, 3.0))

    cx, cy = sw * 0.60, sh * 0.46
    rings = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rings)

    radii = [sw * 0.26, sw * 0.215, sw * 0.175, sw * 0.145]
    for index, r in enumerate(radii):
        alpha = 110 - index * 22
        width_px = max(1, round((2.6 - index * 0.45) * SS))
        draw.polygon(hex_points(cx, cy, r, rotation=-8), outline=LAVENDER + (alpha,), width=width_px)

    # Broken arc on the outer ring: one edge of the hologram is out of phase.
    outer = hex_points(cx, cy, radii[0], rotation=-8)
    draw.line([outer[2], outer[3]], fill=MAGENTA + (150,), width=max(1, 2 * SS))

    # A magenta node at one vertex, the only saturated thing in the frame.
    node = outer[0]
    draw.ellipse([node[0] - 3 * SS, node[1] - 3 * SS, node[0] + 3 * SS, node[1] + 3 * SS], fill=MAGENTA + (210,))

    halo = rings.filter(ImageFilter.GaussianBlur(10 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), halo).convert("RGB")
    base = Image.alpha_composite(base.convert("RGBA"), rings).convert("RGB")

    # A faint lattice emerging from the dark, never fully resolving.
    veil = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil)
    for hx, hy, r in hex_lattice(sw, sh, 46 * SS):
        fade = max(0.0, 1.0 - math.hypot(hx - cx, hy - cy) / (sw * 0.62))
        if fade <= 0.02:
            continue
        veil_draw.polygon(hex_points(hx, hy, r), outline=SLATE + (round(34 * fade),), width=max(1, SS))
    veil = veil.filter(ImageFilter.GaussianBlur(0.8 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), veil).convert("RGB")

    # Floor: a mirrored smear of the ring, cut by the horizon and faded out.
    horizon = int(sh * 0.60)
    floor_height = min(int(sh * 0.16), sh - horizon)
    floor = base.crop((0, horizon - floor_height, sw, horizon)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    floor = floor.convert("RGB").filter(ImageFilter.GaussianBlur(3 * SS))
    fade = vertical_gradient(sw, floor_height, [(0.0, WHITE), (1.0, (0, 0, 0))]).convert("L")
    fade = fade.point(lambda v: round(v * 0.32))
    reflection = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    reflection.paste(floor.convert("RGBA"), (0, horizon), fade)
    base = Image.alpha_composite(base.convert("RGBA"), reflection).convert("RGB")

    base = base.resize((out_width, out_height), Image.Resampling.LANCZOS)
    base = grain(base, 0.32, seed=3)
    base = Image.alpha_composite(base.convert("RGBA"), scanlines(size, 10, 3)).convert("RGB")
    return vignette(base, 0.44)


# ── Wallpaper 3: Lavender Veil ──────────────────────────────────────────────

def lavender_veil(size: tuple[int, int]) -> Image.Image:
    out_width, out_height = size
    width, height = out_width * SS, out_height * SS
    sw, sh = width, height
    canvas = (sw, sh)

    base = vertical_gradient(width, height, [
        (0.0, (24, 31, 62)),
        (0.22, (13, 18, 38)),
        (0.55, INK),
        (0.82, (7, 10, 20)),
        (1.0, (4, 6, 12)),
    ])
    base = ImageChops.screen(base, glow(canvas, (width * 0.30, height * 0.05), width * 0.62, LAVENDER, 0.36, 2.2))
    base = ImageChops.screen(base, glow(canvas, (width * 0.82, height * 0.38), width * 0.34, MAGENTA, 0.10, 3.0))

    # A lattice seen through frosted glass: present, but never crisp.
    veil = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil)
    for hx, hy, r in hex_lattice(sw, sh, 108 * SS):
        fade = max(0.0, min(1.0, 1.0 - hy / (sh * 0.75)))
        if fade <= 0.02:
            continue
        veil_draw.polygon(hex_points(hx, hy, r), outline=LAVENDER + (round(46 * fade ** 2),), width=max(1, SS))
    veil = veil.filter(ImageFilter.GaussianBlur(1.6 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), veil).convert("RGB")

    # Dust: small out-of-focus hexes drifting in the light.
    rng = random.Random(7)
    dust = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    dust_draw = ImageDraw.Draw(dust)
    for _ in range(150):
        x = rng.uniform(0, sw)
        y = rng.uniform(0, sh * 0.92)
        r = rng.uniform(2.5, 12.0) * SS
        tint = LAVENDER if rng.random() > 0.28 else MAGENTA
        alpha = round(rng.uniform(24, 88))
        dust_draw.regular_polygon((x, y, r), 6, fill=tint + (round(alpha * 0.35),), outline=tint + (alpha,),
                                  width=max(1, SS))
    dust = dust.filter(ImageFilter.GaussianBlur(1.4 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), dust).convert("RGB")

    # A half-resolved hexagon in the haze, the way a projection looks when the
    # source is slightly out of focus.
    ghost = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ghost_draw = ImageDraw.Draw(ghost)
    gx, gy = sw * 0.27, sh * 0.30
    for index, r in enumerate((sw * 0.30, sw * 0.255, sw * 0.215)):
        ghost_draw.polygon(hex_points(gx, gy, r, rotation=-6), outline=LAVENDER + (54 - index * 10,),
                           width=max(1, round((2.2 - index * 0.5) * SS)))
    ghost = ghost.filter(ImageFilter.GaussianBlur(3.2 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), ghost).convert("RGB")

    # The horizon: one thin lavender line with a soft bloom under it.
    line = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    line_draw = ImageDraw.Draw(line)
    y = sh * 0.735
    line_draw.line([(0, y), (sw, y)], fill=LAVENDER + (78,), width=max(1, round(1.3 * SS)))
    line = line.filter(ImageFilter.GaussianBlur(0.5 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), line).convert("RGB")
    base = ImageChops.screen(base, glow(canvas, (width * 0.5, height * 0.735), width * 0.55, LAVENDER, 0.14, 3.0))

    base = base.resize((out_width, out_height), Image.Resampling.LANCZOS)
    base = grain(base, 0.24, seed=4)
    base = Image.alpha_composite(base.convert("RGBA"), scanlines(size, 6, 5)).convert("RGB")
    return vignette(base, 0.40)


# ── Wallpaper 4: Signal Hex ─────────────────────────────────────────────────

def signal_hex(size: tuple[int, int]) -> Image.Image:
    out_width, out_height = size
    width, height = out_width * SS, out_height * SS
    sw, sh = width, height
    canvas = (sw, sh)

    base = vertical_gradient(width, height, [
        (0.0, (5, 7, 14)),
        (0.5, (9, 13, 26)),
        (1.0, (4, 6, 12)),
    ])
    base = ImageChops.screen(base, glow(canvas, (width * 0.50, height * 0.52), width * 0.42, (26, 30, 66), 0.6, 2.0))

    # Concentric hexagons, each one a step of the hologram resolving.
    cx, cy = sw * 0.50, sh * 0.50
    rings = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rings)
    steps = 16
    for index in range(steps):
        t = index / (steps - 1)
        r = (sw * 0.075) + t * (sw * 0.30)
        # The stroke walks from lavender at the centre to magenta at the rim.
        colour = (
            round(LAVENDER[0] + (MAGENTA[0] - LAVENDER[0]) * t),
            round(LAVENDER[1] + (MAGENTA[1] - LAVENDER[1]) * t),
            round(LAVENDER[2] + (MAGENTA[2] - LAVENDER[2]) * t),
        )
        alpha = round(120 * (1 - t) ** 1.2 + 46)
        draw.polygon(hex_points(cx, cy, r, rotation=t * 6), outline=colour + (alpha,),
                     width=max(1, round((1.8 - t) * SS)))

    # Scan gap: a horizontal band where the projection loses lock.
    gap = Image.new("L", (sw, sh), 255)
    gap_draw = ImageDraw.Draw(gap)
    band_y = sh * 0.55
    for offset in range(-int(26 * SS), int(26 * SS)):
        strength = max(0.0, 1.0 - abs(offset) / (26 * SS))
        gap_draw.line([(0, band_y + offset), (sw, band_y + offset)], fill=round(255 * (1 - 0.45 * strength)))
    rings.putalpha(ImageChops.multiply(rings.getchannel("A"), gap))

    halo = rings.filter(ImageFilter.GaussianBlur(8 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), halo).convert("RGB")
    base = Image.alpha_composite(base.convert("RGBA"), rings).convert("RGB")

    # Corner brackets, the frame of the projection.
    frame = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(frame)
    margin_x, margin_y = sw * 0.055, sh * 0.075
    arm_x, arm_y = sw * 0.035, sh * 0.055
    for corner_x, corner_y, dx, dy in [
        (margin_x, margin_y, 1, 1),
        (sw - margin_x, margin_y, -1, 1),
        (margin_x, sh - margin_y, 1, -1),
        (sw - margin_x, sh - margin_y, -1, -1),
    ]:
        frame_draw.line([(corner_x, corner_y), (corner_x + dx * arm_x, corner_y)], fill=SLATE + (170,), width=max(1, SS))
        frame_draw.line([(corner_x, corner_y), (corner_x, corner_y + dy * arm_y)], fill=SLATE + (170,), width=max(1, SS))
    frame = frame.filter(ImageFilter.GaussianBlur(0.4 * SS))
    base = Image.alpha_composite(base.convert("RGBA"), frame).convert("RGB")

    base = base.resize((out_width, out_height), Image.Resampling.LANCZOS)
    base = grain(base, 0.26, seed=1)
    base = Image.alpha_composite(base.convert("RGBA"), scanlines(size, 12, 3)).convert("RGB")
    return vignette(base, 0.42)


WALLPAPERS = {
    "01-signal-hex": signal_hex,
    "02-holo-lattice": holo_lattice,
    "03-noir-hex": noir_hex,
    "04-lavender-veil": lavender_veil,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Holo Black wallpapers.")
    parser.add_argument("--size", default="2560x1440", help="WIDTHxHEIGHT (default 2560x1440)")
    parser.add_argument("--out", default=str(OUT_DIR), help="output directory")
    parser.add_argument("--only", choices=sorted(WALLPAPERS), help="render a single wallpaper")
    parser.add_argument("--format", choices=("webp", "png"), default="webp",
                        help="output format (default webp: a 3 MB png becomes ~140 KB)")
    args = parser.parse_args()

    width, height = (int(part) for part in args.size.lower().split("x"))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for stem, painter in WALLPAPERS.items():
        if args.only and stem != args.only:
            continue
        print(f"rendering {stem} at {width}x{height} …", flush=True)
        image = painter((width, height))
        path = out_dir / f"{stem}.{args.format}"
        if args.format == "webp":
            image.save(path, quality=92, method=6)
        else:
            image.save(path, optimize=True)
        print(f"  wrote {path} ({path.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
