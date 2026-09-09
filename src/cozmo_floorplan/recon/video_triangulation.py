"""Calibrated sparse triangulation for accepted metric video segments."""

from __future__ import annotations

from dataclasses import dataclass
from math import degrees

import cv2
import numpy as np

from cozmo_floorplan.geom.rotations import quaternion_xyzw_matrix
from cozmo_floorplan.io.video import SampledVideo
from cozmo_floorplan.io.video_poses import (
    MetricCameraIntrinsics,
    MetricCameraPose,
    MetricPoseSidecar,
)
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_TRACKING,
    DEFAULT_VIDEO_TRIANGULATION,
    VideoTrackingConfig,
    VideoTriangulationConfig,
)
from cozmo_floorplan.recon.video_features import (
    FrameFeatures,
    extract_frame_features,
    match_frame_features,
)
from cozmo_floorplan.recon.video_pose_alignment import MetricTrajectoryAlignment
from cozmo_floorplan.recon.video_trajectory import VideoTrajectoryDiagnostics
from cozmo_floorplan.utils.point_clouds import voxel_centroids


@dataclass(frozen=True, slots=True)
class TriangulatedPairDiagnostics:
    """Acceptance and filtering counts for one adjacent calibrated pair."""

    left_index: int
    right_index: int
    input_inliers: int
    accepted_points: int
    rejection_reason: str | None


@dataclass(frozen=True, slots=True)
class SparseMetricVideoCloud:
    """Voxelized metric feature points with a pair-level audit trail."""

    points_m: np.ndarray
    attempted_pairs: int
    accepted_pairs: int
    raw_accepted_points: int
    voxel_size_m: float
    pairs: tuple[TriangulatedPairDiagnostics, ...]


def triangulate_aligned_video_segments(
    video: SampledVideo,
    trajectory: VideoTrajectoryDiagnostics,
    alignment: MetricTrajectoryAlignment,
    sidecar: MetricPoseSidecar,
    *,
    tracking_config: VideoTrackingConfig = DEFAULT_VIDEO_TRACKING,
    config: VideoTriangulationConfig = DEFAULT_VIDEO_TRIANGULATION,
) -> SparseMetricVideoCloud | None:
    """Triangulate only accepted segments with exact calibrated sidecar poses."""

    _validate_config(config)
    intrinsics = sidecar.intrinsics
    if intrinsics is None or sidecar.camera_axes != "x_right_y_down_z_forward":
        return None
    if intrinsics.image_size_px != video.metadata.display_size_px:
        return None
    if len(video.frames) != len(video.source_frame_indices) or len(video.frames) != len(
        video.timestamps_s
    ):
        return None

    accepted_segments = {
        segment.segment_id for segment in alignment.segments if segment.accepted
    }
    poses_by_source = {pose.source_frame_index: pose for pose in sidecar.poses}
    features: dict[int, FrameFeatures] = {}
    chunks: list[np.ndarray] = []
    diagnostics: list[TriangulatedPairDiagnostics] = []
    for segment in trajectory.segments:
        if segment.segment_id not in accepted_segments:
            continue
        for left_relative, right_relative in zip(
            segment.poses, segment.poses[1:], strict=False
        ):
            left_index = left_relative.frame_index
            right_index = right_relative.frame_index
            left_pose = _exact_pose(video, left_index, poses_by_source, config)
            right_pose = _exact_pose(video, right_index, poses_by_source, config)
            if left_pose is None or right_pose is None:
                diagnostics.append(
                    TriangulatedPairDiagnostics(
                        left_index, right_index, 0, 0, "metric_pose_not_available"
                    )
                )
                continue
            if left_index not in features:
                features[left_index] = extract_frame_features(
                    video.frames[left_index], tracking_config
                )
            if right_index not in features:
                features[right_index] = extract_frame_features(
                    video.frames[right_index], tracking_config
                )
            left_features = features[left_index]
            right_features = features[right_index]
            correspondences = match_frame_features(
                left_features, right_features, tracking_config
            )
            mask = correspondences.fundamental_inliers
            left_points = correspondences.left_points_px[mask]
            right_points = correspondences.right_points_px[mask]
            scaled = _scaled_intrinsics(intrinsics, left_features.image_size_px)
            if right_features.image_size_px != left_features.image_size_px:
                points = np.empty((0, 3), dtype=np.float64)
                reason = "feature_image_size_mismatch"
            else:
                points = triangulate_metric_correspondences(
                    left_points,
                    right_points,
                    left_pose,
                    right_pose,
                    scaled,
                    config=config,
                )
                reason = (
                    "insufficient_fundamental_support"
                    if len(left_points) < config.minimum_pair_inliers
                    else "geometric_filters_rejected_all"
                    if len(points) == 0
                    else None
                )
            if len(points):
                chunks.append(points)
            diagnostics.append(
                TriangulatedPairDiagnostics(
                    left_index,
                    right_index,
                    len(left_points),
                    len(points),
                    reason,
                )
            )
    combined = np.concatenate(chunks) if chunks else np.empty((0, 3), dtype=np.float64)
    cloud = voxel_centroids(combined, config.voxel_size_m)
    return SparseMetricVideoCloud(
        points_m=cloud,
        attempted_pairs=len(diagnostics),
        accepted_pairs=sum(item.accepted_points > 0 for item in diagnostics),
        raw_accepted_points=len(combined),
        voxel_size_m=config.voxel_size_m,
        pairs=tuple(diagnostics),
    )


