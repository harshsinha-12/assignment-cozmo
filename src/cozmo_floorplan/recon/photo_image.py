"""Shared bounded image preparation for photo feature extractors."""

from pathlib import Path

import cv2
import numpy as np

from cozmo_floorplan.utils.images import load_display_oriented_bgr


def load_resized_gray(path: Path, max_dimension_px: int) -> np.ndarray:
    """Decode a photo as grayscale and resize it without changing aspect ratio."""

    bgr = load_display_oriented_bgr(path)
    if bgr is None:
        raise ValueError(f"Could not decode photo for feature extraction: {path}")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    largest = max(height, width)
    if largest > max_dimension_px:
        scale = max_dimension_px / largest
        width = max(1, round(width * scale))
        height = max(1, round(height * scale))
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
    return gray
