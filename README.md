# 🌊 PixelFlood

[中文](README_zh.md) · [日本語](README_ja.md) · [한국어](README_ko.md) · [Français](README_fr.md) · [Español](README_es.md)

![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue?style=flat)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

Edge flood-fill transparency for pixel art. Removes background colour without cutting into the sprite.

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

```bash
# Remove white background
pixelflood sprite.png

# Extract individual sprites from a sprite sheet
pixelflood spritesheet.png --extract -o out/
```

<p align="center"><img src="docs/extract.png" width="780" alt="Extract sprites"></p>

```python
from PIL import Image
from pixelflood import flood, extract

# Single sprite: remove background
result = flood(Image.open("sprite.png"))

# Sprite sheet: extract individual sprites
sprites = extract(Image.open("spritesheet.png"), min_size=500)
for i, sprite in enumerate(sprites):
    sprite.save(f"sprite-{i+1}.png")
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --color` | `#FFFFFF` | Background colour (`#RRGGBB` or `R,G,B`) |
| `-t, --threshold` | `7` | Per-channel tolerance (`0` = exact match) |
| `--connectivity` | `4` | Flood directions (`4` or `8`) |
| `--crop` | off | Auto-crop transparent borders |
| `--margin` | `0` | Extra pixels around crop |
| `--preview` | `0` | Save Nx nearest-neighbour preview |
| `--extract` | off | Extract individual sprites from sheet |
| `--min-size` | `100` | Min pixels per extracted sprite |

## License

MIT
