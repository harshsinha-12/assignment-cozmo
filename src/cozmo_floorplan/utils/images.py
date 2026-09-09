"""Small image-array transformations shared by capture adapters."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


def load_display_oriented_bgr(path: Path) -> np.ndarray | None:
    """Decode an image and apply EXIF/display orientation before returning BGR."""

    try:
        with Image.open(path) as image:
            oriented = ImageOps.exif_transpose(image)
            if oriented is None:
                oriented = image
            rgb = np.asarray(oriented.convert("RGB"))
    except (OSError, UnidentifiedImageError, ValueError):
        return cv2.imread(str(path), cv2.IMREAD_COLOR)
    if rgb.ndim != 3 or rgb.size == 0:
        return None
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def rotate_quarter_turns_clockwise(
    frame: np.ndarray,
    rotation_degrees: int,
) -> np.ndarray:
    """Apply a normalized clockwise display rotation to an image array."""

    rotation = rotation_degrees % 360
    if rotation == 0:
        return frame
    if rotation == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    if rotation == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    if rotation == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise ValueError("display rotation must be a multiple of 90 degrees")
