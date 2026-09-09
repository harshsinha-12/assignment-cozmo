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
    maximum_edge_span: int = 2


DEFAULT_VIDEO_TRAJECTORY = VideoTrajectoryConfig()


@dataclass(frozen=True, slots=True)
class VideoMetricPoseConfig:
    """Validation and similarity-alignment policy for metric pose sidecars."""

    timestamp_tolerance_s: float = 0.025
    quaternion_norm_tolerance: float = 0.01
    minimum_alignment_poses: int = 3
    minimum_alignment_rank: int = 2
    maximum_alignment_rmse_m: float = 0.15


DEFAULT_VIDEO_METRIC_POSE = VideoMetricPoseConfig()


@dataclass(frozen=True, slots=True)
class VideoTriangulationConfig:
    """Geometric acceptance policy for calibrated metric video points."""

    timestamp_tolerance_s: float = 0.025
    minimum_pair_inliers: int = 12
    maximum_reprojection_error_px: float = 2.0
    minimum_triangulation_angle_degrees: float = 1.5
    minimum_depth_m: float = 0.10
    maximum_depth_m: float = 20.0
    voxel_size_m: float = 0.03


DEFAULT_VIDEO_TRIANGULATION = VideoTriangulationConfig()


@dataclass(frozen=True, slots=True)
class VideoSurfaceConfig:
    """Support thresholds for sparse axis-aligned plane diagnostics."""

    coordinate_bin_m: float = 0.08
    minimum_support_points: int = 8
    minimum_support_fraction: float = 0.04
    maximum_candidates_per_axis: int = 4
    minimum_candidate_separation_m: float = 0.35


DEFAULT_VIDEO_SURFACES = VideoSurfaceConfig()


@dataclass(frozen=True, slots=True)
class VideoRoomConfig:
    """Conservative room-envelope qualification from sparse metric points."""

    yaw_step_degrees: float = 1.0
    camera_bracket_quantile: float = 0.10
    camera_wall_margin_m: float = 0.05
    camera_level_clearance_m: float = 0.45
    minimum_room_span_m: float = 1.5
    maximum_room_span_m: float = 12.0
    minimum_ceiling_height_m: float = 2.0
    maximum_ceiling_height_m: float = 4.5


DEFAULT_VIDEO_ROOM = VideoRoomConfig()


@dataclass(frozen=True, slots=True)
class VideoOutputConfig:
    """Uncalibrated interval policy for accepted video room candidates."""

    confidence: float = 0.70
    minimum_length_half_width_cm: float = 8.0
    length_relative_half_width: float = 0.05
    minimum_ceiling_half_width_cm: float = 6.0
    area_relative_half_width: float = 0.12
    opening_confidence: float = 0.55
    opening_width_half_width_cm: float = 12.0
    opening_height_half_width_cm: float = 18.0
    method: str = "calibrated_video_sparse_manhattan_uncalibrated_interval"


DEFAULT_VIDEO_OUTPUT = VideoOutputConfig()
HANDHELD_VIDEO_OUTPUT = VideoOutputConfig(
    confidence=0.55,
    minimum_length_half_width_cm=25.0,
    length_relative_half_width=0.22,
    minimum_ceiling_half_width_cm=20.0,
    area_relative_half_width=0.35,
    opening_confidence=0.40,
    opening_width_half_width_cm=20.0,
    opening_height_half_width_cm=30.0,
    method="handheld_height_prior_uncalibrated_interval",
)


@dataclass(frozen=True, slots=True)
class VideoNativeScaleConfig:
    """Disclosed upright-phone camera-height prior for native Camera video."""

    handheld_camera_height_m: float = 1.45
    minimum_floor_points: int = 8
    floor_bin_m: float = 0.08
    camera_floor_clearance_m: float = 0.20
    world_frame_prefix: str = "native-video-assumed-up"


DEFAULT_VIDEO_NATIVE_SCALE = VideoNativeScaleConfig()