def triangulate_metric_correspondences(
    left_points_px: np.ndarray,
    right_points_px: np.ndarray,
    left_pose: MetricCameraPose,
    right_pose: MetricCameraPose,
    intrinsics: MetricCameraIntrinsics,
    *,
    config: VideoTriangulationConfig = DEFAULT_VIDEO_TRIANGULATION,
) -> np.ndarray:
    """Triangulate calibrated correspondences and apply metric geometry gates."""

    _validate_config(config)
    left = np.asarray(left_points_px, dtype=np.float64)
    right = np.asarray(right_points_px, dtype=np.float64)
    if left.shape != right.shape or left.ndim != 2 or left.shape[1:] != (2,):
        raise ValueError("correspondences must be equal N x 2 arrays")
    if len(left) < config.minimum_pair_inliers:
        return np.empty((0, 3), dtype=np.float64)
    intrinsic_matrix = _intrinsic_matrix(intrinsics)
    left_projection = _projection_matrix(left_pose, intrinsic_matrix)
    right_projection = _projection_matrix(right_pose, intrinsic_matrix)
    homogeneous = cv2.triangulatePoints(
        left_projection, right_projection, left.T, right.T
    )
    finite_w = np.abs(homogeneous[3]) > 1e-12
    points = np.full((len(left), 3), np.nan, dtype=np.float64)
    points[finite_w] = (homogeneous[:3, finite_w] / homogeneous[3, finite_w]).T
    valid = finite_w & np.all(np.isfinite(points), axis=1)
    valid &= _depth_mask(points, left_pose, config)
    valid &= _depth_mask(points, right_pose, config)
    valid &= _reprojection_errors(points, left_projection, left) <= (
        config.maximum_reprojection_error_px
    )
    valid &= _reprojection_errors(points, right_projection, right) <= (
        config.maximum_reprojection_error_px
    )
    valid &= _triangulation_angles(points, left_pose, right_pose) >= (
        config.minimum_triangulation_angle_degrees
    )
    return points[valid]


def _exact_pose(
    video: SampledVideo,
    sample_index: int,
    poses_by_source: dict[int, MetricCameraPose],
    config: VideoTriangulationConfig,
) -> MetricCameraPose | None:
    pose = poses_by_source.get(video.source_frame_indices[sample_index])
    if pose is None:
        return None
    if (
        abs(pose.timestamp_s - video.timestamps_s[sample_index])
        > config.timestamp_tolerance_s
    ):
        return None
    return pose


