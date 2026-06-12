# 🌊 PixelFlood

[中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue?style=flat)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

Pixel art processing toolkit — flood-fill transparency, sprite sheet extraction, and indexed palette sampling for Genesis PetCanvas.

---

## Problem

Traditional "remove white background" destroys white sprite details (fur, eyes, clothing).

<p align="center"><img src="docs/comparison.png" width="780" alt="Before vs After"></p>

PixelFlood only floods from the **edges**. The outline acts as a barrier — interior white is preserved.

---

## Algorithm

<p align="center"><img src="docs/algorithm.png" alt="How it works"></p>

| Step | Description |
|------|-------------|
| Edge seeds | Scan image borders for background-coloured pixels |
| Flood fill | BFS from seeds — outline pixels block the flood |
| Result | Only edge-connected background becomes transparent |

---

## Install

```bash
pip install pixelflood
```

## Usage

### CLI

```bash
# Remove white background (default)
pixelflood flood sprite.png

# Extract sprites from sheet + smart trapped-white removal
pixelflood extract spritesheet.png --smart -o out/

# Downsample to indexed palette + TypeScript (Genesis PetCanvas format)
pixelflood sample sprite.png --grid 6 --name Fox --out FoxSprite.ts
```

### Genesis Pipeline

```
Sprite sheet (2048×512, white bg)
  │  pixelflood extract --smart --smart-aggressiveness 0.6
  ▼
Transparent PNGs (per entity, e.g. 392×205)
  │  pixelflood sample --grid 6 --name Wolf
  ▼
PIXEL data (TypeScript: palette + row-major indices)
  │  Genesis PetCanvas fillRect
  ▼
Crisp pixel art ✅
```

### Python API

```python
from PIL import Image
from pixelflood import flood, extract, sample, to_typescript

# Single sprite: remove background
result = flood(Image.open("sprite.png"))

# Sprite sheet: extract individual sprites
sprites = extract(Image.open("spritesheet.png"), min_size=500,
                  smart=True, smart_bg_threshold=0.5)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")

# Downsample to indexed palette
data = sample(Image.open("wolf-idle.png"), grid=6, name="Wolf")
# → {"name": "Wolf", "w": 65, "h": 33, "palette": [...], "pixels": [...]}

# Export as TypeScript
ts_code = to_typescript(data, source_filename="wolf-idle.png")
with open("WolfSprite.ts", "w") as f:
    f.write(ts_code)
```

## Commands

| Command | Description |
|---------|-------------|
| `flood` | Edge flood-fill: remove background connected to image edges |
| `extract` | Extract sprites from sheet + optional smart clean |
| `sample` | Downsample into logical pixels → TypeScript consts |

## Options

### flood / extract

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --color` | `#FFFFFF` | Background colour (`#RRGGBB` or `R,G,B`) |
| `-t, --threshold` | `7` | Per-channel tolerance (`0` = exact match) |
| `--connectivity` | `4` | Flood direction count (`4` or `8`) |
| `--preview` | `0` | Save Nx nearest-neighbour preview |

### extract only

| Flag | Default | Description |
|------|---------|-------------|
| `--extract` | on | (implicit for `extract` subcommand) |
| `--min-size` | `100` | Min pixels per extracted sprite |
| `--smart` | off | Remove trapped white between sprites |
| `--smart-aggressiveness` | `0.5` | Smart filter strength (0=gentle, 1=aggressive) |

### sample only

| Flag | Default | Description |
|------|---------|-------------|
| `--grid` | `0` (auto) | Pixels per logical cell |
| `--name` | `Sprite` | Export name prefix (e.g. Fox → `FOX_W`) |
| `--out` | — | Output `.ts` file path |
| `--colors` | `16` | Max palette colours |
| `--preview` | `0` | Save Nx scaled preview PNG |

## License

MIT
