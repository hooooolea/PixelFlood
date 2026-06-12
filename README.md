# 🌊 PixelFlood

**Edge flood-fill transparency for pixel art.**

Removes background colour from images — but ONLY the pixels connected to the edges. Interior details of the same colour (like white fur on a white background) are preserved because the sprite's outline blocks the flood.

## The Problem

Traditional tools set ALL white pixels to transparent. The rabbit's white body gets cut off with its background.

![Comparison](docs/comparison.png)

PixelFlood only floods from the edges — interior white pixels are preserved because the outline blocks the flood.

## Install

```bash
pip install pixelflood
```

## Usage

### CLI

```bash
# Basic: white background → transparent
pixelflood sprite.png

# With auto-crop + 8x preview
pixelflood sprite.png --crop --preview 8

# Custom background colour + tolerance
pixelflood sprite.png -c "#00FF00" -t 10

# Full options
pixelflood input.png -o output.png -c 255,255,255 -t 7 --connectivity 4 --crop --margin 2
```

### Python API

```python
from pixelflood import flood, auto_crop

# Core function — works with any PIL Image
from PIL import Image
img = Image.open("sprite.png")
result = flood(img, background_color=(255, 255, 255), threshold=7)

# Or one-shot convenience
from pixelflood import process
process("sprite.png", output_path="out.png", crop=True)
```

## Algorithm

```
1. Scan all 4 image edges → find background-coloured pixels
2. BFS flood-fill from those seeds (4-directional)
3. Set alpha=0 for all flooded pixels
4. Interior pixels of the same colour are NOT flooded —
   the sprite outline acts as a flood barrier
```

```
┌─────────────────────────┐
│ B B B B B B B B B B B  │  B = Background (flooded → transparent)
│ B B B . . . . B B B B  │  . = Outline (blocks flood)
│ B B . W W W . B B B B  │  W = Interior white (PRESERVED!)
│ B B . W W W . B B B B  │
│ B B B . . . . B B B B  │
│ B B B B B B B B B B B  │
└─────────────────────────┘
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-c, --color` | `#FFFFFF` | Background colour to flood |
| `-t, --threshold` | `7` | Per-channel tolerance (0 = exact) |
| `--connectivity` | `4` | `4` or `8` flood directions |
| `--crop` | off | Auto-crop transparent borders |
| `--margin` | `0` | Extra px around crop |
| `--preview` | `0` | Save N× nearest-neighbour preview |

## License

MIT
