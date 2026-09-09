"""Sparse, gravity-aligned floor and wall-plane diagnostics for video points."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_SURFACES,
    VideoSurfaceConfig,
)


@dataclass(frozen=True, slots=True)
class VideoPlaneCandidate:
    """One supported coordinate band; it is evidence, not room geometry."""

    kind: str
    axis: str
    coordinate_m: float
    support_points: int
    support_fraction: float


def diagnose_video_planes(
    points_m: np.ndarray,
    *,
    config: VideoSurfaceConfig = DEFAULT_VIDEO_SURFACES,
) -> tuple[VideoPlaneCandidate, ...]:
    """Find separated coordinate peaks in a right-handed, y-up world frame."""

    _validate(points_m, config)
    candidates: list[VideoPlaneCandidate] = []
    for axis_index, axis in enumerate(("x", "y", "z")):
        candidates.extend(_axis_candidates(points_m[:, axis_index], axis, config))
    return tuple(sorted(candidates, key=lambda item: (item.axis, item.coordinate_m)))


def _axis_candidates(
    values: np.ndarray,
    axis: str,
    config: VideoSurfaceConfig,
) -> list[VideoPlaneCandidate]:
    keys = np.floor(values / config.coordinate_bin_m).astype(np.int64)
    unique, counts = np.unique(keys, return_counts=True)
    order = sorted(
        range(len(unique)),
        key=lambda index: (-int(counts[index]), int(unique[index])),
    )
    accepted: list[VideoPlaneCandidate] = []
    minimum_support = max(
        config.minimum_support_points,
        int(np.ceil(config.minimum_support_fraction * len(values))),
    )
    for index in order:
        support = int(counts[index])
        if support < minimum_support:
            break
        coordinate = float(np.median(values[keys == unique[index]]))
        if any(
            abs(coordinate - other.coordinate_m) < config.minimum_candidate_separation_m
            for other in accepted
        ):
            continue
        accepted.append(
            VideoPlaneCandidate(
                kind="horizontal" if axis == "y" else "wall",
                axis=axis,
                coordinate_m=coordinate,
                support_points=support,
                support_fraction=support / len(values),
            )
        )
        if len(accepted) >= config.maximum_candidates_per_axis:
            break
    return accepted


def _validate(points_m: np.ndarray, config: VideoSurfaceConfig) -> None:
    if points_m.ndim != 2 or points_m.shape[1] != 3:
        raise ValueError("video surface diagnostics require an N x 3 point cloud")
    if not np.all(np.isfinite(points_m)):
        raise ValueError("video surface points must be finite")
    if config.coordinate_bin_m <= 0:
        raise ValueError("video surface coordinate_bin_m must be positive")
    if config.minimum_support_points <= 0:
        raise ValueError("video surface minimum_support_points must be positive")
    if not 0 < config.minimum_support_fraction <= 1:
        raise ValueError("video surface minimum_support_fraction must be in (0, 1]")
    if config.maximum_candidates_per_axis <= 0:
        raise ValueError("maximum_candidates_per_axis must be positive")
    if config.minimum_candidate_separation_m < 0:
        raise ValueError("minimum_candidate_separation_m must be non-negative")
