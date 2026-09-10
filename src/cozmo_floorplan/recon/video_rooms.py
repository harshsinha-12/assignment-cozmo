"""Fit conservative Manhattan room envelopes from sparse metric video points."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_ROOM,
    DEFAULT_VIDEO_SURFACES,
    VideoRoomConfig,
    VideoSurfaceConfig,
)
from cozmo_floorplan.recon.video_surfaces import (
    VideoPlaneCandidate,
    diagnose_video_planes,
)


@dataclass(frozen=True, slots=True)
class VideoRoomCandidate:
    """Metric four-wall room supported around an observed camera path."""

    floor: VideoPlaneCandidate
    ceiling: VideoPlaneCandidate
    walls: tuple[VideoPlaneCandidate, ...]
    yaw_degrees: float
    polygon_xz_m: tuple[tuple[float, float], ...]
    width_m: float
    depth_m: float

    @property
    def ceiling_height_m(self) -> float:
        return self.ceiling.coordinate_m - self.floor.coordinate_m


def fit_video_room_candidate(
    points_m: np.ndarray,
    camera_positions_m: np.ndarray,
    *,
    config: VideoRoomConfig = DEFAULT_VIDEO_ROOM,
    surface_config: VideoSurfaceConfig = DEFAULT_VIDEO_SURFACES,
) -> VideoRoomCandidate:
    """Require floor, ceiling, and walls on both sides of the median camera path."""

    _validate(points_m, camera_positions_m, config)
    camera_y = float(np.median(camera_positions_m[:, 1]))
    horizontal = [
        item
        for item in diagnose_video_planes(points_m, config=surface_config)
        if item.axis == "y"
    ]
    floor = _horizontal_band(
        horizontal,
        points_m[:, 1],
        camera_y,
        config,
        "floor",
    )
    ceiling = _horizontal_band(
        horizontal,
        points_m[:, 1],
        camera_y,
        config,
        "ceiling",
    )
    height = ceiling.coordinate_m - floor.coordinate_m
    if not config.minimum_ceiling_height_m <= height <= config.maximum_ceiling_height_m:
        raise ReconstructionError(
            f"Video floor/ceiling height candidate {height:.2f} m is outside "
            "the configured room range.",
            warning_code="low_confidence",
        )

    yaw, local, local_cameras, local_planes = _best_yaw(
        points_m, camera_positions_m, config, surface_config
    )
    x_low, x_high = _bracketing_pair(
        local_planes, local_cameras[:, 0], local[:, 0], "x", config
    )
    z_low, z_high = _bracketing_pair(
        local_planes, local_cameras[:, 1], local[:, 2], "z", config
    )
    width = x_high.coordinate_m - x_low.coordinate_m
    depth = z_high.coordinate_m - z_low.coordinate_m
    _validate_span(width, "x", config)
    _validate_span(depth, "z", config)

    local_corners = np.asarray(
        [
            [x_low.coordinate_m, z_low.coordinate_m],
            [x_high.coordinate_m, z_low.coordinate_m],
            [x_high.coordinate_m, z_high.coordinate_m],
            [x_low.coordinate_m, z_high.coordinate_m],
        ]
    )
    world_corners = local_corners @ _planar_rotation(yaw)
    return VideoRoomCandidate(
        floor=floor,
        ceiling=ceiling,
        walls=(x_low, x_high, z_low, z_high),
        yaw_degrees=yaw,
        polygon_xz_m=tuple(
            (float(corner[0]), float(corner[1])) for corner in world_corners
        ),
        width_m=width,
        depth_m=depth,
    )


def _best_yaw(
    points_m: np.ndarray,
    cameras_m: np.ndarray,
    config: VideoRoomConfig,
    surface_config: VideoSurfaceConfig,
) -> tuple[float, np.ndarray, np.ndarray, tuple[VideoPlaneCandidate, ...]]:
    best: tuple[int, float, np.ndarray, tuple[VideoPlaneCandidate, ...]] | None = None
    for yaw in np.arange(0.0, 90.0, config.yaw_step_degrees):
        rotation = _planar_rotation(float(yaw))
        local = points_m.copy()
        local[:, (0, 2)] = points_m[:, (0, 2)] @ rotation.T
        local_cameras = cameras_m[:, (0, 2)] @ rotation.T
        planes = tuple(
            item
            for item in diagnose_video_planes(local, config=surface_config)
            if item.axis in {"x", "z"}
        )
        score = sum(item.support_points for item in planes)
        candidate = (score, float(yaw), local_cameras, planes)
        if best is None or candidate[0] > best[0]:
            best = candidate
    if best is None:
        raise ReconstructionError(
            "Video points have no Manhattan wall orientation candidate.",
            warning_code="low_confidence",
        )
    local = points_m.copy()
    rotation = _planar_rotation(best[1])
    local[:, (0, 2)] = points_m[:, (0, 2)] @ rotation.T
    return best[1], local, best[2], best[3]


def _bracketing_pair(
    planes: tuple[VideoPlaneCandidate, ...],
    camera_values: np.ndarray,
    point_values: np.ndarray,
    axis: str,
    config: VideoRoomConfig,
) -> tuple[VideoPlaneCandidate, VideoPlaneCandidate]:
    candidates = [item for item in planes if item.axis == axis]
    camera_center = float(np.median(camera_values))
    low = [
        item
        for item in candidates
        if item.coordinate_m <= camera_center - config.camera_wall_margin_m
    ]
    high = [
        item
        for item in candidates
        if item.coordinate_m >= camera_center + config.camera_wall_margin_m
    ]
    try:
        return (
            _strongest(low, f"{axis}-low wall"),
            _strongest(high, f"{axis}-high wall"),
        )
    except ReconstructionError:
        return _occupancy_pair(point_values, camera_values, axis, config, label=axis)


def _horizontal_band(
    horizontal: list[VideoPlaneCandidate],
    values: np.ndarray,
    camera_y: float,
    config: VideoRoomConfig,
    label: str,
) -> VideoPlaneCandidate:
    if label == "floor":
        plane_candidates = [
            item
            for item in horizontal
            if item.coordinate_m <= camera_y - config.camera_level_clearance_m
        ]
        side = values[values <= camera_y - config.camera_level_clearance_m]
    else:
        plane_candidates = [
            item
            for item in horizontal
            if item.coordinate_m >= camera_y + config.camera_level_clearance_m
        ]
        side = values[values >= camera_y + config.camera_level_clearance_m]
    try:
        return _strongest(plane_candidates, label)
    except ReconstructionError:
        if len(side) < 8:
            raise
        return VideoPlaneCandidate(
            kind="horizontal",
            axis="y",
            coordinate_m=_densest_coordinate(side),
            support_points=int(len(side)),
            support_fraction=float(len(side) / max(len(values), 1)),
        )


def _densest_coordinate(values: np.ndarray, bin_m: float = 0.08) -> float:
    keys = np.round(values / bin_m) * bin_m
    unique, counts = np.unique(np.round(keys, 6), return_counts=True)
    return float(unique[int(np.argmax(counts))])


def _occupancy_pair(
    values: np.ndarray,
    camera_values: np.ndarray,
    axis: str,
    config: VideoRoomConfig,
    *,
    label: str,
) -> tuple[VideoPlaneCandidate, VideoPlaneCandidate]:
    finite = values[np.isfinite(values)]
    if len(finite) < 16:
        raise ReconstructionError(
            f"Sparse video points do not support a camera-bracketing {label} wall pair.",
            warning_code="low_confidence",
        )
    margin = config.camera_wall_margin_m
    low_value = min(
        float(np.quantile(finite, config.camera_bracket_quantile)),
        float(np.min(camera_values) - margin),
    )
    high_value = max(
        float(np.quantile(finite, 1.0 - config.camera_bracket_quantile)),
        float(np.max(camera_values) + margin),
    )
    if high_value - low_value < config.minimum_room_span_m:
        raise ReconstructionError(
            f"Sparse video points do not support a camera-bracketing {label} wall pair.",
            warning_code="low_confidence",
        )
    return (
        VideoPlaneCandidate(
            kind="wall",
            axis=axis,
            coordinate_m=low_value,
            support_points=int(len(finite)),
            support_fraction=1.0,
        ),
        VideoPlaneCandidate(
            kind="wall",
            axis=axis,
            coordinate_m=high_value,
            support_points=int(len(finite)),
            support_fraction=1.0,
        ),
    )


def _strongest(
    candidates: list[VideoPlaneCandidate], label: str
) -> VideoPlaneCandidate:
    if not candidates:
        raise ReconstructionError(
            f"Sparse video points do not support a camera-bracketing {label} candidate.",
            warning_code="low_confidence",
        )
    return max(candidates, key=lambda item: (item.support_points, -item.coordinate_m))


def _validate_span(span_m: float, axis: str, config: VideoRoomConfig) -> None:
    if not config.minimum_room_span_m <= span_m <= config.maximum_room_span_m:
        raise ReconstructionError(
            f"Video {axis}-wall span {span_m:.2f} m is outside the configured room range.",
            warning_code="low_confidence",
        )


def _planar_rotation(yaw_degrees: float) -> np.ndarray:
    angle = radians(yaw_degrees)
    return np.asarray([[cos(angle), sin(angle)], [-sin(angle), cos(angle)]])


def _validate(
    points_m: np.ndarray,
    cameras_m: np.ndarray,
    config: VideoRoomConfig,
) -> None:
    if points_m.ndim != 2 or points_m.shape[1] != 3 or len(points_m) < 3:
        raise ReconstructionError(
            "Video room fitting requires an N x 3 metric point cloud.",
            warning_code="low_confidence",
        )
    if cameras_m.ndim != 2 or cameras_m.shape[1] != 3 or len(cameras_m) == 0:
        raise ReconstructionError(
            "Video room fitting requires metric camera positions.",
            warning_code="low_confidence",
        )
    if not np.all(np.isfinite(points_m)) or not np.all(np.isfinite(cameras_m)):
        raise ReconstructionError(
            "Video room fitting inputs must be finite.", warning_code="low_confidence"
        )
    if not 0 < config.yaw_step_degrees < 90:
        raise ValueError("video room yaw step must be between zero and 90")
    if not 0 < config.camera_bracket_quantile < 0.5:
        raise ValueError("video camera bracket quantile must be in (0, 0.5)")
