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
    smart: bool = False,
    smart_bg_threshold: float = 0.6,
) -> List[Image.Image]:
    """
    Extract individual sprites from a sprite sheet.

    First applies edge flood-fill to remove the background, then finds
    connected components of the remaining pixels. Each component with
    at least `min_size` pixels is returned as a separate cropped image.

    When `smart` is True, a secondary pass analyses white regions within
    each extracted sprite and removes those that look like trapped
    background (e.g. white gaps between adjacent sprites) rather than
    actual sprite content.

    Args:
        image:              PIL Image (RGBA or will be converted).
        background_color:   RGB tuple of the background colour.
        threshold:          Per-channel tolerance for background matching.
        connectivity:       4 or 8 for component connectivity.
        min_size:           Minimum pixel count per sprite (filters noise).
        smart:              Enable smart white-region removal.
        smart_bg_threshold: Aggressiveness (0=keep all, 1=remove all white).

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

        # Build sprite pixel map (local coords)
        local_px: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}
        for x, y in pixels:
            local_px[(x - x0, y - y0)] = px[x, y]  # type: ignore[index]

        # ── Smart clean: remove trapped white regions ──
        if smart:
            local_px = _smart_clean(
                sw, sh, local_px, background_color, threshold,
                smart_bg_threshold,
            )

        sprite = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        sp = sprite.load()
        assert sp is not None
        for (lx, ly), color in local_px.items():
            sp[lx, ly] = color  # type: ignore[index]

        sprites.append(sprite)

    return sprites


def _is_near_color_px(
    px: Tuple[int, int, int, int],
    target: Tuple[int, int, int],
    threshold: int,
) -> bool:
    return all(abs(px[c] - target[c]) <= threshold for c in range(3))


def _smart_clean(
    w: int,
    h: int,
    pixels: Dict[Tuple[int, int], Tuple[int, int, int, int]],
    bg_color: Tuple[int, int, int],
    threshold: int,
    aggressiveness: float,
) -> Dict[Tuple[int, int], Tuple[int, int, int, int]]:
    """
    Analyse white regions within a sprite and remove trapped background.

    Heuristics per white connected-component:
      - edge_contact: fraction touching sprite bbox edges (high → bg)
      - neighbor_bg:  fraction of adjacent pixels that are transparent (high → bg)
      - size_score:   large region relative to sprite (high → bg)

    Combined score > aggressiveness → region removed.
    """
    # Find white pixels
    white_mask = [[False] * w for _ in range(h)]
    white_list: List[Tuple[int, int]] = []
    for (x, y), c in pixels.items():
        if _is_near_color_px(c, bg_color, threshold):
            white_mask[y][x] = True
            white_list.append((x, y))

    if not white_list:
        return pixels

    # Connected components of white pixels (8-way)
    wlabel = [[0] * w for _ in range(h)]
    parent: Dict[int, int] = {}
    nl = 1

    def ufind(c: int) -> int:
        while parent.get(c, c) != c:
            parent[c] = parent.get(parent[c], parent[c])
            c = parent[c]
        return c

    for y in range(h):
        for x in range(w):
            if not white_mask[y][x]:
                continue
            nb: set[int] = set()
            for dx, dy in [(-1, 0), (0, -1), (-1, -1), (-1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and wlabel[ny][nx]:
                    nb.add(wlabel[ny][nx])
            if nb:
                root = min(nb)
                wlabel[y][x] = root
                for n in nb:
                    ra, rb = ufind(root), ufind(n)
                    if ra != rb:
                        parent[max(ra, rb)] = min(ra, rb)
            else:
                wlabel[y][x] = nl
                parent[nl] = nl
                nl += 1

    for y in range(h):
        for x in range(w):
            if wlabel[y][x]:
                wlabel[y][x] = ufind(wlabel[y][x])

    # Group white regions
    from collections import defaultdict
    wgroups: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for y in range(h):
        for x in range(w):
            lbl = wlabel[y][x]
            if lbl:
                wgroups[lbl].append((x, y))

    total_pixels = len(pixels)
    to_remove: set[Tuple[int, int]] = set()

    for lbl, wpix in wgroups.items():
        size = len(wpix)
        wxs = [p[0] for p in wpix]
        wys = [p[1] for p in wpix]

        # 1) Edge contact score
        edge_count = sum(
            1 for x, y in wpix
            if x == 0 or x == w - 1 or y == 0 or y == h - 1
        )
        edge_score = edge_count / max(size, 1)

        # 2) Neighbor score: fraction of adjacent non-white pixels
        #    that are transparent (not outline)
        transparent_neighbors = 0
        solid_neighbors = 0
        seen: set[Tuple[int, int]] = set()
        for x, y in wpix:
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    if (nx, ny) not in pixels:
                        # Outside sprite entirely
                        transparent_neighbors += 1
                    elif not white_mask[ny][nx]:
                        # Adjacent to non-white sprite content (outline)
                        solid_neighbors += 1
        neighbor_total = transparent_neighbors + solid_neighbors
        neighbor_score = transparent_neighbors / max(neighbor_total, 1)

        # 3) Size score
        size_score = min(size / max(total_pixels, 1) * 5, 1.0)

        # Combined: weighted towards edge and neighbor signals
        score = 0.35 * edge_score + 0.40 * neighbor_score + 0.25 * size_score

        if score > aggressiveness:
            to_remove.update(wpix)

    # Remove flagged pixels
    return {k: v for k, v in pixels.items() if k not in to_remove}


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
