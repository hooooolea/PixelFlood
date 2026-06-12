"""
Pixel sample — downsample pixel art into indexed palette + TypeScript data.

Takes a cleaned pixel art image (e.g. from `pixelflood flood`) and produces
the format consumed by Genesis PetCanvas: logical width/height, palette, and
row-major pixel indices. Index 0 = transparent.

Algorithm:
  1. Detect or accept a grid size (pixels per logical cell).
  2. Per cell: count colour frequencies (dark pixels weighted ×2 to preserve
     thin black outlines).
  3. Edge flood-fill white → transparent (only border-connected white removed,
     interior white details kept).
  4. Build palette with greedy nearest-merge to stay under max_colors.
  5. Convert to index array, auto-crop transparent borders.
  6. Output as TypeScript consts or a Python dict.
"""

from collections import Counter, deque
from typing import Dict, List, Optional, Tuple

from PIL import Image


def _dist2(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def _luminance(c: Tuple[int, ...]) -> float:
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _is_near_white(c: Tuple[int, ...], thr: int = 248) -> bool:
    return c[0] >= thr and c[1] >= thr and c[2] >= thr


def _auto_grid(im: Image.Image, max_logical: int = 128) -> Optional[int]:
    """Detect the pixel grid size by trying 8..40 and picking the cleanest."""
    w, h = im.size
    px = im.load()
    if px is None:
        return None
    best, best_score = None, -1.0
    for g in range(8, 41):
        lw, lh = w // g, h // g
        if not (16 <= lw <= max_logical):
            continue
        same = total = 0
        for gy in range(0, lh, 2):
            for gx in range(0, lw, 2):
                cx, cy = gx * g + g // 2, gy * g + g // 2
                c1 = px[cx, cy]
                c2 = px[min(cx + g // 3, w - 1), cy]
                total += 1
                if _dist2(c1, c2) < 900:
                    same += 1
        score = same / max(total, 1)
        if score > best_score:
            best_score, best = score, g
    return best


def _prep_image(image: Image.Image) -> Image.Image:
    """Convert to RGB, compositing onto white if RGBA input."""
    if image.mode == "RGBA":
        bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
        return Image.alpha_composite(bg, image).convert("RGB")
    return image.convert("RGB")


def sample(
    image: Image.Image,
    *,
    grid: int = 0,
    name: str = "Sprite",
    max_colors: int = 16,
    merge_threshold: int = 35 * 35,
) -> dict:
    """
    Downsample a pixel art image into indexed palette data.

    Args:
        image:           PIL Image (RGB or RGBA; alpha → white composite).
        grid:            Pixels per logical cell (0 = auto-detect).
        name:            Name for export constants (e.g. 'Fox' → FOX_W).
        max_colors:      Maximum palette entries (default 16).
        merge_threshold: Squared Euclidean distance for colour merging.

    Returns:
        dict with keys:
          name     — export name string
          w, h     — cropped logical width / height
          palette  — list of '#RRGGBB' hex strings (index 0 = white/transparent)
          pixels   — flat list of indices, row-major, length = w*h
          colors   — colour count (excluding index 0)
          grid     — detected or supplied grid size
    """
    im = _prep_image(image)
    w, h = im.size
    px = im.load()
    if px is None:
        raise ValueError("cannot load image pixels")

    g = grid or _auto_grid(im)
    if not g:
        raise ValueError(
            "cannot detect grid size — specify --grid (e.g. --grid 8)"
        )
    lw, lh = w // g, h // g

    # 1) Per-cell dominant colour (dark ×2 weight)
    cells = [[None] * lw for _ in range(lh)]  # type: ignore
    for gy in range(lh):
        for gx in range(lw):
            cnt: Counter = Counter()
            for dy in range(g):
                for dx in range(g):
                    c = px[gx * g + dx, gy * g + dy]
                    wgt = 2 if _luminance(c) < 80 else 1
                    cnt[c] += wgt
            cells[gy][gx] = cnt.most_common(1)[0][0]

    # 2) Edge flood-fill: border-connected near-white → transparent
    bg = [[False] * lw for _ in range(lh)]
    dq: deque = deque()
    for gx in range(lw):
        for gy in (0, lh - 1):
            if _is_near_white(cells[gy][gx]) and not bg[gy][gx]:
                bg[gy][gx] = True
                dq.append((gx, gy))
    for gy in range(lh):
        for gx in (0, lw - 1):
            if _is_near_white(cells[gy][gx]) and not bg[gy][gx]:
                bg[gy][gx] = True
                dq.append((gx, gy))
    while dq:
        x, y = dq.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (
                0 <= nx < lw
                and 0 <= ny < lh
                and not bg[ny][nx]
                and _is_near_white(cells[ny][nx])
            ):
                bg[ny][nx] = True
                dq.append((nx, ny))

    # 3) Palette: greedy nearest-merge ≤ max_colors
    cnt = Counter()
    for gy in range(lh):
        for gx in range(lw):
            if not bg[gy][gx]:
                cnt[cells[gy][gx]] += 1
    palette: List[Tuple[Tuple[int, ...], int]] = []
    for c, n in cnt.most_common():
        for i, (pc, pn) in enumerate(palette):
            if _dist2(c, pc) < merge_threshold:
                palette[i] = (pc, pn + n)
                break
        else:
            palette.append((c, n))
    palette.sort(key=lambda t: -t[1])
    palette_rgb = [c for c, _ in palette[:max_colors]]

    def nearest(c: Tuple[int, ...]) -> int:
        return min(
            range(len(palette_rgb)),
            key=lambda i: _dist2(c, palette_rgb[i]),
        )

    # 4) Index array (0 = transparent)
    pixels_flat: List[int] = []
    for gy in range(lh):
        for gx in range(lw):
            pixels_flat.append(
                0 if bg[gy][gx] else nearest(cells[gy][gx]) + 1
            )

    # Auto-crop transparent borders
    xs = [i % lw for i, v in enumerate(pixels_flat) if v]
    ys = [i // lw for i, v in enumerate(pixels_flat) if v]
    if not xs:
        raise ValueError("image has no non-transparent pixels after flood-fill")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cw, ch = x1 - x0 + 1, y1 - y0 + 1
    cropped = [
        pixels_flat[(y0 + y) * lw + (x0 + x)]
        for y in range(ch)
        for x in range(cw)
    ]
    hexes = ["#FFFFFF"] + [
        "#%02X%02X%02X" % c for c in palette_rgb
    ]

    return {
        "name": name,
        "w": cw,
        "h": ch,
        "palette": hexes,
        "pixels": cropped,
        "colors": len(palette_rgb),
        "grid": g,
    }


def to_typescript(data: dict, source_filename: str = "") -> str:
    """Format sample() output as a TypeScript const file."""
    name = data["name"].upper()
    cw, ch = data["w"], data["h"]
    palette = data["palette"]
    pixels = data["pixels"]

    rows = []
    for y in range(ch):
        rows.append(
            "  " + ",".join(str(v) for v in pixels[y * cw : (y + 1) * cw]) + ","
        )

    src = f" ({source_filename})" if source_filename else ""
    return (
        f"// {data['name']}Sprite.ts — auto-generated by pixelflood sample"
        f"{src}\n"
        f"// {cw}x{ch}, {data['colors']} colors, grid={data['grid']}px\n"
        f"// DO NOT EDIT — re-run the generator to update\n\n"
        f"export const {name}_W = {cw}\n"
        f"export const {name}_H = {ch}\n\n"
        f"/** 调色板:索引 0 = 透明,1–{data['colors']} = 颜色 */\n"
        f"export const {name}_PALETTE: readonly string[] = [\n"
        + "".join(f"  '{c}', // {i}\n" for i, c in enumerate(palette))
        + "] as const\n\n"
        f"/** 像素索引,行优先,长度 {cw}x{ch} = {cw*ch}。0 = 透明。 */\n"
        "// prettier-ignore\n"
        f"export const {name}_PIXELS: readonly number[] = [\n"
        + "\n".join(rows)
        + "\n] as const\n"
    )


def preview_image(data: dict, scale: int = 8) -> Image.Image:
    """Render sample() output as an RGBA preview image at the given scale."""
    cw, ch = data["w"], data["h"]
    palette_rgb = data["palette"][1:]  # skip index 0 (transparent)
    pixels = data["pixels"]

    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    op = out.load()
    if op is None:
        return out
    for y in range(ch):
        for x in range(cw):
            v = pixels[y * cw + x]
            if v:
                hex_str = data["palette"][v]
                r = int(hex_str[1:3], 16)
                g = int(hex_str[3:5], 16)
                b = int(hex_str[5:7], 16)
                op[x, y] = (r, g, b, 255)
    if scale > 1:
        out = out.resize((cw * scale, ch * scale), Image.NEAREST)
    return out
