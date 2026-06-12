"""PixelFlood — Pixel Art Processing Toolkit.

Flood-fill transparency + sprite extraction + indexed palette sampling.
"""

from .engine import auto_crop, extract, flood, process
from .sample import preview_image, sample, to_typescript

__version__ = "0.2.0"
__all__ = [
    "flood", "auto_crop", "extract", "process",
    "sample", "to_typescript", "preview_image",
]
