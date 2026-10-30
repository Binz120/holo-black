# Holo Black

An elegant, slightly mysterious Omarchy theme built around a glassy interface
floating in an unlit room. Indigo black and slate make the room; lavender is the
edge of every pane; magenta is the glint of something changing; mint appears
only when something succeeds.

![Holo Black preview](preview.png)

**Applied on this machine:** yes — `omarchy theme current` → `Holo Black`.

---

## Apply

Published at [github.com/Binz120/holoblack](https://github.com/Binz120/holoblack).
Omarchy names a cloned theme after its repository, so a fresh install arrives as
`Holoblack`; the theme itself is Holo Black.

```bash
omarchy theme install https://github.com/Binz120/holoblack
omarchy theme set "Holo Black"
```

Already on this machine:

```bash
omarchy theme set "Holo Black"
```

Switch between the four backgrounds with:

```bash
omarchy theme bg next
```

Your own wallpapers for this theme go in
`~/.config/omarchy/backgrounds/holo-black/`.

If you want Omarchy's stock window feel back after trying this theme, run
`omarchy refresh hyprland` (the theme sets rounding, gaps, blur, shadows and
motion). Switching to another theme leaves those values in place, by design of
`hyprland.lua` themes.

---

## Palette

Five anchors, everything else mixed from them:

| Colour     | Hex       | Role                                                        |
|------------|-----------|-------------------------------------------------------------|
| Ink        | `#0A0F1E` | The room: background, depth, scrim, shadow                  |
| Slate      | `#2A2F45` | Texture: selection, dividers, muted edges, inactive chrome  |
| Lavender   | `#B8B8FF` | Structure: panels, borders, focus, the lit edge of glass    |
| Magenta    | `#FF4FD8` | Attention: changes, alerts, countdowns, modified files      |
| Mint       | `#2EF9B6` | Success only: confirmation, completion, a clean exit        |

The full `colors.toml` adds the in-between values the templates need (a
lavender-tinted panel, an ice blue for cyan, a champagne for constants, a rose
for errors) and keeps them inside the same hue family.

**The mint rule.** There is no mint in `shell.toml`, none in `btop.theme`, and
none in the wallpapers. It appears in the terminal palette because `green` must
mean success there, and in the preview's two success marks. That restraint is
what makes magenta read as an event rather than decoration.

---

## The glass

- Windows: indigo shadow, `rounding = 12`, a 2px lavender→magenta hologram
  border on the focused window and a faint lavender edge on the rest.
- The bar is 82% opaque; menus, launchers, notifications and the lock field are
  between 92% and 96%, so the wallpaper is always slightly present.
- Terminals ship at 86–88% opacity. Omarchy's Glassy profile adds the blur; if
  you turn Glassy off, the terminals stay translucent but crisp. That is
  intentional — the room should still read through the pane.
- Shell borders use the same `hyprland.active-border` gradient as the compositor,
  so a notification, the lock field and the window it sits over agree.

---

## File map

| Path | Purpose |
|---|---|
| `colors.toml` | The palette. Feeds terminals, editors, btop, the shell and the templates. |
| `shell.toml` | Bar, menus, launcher, notifications, polkit, lock, image picker. |
| `hyprland.lua` | Borders, rounding, gaps, blur, shadows, motion, group bar. |
| `kitty.conf`, `ghostty.conf`, `alacritty.toml`, `foot.ini` | Terminal palettes and opacity. |
| `btop.theme` | Slate boxes, lavender throughput, magenta load; no mint. |
| `icons.theme` | `Yaru-purple-dark`. |
| `backgrounds/` | Four 2560×1440 wallpapers: lattice, noir ring, lavender veil, signal. |
| `unlock.png` | The Omarchy wordmark in lavender, for Plymouth. |
| `preview.png`, `preview-unlock.png` | The desktop and the lock screen. |
| `design/wallpapers.py` | Regenerates the four wallpapers from the five anchors. |
| `design/lock_preview.py` | Regenerates the lock preview and the Plymouth wordmark. |

No stock files are touched: everything lives in
`~/.config/omarchy/themes/holo-black/`.

---

## Rebuild the artwork

Both scripts are self-contained (Pillow only):

```bash
python3 design/wallpapers.py                    # 2560x1440 set
python3 design/wallpapers.py --size 3840x2160   # larger set
python3 design/lock_preview.py                  # preview-unlock.png + unlock.png
```

`preview.png` is a real screenshot of this desktop (1920×1080) after applying
the theme, not a mock-up.
