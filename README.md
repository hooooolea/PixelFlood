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
# Quick start
pixelflood sprite.png

# Auto-crop transparent borders + 8x preview
pixelflood sprite.png --crop --preview 8

# Custom background colour with tolerance
pixelflood sprite.png -c "#00FF00" -t 10
```

```python
# Python API
from PIL import Image
from pixelflood import flood, process

result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
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

## License

MIT
