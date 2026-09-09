"""Immutable settings for video ingest. Reconstruction stays metric-honest."""

from dataclasses import dataclass


VIDEO_EXTENSIONS = (".mp4", ".mov", ".m4v", ".avi")
POSE_SIDECAR_NAMES = ("poses.json", "arkit_poses.json", "cameras.json")
POSE_SIDECAR_SUFFIXES = (".poses.json", ".arkit_poses.json", ".cameras.json")


@dataclass(frozen=True, slots=True)
class VideoIngestConfig:
    sample_fps: float = 2.0
    max_frames: int = 240
    min_frames: int = 8
    rotation_tolerance_degrees: float = 1.0


DEFAULT_VIDEO_INGEST = VideoIngestConfig()


@dataclass(frozen=True, slots=True)
class VideoTrackingConfig:
    """Bounded ORB and geometric-consistency policy for video diagnostics."""

    maximum_pair_count: int = 60
    resize_max_dimension_px: int = 640
    orb_feature_count: int = 1200
    orb_fast_threshold: int = 12
    ratio_test: float = 0.75
    minimum_keypoints_per_frame: int = 80
    minimum_matches: int = 24
    minimum_fundamental_inliers: int = 16
    minimum_fundamental_inlier_ratio: float = 0.35
    ransac_reprojection_threshold_px: float = 1.5
    minimum_motion_fraction: float = 0.004
    minimum_parallax_fraction: float = 0.0015
    minimum_coverage_fraction: float = 0.08
    minimum_eligible_pair_ratio: float = 0.35


DEFAULT_VIDEO_TRACKING = VideoTrackingConfig()


@dataclass(frozen=True, slots=True)
class VideoTrajectoryConfig:
    """Policy for scale-free relative-pose recovery and segment retention."""

    maximum_frame_count: int = 90
    assumed_focal_length_fraction: float = 0.9
    minimum_pose_inliers: int = 12
    minimum_cheirality_ratio: float = 0.6
    minimum_segment_pose_count: int = 2


DEFAULT_VIDEO_TRAJECTORY = VideoTrajectoryConfig()
