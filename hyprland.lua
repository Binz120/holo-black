-- Holo Black — Hyprland translation layer.
--
-- A window is a pane of glass floating over the room: lavender on the lit edge,
-- a magenta glint where the hologram turns, indigo shadow underneath, blurred
-- room behind. The border is the only place the two accents meet; everything
-- else stays slate so the glint keeps its meaning.

local lavender = "rgba(b8b8ffee)"
local magenta = "rgba(ff4fd8aa)"
local inactive_edge = "rgba(a9a9e655)"

local active_border = { colors = { lavender, magenta }, angle = 45 }

hl.config({
  general = {
    gaps_in = 6,
    gaps_out = 12,
    border_size = 2,

    col = {
      active_border = active_border,
      inactive_border = inactive_edge,
    },

    resize_on_border = true,
    extend_border_grab_area = 10,
    hover_icon_on_border = true,
    layout = "dwindle",
  },

  decoration = {
    rounding = 12,
    rounding_power = 2.2,

    active_opacity = 0.97,
    inactive_opacity = 0.92,

    dim_inactive = true,
    dim_strength = 0.18,

    shadow = {
      enabled = true,
      range = 36,
      render_power = 4,
      color = "rgba(02040acc)",
      color_inactive = "rgba(02040a66)",
      offset = { 0, 10 },
      scale = 1.0,
    },

    blur = {
      enabled = true,
      size = 6,
      passes = 3,
      new_optimizations = true,
      xray = false,
      noise = 0.018,
      contrast = 1.05,
      brightness = 0.78,
      vibrancy = 0.22,
      vibrancy_darkness = 0.38,
      popups = true,
      popups_ignorealpha = 0.15,
      special = true,
    },
  },

  group = {
    col = {
      border_active = active_border,
      border_inactive = inactive_edge,
    },

    groupbar = {
      font_size = 12,
      font_family = "monospace",
      font_weight_active = "ultraheavy",
      font_weight_inactive = "normal",
      indicator_height = 1,
      indicator_gap = 5,
      height = 22,
      gaps_in = 5,
      gaps_out = 0,
      text_color = "rgb(dcddf7)",
      text_color_inactive = "rgba(dcddf799)",
      col = {
        active = "rgba(b8b8ff22)",
        inactive = "rgba(2a2f4533)",
      },
      gradients = true,
      gradient_rounding = 10,
      gradient_round_only_edges = false,
    },
  },

  animations = {
    enabled = true,
  },

  misc = {
    background_color = "rgb(05080f)",
  },
})

-- ── Motion ──────────────────────────────────────────────────────────────────
-- One curve, everywhere: a hologram does not bounce, it resolves. Entrances
-- land inside 250ms; exits leave a little sooner than they arrived.

hl.curve("holoGlide", { type = "bezier", points = { { 0.16, 1 }, { 0.3, 1 } } })
hl.curve("holoOut", { type = "bezier", points = { { 0.7, 0 }, { 0.84, 0 } } })

hl.animation({ leaf = "global", enabled = true, speed = 2.5, bezier = "holoGlide" })
hl.animation({ leaf = "border", enabled = true, speed = 1.6, bezier = "holoGlide" })

hl.animation({ leaf = "windows", enabled = true, speed = 2.6, bezier = "holoGlide" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 3.6, bezier = "holoGlide", style = "popin 96%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.5, bezier = "holoOut", style = "popin 98%" })

hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.8, bezier = "holoGlide" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.1, bezier = "holoOut" })
hl.animation({ leaf = "fade", enabled = true, speed = 2.0, bezier = "holoGlide" })
hl.animation({ leaf = "fadeSwitch", enabled = false })
hl.animation({ leaf = "fadeShadow", enabled = true, speed = 2.0, bezier = "holoGlide" })
hl.animation({ leaf = "fadeDim", enabled = true, speed = 2.2, bezier = "holoGlide" })

hl.animation({ leaf = "layers", enabled = true, speed = 2.2, bezier = "holoGlide" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 2.4, bezier = "holoGlide", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.4, bezier = "holoOut", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.6, bezier = "holoGlide" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.0, bezier = "holoOut" })

hl.animation({ leaf = "workspaces", enabled = true, speed = 2.4, bezier = "holoGlide", style = "slidefade" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 2.4, bezier = "holoGlide", style = "slidefadevert" })
