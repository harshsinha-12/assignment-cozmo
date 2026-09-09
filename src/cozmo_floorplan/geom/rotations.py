"""Small 3D rotation utilities for sensor poses."""

from __future__ import annotations

import numpy as np

from cozmo_floorplan.errors import ReconstructionError


def quaternion_xyzw_matrix(quaternion: tuple[float, ...]) -> np.ndarray:
    """Return a normalized 3x3 rotation matrix for an `(x, y, z, w)` quaternion."""

    if len(quaternion) != 4:
        raise ReconstructionError("A Record3D quaternion must contain four values.")
    x, y, z, w = (float(value) for value in quaternion)
    norm = float(np.sqrt(x * x + y * y + z * z + w * w))
    if not np.isfinite(norm) or norm <= 1e-12:
        raise ReconstructionError(
            "A Record3D quaternion must have a finite non-zero norm."
        )
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    return np.asarray(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )
