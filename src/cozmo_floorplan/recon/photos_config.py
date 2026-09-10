"""Immutable limits for photo-folder ingest."""

from dataclasses import dataclass


PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


@dataclass(frozen=True, slots=True)
class PhotoIngestConfig:
    min_photos_per_room: int = 2
    max_photos_per_room: int = 8
    min_edge_px: int = 64


DEFAULT_PHOTO_INGEST = PhotoIngestConfig()


@dataclass(frozen=True, slots=True)
class PhotoOverlapConfig:
    """Bounded feature-ensemble and geometric graph policy for room photos."""

    resize_max_dimension_px: int = 900
    orb_feature_count: int = 1800
    orb_fast_threshold: int = 10
    ratio_test: float = 0.78
    ransac_reprojection_threshold_px: float = 2.0
    enable_sift_fallback: bool = True
    sift_resize_max_dimension_px: int = 1200
    sift_feature_count: int = 3000
    sift_contrast_threshold: float = 0.02
    sift_edge_threshold: float = 12.0
    sift_ratio_test: float = 0.76
    sift_ransac_reprojection_threshold_px: float = 2.5
    minimum_keypoints_per_image: int = 100
    minimum_within_matches: int = 18
    minimum_within_inliers: int = 12
    minimum_within_inlier_ratio: float = 0.30
    minimum_within_coverage_fraction: float = 0.02
    minimum_cross_matches: int = 28
    minimum_cross_inliers: int = 18
    minimum_cross_inlier_ratio: float = 0.40
    minimum_cross_coverage_fraction: float = 0.03


DEFAULT_PHOTO_OVERLAP = PhotoOverlapConfig()


@dataclass(frozen=True, slots=True)
class PhotoSfmConfig:
    """Assumed-intrinsics incremental SfM and handheld-height scale."""

    assumed_focal_length_fraction: float = 0.9
    minimum_pose_inliers: int = 12
    minimum_cheirality_ratio: float = 0.55
    minimum_triangulation_angle_degrees: float = 1.5
    maximum_reprojection_error_px: float = 3.0
    minimum_depth_m: float = 0.3
    maximum_depth_m: float = 20.0
    voxel_size_m: float = 0.05
    handheld_camera_height_m: float = 1.45
    minimum_floor_points: int = 8
    floor_bin_m: float = 0.08
    camera_floor_clearance_m: float = 0.20
    pnp_reprojection_error_px: float = 4.0
    minimum_pnp_inliers: int = 8


DEFAULT_PHOTO_SFM = PhotoSfmConfig()


@dataclass(frozen=True, slots=True)
class PhotoOutputConfig:
    """Wide uncalibrated intervals for photo-tier centimetres."""

    confidence: float = 0.50
    minimum_length_half_width_cm: float = 25.0
    length_relative_half_width: float = 0.18
    minimum_ceiling_half_width_cm: float = 20.0
    area_relative_half_width: float = 0.30
    opening_confidence: float = 0.40
    opening_width_half_width_cm: float = 20.0
    opening_height_half_width_cm: float = 30.0
    method: str = "photo_sfm_handheld_height_uncalibrated_interval"


DEFAULT_PHOTO_OUTPUT = PhotoOutputConfig()
