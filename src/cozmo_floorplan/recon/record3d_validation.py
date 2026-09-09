"""Bounded integrity checks for Record3D RGB-D captures."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.record3d import Record3DCapture, read_record3d_frame
from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_VALIDATION,
    Record3DValidationConfig,
)
from cozmo_floorplan.utils.sampling import evenly_spaced_indices


@dataclass(frozen=True, slots=True)
class Record3DValidationSummary:
    frame_count: int
    sampled_frame_indices: tuple[int, ...]
    valid_depth_fraction: float
    depth_range_m: tuple[float, float]
    trajectory_extent_m: tuple[float, float, float]


def validate_record3d_capture(
    capture: Record3DCapture,
    *,
    config: Record3DValidationConfig = DEFAULT_RECORD3D_VALIDATION,
) -> Record3DValidationSummary:
    """Decode representative frames and summarize evidence without fitting walls."""

    indices = evenly_spaced_indices(
        capture.metadata.frame_count,
        config.sample_frame_count,
    )
    valid_count = 0
    total_count = 0
    valid_depths: list[np.ndarray] = []
    for index in indices:
        frame = read_record3d_frame(capture, index)
        if np.any(frame.confidence > 2):
            raise ReconstructionError(
                f"Record3D frame {index} in {capture.source.name!r} has confidence outside 0..2."
            )
        valid = (
            np.isfinite(frame.depth_m)
            & (frame.depth_m >= config.minimum_depth_m)
            & (frame.depth_m <= config.maximum_depth_m)
        )
        valid_count += int(np.count_nonzero(valid))
        total_count += int(valid.size)
        if np.any(valid):
            valid_depths.append(frame.depth_m[valid])

    if not valid_depths:
        raise ReconstructionError(
            f"Record3D capture {capture.source.name!r} has no valid depth in sampled frames."
        )
    concatenated = np.concatenate(valid_depths)
    translations = np.asarray(
        [pose[4:7] for pose in capture.metadata.poses], dtype=float
    )
    extent = np.ptp(translations, axis=0)
    return Record3DValidationSummary(
        frame_count=capture.metadata.frame_count,
        sampled_frame_indices=indices,
        valid_depth_fraction=valid_count / total_count,
        depth_range_m=(float(np.min(concatenated)), float(np.max(concatenated))),
        trajectory_extent_m=(float(extent[0]), float(extent[1]), float(extent[2])),
    )
