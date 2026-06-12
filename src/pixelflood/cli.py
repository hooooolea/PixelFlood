"""PixelFlood CLI — edge flood-fill transparency for pixel art."""

import argparse
import sys
from pathlib import Path

from .engine import extract, process


def parse_color(s: str) -> tuple[int, int, int]:
    """Parse '#RRGGBB' or 'R,G,B' into (R, G, B)."""
    s = s.strip()
    if s.startswith("#"):
        s = s.lstrip("#")
        if len(s) != 6:
            raise ValueError(f"Hex color must be #RRGGBB, got: {s}")
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    parts = s.split(",")
    if len(parts) != 3:
        raise ValueError(f"Color must be '#RRGGBB' or 'R,G,B', got: {s}")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="pixelflood",
        description="Edge flood-fill transparency for pixel art. "
                    "Removes background colour connected to image edges "
                    "while preserving interior details.",
    )
    ap.add_argument("input", help="Input image path")
    ap.add_argument("-o", "--output", default=None, help="Output PNG path (default: input-alpha.png)")
    ap.add_argument(
        "-c", "--color", default="#FFFFFF",
        help="Background colour to flood (#RRGGBB or R,G,B, default: #FFFFFF)"
    )
    ap.add_argument(
        "-t", "--threshold", type=int, default=7,
        help="Per-channel colour tolerance (0 = exact match, default: 7)"
    )
    ap.add_argument(
        "--connectivity", type=int, choices=[4, 8], default=4,
        help="Flood direction count (default: 4)"
    )
    ap.add_argument(
        "--crop", action="store_true",
        help="Auto-crop to bounding box of non-transparent pixels"
    )
    ap.add_argument(
        "--margin", type=int, default=0,
        help="Extra margin around auto-crop (default: 0)"
    )
    ap.add_argument(
        "--preview", type=int, default=0,
        help="Save a nearest-neighbour scaled preview (e.g. 8 = 8x)"
    )
    ap.add_argument(
        "--extract", action="store_true",
        help="Extract individual sprites from a sprite sheet"
    )
    ap.add_argument(
        "--min-size", type=int, default=100,
        help="Minimum pixel count per extracted sprite (default: 100)"
    )
    ap.add_argument(
        "--smart", action="store_true",
        help="Enable smart white-region removal during extraction"
    )
    ap.add_argument(
        "--smart-aggressiveness", type=float, default=0.5,
        help="Smart filter aggressiveness 0-1 (default: 0.5)"
    )
    ap.add_argument("--version", action="version", version="pixelflood 0.1.0")

    args = ap.parse_args()

    try:
        bg = parse_color(args.color)
    except ValueError as e:
        print(f"pixelflood: bad --color: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.extract:
            from PIL import Image

            img = Image.open(args.input)
            sprites = extract(
                img,
                background_color=bg,
                threshold=args.threshold,
                connectivity=args.connectivity,
                min_size=args.min_size,
                smart=args.smart,
                smart_bg_threshold=args.smart_aggressiveness,
            )
            stem = Path(args.input).stem
            out_dir = args.output or str(Path(args.input).parent)
            # If output is not a directory, treat it as a prefix
            out_path = Path(out_dir)
            if out_path.suffix:
                prefix = str(out_path.with_suffix(""))
            else:
                out_path.mkdir(parents=True, exist_ok=True)
                prefix = str(out_path / stem)

            for i, sprite in enumerate(sprites):
                name = f"{prefix}-{i+1:02d}.png"
                sprite.save(name, optimize=True)
                print(f"  ✅ {name}  ({sprite.width}×{sprite.height})")

                if args.preview > 0:
                    pw = sprite.width * args.preview
                    ph = sprite.height * args.preview
                    prev = sprite.resize((pw, ph), Image.NEAREST)
                    prev_path = f"{prefix}-{i+1:02d}@{args.preview}x.png"
                    prev.save(prev_path, optimize=True)

            print(f"\n  Extracted {len(sprites)} sprites")
        else:
            result = process(
                args.input,
                output_path=args.output,
                background_color=bg,
                threshold=args.threshold,
                connectivity=args.connectivity,
                crop=args.crop,
                margin=args.margin,
                preview_scale=args.preview,
            )
            out = args.output or str(Path(args.input).with_stem(Path(args.input).stem + "-alpha").with_suffix(".png"))
            print(f"  ✅ {out}  ({result.width}×{result.height})")

            if args.preview > 0:
                stem = Path(out).stem
                prev = str(Path(out).with_stem(f"{stem}@{args.preview}x"))
                print(f"  🔍 preview: {prev}")

    except FileNotFoundError:
        print(f"pixelflood: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"pixelflood: {e}", file=sys.stderr)
        sys.exit(1)
