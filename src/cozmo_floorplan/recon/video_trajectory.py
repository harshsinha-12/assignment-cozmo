"""Scale-free relative camera trajectory recovery for normalized videos."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from cozmo_floorplan.io.video import SampledVideo
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_TRACKING,
    DEFAULT_VIDEO_TRAJECTORY,
    VideoTrackingConfig,
    VideoTrajectoryConfig,
)
from cozmo_floorplan.recon.video_features import (
    PairCorrespondences,
    extract_frame_features,
    match_frame_features,
)
from cozmo_floorplan.recon.video_tracks import analyze_feature_pair
from cozmo_floorplan.utils.sampling import evenly_spaced_indices


@dataclass(frozen=True, slots=True)
class RelativeCameraPose:
    """Camera-to-segment pose; translation units are deliberately arbitrary."""

    frame_index: int
    position_unitless: tuple[float, float, float]
    rotation_camera_to_segment: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class TrajectorySegment:
    """One connected run of relative poses separated by rejected edges."""

    segment_id: int
    poses: tuple[RelativeCameraPose, ...]


@dataclass(frozen=True, slots=True)
class PoseEdgeDiagnostics:
    """Acceptance evidence for one attempted relative-pose edge."""

    left_index: int
    right_index: int
    accepted: bool
    pose_inliers: int
    cheirality_ratio: float
    rejection_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VideoTrajectoryDiagnostics:
    """Scale-free pose segments and the assumptions used to recover them."""

    identifier: str
    selected_frames: int
    attempted_edges: int
    accepted_edges: int
    segment_breaks: int
    segment_restarts: int
    assumed_focal_length_px: float
    intrinsics_source: str
    segments: tuple[TrajectorySegment, ...]
    edges: tuple[PoseEdgeDiagnostics, ...]


@dataclass(frozen=True, slots=True)
class RelativePoseEstimate:
    """Two-camera transform taking coordinates in the left camera to right."""

    rotation_left_to_right: np.ndarray
    translation_direction_left_to_right: np.ndarray
    pose_inliers: int
    cheirality_ratio: float


def recover_scale_free_trajectory(
    video: SampledVideo,
    *,
    tracking_config: VideoTrackingConfig = DEFAULT_VIDEO_TRACKING,
    trajectory_config: VideoTrajectoryConfig = DEFAULT_VIDEO_TRAJECTORY,
) -> VideoTrajectoryDiagnostics:
    """Recover connected unit-step poses without interpreting scale as metres."""

    _validate_config(trajectory_config)
    if len(video.frames) < 2:
        return _empty_trajectory(video.identifier)
    indices = evenly_spaced_indices(
        len(video.frames),
        min(trajectory_config.maximum_frame_count, len(video.frames)),
    )
    features = {
        index: extract_frame_features(video.frames[index], tracking_config)
        for index in indices
    }
    image_size = features[indices[0]].image_size_px
    intrinsic_matrix = _assumed_intrinsic_matrix(image_size, trajectory_config)

    edges: list[PoseEdgeDiagnostics] = []
    segments: list[TrajectorySegment] = []
    active_poses: list[RelativeCameraPose] = []
    segment_breaks = 0
    selected = tuple(indices)
    position = 0

    while position < len(selected) - 1:
        found = False
        for span in range(1, trajectory_config.maximum_edge_span + 1):
            target = position + span
            if target >= len(selected):
                break
            left_index = selected[position]
            right_index = selected[target]
            left = features[left_index]
            right = features[right_index]
            correspondences = match_frame_features(left, right, tracking_config)
            track = analyze_feature_pair(
                left_index,
                left,
                right,
                tracking_config,
                correspondences,
            )
            estimate, pose_reasons = (
                _recover_relative_pose(
                    correspondences,
                    intrinsic_matrix,
                    trajectory_config,
                )
                if track.eligible
                else (None, track.rejection_reasons)
            )
            accepted = estimate is not None
            edges.append(
                PoseEdgeDiagnostics(
                    left_index=left_index,
                    right_index=right_index,
                    accepted=accepted,
                    pose_inliers=estimate.pose_inliers if estimate else 0,
                    cheirality_ratio=estimate.cheirality_ratio if estimate else 0.0,
                    rejection_reasons=pose_reasons,
                )
            )
            if not accepted:
                continue
            if not active_poses:
                active_poses = [_identity_pose(left_index)]
            active_poses.append(
                _compose_pose(
                    active_poses[-1],
                    right_index,
                    estimate,
                    step_length=float(span),
                )
            )
            position = target
            found = True
            break
        if found:
            continue
        if active_poses:
            _append_segment(segments, active_poses, trajectory_config)
            active_poses = []
            segment_breaks += 1
        position += 1

    if active_poses:
        _append_segment(segments, active_poses, trajectory_config)

    accepted_edges = sum(edge.accepted for edge in edges)
    restarts = max(0, len(segments) - 1)
    focal = float(intrinsic_matrix[0, 0])
    return VideoTrajectoryDiagnostics(
        identifier=video.identifier,
        selected_frames=len(indices),
        attempted_edges=len(edges),
        accepted_edges=accepted_edges,
        segment_breaks=segment_breaks,
        segment_restarts=restarts,
        assumed_focal_length_px=focal,
        intrinsics_source="image_size_focal_prior_unvalidated",
        segments=tuple(segments),
        edges=tuple(edges),
    )


def recover_relative_pose_from_points(
    left_points_px: np.ndarray,
    right_points_px: np.ndarray,
    image_size_px: tuple[int, int],
    *,
    config: VideoTrajectoryConfig = DEFAULT_VIDEO_TRAJECTORY,
) -> RelativePoseEstimate | None:
    """Testable two-view pose primitive using explicitly assumed intrinsics."""

    _validate_config(config)
    if len(left_points_px) != len(right_points_px) or len(left_points_px) < 8:
        return None
    intrinsic_matrix = _assumed_intrinsic_matrix(image_size_px, config)
    correspondences = PairCorrespondences(
        left_points_px=np.asarray(left_points_px, dtype=np.float32),
        right_points_px=np.asarray(right_points_px, dtype=np.float32),
        fundamental_matrix=None,
        fundamental_inliers=np.ones(len(left_points_px), dtype=bool),
    )
    estimate, _reasons = _recover_relative_pose(
        correspondences, intrinsic_matrix, config
    )
    return estimate


def _recover_relative_pose(
    correspondences: PairCorrespondences,
    intrinsic_matrix: np.ndarray,
    config: VideoTrajectoryConfig,
) -> tuple[RelativePoseEstimate | None, tuple[str, ...]]:
    mask = correspondences.fundamental_inliers
    left = correspondences.left_points_px[mask]
    right = correspondences.right_points_px[mask]
    if len(left) < 8:
        return None, ("insufficient_fundamental_support",)
    cv2.setRNGSeed(0)
    essential, essential_mask = cv2.findEssentialMat(
        left,
        right,
        intrinsic_matrix,
        method=cv2.RANSAC,
        prob=0.999,
        threshold=1.0,
    )
    if essential is None or essential_mask is None:
        return None, ("essential_estimation_failed",)
    supported = int(np.count_nonzero(essential_mask))
    pose_inliers, rotation, translation, pose_mask = cv2.recoverPose(
        essential,
        left,
        right,
        intrinsic_matrix,
        mask=essential_mask.copy(),
    )
    cheirality = int(np.count_nonzero(pose_mask))
    ratio = cheirality / supported if supported else 0.0
    reasons: list[str] = []
    if pose_inliers < config.minimum_pose_inliers:
        reasons.append("too_few_pose_inliers")
    if ratio < config.minimum_cheirality_ratio:
        reasons.append("low_cheirality_support")
    translation_vector = translation.reshape(3)
    norm = float(np.linalg.norm(translation_vector))
    if norm <= 1e-12:
        reasons.append("zero_translation_direction")
    if reasons:
        return None, tuple(reasons)
    return (
        RelativePoseEstimate(
            rotation_left_to_right=rotation,
            translation_direction_left_to_right=translation_vector / norm,
            pose_inliers=int(pose_inliers),
            cheirality_ratio=ratio,
        ),
        (),
    )


def _compose_pose(
    previous: RelativeCameraPose,
    frame_index: int,
    estimate: RelativePoseEstimate,
    *,
    step_length: float = 1.0,
) -> RelativeCameraPose:
    previous_rotation = np.asarray(previous.rotation_camera_to_segment).reshape(3, 3)
    relative_rotation = estimate.rotation_left_to_right
    camera_step_left = (
        -relative_rotation.T
        @ (estimate.translation_direction_left_to_right * step_length)
    )
    position = (
        np.asarray(previous.position_unitless) + previous_rotation @ camera_step_left
    )
    rotation = previous_rotation @ relative_rotation.T
    return RelativeCameraPose(
        frame_index=frame_index,
        position_unitless=tuple(float(value) for value in position),
        rotation_camera_to_segment=tuple(float(value) for value in rotation.ravel()),
    )


def _identity_pose(frame_index: int) -> RelativeCameraPose:
    return RelativeCameraPose(
        frame_index=frame_index,
        position_unitless=(0.0, 0.0, 0.0),
        rotation_camera_to_segment=tuple(float(value) for value in np.eye(3).ravel()),
    )


def _append_segment(
    segments: list[TrajectorySegment],
    poses: list[RelativeCameraPose],
    config: VideoTrajectoryConfig,
) -> None:
    if len(poses) >= config.minimum_segment_pose_count:
        segments.append(TrajectorySegment(len(segments), tuple(poses)))


def _assumed_intrinsic_matrix(
    image_size_px: tuple[int, int],
    config: VideoTrajectoryConfig,
) -> np.ndarray:
    width, height = image_size_px
    focal = config.assumed_focal_length_fraction * max(width, height)
    return np.array(
        [[focal, 0.0, width / 2.0], [0.0, focal, height / 2.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )


def _empty_trajectory(identifier: str) -> VideoTrajectoryDiagnostics:
    return VideoTrajectoryDiagnostics(
        identifier=identifier,
        selected_frames=0,
        attempted_edges=0,
        accepted_edges=0,
        segment_breaks=0,
        segment_restarts=0,
        assumed_focal_length_px=0.0,
        intrinsics_source="image_size_focal_prior_unvalidated",
        segments=(),
        edges=(),
    )


def _validate_config(config: VideoTrajectoryConfig) -> None:
    if config.maximum_frame_count < 2:
        raise ValueError("video trajectory frame bound must be at least two")
    if config.assumed_focal_length_fraction <= 0:
        raise ValueError("video trajectory focal prior must be positive")
    if config.minimum_pose_inliers < 8:
        raise ValueError("video trajectory pose support must be at least eight")
    if not 0 < config.minimum_cheirality_ratio <= 1:
        raise ValueError("video trajectory cheirality ratio must be in (0, 1]")
    if config.minimum_segment_pose_count < 2:
        raise ValueError("video trajectory segments must contain at least two poses")
    if config.maximum_edge_span < 1:
        raise ValueError("video trajectory edge span must be at least one")
