"""
PixelFlood — Edge Flood-Fill Transparency Engine.

Core algorithm: finds all background-coloured pixels connected to image edges
via 4-directional flood fill, and sets their alpha to 0. Interior pixels of the
same colour (e.g. white fur on a white-background sprite) are preserved because
the sprite's outline blocks the flood.
"""

from collections import deque
from typing import Optional, Tuple

from PIL import Image


def _is_near_color(
    pixel: Tuple[int, int, int, int],
    target: Tuple[int, int, int],
    threshold: int,
) -> bool:
    """Check if pixel's RGB channels are all within `threshold` of target."""
    return all(abs(pixel[c] - target[c]) <= threshold for c in range(3))


def flood(
    image: Image.Image,
    *,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    threshold: int = 7,
    connectivity: int = 4,
    inplace: bool = False,
) -> Image.Image:
    """
    Apply edge flood-fill to make background-coloured border pixels transparent.

    Only pixels connected to image EDGES are removed. Interior pixels of the
    same colour, surrounded by different-coloured outlines, are kept.

    Args:
        image:      PIL Image (RGBA or will be converted).
        background_color: RGB tuple of the background colour to flood.
        threshold:  Per-channel tolerance (0 = exact match).
        connectivity: 4 or 8 for flood direction count.
        inplace:    If True, modify the input image. Default returns a copy.

    Returns:
        PIL Image in RGBA mode with background alpha-zeroed.
    """
    if not inplace:
        image = image.copy()

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    w, h = image.size
    px = image.load()
    assert px is not None

    # ── Edge flood fill ──
    visited = [[False] * w for _ in range(h)]
    queue: deque[Tuple[int, int]] = deque()

    # Seed: all 4 edges
    for x in range(w):
        for y in (0, h - 1):
            if not visited[y][x] and _is_near_color(px[x, y], background_color, threshold):  # type: ignore[index]
                visited[y][x] = True
                queue.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not visited[y][x] and _is_near_color(px[x, y], background_color, threshold):  # type: ignore[index]
                visited[y][x] = True
                queue.append((x, y))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if connectivity == 8:
        dirs += [(1, 1), (-1, 1), (1, -1), (-1, -1)]

    while queue:
        x, y = queue.popleft()
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                if _is_near_color(px[nx, ny], background_color, threshold):  # type: ignore[index]
                    visited[ny][nx] = True
                    queue.append((nx, ny))

    # ── Apply alpha ──
    for y in range(h):
        for x in range(w):
            if visited[y][x]:
                r, g, b, _ = px[x, y]  # type: ignore[index]
                px[x, y] = (r, g, b, 0)  # type: ignore[index]

    return image


def auto_crop(
    image: Image.Image,
    *,
    margin: int = 0,
) -> Image.Image:
    """Crop to the bounding box of non-transparent pixels."""
    bbox = image.getbbox()
    if bbox is None:
        return image
    x0 = max(0, bbox[0] - margin)
    y0 = max(0, bbox[1] - margin)
    x1 = min(image.width, bbox[2] + margin)
    y1 = min(image.height, bbox[3] + margin)
    return image.crop((x0, y0, x1, y1))


def process(
    input_path: str,
    output_path: Optional[str] = None,
    *,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    threshold: int = 7,
    connectivity: int = 4,
    crop: bool = False,
    margin: int = 0,
    preview_scale: int = 0,
) -> Image.Image:
    """
    One-shot: load → flood → (crop) → save.

    Args:
        input_path:   Path to source image.
        output_path:  Path for output PNG (auto-generated if None).
        preview_scale: If > 0, save an additional nearest-neighbour scaled preview.

    Returns:
        The processed PIL Image.
    """
    from pathlib import Path

    img = Image.open(input_path)
    result = flood(img, background_color=background_color, threshold=threshold,
                   connectivity=connectivity)

    if crop:
        result = auto_crop(result, margin=margin)

    out = Path(output_path) if output_path else Path(input_path).with_stem(
        Path(input_path).stem + "-alpha"
    )
    out = out.with_suffix(".png")
    result.save(out, optimize=True)

    if preview_scale > 0:
        pw, ph = result.width * preview_scale, result.height * preview_scale
        preview = result.resize((pw, ph), Image.NEAREST)
        preview_path = out.with_stem(out.stem + f"@{preview_scale}x")
        preview.save(preview_path, optimize=True)

    return result
