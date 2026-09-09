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


def matrix_to_quaternion_xyzw(matrix: np.ndarray) -> tuple[float, float, float, float]:
    """Convert a 3x3 rotation matrix to a unit `(x, y, z, w)` quaternion."""

    rotation = np.asarray(matrix, dtype=np.float64)
    if rotation.shape != (3, 3):
        raise ValueError("rotation matrix must be 3x3")
    trace = float(np.trace(rotation))
    if trace > 0.0:
        scale = 0.5 / float(np.sqrt(trace + 1.0))
        quaternion = np.array(
            [
                (rotation[2, 1] - rotation[1, 2]) * scale,
                (rotation[0, 2] - rotation[2, 0]) * scale,
                (rotation[1, 0] - rotation[0, 1]) * scale,
                0.25 / scale,
            ],
            dtype=np.float64,
        )
    else:
        index = int(np.argmax(np.diag(rotation)))
        next_index = (index + 1) % 3
        last_index = (index + 2) % 3
        scale = 2.0 * float(
            np.sqrt(
                1.0
                + rotation[index, index]
                - rotation[next_index, next_index]
                - rotation[last_index, last_index]
            )
        )
        quaternion = np.zeros(4, dtype=np.float64)
        quaternion[index] = 0.25 * scale
        quaternion[next_index] = (
            rotation[next_index, index] + rotation[index, next_index]
        ) / scale
        quaternion[last_index] = (
            rotation[last_index, index] + rotation[index, last_index]
        ) / scale
        quaternion[3] = (
            rotation[last_index, next_index] - rotation[next_index, last_index]
        ) / scale
    norm = float(np.linalg.norm(quaternion))
    if not np.isfinite(norm) or norm <= 1e-12:
        raise ValueError("rotation matrix must produce a finite quaternion")
    quaternion /= norm
    return tuple(float(value) for value in quaternion)
