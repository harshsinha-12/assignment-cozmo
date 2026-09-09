"""Back-project Record3D depth into deterministic metric world points."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.geom.rotations import quaternion_xyzw_matrix
from cozmo_floorplan.io.record3d import Record3DCapture, read_record3d_frame
from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_POINT_CLOUD,
    Record3DPointCloudConfig,
)
from cozmo_floorplan.utils.sampling import evenly_spaced_indices


@dataclass(frozen=True, slots=True)
class MetricPointCloud:
    """Downsampled world-space points plus auditable capture counts."""

    points_m: np.ndarray
    sampled_frame_indices: tuple[int, ...]
    observed_depth_pixels: int
    accepted_depth_pixels: int
    voxel_size_m: float

    @property
    def bounds_m(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        minimum = np.min(self.points_m, axis=0)
        maximum = np.max(self.points_m, axis=0)
        return tuple(float(value) for value in minimum), tuple(
            float(value) for value in maximum
        )


def build_metric_point_cloud(
    capture: Record3DCapture,
    *,
    config: Record3DPointCloudConfig = DEFAULT_RECORD3D_POINT_CLOUD,
) -> MetricPointCloud:
    """Fuse sampled depth using registered intrinsics and camera-to-world poses."""

    _validate_config(config)
    metadata = capture.metadata
    indices = evenly_spaced_indices(metadata.frame_count, config.sampled_frame_count)
    chunks: list[np.ndarray] = []
    observed = 0
    accepted = 0
    for index in indices:
        frame = read_record3d_frame(capture, index)
        camera_points, frame_observed = _back_project_frame(
            frame.depth_m,
            frame.confidence,
            metadata.intrinsics[index],
            color_size=(metadata.color_width_px, metadata.color_height_px),
            config=config,
        )
        observed += frame_observed
        accepted += len(camera_points)
        if len(camera_points) == 0:
            continue
        pose = metadata.poses[index]
        rotation = quaternion_xyzw_matrix(pose[:4])
        translation = np.asarray(pose[4:7], dtype=np.float64)
        chunks.append(camera_points @ rotation.T + translation)

    if not chunks:
        raise ReconstructionError(
            f"Record3D capture {capture.source.name!r} produced no usable metric points."
        )
    points = _voxel_centroids(np.concatenate(chunks), config.voxel_size_m)
    if len(points) < 3:
        raise ReconstructionError(
            f"Record3D capture {capture.source.name!r} produced fewer than three voxels."
        )
    return MetricPointCloud(
        points_m=points,
        sampled_frame_indices=indices,
        observed_depth_pixels=observed,
        accepted_depth_pixels=accepted,
        voxel_size_m=config.voxel_size_m,
    )


def _back_project_frame(
    depth_m: np.ndarray,
    confidence: np.ndarray,
    intrinsics: tuple[float, ...],
    *,
    color_size: tuple[int, int],
    config: Record3DPointCloudConfig,
) -> tuple[np.ndarray, int]:
    """Return OpenGL camera-space points where forward is negative z."""

    if depth_m.shape != confidence.shape:
        raise ReconstructionError("Record3D depth and confidence shapes must match.")
    depth_height, depth_width = depth_m.shape
    color_width, color_height = color_size
    fx, fy, cx, cy = intrinsics
    scale_x = depth_width / color_width
    scale_y = depth_height / color_height
    fx, cx = fx * scale_x, cx * scale_x
    fy, cy = fy * scale_y, cy * scale_y
    if fx <= 0 or fy <= 0:
        raise ReconstructionError("Record3D focal lengths must be positive.")

    rows = np.arange(0, depth_height, config.pixel_stride)
    columns = np.arange(0, depth_width, config.pixel_stride)
    pixel_x, pixel_y = np.meshgrid(columns, rows)
    sampled_depth = depth_m[:: config.pixel_stride, :: config.pixel_stride]
    sampled_confidence = confidence[:: config.pixel_stride, :: config.pixel_stride]
    if np.any(sampled_confidence > 2):
        raise ReconstructionError("Record3D confidence values must be in 0..2.")
    observed = int(sampled_depth.size)
    usable = (
        np.isfinite(sampled_depth)
        & (sampled_depth >= config.minimum_depth_m)
        & (sampled_depth <= config.maximum_depth_m)
        & (sampled_confidence >= config.minimum_confidence)
    )
    distance = sampled_depth[usable].astype(np.float64, copy=False)
    x = (pixel_x[usable] - cx) * distance / fx
    y = (cy - pixel_y[usable]) * distance / fy
    z = -distance
    return np.column_stack((x, y, z)), observed


def _voxel_centroids(points: np.ndarray, voxel_size_m: float) -> np.ndarray:
    keys = np.floor(points / voxel_size_m).astype(np.int64)
    _, inverse = np.unique(keys, axis=0, return_inverse=True)
    counts = np.bincount(inverse)
    coordinates = [
        np.bincount(inverse, weights=points[:, axis]) / counts for axis in range(3)
    ]
    return np.column_stack(coordinates)


def _validate_config(config: Record3DPointCloudConfig) -> None:
    if config.sampled_frame_count <= 0:
        raise ValueError("sampled_frame_count must be positive")
    if config.pixel_stride <= 0:
        raise ValueError("pixel_stride must be positive")
    if not 0 <= config.minimum_confidence <= 2:
        raise ValueError("minimum_confidence must be in 0..2")
    if not 0 < config.minimum_depth_m < config.maximum_depth_m:
        raise ValueError("depth bounds must be positive and increasing")
    if config.voxel_size_m <= 0:
        raise ValueError("voxel_size_m must be positive")
