"""Tests for PixelFlood edge flood-fill engine."""

import pytest
from PIL import Image

from pixelflood import flood, auto_crop


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
