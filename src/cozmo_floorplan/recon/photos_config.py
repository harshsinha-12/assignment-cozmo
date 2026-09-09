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
    """Bounded ORB and geometric graph policy for unordered room photos."""

    resize_max_dimension_px: int = 900
    orb_feature_count: int = 1800
    orb_fast_threshold: int = 10
    ratio_test: float = 0.78
    ransac_reprojection_threshold_px: float = 2.0
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
