"""Detect supported door and window gaps on fitted Record3D wall planes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.geom.segments import point_segment_coordinates
from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_OPENINGS,
    Record3DOpeningConfig,
)
from cozmo_floorplan.recon.record3d_planes import ManhattanRoomCandidate


@dataclass(frozen=True, slots=True)
class Record3DOpeningCandidate:
    """An occupancy-supported gap measured along one polygon edge."""

    wall_index: int
    kind: str
    offset_m: float
    width_m: float
    height_m: float
    sparse_profile_bins: int
    lintel_support_points: int


def detect_record3d_openings(
    points_m: np.ndarray,
    room: ManhattanRoomCandidate,
    *,
    config: Record3DOpeningConfig = DEFAULT_RECORD3D_OPENINGS,
) -> tuple[Record3DOpeningCandidate, ...]:
    """Find wall gaps only when floor/sill and lintel evidence disambiguate them."""

    _validate_config(config)
    openings: list[Record3DOpeningCandidate] = []
    polygon = room.polygon_xz_m
    relative_y = points_m[:, 1] - room.levels.floor_y_m
    for wall_index, start in enumerate(polygon):
        end = polygon[(wall_index + 1) % len(polygon)]
        along, normal, wall_length = point_segment_coordinates(
            points_m[:, (0, 2)], start, end
        )
        on_wall = (
            (np.abs(normal) <= config.wall_normal_tolerance_m)
            & (along >= 0.0)
            & (along <= wall_length)
        )
        openings.extend(
            _wall_openings(
                wall_index,
                along[on_wall],
                relative_y[on_wall],
                wall_length,
                room.levels.ceiling_height_m,
                config,
            )
        )
    return tuple(openings)


def _wall_openings(
    wall_index: int,
    along_m: np.ndarray,
    relative_y_m: np.ndarray,
    wall_length_m: float,
    ceiling_height_m: float,
    config: Record3DOpeningConfig,
) -> list[Record3DOpeningCandidate]:
    edges = _profile_edges(wall_length_m, config.profile_bin_m)
    centers = (edges[:-1] + edges[1:]) / 2.0
    interior = (centers >= config.wall_end_margin_m) & (
        centers <= wall_length_m - config.wall_end_margin_m
    )
    door_counts = _band_counts(
        along_m,
        relative_y_m,
        edges,
        config.door_band_low_m,
        config.door_band_high_m,
    )
    sill_counts = _band_counts(
        along_m,
        relative_y_m,
        edges,
        config.door_band_low_m,
        config.sill_band_high_m,
    )
    window_counts = _band_counts(
        along_m,
        relative_y_m,
        edges,
        config.window_band_low_m,
        config.window_band_high_m,
    )
    lintel_counts = _band_counts(
        along_m,
        relative_y_m,
        edges,
        config.lintel_band_low_m,
        ceiling_height_m - config.ceiling_margin_m,
    )
    door_mask = (
        interior
        & _sparse_mask(door_counts, interior, config)
        & _supported_mask(lintel_counts, interior, config)
    )
    window_mask = (
        interior
        & ~door_mask
        & _sparse_mask(window_counts, interior, config)
        & _supported_mask(sill_counts, interior, config)
        & _supported_mask(lintel_counts, interior, config)
    )

    openings = _opening_runs(
        wall_index,
        "door",
        door_mask,
        edges,
        along_m,
        relative_y_m,
        lintel_counts,
        config.minimum_door_width_m,
        config.maximum_door_width_m,
        ceiling_height_m,
        config,
    )
    openings.extend(
        _opening_runs(
            wall_index,
            "window",
            window_mask,
            edges,
            along_m,
            relative_y_m,
            lintel_counts,
            config.minimum_window_width_m,
            config.maximum_window_width_m,
            ceiling_height_m,
            config,
        )
    )
    return openings


def _profile_edges(length_m: float, bin_m: float) -> np.ndarray:
    edges = np.arange(0.0, length_m, bin_m)
    if len(edges) == 0 or not np.isclose(edges[-1], length_m):
        edges = np.append(edges, length_m)
    return edges


def _band_counts(
    along_m: np.ndarray,
    relative_y_m: np.ndarray,
    edges: np.ndarray,
    low_m: float,
    high_m: float,
) -> np.ndarray:
    if high_m <= low_m:
        return np.zeros(len(edges) - 1, dtype=np.int64)
    in_band = (relative_y_m >= low_m) & (relative_y_m <= high_m)
    return np.histogram(along_m[in_band], edges)[0]


def _sparse_mask(
    counts: np.ndarray,
    interior: np.ndarray,
    config: Record3DOpeningConfig,
) -> np.ndarray:
    baseline = _profile_baseline(counts, interior)
    threshold = max(config.minimum_band_points, baseline * config.sparse_ratio)
    return counts <= threshold


def _supported_mask(
    counts: np.ndarray,
    interior: np.ndarray,
    config: Record3DOpeningConfig,
) -> np.ndarray:
    baseline = _profile_baseline(counts, interior)
    threshold = max(config.minimum_band_points, baseline * config.supported_ratio)
    return counts >= threshold


def _profile_baseline(counts: np.ndarray, interior: np.ndarray) -> float:
    values = counts[interior]
    positive = values[values > 0]
    return float(np.percentile(positive, 70)) if len(positive) else 0.0


def _opening_runs(
    wall_index: int,
    kind: str,
    mask: np.ndarray,
    edges: np.ndarray,
    along_m: np.ndarray,
    relative_y_m: np.ndarray,
    lintel_counts: np.ndarray,
    minimum_width_m: float,
    maximum_width_m: float,
    ceiling_height_m: float,
    config: Record3DOpeningConfig,
) -> list[Record3DOpeningCandidate]:
    repaired = _bridge_short_interruptions(mask, config.maximum_interruption_bins)
    openings: list[Record3DOpeningCandidate] = []
    for start_index, end_index in _true_runs(repaired):
        start_m = float(edges[start_index])
        end_m = float(edges[end_index])
        width_m = end_m - start_m
        if not minimum_width_m <= width_m <= maximum_width_m:
            continue
        in_span = (along_m >= start_m) & (along_m <= end_m)
        span_y = relative_y_m[in_span]
        top_m = _opening_top(span_y, ceiling_height_m, config)
        if top_m is None:
            continue
        bottom_m = _window_bottom(span_y, config) if kind == "window" else 0.0
        height_m = top_m - bottom_m
        if height_m <= 0:
            continue
        openings.append(
            Record3DOpeningCandidate(
                wall_index=wall_index,
                kind=kind,
                offset_m=start_m,
                width_m=width_m,
                height_m=height_m,
                sparse_profile_bins=end_index - start_index,
                lintel_support_points=int(lintel_counts[start_index:end_index].sum()),
            )
        )
    return openings


def _opening_top(
    relative_y_m: np.ndarray,
    ceiling_height_m: float,
    config: Record3DOpeningConfig,
) -> float | None:
    edges = np.arange(
        config.minimum_opening_height_m,
        ceiling_height_m + config.height_bin_m,
        config.height_bin_m,
    )
    if len(edges) < config.height_support_run_bins + 1:
        return None
    counts = np.histogram(relative_y_m, edges)[0]
    threshold = max(
        config.minimum_band_points,
        float(np.max(counts)) * config.height_support_ratio,
    )
    supported = counts >= threshold
    run = config.height_support_run_bins
    for index in range(0, len(supported) - run + 1):
        if np.all(supported[index : index + run]):
            return float(edges[index])
    return None


def _window_bottom(
    relative_y_m: np.ndarray,
    config: Record3DOpeningConfig,
) -> float:
    sill_points = relative_y_m[
        (relative_y_m >= config.door_band_low_m)
        & (relative_y_m < config.window_band_low_m)
    ]
    if len(sill_points) == 0:
        return config.window_band_low_m
    top_bin = np.floor(np.max(sill_points) / config.height_bin_m) + 1.0
    return min(config.window_band_low_m, float(top_bin * config.height_bin_m))


def _bridge_short_interruptions(mask: np.ndarray, maximum_bins: int) -> np.ndarray:
    result = mask.copy()
    if maximum_bins <= 0:
        return result
    for start, end in _false_runs(result):
        if start == 0 or end == len(result) or end - start > maximum_bins:
            continue
        if result[start - 1] and result[end]:
            result[start:end] = True
    return result


def _true_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    padded = np.pad(mask.astype(np.int8), (1, 1))
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1)
    return list(zip(starts.tolist(), ends.tolist(), strict=True))


def _false_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    return _true_runs(~mask)


def _validate_config(config: Record3DOpeningConfig) -> None:
    positive = (
        config.wall_normal_tolerance_m,
        config.profile_bin_m,
        config.minimum_door_width_m,
        config.maximum_door_width_m,
        config.minimum_window_width_m,
        config.maximum_window_width_m,
        config.height_bin_m,
        config.height_support_run_bins,
    )
    if any(value <= 0 for value in positive):
        raise ValueError("Record3D opening thresholds must be positive")
    if config.minimum_door_width_m > config.maximum_door_width_m:
        raise ValueError("Record3D door width bounds must be increasing")
    if config.minimum_window_width_m > config.maximum_window_width_m:
        raise ValueError("Record3D window width bounds must be increasing")
