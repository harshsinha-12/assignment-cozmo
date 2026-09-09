"""Vectorized helpers for points relative to planar segments."""

from __future__ import annotations

import numpy as np


def point_segment_coordinates(
    points_xy: np.ndarray,
    start_xy: tuple[float, float],
    end_xy: tuple[float, float],
) -> tuple[np.ndarray, np.ndarray, float]:
    """Return signed along/normal coordinates and segment length."""

    start = np.asarray(start_xy, dtype=np.float64)
    end = np.asarray(end_xy, dtype=np.float64)
    direction = end - start
    length = float(np.linalg.norm(direction))
    if length <= 1e-9:
        raise ValueError("segment endpoints must be distinct")
    tangent = direction / length
    normal = np.asarray([-tangent[1], tangent[0]])
    relative = np.asarray(points_xy, dtype=np.float64) - start
    return relative @ tangent, relative @ normal, length
