"""Extract conservative Manhattan room-plane candidates from Record3D points."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_PLANES,
    Record3DPlaneConfig,
)


@dataclass(frozen=True, slots=True)
class HorizontalPlaneLevels:
    """Floor and ceiling candidates in the Record3D world frame."""

    floor_y_m: float
    ceiling_y_m: float
    floor_support_points: int
    ceiling_support_points: int

    @property
    def ceiling_height_m(self) -> float:
        return self.ceiling_y_m - self.floor_y_m


@dataclass(frozen=True, slots=True)
class WallPlaneCandidate:
    """One axis-aligned wall in the regularized room-local frame."""

    axis: str
    coordinate_m: float
    support_columns: int


@dataclass(frozen=True, slots=True)
class ManhattanRoomCandidate:
    """Four-wall candidate that brackets the observed camera trajectory."""

    levels: HorizontalPlaneLevels
    yaw_degrees: float
    walls: tuple[WallPlaneCandidate, ...]
    polygon_xz_m: tuple[tuple[float, float], ...]
    width_m: float
    depth_m: float
    vertical_support_columns: int


def extract_manhattan_room_candidate(
    points_m: np.ndarray,
    camera_positions_m: np.ndarray,
    *,
    config: Record3DPlaneConfig = DEFAULT_RECORD3D_PLANES,
) -> ManhattanRoomCandidate:
    """Fit horizontal levels and four Manhattan walls around the camera path."""

    _validate_inputs(points_m, camera_positions_m, config)
    levels = _horizontal_levels(points_m[:, 1], camera_positions_m[:, 1], config)
    columns_xz = _persistent_vertical_columns(points_m, levels, config)
    yaw_degrees = _best_manhattan_yaw(columns_xz, config)

    rotation = _planar_rotation(yaw_degrees)
    local_columns = columns_xz @ rotation.T
    local_cameras = camera_positions_m[:, (0, 2)] @ rotation.T
    x_low, x_high = _bracketing_wall_pair(
        local_columns[:, 0], local_cameras[:, 0], "x", config
    )
    z_low, z_high = _bracketing_wall_pair(
        local_columns[:, 1], local_cameras[:, 1], "z", config
    )

    local_corners = np.asarray(
        [
            [x_low.coordinate_m, z_low.coordinate_m],
            [x_high.coordinate_m, z_low.coordinate_m],
            [x_high.coordinate_m, z_high.coordinate_m],
            [x_low.coordinate_m, z_high.coordinate_m],
        ]
    )
    world_corners = local_corners @ rotation
    return ManhattanRoomCandidate(
        levels=levels,
        yaw_degrees=yaw_degrees,
        walls=(x_low, x_high, z_low, z_high),
        polygon_xz_m=tuple(
            (float(corner[0]), float(corner[1])) for corner in world_corners
        ),
        width_m=x_high.coordinate_m - x_low.coordinate_m,
        depth_m=z_high.coordinate_m - z_low.coordinate_m,
        vertical_support_columns=len(columns_xz),
    )


def _horizontal_levels(
    point_y: np.ndarray,
    camera_y: np.ndarray,
    config: Record3DPlaneConfig,
) -> HorizontalPlaneLevels:
    camera_level = float(np.median(camera_y))
    quantized = np.floor(point_y / config.horizontal_bin_m).astype(np.int64)
    bins, counts = np.unique(quantized, return_counts=True)
    dense_counts = np.zeros(int(bins[-1] - bins[0] + 1), dtype=np.int64)
    dense_counts[bins - bins[0]] = counts
    smoothing_width = min(config.horizontal_smoothing_bins, len(dense_counts))
    kernel = np.ones(smoothing_width, dtype=np.int64)
    smoothed = np.convolve(dense_counts, kernel, mode="same")
    centers = (np.arange(len(dense_counts)) + bins[0] + 0.5) * config.horizontal_bin_m

    floor_mask = centers < camera_level - config.camera_level_clearance_m
    ceiling_mask = centers > camera_level + config.camera_level_clearance_m
    if not np.any(floor_mask) or not np.any(ceiling_mask):
        raise ReconstructionError(
            "Record3D points do not contain floor and ceiling candidates on opposite sides of the camera path."
        )
    floor_seed = _peak_seed(centers, dense_counts, smoothed, floor_mask, config, preference="lowest")
    ceiling_seed = _peak_seed(centers, dense_counts, smoothed, ceiling_mask, config, preference="highest")
    floor_y, floor_support = _refine_level(point_y, floor_seed, config)
    ceiling_y, ceiling_support = _refine_level(point_y, ceiling_seed, config)
    height = ceiling_y - floor_y
    if not config.minimum_ceiling_height_m <= height <= config.maximum_ceiling_height_m:
        raise ReconstructionError(
            f"Record3D floor/ceiling candidate height {height:.2f} m is outside "
            f"the configured {config.minimum_ceiling_height_m:.2f}–"
            f"{config.maximum_ceiling_height_m:.2f} m range."
        )
    return HorizontalPlaneLevels(
        floor_y_m=floor_y,
        ceiling_y_m=ceiling_y,
        floor_support_points=floor_support,
        ceiling_support_points=ceiling_support,
    )


def _peak_seed(
    centers: np.ndarray,
    counts: np.ndarray,
    smoothed: np.ndarray,
    eligible: np.ndarray,
    config: Record3DPlaneConfig,
    *,
    preference: str,
) -> float:
    eligible_indices = np.flatnonzero(eligible)
    peak_smooth = float(np.max(smoothed[eligible]))
    significant = eligible_indices[
        smoothed[eligible] >= peak_smooth * config.horizontal_envelope_ratio
    ]
    if preference == "lowest":
        chosen = int(significant[np.argmin(centers[significant])])
    elif preference == "highest":
        chosen = int(significant[np.argmax(centers[significant])])
    else:
        raise ValueError(f"Unsupported horizontal peak preference {preference!r}")
    radius = config.horizontal_smoothing_bins // 2
    neighborhood = eligible_indices[np.abs(eligible_indices - chosen) <= radius]
    raw_peak = int(neighborhood[np.argmax(counts[neighborhood])])
    return float(centers[raw_peak])


def _refine_level(
    point_y: np.ndarray,
    seed: float,
    config: Record3DPlaneConfig,
) -> tuple[float, int]:
    support = np.abs(point_y - seed) <= config.level_refine_half_width_m
    if not np.any(support):
        raise ReconstructionError("Record3D horizontal plane has no local support.")
    return float(np.median(point_y[support])), int(np.count_nonzero(support))


def _persistent_vertical_columns(
    points_m: np.ndarray,
    levels: HorizontalPlaneLevels,
    config: Record3DPlaneConfig,
) -> np.ndarray:
    inside_height = (
        points_m[:, 1] >= levels.floor_y_m + config.wall_vertical_margin_m
    ) & (points_m[:, 1] <= levels.ceiling_y_m - config.wall_vertical_margin_m)
    candidates = points_m[inside_height]
    if len(candidates) == 0:
        raise ReconstructionError(
            "Record3D capture has no points between floor and ceiling."
        )
    keys = np.floor(candidates[:, (0, 2)] / config.wall_column_bin_m).astype(np.int64)
    unique_keys, inverse, counts = np.unique(
        keys, axis=0, return_inverse=True, return_counts=True
    )
    minimum_y = np.full(len(unique_keys), np.inf)
    maximum_y = np.full(len(unique_keys), -np.inf)
    np.minimum.at(minimum_y, inverse, candidates[:, 1])
    np.maximum.at(maximum_y, inverse, candidates[:, 1])
    persistent = (counts >= config.minimum_column_points) & (
        maximum_y - minimum_y >= config.minimum_column_vertical_span_m
    )
    columns = (
        unique_keys[persistent].astype(np.float64) + 0.5
    ) * config.wall_column_bin_m
    if len(columns) < config.yaw_peak_count:
        raise ReconstructionError(
            "Record3D capture has too few vertically persistent columns for wall fitting."
        )
    return columns


def _best_manhattan_yaw(columns_xz: np.ndarray, config: Record3DPlaneConfig) -> float:
    yaws = np.arange(0.0, 90.0, config.yaw_step_degrees)
    scores = np.empty(len(yaws), dtype=np.int64)
    for index, yaw in enumerate(yaws):
        local = columns_xz @ _planar_rotation(float(yaw)).T
        scores[index] = sum(
            _dominant_histogram_support(local[:, axis], config) for axis in range(2)
        )
    return float(yaws[int(np.argmax(scores))])


def _dominant_histogram_support(values: np.ndarray, config: Record3DPlaneConfig) -> int:
    keys = np.floor(values / config.wall_histogram_bin_m).astype(np.int64)
    counts = np.unique(keys, return_counts=True)[1]
    peak_count = min(config.yaw_peak_count, len(counts))
    return int(np.partition(counts, -peak_count)[-peak_count:].sum())


def _bracketing_wall_pair(
    values: np.ndarray,
    camera_values: np.ndarray,
    axis: str,
    config: Record3DPlaneConfig,
) -> tuple[WallPlaneCandidate, WallPlaneCandidate]:
    keys = np.floor(values / config.wall_histogram_bin_m).astype(np.int64)
    unique_keys, counts = np.unique(keys, return_counts=True)
    coordinates = (unique_keys.astype(np.float64) + 0.5) * config.wall_histogram_bin_m
    camera_low, camera_high = np.quantile(
        camera_values,
        [config.camera_bracket_quantile, 1.0 - config.camera_bracket_quantile],
    )
    low_candidates = np.flatnonzero(
        coordinates <= camera_low - config.camera_wall_margin_m
    )
    high_candidates = np.flatnonzero(
        coordinates >= camera_high + config.camera_wall_margin_m
    )
    if len(low_candidates) == 0 or len(high_candidates) == 0:
        raise ReconstructionError(
            "Record3D wall candidates do not bracket the observed camera trajectory."
        )
    low_index = _outer_supported_peak(coordinates, counts, low_candidates, "low", config)
    high_index = _outer_supported_peak(coordinates, counts, high_candidates, "high", config)
    span = float(coordinates[high_index] - coordinates[low_index])
    if not config.minimum_room_span_m <= span <= config.maximum_room_span_m:
        raise ReconstructionError(
            f"Record3D wall-pair span {span:.2f} m is outside the configured "
            f"{config.minimum_room_span_m:.2f}–{config.maximum_room_span_m:.2f} m range."
        )
    return (
        WallPlaneCandidate(
            axis=axis,
            coordinate_m=float(coordinates[low_index]),
            support_columns=int(counts[low_index]),
        ),
        WallPlaneCandidate(
            axis=axis,
            coordinate_m=float(coordinates[high_index]),
            support_columns=int(counts[high_index]),
        ),
        )


def _outer_supported_peak(
    coordinates: np.ndarray,
    counts: np.ndarray,
    candidates: np.ndarray,
    side: str,
    config: Record3DPlaneConfig,
) -> int:
    """Prefer the architectural envelope over a denser inward clutter plane."""

    peak_support = float(np.max(counts[candidates]))
    significant = candidates[counts[candidates] >= peak_support * config.outer_wall_support_ratio]
    if side == "low":
        return int(significant[np.argmin(coordinates[significant])])
    if side == "high":
        return int(significant[np.argmax(coordinates[significant])])
    raise ValueError(f"Unsupported wall side {side!r}")


def _planar_rotation(yaw_degrees: float) -> np.ndarray:
    angle = radians(yaw_degrees)
    return np.asarray([[cos(angle), sin(angle)], [-sin(angle), cos(angle)]])


def _validate_inputs(
    points_m: np.ndarray,
    camera_positions_m: np.ndarray,
    config: Record3DPlaneConfig,
) -> None:
    if points_m.ndim != 2 or points_m.shape[1] != 3 or len(points_m) < 3:
        raise ReconstructionError(
            "Record3D plane fitting requires an N x 3 point cloud."
        )
    if (
        camera_positions_m.ndim != 2
        or camera_positions_m.shape[1] != 3
        or len(camera_positions_m) == 0
    ):
        raise ReconstructionError("Record3D plane fitting requires camera positions.")
    if not np.all(np.isfinite(points_m)) or not np.all(np.isfinite(camera_positions_m)):
        raise ReconstructionError("Record3D plane fitting inputs must be finite.")
    if config.horizontal_bin_m <= 0 or config.wall_column_bin_m <= 0:
        raise ValueError("Record3D plane bins must be positive")
    if config.horizontal_smoothing_bins <= 0:
        raise ValueError("horizontal_smoothing_bins must be positive")
    if not 0 < config.camera_bracket_quantile < 0.5:
        raise ValueError("camera_bracket_quantile must be between zero and one half")
    if not 0 < config.yaw_step_degrees < 90:
        raise ValueError("yaw_step_degrees must be between zero and 90")
    if not 0 < config.outer_wall_support_ratio <= 1:
        raise ValueError("outer_wall_support_ratio must be in (0, 1]")
    if not 0 < config.horizontal_envelope_ratio <= 1:
        raise ValueError("horizontal_envelope_ratio must be in (0, 1]")