def _scaled_intrinsics(
    intrinsics: MetricCameraIntrinsics,
    target_size: tuple[int, int],
) -> MetricCameraIntrinsics:
    scale_x = target_size[0] / intrinsics.image_size_px[0]
    scale_y = target_size[1] / intrinsics.image_size_px[1]
    return MetricCameraIntrinsics(
        fx_px=intrinsics.fx_px * scale_x,
        fy_px=intrinsics.fy_px * scale_y,
        cx_px=intrinsics.cx_px * scale_x,
        cy_px=intrinsics.cy_px * scale_y,
        image_size_px=target_size,
    )


def _intrinsic_matrix(intrinsics: MetricCameraIntrinsics) -> np.ndarray:
    return np.asarray(
        [
            [intrinsics.fx_px, 0.0, intrinsics.cx_px],
            [0.0, intrinsics.fy_px, intrinsics.cy_px],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )


def _projection_matrix(pose: MetricCameraPose, intrinsic: np.ndarray) -> np.ndarray:
    camera_to_world = quaternion_xyzw_matrix(pose.rotation_xyzw)
    world_to_camera = camera_to_world.T
    center = np.asarray(pose.position_m, dtype=np.float64)
    translation = -world_to_camera @ center
    return intrinsic @ np.column_stack((world_to_camera, translation))


def _camera_points(points: np.ndarray, pose: MetricCameraPose) -> np.ndarray:
    rotation = quaternion_xyzw_matrix(pose.rotation_xyzw)
    center = np.asarray(pose.position_m, dtype=np.float64)
    return (points - center) @ rotation


def _depth_mask(
    points: np.ndarray,
    pose: MetricCameraPose,
    config: VideoTriangulationConfig,
) -> np.ndarray:
    depth = _camera_points(points, pose)[:, 2]
    return (depth >= config.minimum_depth_m) & (depth <= config.maximum_depth_m)


def _reprojection_errors(
    points: np.ndarray,
    projection: np.ndarray,
    observations: np.ndarray,
) -> np.ndarray:
    homogeneous = np.column_stack((points, np.ones(len(points))))
    projected = homogeneous @ projection.T
    pixels = projected[:, :2] / projected[:, 2:3]
    return np.linalg.norm(pixels - observations, axis=1)


def _triangulation_angles(
    points: np.ndarray,
    left_pose: MetricCameraPose,
    right_pose: MetricCameraPose,
) -> np.ndarray:
    left_rays = points - np.asarray(left_pose.position_m)
    right_rays = points - np.asarray(right_pose.position_m)
    denominator = np.linalg.norm(left_rays, axis=1) * np.linalg.norm(right_rays, axis=1)
    cosine = np.divide(
        np.sum(left_rays * right_rays, axis=1),
        denominator,
        out=np.ones(len(points)),
        where=denominator > 1e-12,
    )
    return np.asarray(
        [degrees(np.arccos(np.clip(value, -1.0, 1.0))) for value in cosine]
    )


def _validate_config(config: VideoTriangulationConfig) -> None:
    if config.timestamp_tolerance_s < 0:
        raise ValueError("triangulation timestamp tolerance must be non-negative")
    if config.minimum_pair_inliers < 2:
        raise ValueError("video triangulation needs at least two correspondences")
    if config.maximum_reprojection_error_px <= 0:
        raise ValueError("maximum reprojection error must be positive")
    if not 0 < config.minimum_triangulation_angle_degrees < 180:
        raise ValueError("triangulation angle must be between zero and 180 degrees")
    if not 0 < config.minimum_depth_m < config.maximum_depth_m:
        raise ValueError("triangulation depth bounds must be positive and increasing")
    if config.voxel_size_m <= 0:
        raise ValueError("triangulation voxel size must be positive")
