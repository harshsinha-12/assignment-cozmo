"""Small deterministic point-cloud utilities shared by reconstruction tiers."""

from __future__ import annotations

import numpy as np


def voxel_centroids(points: np.ndarray, voxel_size_m: float) -> np.ndarray:
    """Replace finite N x 3 points with one centroid per metric voxel."""

    values = np.asarray(points, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("point cloud must have shape N x 3")
    if voxel_size_m <= 0:
        raise ValueError("voxel_size_m must be positive")
    if len(values) == 0:
        return np.empty((0, 3), dtype=np.float64)
    if not np.all(np.isfinite(values)):
        raise ValueError("point cloud must contain only finite coordinates")
    keys = np.floor(values / voxel_size_m).astype(np.int64)
    _, inverse = np.unique(keys, axis=0, return_inverse=True)
    counts = np.bincount(inverse)
    coordinates = [
        np.bincount(inverse, weights=values[:, axis]) / counts for axis in range(3)
    ]
    return np.column_stack(coordinates)
