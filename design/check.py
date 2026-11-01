#!/usr/bin/env python3
"""Holo Black palette check.

Everything this theme ships is derived from `colors.toml`, so the files that
repeat its values must not drift apart. This walks the four terminal palettes
and the window borders back to the palette; it is what CI runs, and it needs
nothing but the standard library (Python 3.11+, for `tomllib`):

    python3 design/check.py      # exits non-zero if anything disagrees
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

THEME = Path(__file__).resolve().parent.parent

# The sixteen ANSI slots, in the order every terminal numbers them.
ANSI = (
    "background",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "foreground",
    "muted",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_foreground",
)

BLACK_TO_WHITE = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")

HEX = r"[0-9A-Fa-f]{6}"


def numbered(slots: dict[int, str]) -> list[str]:
    """The slots in order, with a marker for any the file forgot to set."""
    return [slots.get(index, "missing") for index in range(16)]


def kitty(text: str) -> list[str]:
    found = re.findall(rf"^color(\d+) (#{HEX})$", text, re.M)
    return numbered({int(index): colour.upper() for index, colour in found})


def ghostty(text: str) -> list[str]:
    found = re.findall(rf"^palette = (\d+)=#({HEX})$", text, re.M)
    return numbered({int(index): f"#{colour.upper()}" for index, colour in found})


def foot(text: str) -> list[str]:
    """foot names its slots regular0..7 and bright0..7 rather than color0..15."""
    slots: dict[int, str] = {}
    found = re.findall(rf"^(regular|bright)(\d)=({HEX})$", text, re.M)
    for kind, index, colour in found:
        slots[int(index) + (0 if kind == "regular" else 8)] = f"#{colour.upper()}"
    return numbered(slots)


def alacritty(text: str) -> list[str]:
    colours = tomllib.loads(text)["colors"]
    normal = [colours["normal"][name].upper() for name in BLACK_TO_WHITE]
    bright = [colours["bright"][name].upper() for name in BLACK_TO_WHITE]
    return normal + bright


READERS = {
    "kitty.conf": kitty,
    "ghostty.conf": ghostty,
    "foot.ini": foot,
    "alacritty.toml": alacritty,
}


def gradient(value: str) -> tuple[list[str], int | None]:
    """The rgba stops of a border setting, and its angle when it has one."""
    stops = [f"rgba({stop.lower()})" for stop in re.findall(rf"rgba\(([0-9A-Fa-f]{{8}})\)", value)]
    angle = re.search(r"(\d+)deg", value)
    return stops, int(angle.group(1)) if angle else None


def main() -> int:
    colours = tomllib.loads((THEME / "colors.toml").read_text())
    shell = tomllib.loads((THEME / "shell.toml").read_text())
    hyprland = (THEME / "hyprland.lua").read_text()

    missing = [key for key in ANSI if key not in colours]
    if missing:
        print(f"colors.toml is missing {', '.join(missing)}", file=sys.stderr)
        return 1

    failures: list[str] = []

    # Each terminal palette must be the palette, slot for slot.
    expected = [colours[key].upper() for key in ANSI]
    for name, read in READERS.items():
        found = read((THEME / name).read_text())
        for index, (want, got) in enumerate(zip(expected, found)):
            if got != want:
                failures.append(f"{name}: color{index} is {got}, colors.toml says {want}")

    # The compositor border, the shell border and the Hyprland overrides must
    # describe the same hologram.
    active, angle = gradient(colours.get("hyprland_active_border", ""))
    inactive, _ = gradient(colours.get("hyprland_inactive_border", ""))
    if len(active) != 2 or angle is None or len(inactive) != 1:
        failures.append(
            "colors.toml: hyprland_active_border needs two stops and an angle, "
            "hyprland_inactive_border one stop")

    shell_border, shell_angle = gradient(shell.get("hyprland", {}).get("active-border", ""))
    if (shell_border, shell_angle) != (active, angle):
        failures.append(
            f"shell.toml: active-border is {shell_border} at {shell_angle}deg, "
            f"colors.toml says {active} at {angle}deg")

    literals = dict(re.findall(rf'local (\w+) = "rgba\(([0-9A-Fa-f]{{8}})\)"', hyprland))
    wanted = {
        "lavender": active[0] if len(active) > 0 else None,
        "magenta": active[1] if len(active) > 1 else None,
        "inactive_edge": inactive[0] if inactive else None,
    }
    for name, want in wanted.items():
        if want is None:
            continue
        got = f"rgba({literals[name].lower()})" if name in literals else "missing"
        if got != want:
            failures.append(f"hyprland.lua: local {name} is {got}, colors.toml says {want}")

    lua_angle = re.search(r"angle = (\d+)", hyprland)
    if lua_angle and angle is not None and int(lua_angle.group(1)) != angle:
        failures.append(
            f"hyprland.lua: border angle is {lua_angle.group(1)}deg, colors.toml says {angle}deg")

    if failures:
        print("Holo Black palette check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"ok: {len(READERS)} terminals x {len(ANSI)} slots, borders agree at {angle}deg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
