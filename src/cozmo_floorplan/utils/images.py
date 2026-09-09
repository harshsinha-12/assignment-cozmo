"""Small image-array transformations shared by capture adapters."""

from __future__ import annotations

import cv2
import numpy as np


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
