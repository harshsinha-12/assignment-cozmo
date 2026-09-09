"""Strict input boundary for metric per-video camera-pose sidecars."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_METRIC_POSE,
    VideoMetricPoseConfig,
)


@dataclass(frozen=True, slots=True)
class MetricCameraPose:
    """One metric camera-to-world pose tied to an encoded video frame."""

    source_frame_index: int
    timestamp_s: float
    position_m: tuple[float, float, float]
    rotation_xyzw: tuple[float, float, float, float]


@dataclass(frozen=True, slots=True)
class MetricPoseSidecar:
    """Validated metric camera poses in the documented coordinate contract."""

    source: Path
    poses: tuple[MetricCameraPose, ...]
    units: str = "m"
    transform: str = "camera_to_world"
    coordinate_system: str = "right_handed_y_up"
    timestamp_origin: str = "video_start"


def load_metric_pose_sidecar(
    path: Path,
    *,
    config: VideoMetricPoseConfig = DEFAULT_VIDEO_METRIC_POSE,
) -> MetricPoseSidecar:
    """Load and validate one versioned JSON metric-pose sidecar."""

    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Could not read metric pose sidecar {path.name}: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise ValueError(f"Metric pose sidecar {path.name} must be a JSON object")
    expected = {
        "schema_version": "1.0.0",
        "units": "m",
        "transform": "camera_to_world",
        "coordinate_system": "right_handed_y_up",
        "timestamp_origin": "video_start",
    }
    for field, value in expected.items():
        if document.get(field) != value:
            raise ValueError(
                f"Metric pose sidecar {path.name} requires {field}={value!r}"
            )
    raw_poses = document.get("poses")
    if not isinstance(raw_poses, list) or not raw_poses:
        raise ValueError(
            f"Metric pose sidecar {path.name} requires a non-empty poses[]"
        )

    poses = tuple(
        _parse_pose(item, index, path.name, config)
        for index, item in enumerate(raw_poses)
    )
    frame_indices = [pose.source_frame_index for pose in poses]
    timestamps = [pose.timestamp_s for pose in poses]
    if any(right <= left for left, right in zip(frame_indices, frame_indices[1:])):
        raise ValueError(
            f"Metric pose sidecar {path.name} frame indices must be unique and increasing"
        )
    if any(right <= left for left, right in zip(timestamps, timestamps[1:])):
        raise ValueError(
            f"Metric pose sidecar {path.name} timestamps must be unique and increasing"
        )
    return MetricPoseSidecar(source=path, poses=poses)


def _parse_pose(
    item: object,
    index: int,
    filename: str,
    config: VideoMetricPoseConfig,
) -> MetricCameraPose:
    if not isinstance(item, dict):
        raise ValueError(f"{filename} poses[{index}] must be an object")
    frame_index = item.get("source_frame_index")
    if (
        isinstance(frame_index, bool)
        or not isinstance(frame_index, int)
        or frame_index < 0
    ):
        raise ValueError(
            f"{filename} poses[{index}].source_frame_index must be a non-negative integer"
        )
    timestamp = _finite_number(
        item.get("timestamp_s"), f"{filename} poses[{index}].timestamp_s"
    )
    if timestamp < 0:
        raise ValueError(f"{filename} poses[{index}].timestamp_s must be non-negative")
    position = _finite_vector(
        item.get("position_m"), 3, f"{filename} poses[{index}].position_m"
    )
    quaternion = _finite_vector(
        item.get("rotation_xyzw"),
        4,
        f"{filename} poses[{index}].rotation_xyzw",
    )
    norm = float(np.linalg.norm(quaternion))
    if abs(norm - 1.0) > config.quaternion_norm_tolerance:
        raise ValueError(f"{filename} poses[{index}].rotation_xyzw must have unit norm")
    normalized = quaternion / norm
    return MetricCameraPose(
        source_frame_index=frame_index,
        timestamp_s=timestamp,
        position_m=tuple(float(value) for value in position),
        rotation_xyzw=tuple(float(value) for value in normalized),
    )


def _finite_vector(value: object, length: int, label: str) -> np.ndarray:
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{label} must contain exactly {length} numbers")
    return np.asarray([_finite_number(item, label) for item in value], dtype=np.float64)


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number")
    return number
