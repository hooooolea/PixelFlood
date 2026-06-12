# 🌊 PixelFlood

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
# CLI
pixelflood sprite.png                      # white bg to alpha
pixelflood sprite.png --crop --preview 8   # autocrop + 8x preview

# Python
from pixelflood import flood, process
result = flood(Image.open("sprite.png"))
process("sprite.png", output_path="out.png", crop=True)
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-c` | `#FFFFFF` | Background colour |
| `-t` | `7` | Per-channel tolerance |
| `--crop` | off | Auto-crop transparent borders |
| `--preview` | `0` | Save Nx scaled preview |

## License

MIT

---

[中文](README_zh.md) · [日本語](README_ja.md)
