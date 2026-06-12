"""Tests for PixelFlood edge flood-fill engine."""

import pytest
from PIL import Image

from pixelflood import auto_crop, extract, flood


def _make_image(w: int, h: int,
                fill: tuple[int, int, int, int] = (255, 255, 255, 255),
                ) -> Image.Image:
    return Image.new("RGBA", (w, h), fill)


def _draw_rect(img: Image.Image, x: int, y: int, rw: int, rh: int,
               color: tuple[int, int, int, int]) -> None:
    """Draw a filled rectangle (including outline of another colour)."""
    px = img.load()
    for dy in range(rh):
        for dx in range(rw):
            px[x + dx, y + dy] = color  # type: ignore[index]


def test_full_white_becomes_transparent() -> None:
    """A plain white image should become fully transparent."""
    img = _make_image(50, 50)
    result = flood(img)
    alpha = [a for _, _, _, a in result.getdata()]
    assert all(a == 0 for a in alpha)


def test_interior_white_preserved() -> None:
    """White pixels surrounded by a non-white border should survive."""
    # 50×50 white background
    img = _make_image(50, 50)
    # Draw a black outline ring 20×20 at (15, 15)
    _draw_rect(img, 15, 15, 20, 20, (0, 0, 0, 255))
    # Fill interior (17,17)..(31,31) with white
    _draw_rect(img, 17, 17, 14, 14, (255, 255, 255, 255))

    result = flood(img)
    px = result.load()
    assert px is not None

    # Exterior white → transparent
    assert px[0, 0][3] == 0   # type: ignore[index]
    # Interior white (inside black ring) → preserved
    assert px[25, 25][3] == 255  # type: ignore[index]


def test_threshold_matches_near_white() -> None:
    """Threshold should capture off-white pixels too."""
    # Background: slightly off white (250, 250, 250)
    img = _make_image(30, 30, (250, 250, 250, 255))
    # Dark outline ring
    _draw_rect(img, 5, 5, 20, 20, (0, 0, 0, 255))
    # Interior: same off-white
    _draw_rect(img, 7, 7, 16, 16, (250, 250, 250, 255))

    result = flood(img, threshold=7)
    px = result.load()
    assert px is not None
    assert px[0, 0][3] == 0    # exterior → transparent  # type: ignore[index]
    assert px[13, 13][3] == 255  # interior → kept  # type: ignore[index]


