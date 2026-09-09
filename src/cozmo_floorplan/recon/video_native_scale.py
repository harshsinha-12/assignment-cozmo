"""Disclosed handheld-height metric prior for native Camera-app video."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.geom.rotations import matrix_to_quaternion_xyzw
from cozmo_floorplan.io.video import SampledVideo
from cozmo_floorplan.io.video_poses import (
    MetricCameraIntrinsics,
    MetricCameraPose,
    MetricPoseSidecar,
)
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_NATIVE_SCALE,
    DEFAULT_VIDEO_TRAJECTORY,
    VideoNativeScaleConfig,
    VideoTrajectoryConfig,
)
from cozmo_floorplan.recon.video_trajectory import (
    TrajectorySegment,
    VideoTrajectoryDiagnostics,
)

# OpenCV camera coordinates are x-right, y-down, z-forward. Rotating 180 degrees
# around x gives a proper right-handed y-up frame (z points backward).
OPENCV_TO_Y_UP = np.diag([1.0, -1.0, -1.0])
NATIVE_SCALE_SOURCE = "known_length"


@dataclass(frozen=True, slots=True)
class HandheldHeightScale:
    """Floor-supported conversion from unitless y-up coordinates to metres."""

    floor_y: float
    scale_m_per_unit: float
    camera_height_m: float


def build_native_unit_sidecar(
    video: SampledVideo,
    trajectory: VideoTrajectoryDiagnostics,
    *,
    trajectory_config: VideoTrajectoryConfig = DEFAULT_VIDEO_TRAJECTORY,
    native_config: VideoNativeScaleConfig = DEFAULT_VIDEO_NATIVE_SCALE,
) -> MetricPoseSidecar | None:
    """Build a y-up camera-to-world sidecar at unit scale from the longest segment."""

    segment = _longest_segment(trajectory)
    if (
        segment is None
        or len(segment.poses) < 3
        or len(video.source_frame_indices) != len(video.frames)
        or len(video.timestamps_s) != len(video.frames)
    ):
        return None
    width, height = video.metadata.display_size_px
    focal = trajectory.assumed_focal_length_px or (
        trajectory_config.assumed_focal_length_fraction * max(width, height)
    )
    poses = tuple(
        _yup_pose(video, pose.frame_index, pose.position_unitless, pose.rotation_camera_to_segment)
        for pose in segment.poses
    )
    source = video.metadata.source.with_name(
        f"{video.identifier}.native-height.poses.json"
    )
    return MetricPoseSidecar(
        source=source,
        poses=poses,
        schema_version="1.2.0",
        intrinsics=MetricCameraIntrinsics(
            fx_px=float(focal),
            fy_px=float(focal),
            cx_px=width / 2.0,
            cy_px=height / 2.0,
            image_size_px=(width, height),
        ),
        camera_axes="x_right_y_down_z_forward",
        world_frame_id=f"{native_config.world_frame_prefix}:{video.identifier}",
        scale_source=NATIVE_SCALE_SOURCE,
    )


def estimate_handheld_height_scale(
    camera_positions_m: np.ndarray,
    points_m: np.ndarray,
    *,
    config: VideoNativeScaleConfig = DEFAULT_VIDEO_NATIVE_SCALE,
) -> HandheldHeightScale | None:
    """Scale unitless y-up geometry so median camera height matches the prior."""

    cameras = np.asarray(camera_positions_m, dtype=np.float64)
    points = np.asarray(points_m, dtype=np.float64)
    if cameras.ndim != 2 or cameras.shape[1] != 3 or len(cameras) < 3:
        return None
    if points.ndim != 2 or points.shape[1] != 3:
        return None
    camera_y = float(np.median(cameras[:, 1]))
    below = points[points[:, 1] < camera_y - config.camera_floor_clearance_m]
    if len(below) < config.minimum_floor_points:
        return None
    bins = np.round(below[:, 1] / config.floor_bin_m) * config.floor_bin_m
    values, counts = np.unique(np.round(bins, 6), return_counts=True)
    floor_y = float(values[int(np.argmax(counts))])
    unitless_height = camera_y - floor_y
    if unitless_height <= 1e-6:
        return None
    scale = config.handheld_camera_height_m / unitless_height
    if not np.isfinite(scale) or scale <= 0:
        return None
    return HandheldHeightScale(
        floor_y=floor_y,
        scale_m_per_unit=float(scale),
        camera_height_m=config.handheld_camera_height_m,
    )


def apply_handheld_height_scale(
    sidecar: MetricPoseSidecar,
    points_m: np.ndarray,
    scale: HandheldHeightScale,
) -> tuple[MetricPoseSidecar, np.ndarray]:
    """Move the floor to y=0 and convert unitless coordinates into metres."""

    poses = tuple(
        MetricCameraPose(
            source_frame_index=pose.source_frame_index,
            timestamp_s=pose.timestamp_s,
            position_m=_offset_and_scale(pose.position_m, scale),
            rotation_xyzw=pose.rotation_xyzw,
        )
        for pose in sidecar.poses
    )
    scaled_points = np.asarray(
        [_offset_and_scale(point, scale) for point in points_m],
        dtype=np.float64,
    )
    return (
        MetricPoseSidecar(
            source=sidecar.source,
            poses=poses,
            schema_version=sidecar.schema_version,
            intrinsics=sidecar.intrinsics,
            camera_axes=sidecar.camera_axes,
            world_frame_id=sidecar.world_frame_id,
            scale_source=sidecar.scale_source,
            units=sidecar.units,
            transform=sidecar.transform,
            coordinate_system=sidecar.coordinate_system,
            timestamp_origin=sidecar.timestamp_origin,
        ),
        scaled_points,
    )


def _longest_segment(
    trajectory: VideoTrajectoryDiagnostics,
) -> TrajectorySegment | None:
    if not trajectory.segments:
        return None
    return max(trajectory.segments, key=lambda item: (len(item.poses), -item.segment_id))


def _yup_pose(
    video: SampledVideo,
    sample_index: int,
    position_unitless: tuple[float, float, float],
    rotation_camera_to_segment: tuple[float, ...],
) -> MetricCameraPose:
    rotation = OPENCV_TO_Y_UP @ np.asarray(rotation_camera_to_segment, dtype=np.float64).reshape(
        3, 3
    )
    position = OPENCV_TO_Y_UP @ np.asarray(position_unitless, dtype=np.float64)
    return MetricCameraPose(
        source_frame_index=video.source_frame_indices[sample_index],
        timestamp_s=video.timestamps_s[sample_index],
        position_m=tuple(float(value) for value in position),
        rotation_xyzw=matrix_to_quaternion_xyzw(rotation),
    )


def _offset_and_scale(
    position: tuple[float, ...] | np.ndarray,
    scale: HandheldHeightScale,
) -> tuple[float, float, float]:
    x, y, z = (float(value) for value in position)
    return (
        x * scale.scale_m_per_unit,
        (y - scale.floor_y) * scale.scale_m_per_unit,
        z * scale.scale_m_per_unit,
    )
