"""PixelFlood CLI — pixel art processing toolkit."""

import argparse
import sys
from pathlib import Path

from .engine import extract, process
from .sample import sample, to_typescript, preview_image


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


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("input", help="Input image path")
    p.add_argument(
        "-c", "--color", default="#FFFFFF",
        help="Background colour (#RRGGBB or R,G,B, default: #FFFFFF)"
    )
    p.add_argument(
        "-t", "--threshold", type=int, default=7,
        help="Per-channel colour tolerance (default: 7)"
    )
    p.add_argument(
        "--connectivity", type=int, choices=[4, 8], default=4,
        help="Flood direction count (default: 4)"
    )
    p.add_argument(
        "--preview", type=int, default=0,
        help="Save a nearest-neighbour scaled preview (e.g. 8 = 8x)"
    )


def _cmd_flood(args: argparse.Namespace) -> None:
    bg = parse_color(args.color)
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
    out = args.output or str(
        Path(args.input)
        .with_stem(Path(args.input).stem + "-alpha")
        .with_suffix(".png")
    )
    print(f"  ✅ {out}  ({result.width}×{result.height})")
    if args.preview > 0:
        stem = Path(out).stem
        prev = str(Path(out).with_stem(f"{stem}@{args.preview}x"))
        print(f"  🔍 preview: {prev}")


def _cmd_extract(args: argparse.Namespace) -> None:
    from PIL import Image

    bg = parse_color(args.color)
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


def _cmd_sample(args: argparse.Namespace) -> None:
    from PIL import Image

    img = Image.open(args.input)
    data = sample(
        img,
        grid=args.grid,
        name=args.name,
        max_colors=args.colors,
    )
    cw, ch = data["w"], data["h"]
    print(
        f"  grid={data['grid']}px  logical={cw}x{ch}  "
        f"cropped={cw}x{ch}  colors={data['colors']}"
    )

    if args.out:
        ts = to_typescript(
            data,
            source_filename=Path(args.input).name,
        )
        with open(args.out, "w") as f:
            f.write(ts)
        print(f"  ✅ {args.out}")

    if args.preview > 0:
        prev = preview_image(data, scale=args.preview)
        stem = Path(args.input).stem
        prev_path = (
            Path(args.out).with_suffix("")
            if args.out
            else Path(stem)
        )
        prev_name = str(prev_path) + f"@{args.preview}x.png"
        prev.save(prev_name, optimize=True)
        print(f"  🔍 preview: {prev_name}")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="pixelflood",
        description="Pixel art toolkit — flood-fill, extract sprites, "
                    "sample into indexed palette data.",
    )
    sub = ap.add_subparsers(dest="command")

    # ── flood (default, backward-compatible) ──
    p_flood = sub.add_parser(
        "flood",
        help="Edge flood-fill: remove background connected to image edges",
        description="Remove background colour connected to image edges "
                    "while preserving interior details.",
    )
    _add_common_args(p_flood)
    p_flood.add_argument("-o", "--output", default=None,
                         help="Output PNG path (default: input-alpha.png)")
    p_flood.add_argument("--crop", action="store_true",
                         help="Auto-crop to bounding box")
    p_flood.add_argument("--margin", type=int, default=0,
                         help="Extra margin around auto-crop")
    p_flood.add_argument("--version", action="version",
                         version="pixelflood 0.2.0")

    # ── extract ──
    p_extract = sub.add_parser(
        "extract",
        help="Extract individual sprites from a sprite sheet",
        description="Remove background via edge flood-fill, then split "
                    "into individual sprites via connected-component labeling.",
    )
    _add_common_args(p_extract)
    p_extract.add_argument("-o", "--output", default=None,
                           help="Output directory or filename prefix")
    p_extract.add_argument("--min-size", type=int, default=100,
                           help="Minimum pixel count per sprite (default: 100)")
    p_extract.add_argument("--smart", action="store_true",
                           help="Enable smart white-region removal")
    p_extract.add_argument("--smart-aggressiveness", type=float, default=0.5,
                           help="Smart filter aggressiveness 0-1 (default: 0.5)")

    # ── sample ──
    p_sample = sub.add_parser(
        "sample",
        help="Downsample pixel art into indexed palette + TypeScript data",
        description="Downsample a cleaned pixel art image into logical "
                    "pixels (grid detection), build a palette, and output "
                    "TypeScript consts for Genesis PetCanvas rendering.",
    )
    p_sample.add_argument("input", help="Input image (transparent PNG recommended)")
    p_sample.add_argument("--grid", type=int, default=0,
                          help="Pixels per logical cell (0 = auto-detect)")
    p_sample.add_argument("--name", default="Sprite",
                          help="Export name prefix (e.g. Fox → FOX_W)")
    p_sample.add_argument("--out", default="",
                          help="Output .ts file path")
    p_sample.add_argument("--colors", type=int, default=16,
                          help="Max palette colours (default: 16)")
    p_sample.add_argument("--preview", type=int, default=0,
                          help="Save a N× scaled preview PNG")

    # ── Backward-compat: no subcommand → flood ──
    # argparse with subparsers makes "input" required for flood.
    # For backward-compat with `pixelflood input.png --extract`, we
    # intercept before argparse if the first positional arg isn't a command.
    if len(sys.argv) > 1 and sys.argv[1] not in {"flood", "extract", "sample",
                                                   "-h", "--help", "--version"}:
        # Rephrase old-style invocation: pixelflood foo.png --extract ...
        has_extract = "--extract" in sys.argv
        cmd = "extract" if has_extract else "flood"
        # Remove --extract flag (it's the default for extract subcommand)
        new_argv = [sys.argv[0], cmd] + [
            a for a in sys.argv[1:] if a != "--extract"
        ]
        sys.argv = new_argv

    args = ap.parse_args()

    if args.command is None:
        ap.print_help()
        sys.exit(1)

    try:
        if args.command == "flood":
            _cmd_flood(args)
        elif args.command == "extract":
            _cmd_extract(args)
        elif args.command == "sample":
            _cmd_sample(args)
    except FileNotFoundError:
        print(f"pixelflood: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"pixelflood: {e}", file=sys.stderr)
        sys.exit(1)