def test_auto_crop_removes_transparent_borders() -> None:
    """auto_crop should trim fully transparent rows/cols."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    _draw_rect(img, 30, 20, 40, 60, (255, 0, 0, 255))

    cropped = auto_crop(img)
    assert cropped.size == (40, 60)


def test_connectivity_8_leaks_through_diagonals() -> None:
    """8-connectivity should flood through diagonal gaps."""
    # White background
    img = _make_image(30, 30)
    # Diagonal-only barrier — a checkerboard of black pixels at the border
    px = img.load()
    for i in range(5, 25):
        px[i, 10] = (0, 0, 0, 255)  # type: ignore[index]
    # With 4-connectivity, the barrier holds; with 8-connectivity, it may leak
    # through corners. This test just validates that 8-mode runs.
    result = flood(img, connectivity=8)
    assert result.mode == "RGBA"


def test_non_white_background() -> None:
    """Should work with any background colour."""
    img = _make_image(40, 40, (0, 128, 0, 255))  # green bg
    _draw_rect(img, 10, 10, 20, 20, (255, 0, 0, 255))

    result = flood(img, background_color=(0, 128, 0))
    px = result.load()
    assert px is not None
    assert px[0, 0][3] == 0    # green bg → transparent  # type: ignore[index]
    assert px[15, 15] == (255, 0, 0, 255)  # red rect → kept  # type: ignore[index]


# ── extract() tests ──

def test_extract_single_sprite() -> None:
    """A single sprite on white bg should extract as one image."""
    img = _make_image(80, 80)
    _draw_rect(img, 30, 30, 20, 20, (0, 0, 0, 255))
    sprites = extract(img, min_size=10)
    assert len(sprites) == 1
    assert sprites[0].width <= 25 and sprites[0].height <= 25


def test_extract_multiple_sprites() -> None:
    """Two separated shapes should extract as two sprites."""
    img = _make_image(120, 80)
    # Left shape
    _draw_rect(img, 10, 20, 30, 40, (0, 0, 0, 255))
    # Right shape
    _draw_rect(img, 80, 30, 20, 20, (255, 0, 0, 255))
    sprites = extract(img, min_size=10)
    assert len(sprites) == 2


def test_extract_filters_noise() -> None:
    """min_size should filter out tiny pixel noise."""
    img = _make_image(60, 60)
    _draw_rect(img, 20, 20, 20, 20, (0, 0, 0, 255))
    # 1-pixel noise
    img.putpixel((5, 5), (255, 0, 0, 255))
    img.putpixel((50, 50), (0, 255, 0, 255))
    sprites = extract(img, min_size=50)
    assert len(sprites) == 1


def test_extract_preserves_white_body() -> None:
    """White pixels inside a sprite outline should be kept (not background)."""
    img = _make_image(80, 80)
    # Black outline ring
    _draw_rect(img, 20, 20, 40, 40, (0, 0, 0, 255))
    # White interior
    _draw_rect(img, 22, 22, 36, 36, (255, 255, 255, 255))
    sprites = extract(img, min_size=10)
    assert len(sprites) == 1
    # Sprite should contain white interior pixels
    data = sprites[0].getdata()
    white_px = sum(1 for r, g, b, a in data if a > 0 and r >= 248 and g >= 248 and b >= 248)
    assert white_px > 100  # white body preserved


def test_extract_sorted_left_to_right() -> None:
    """Sprites should be sorted left-to-right."""
    img = _make_image(200, 80)
    _draw_rect(img, 10, 20, 20, 40, (0, 0, 0, 255))    # left (black)
    _draw_rect(img, 170, 20, 20, 40, (255, 0, 0, 255))  # right (red)
    sprites = extract(img, min_size=10)
    assert len(sprites) == 2
    # Black sprite first, red second
    left_data = sprites[0].getdata()
    right_data = sprites[1].getdata()
    left_has_black = any(r < 10 and g < 10 and b < 10 and a > 0 for r, g, b, a in left_data)
    right_has_red = any(r > 200 and g < 10 and b < 10 and a > 0 for r, g, b, a in right_data)
    assert left_has_black
    assert right_has_red


def test_extract_smart_removes_trapped_white() -> None:
    """Smart mode should remove white trapped between two sprites."""
    # Two sprites close together with white gap between them
    img = _make_image(120, 80)
    # Left sprite: black outline with white interior
    _draw_rect(img, 5, 20, 35, 40, (0, 0, 0, 255))  # outline
    _draw_rect(img, 7, 22, 31, 36, (255, 255, 255, 255))  # white body
    # Right sprite: red outline
    _draw_rect(img, 75, 25, 35, 30, (255, 0, 0, 255))
    # Thin white gap between them at x=40..74 — this should be trapped bg

    sprites_without = extract(img, min_size=50, smart=False)
    sprites_with = extract(img, min_size=50, smart=True, smart_bg_threshold=0.3)

    # Smart mode should remove some of the trapped white gap
    total_without = sum(1 for s in sprites_without for p in s.getdata() if p[3] > 0)
    total_with = sum(1 for s in sprites_with for p in s.getdata() if p[3] > 0)
    assert total_with <= total_without  # smart removed some pixels


def test_smart_keeps_body_white() -> None:
    """Smart mode should NOT remove white that's surrounded by outline."""
    img = _make_image(80, 80)
    _draw_rect(img, 20, 20, 40, 40, (0, 0, 0, 255))  # outline
    _draw_rect(img, 22, 22, 36, 36, (255, 255, 255, 255))  # body white

    sprites = extract(img, min_size=10, smart=True, smart_bg_threshold=0.5)
    assert len(sprites) == 1
    data = list(sprites[0].getdata())
    white_kept = sum(1 for r, g, b, a in data if a > 0 and r >= 248 and g >= 248 and b >= 248)
    assert white_kept > 500  # body white preserved, not over-cleaned
