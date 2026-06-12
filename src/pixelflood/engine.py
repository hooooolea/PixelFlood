"""
PixelFlood — Edge Flood-Fill Transparency Engine.

Core algorithm: finds all background-coloured pixels connected to image edges
via 4-directional flood fill, and sets their alpha to 0. Interior pixels of the
same colour (e.g. white fur on a white-background sprite) are preserved because
the sprite's outline blocks the flood.

Also includes sprite extraction: after removing the background, disconnected
pixel islands (individual sprites) can be split into separate images via
connected-component labeling.
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

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


def extract(
    image: Image.Image,
    *,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    threshold: int = 7,
    connectivity: int = 4,
    min_size: int = 100,
) -> List[Image.Image]:
    """
    Extract individual sprites from a sprite sheet.

    First applies edge flood-fill to remove the background, then finds
    connected components of the remaining pixels. Each component with
    at least `min_size` pixels is returned as a separate cropped image.

    Args:
        image:            PIL Image (RGBA or will be converted).
        background_color: RGB tuple of the background colour.
        threshold:        Per-channel tolerance for background matching.
        connectivity:     4 or 8 for component connectivity.
        min_size:         Minimum pixel count per sprite (filters noise).

    Returns:
        List of PIL Images, one per extracted sprite (cropped to content).
    """
    # Step 1: remove background
    cleaned = flood(
        image,
        background_color=background_color,
        threshold=threshold,
        connectivity=connectivity,
        inplace=False,
    )
    w, h = cleaned.size
    px = cleaned.load()
    assert px is not None

    # Step 2: connected-component labeling (union-find, 8-connectivity)
    labels = [[0] * w for _ in range(h)]
    parent: Dict[int, int] = {}
    next_label = 1

    def find(c: int) -> int:
        while parent.get(c, c) != c:
            parent[c] = parent.get(parent[c], parent[c])
            c = parent[c]
        return c

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    # Directions for component connectivity (always 8-way for solid sprites)
    comp_dirs = [(0, -1), (-1, 0), (-1, -1), (-1, 1)]

    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:  # type: ignore[index]
                continue
            # Check previously-scanned neighbours
            neighbours: set[int] = set()
            for dx, dy in comp_dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    nl = labels[ny][nx]
                    if nl:
                        neighbours.add(nl)
            if neighbours:
                root = min(neighbours)
                labels[y][x] = root
                for n in neighbours:
                    union(root, n)
            else:
                labels[y][x] = next_label
                parent[next_label] = next_label
                next_label += 1

    # Resolve equivalences
    for y in range(h):
        for x in range(w):
            if labels[y][x]:
                labels[y][x] = find(labels[y][x])

    # Step 3: group by label
    groups: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for y in range(h):
        for x in range(w):
            lbl = labels[y][x]
            if lbl:
                groups[lbl].append((x, y))

    # Step 4: crop and export
    sprites: List[Image.Image] = []
    # Sort left-to-right
    sorted_groups = sorted(
        groups.items(), key=lambda kv: min(p[0] for p in kv[1])
    )

    for _label, pixels in sorted_groups:
        if len(pixels) < min_size:
            continue
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        sw, sh = x1 - x0 + 1, y1 - y0 + 1

        sprite = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        sp = sprite.load()
        assert sp is not None
        for x, y in pixels:
            sp[x - x0, y - y0] = px[x, y]  # type: ignore[index]

        sprites.append(sprite)

    return sprites


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
