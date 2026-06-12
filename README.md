# 🌊 PixelFlood

**Edge flood-fill transparency for pixel art.**

Remove background colour from sprites — without cutting into the sprite itself.

---

### The Problem

Traditional "remove white background" tools set **all** white pixels to transparent.
If your sprite has white details (fur, eyes, clothing), they get destroyed.

<p align="center"><img src="docs/comparison.png" width="356" alt="Comparison"></p>

PixelFlood only floods from the **edges**. Interior white pixels — surrounded by the sprite's outline — are preserved.

---

### How It Works

<p align="center"><img src="docs/algorithm.png" width="800" alt="Algorithm"></p>

| Step | Description |
|------|-------------|
| ① Edge seeds | Scan image edges for background-coloured pixels |
| ② Flood fill | BFS from seeds — outline pixels block the flood |
| ③ Result | Only edge-connected background is removed |

---

### Install

```bash
pip install pixelflood
```

### CLI

```bash
pixelflood sprite.png                      # white bg → alpha
pixelflood sprite.png --crop --preview 8   # autocrop + 8x preview
pixelflood sprite.png -c "#00FF00" -t 10   # custom colour + tolerance
```

### Python API

```python
from pixelflood import flood

result = flood(Image.open("sprite.png"), background_color=(255, 255, 255))

# Or one-shot with autocrop
from pixelflood import process
process("sprite.png", output_path="out.png", crop=True)
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --color` | `#FFFFFF` | Background colour |
| `-t, --threshold` | `7` | Per-channel tolerance |
| `--connectivity` | `4` | Flood directions (`4` or `8`) |
| `--crop` | off | Auto-crop transparent borders |
| `--margin` | `0` | Extra px around crop |
| `--preview` | `0` | Save N× nearest-neighbour preview |

### License

MIT
