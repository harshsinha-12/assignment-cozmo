"""Similarity alignment from unitless VO segments to matched metric poses."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.io.video import SampledVideo
from cozmo_floorplan.io.video_poses import MetricCameraPose, MetricPoseSidecar
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_METRIC_POSE,
    VideoMetricPoseConfig,
)
from cozmo_floorplan.recon.video_trajectory import (
    TrajectorySegment,
    VideoTrajectoryDiagnostics,
)


@dataclass(frozen=True, slots=True)
class MetricSegmentAlignment:
    """One accepted or rejected local-segment metric alignment."""

    segment_id: int
    matched_pose_count: int
    timestamp_mismatch_count: int
    accepted: bool
    rejection_reason: str | None
    scale_m_per_unit: float | None
    rmse_m: float | None
    aligned_positions_m: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True, slots=True)
class MetricTrajectoryAlignment:
    """Alignment audit across all scale-free trajectory segments."""

    sidecar_name: str
    sidecar_pose_count: int
    aligned_segment_count: int
    segments: tuple[MetricSegmentAlignment, ...]


def align_trajectory_to_metric_poses(
    video: SampledVideo,
    trajectory: VideoTrajectoryDiagnostics,
    sidecar: MetricPoseSidecar,
    *,
    config: VideoMetricPoseConfig = DEFAULT_VIDEO_METRIC_POSE,
) -> MetricTrajectoryAlignment:
    """Align each local VO segment only through exact frame/time matches."""

    _validate_config(config)
    mapping_valid = len(video.source_frame_indices) == len(video.frames) and len(
        video.timestamps_s
    ) == len(video.frames)
    sidecar_by_frame = {pose.source_frame_index: pose for pose in sidecar.poses}
    results = tuple(
        _align_segment(
            segment,
            video,
            sidecar_by_frame,
            mapping_valid,
            config,
        )
        for segment in trajectory.segments
    )
    return MetricTrajectoryAlignment(
        sidecar_name=sidecar.source.name,
        sidecar_pose_count=len(sidecar.poses),
        aligned_segment_count=sum(result.accepted for result in results),
        segments=results,
    )


def _align_segment(
    segment: TrajectorySegment,
    video: SampledVideo,
    sidecar_by_frame: dict[int, MetricCameraPose],
    mapping_valid: bool,
    config: VideoMetricPoseConfig,
) -> MetricSegmentAlignment:
    if not mapping_valid:
        return _rejected(segment.segment_id, "sample_frame_mapping_unavailable")

    source_points: list[tuple[float, float, float]] = []
    target_points: list[tuple[float, float, float]] = []
    timestamp_mismatches = 0
    for pose in segment.poses:
        source_frame_index = video.source_frame_indices[pose.frame_index]
        metric_pose = sidecar_by_frame.get(source_frame_index)
        if metric_pose is None:
            continue
        timestamp_error = abs(
            metric_pose.timestamp_s - video.timestamps_s[pose.frame_index]
        )
        if timestamp_error > config.timestamp_tolerance_s:
            timestamp_mismatches += 1
            continue
        source_points.append(pose.position_unitless)
        target_points.append(metric_pose.position_m)

    matched = len(source_points)
    if matched < config.minimum_alignment_poses:
        return _rejected(
            segment.segment_id,
            "insufficient_exact_frame_time_matches",
            matched,
            timestamp_mismatches,
        )
    source = np.asarray(source_points, dtype=np.float64)
    target = np.asarray(target_points, dtype=np.float64)
    centered = source - source.mean(axis=0)
    rank = int(np.linalg.matrix_rank(centered))
    if rank < config.minimum_alignment_rank:
        return _rejected(
            segment.segment_id,
            "degenerate_unitless_trajectory",
            matched,
            timestamp_mismatches,
        )

    transform = _similarity_transform(source, target)
    if transform is None:
        return _rejected(
            segment.segment_id,
            "similarity_estimation_failed",
            matched,
            timestamp_mismatches,
        )
    scale, rotation, translation = transform
    predicted = scale * (source @ rotation.T) + translation
    rmse = float(np.sqrt(np.mean(np.sum((predicted - target) ** 2, axis=1))))
    if rmse > config.maximum_alignment_rmse_m:
        return _rejected(
            segment.segment_id,
            "alignment_rmse_too_high",
            matched,
            timestamp_mismatches,
            scale,
            rmse,
        )
    all_positions = np.asarray(
        [pose.position_unitless for pose in segment.poses], dtype=np.float64
    )
    aligned = scale * (all_positions @ rotation.T) + translation
    return MetricSegmentAlignment(
        segment_id=segment.segment_id,
        matched_pose_count=matched,
        timestamp_mismatch_count=timestamp_mismatches,
        accepted=True,
        rejection_reason=None,
        scale_m_per_unit=float(scale),
        rmse_m=rmse,
        aligned_positions_m=tuple(
            tuple(float(value) for value in position) for position in aligned
        ),
    )


def _similarity_transform(
    source: np.ndarray,
    target: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray] | None:
    source_mean = source.mean(axis=0)
    target_mean = target.mean(axis=0)
    source_centered = source - source_mean
    target_centered = target - target_mean
    variance = float(np.mean(np.sum(source_centered**2, axis=1)))
    if variance <= 1e-12:
        return None
    covariance = target_centered.T @ source_centered / len(source)
    left, singular_values, right_transpose = np.linalg.svd(covariance)
    sign = 1.0 if np.linalg.det(left @ right_transpose) >= 0 else -1.0
    correction = np.diag([1.0, 1.0, sign])
    rotation = left @ correction @ right_transpose
    scale = float(np.sum(singular_values * np.diag(correction)) / variance)
    if not np.isfinite(scale) or scale <= 0:
        return None
    translation = target_mean - scale * (rotation @ source_mean)
    return scale, rotation, translation


def _rejected(
    segment_id: int,
    reason: str,
    matched: int = 0,
    timestamp_mismatches: int = 0,
    scale: float | None = None,
    rmse: float | None = None,
) -> MetricSegmentAlignment:
    return MetricSegmentAlignment(
        segment_id=segment_id,
        matched_pose_count=matched,
        timestamp_mismatch_count=timestamp_mismatches,
        accepted=False,
        rejection_reason=reason,
        scale_m_per_unit=scale,
        rmse_m=rmse,
        aligned_positions_m=(),
    )


def _validate_config(config: VideoMetricPoseConfig) -> None:
    if config.timestamp_tolerance_s < 0:
        raise ValueError("metric pose timestamp tolerance must be non-negative")
    if config.quaternion_norm_tolerance < 0:
        raise ValueError("metric pose quaternion tolerance must be non-negative")
    if config.minimum_alignment_poses < 3:
        raise ValueError("metric pose alignment needs at least three poses")
    if config.minimum_alignment_rank not in {1, 2, 3}:
        raise ValueError("metric pose alignment rank must be one, two, or three")
    if config.maximum_alignment_rmse_m <= 0:
        raise ValueError("metric pose alignment RMSE threshold must be positive")
