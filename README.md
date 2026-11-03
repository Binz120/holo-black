# Holo Black

An elegant, slightly mysterious Omarchy theme built around a glassy interface
floating in an unlit room. Indigo black and slate make the room; lavender is the
edge of every pane; magenta is the glint of something changing; mint appears
only when something succeeds.

![Holo Black with a browser and an editor open](preview.png?v=2)
![Holo Black in a terminal session](preview-terminal.png)
![Holo Black on an empty desktop](preview-wallpaper.png)

---

## Apply

Omarchy treats a theme cloned by `omarchy theme install` differently from one you
put in place yourself. From a clone it drops everything that runs code — every
`*.lua`, `hyprland.lua` included, and the terminal configs `alacritty.toml`,
`foot.ini`, `ghostty.conf` and `kitty.conf` — then regenerates them from
`colors.toml` alone. So there are two ways in, and they are not the same theme.

### Full theme: keeps the glass

Clone it where Omarchy keeps themes, remove the clone marker it looks for, and
apply it:

```bash
git clone https://github.com/Binz120/holo-black ~/.config/omarchy/themes/holo-black
rm -rf ~/.config/omarchy/themes/holo-black/.git
omarchy theme set "Holo Black"
```

This is the theme as described below: the hologram border, rounding 12, the blur
and bloom, indigo shadows, `holoGlide` motion, and terminals at 86–88% opacity.
To update, repeat the clone over the directory.

### From the repository URL: colours only

```bash
omarchy theme install https://github.com/Binz120/holo-black
omarchy theme set "Holo Black"
```

The palette, `shell.toml`, `btop.theme`, `icons.theme`, the wallpapers, the
Plymouth wordmark and the lavender→magenta border all apply. `hyprland.lua` and
the terminal opacity do not: Omarchy regenerates those from `colors.toml`, so
your own rounding, blur and opaque terminals stay as they were.

Switch between the four backgrounds with:

```bash
omarchy theme bg next
```

Your own wallpapers for this theme go in
`~/.config/omarchy/backgrounds/holo-black/`.

If you took the full theme and want Omarchy's stock window feel back, run
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
  intentional — the room should still read through the pane. A repository
  install loses that opacity, because Omarchy writes terminal configs from the
  palette; use the full install above for it.
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
| `backgrounds/` | Four 2560×1440 wallpapers, WebP (about 150 KB each). The signal rings are the default; lattice, noir ring and lavender veil follow. |
| `unlock.png` | The Omarchy wordmark in lavender, for Plymouth. |
| `preview.png`, `preview-terminal.png`, `preview-wallpaper.png`, `preview-unlock.png` | A browser-and-editor session, a terminal session, the bare desktop, and the lock screen. |
| `design/wallpapers.py` | Regenerates the four wallpapers from the five anchors; the grain is seeded, so it rebuilds the committed set. |
| `design/lock_preview.py` | Regenerates the lock preview and the Plymouth wordmark. |
| `design/check.py` | Checks the terminal palettes and borders against `colors.toml`. |

No stock files are touched: everything lives in
`~/.config/omarchy/themes/holo-black/`.

---

## Rebuild the artwork

Both scripts are self-contained (Pillow only):

```bash
python3 design/wallpapers.py                    # 2560x1440 WebP set
python3 design/wallpapers.py --size 3840x2160   # larger set
python3 design/wallpapers.py --format png       # PNG instead of WebP
python3 design/lock_preview.py                  # preview-unlock.png + unlock.png
python3 design/check.py                         # palette check (stdlib only)
```

The grain is seeded per wallpaper, so a rerun reproduces the committed files
rather than merely something similar. WebP at quality 92 keeps a 3 MB PNG's
background at about 140 KB, at no visible cost on gradients.

`preview.png` is a real screenshot of this desktop (1920×1080) after applying
the theme, not a mock-up.

---

## License

MIT — see [`LICENSE`](LICENSE). The Omarchy wordmark in `unlock.png` is the
Omarchy project's; this theme only recolours it.
