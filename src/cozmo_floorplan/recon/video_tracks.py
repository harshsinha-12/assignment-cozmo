"""Deterministic, non-metric feature-track diagnostics for room videos."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import median

import cv2
import numpy as np

from cozmo_floorplan.io.video import SampledVideo
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_TRACKING,
    VideoTrackingConfig,
)
from cozmo_floorplan.utils.sampling import evenly_spaced_indices


@dataclass(frozen=True, slots=True)
class FrameFeatures:
    """ORB observations cached once for one normalized sample."""

    keypoints: tuple[cv2.KeyPoint, ...]
    descriptors: np.ndarray | None
    image_size_px: tuple[int, int]


@dataclass(frozen=True, slots=True)
class PairTrackDiagnostics:
    """Geometric evidence and rejection reasons for one adjacent sample pair."""

    left_index: int
    right_index: int
    left_keypoints: int
    right_keypoints: int
    matches: int
    fundamental_inliers: int
    fundamental_inlier_ratio: float
    median_motion_px: float
    median_parallax_px: float
    coverage_fraction: float
    eligible: bool
    rejection_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VideoTrackDiagnostics:
    """Aggregate non-metric tracking health for one room walkthrough."""

    identifier: str
    analyzed_pairs: int
    eligible_pairs: int
    eligible_pair_ratio: float
    median_keypoints: float
    median_matches: float
    median_fundamental_inliers: float
    median_motion_px: float
    median_parallax_px: float
    median_coverage_fraction: float
    rejection_reason_counts: tuple[tuple[str, int], ...]
    accepted_for_relative_vo: bool


def analyze_video_tracks(
    video: SampledVideo,
    *,
    config: VideoTrackingConfig = DEFAULT_VIDEO_TRACKING,
) -> VideoTrackDiagnostics:
    """Measure whether normalized frames support relative, still-unscaled VO."""

    _validate_config(config)
    if len(video.frames) < 2:
        return _empty_diagnostics(video.identifier)
    left_indices = evenly_spaced_indices(
        len(video.frames) - 1,
        min(config.maximum_pair_count, len(video.frames) - 1),
    )
    required_indices = sorted(
        {index for left_index in left_indices for index in (left_index, left_index + 1)}
    )
    features = {
        index: _extract_features(video.frames[index], config)
        for index in required_indices
    }
    pairs = tuple(
        _pair_diagnostics(index, features[index], features[index + 1], config)
        for index in left_indices
    )
    eligible_pairs = sum(pair.eligible for pair in pairs)
    eligible_ratio = eligible_pairs / len(pairs) if pairs else 0.0
    reason_counts = Counter(
        reason for pair in pairs for reason in pair.rejection_reasons
    )
    return VideoTrackDiagnostics(
        identifier=video.identifier,
        analyzed_pairs=len(pairs),
        eligible_pairs=eligible_pairs,
        eligible_pair_ratio=eligible_ratio,
        median_keypoints=median(
            (pair.left_keypoints + pair.right_keypoints) / 2.0 for pair in pairs
        ),
        median_matches=median(pair.matches for pair in pairs),
        median_fundamental_inliers=median(pair.fundamental_inliers for pair in pairs),
        median_motion_px=median(pair.median_motion_px for pair in pairs),
        median_parallax_px=median(pair.median_parallax_px for pair in pairs),
        median_coverage_fraction=median(pair.coverage_fraction for pair in pairs),
        rejection_reason_counts=tuple(
            sorted(reason_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        accepted_for_relative_vo=eligible_ratio >= config.minimum_eligible_pair_ratio,
    )


def _extract_features(
    frame_rgb: np.ndarray, config: VideoTrackingConfig
) -> FrameFeatures:
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape
    largest = max(height, width)
    if largest > config.resize_max_dimension_px:
        scale = config.resize_max_dimension_px / largest
        width = max(1, round(width * scale))
        height = max(1, round(height * scale))
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_AREA)
    detector = cv2.ORB_create(
        nfeatures=config.orb_feature_count,
        fastThreshold=config.orb_fast_threshold,
    )
    keypoints, descriptors = detector.detectAndCompute(gray, None)
    return FrameFeatures(tuple(keypoints), descriptors, (width, height))


def _pair_diagnostics(
    index: int,
    left: FrameFeatures,
    right: FrameFeatures,
    config: VideoTrackingConfig,
) -> PairTrackDiagnostics:
    matches = _ratio_matches(left.descriptors, right.descriptors, config.ratio_test)
    if matches:
        left_points = np.float32([left.keypoints[item.queryIdx].pt for item in matches])
        right_points = np.float32(
            [right.keypoints[item.trainIdx].pt for item in matches]
        )
    else:
        left_points = np.empty((0, 2), dtype=np.float32)
        right_points = np.empty((0, 2), dtype=np.float32)
    inlier_mask = _fundamental_inliers(left_points, right_points, config)
    inlier_count = int(np.count_nonzero(inlier_mask))
    inlier_ratio = inlier_count / len(matches) if matches else 0.0
    diagonal = max(1.0, float(np.hypot(*left.image_size_px)))
    motion = _median_distance(left_points, right_points)
    parallax = _homography_residual(
        left_points[inlier_mask], right_points[inlier_mask], config
    )
    coverage = _track_coverage(
        left_points[inlier_mask], right_points[inlier_mask], left.image_size_px
    )
    reasons = _rejection_reasons(
        len(left.keypoints),
        len(right.keypoints),
        len(matches),
        inlier_count,
        inlier_ratio,
        motion / diagonal,
        parallax / diagonal,
        coverage,
        config,
    )
    return PairTrackDiagnostics(
        left_index=index,
        right_index=index + 1,
        left_keypoints=len(left.keypoints),
        right_keypoints=len(right.keypoints),
        matches=len(matches),
        fundamental_inliers=inlier_count,
        fundamental_inlier_ratio=inlier_ratio,
        median_motion_px=motion,
        median_parallax_px=parallax,
        coverage_fraction=coverage,
        eligible=not reasons,
        rejection_reasons=reasons,
    )


def _ratio_matches(
    left: np.ndarray | None,
    right: np.ndarray | None,
    ratio: float,
) -> tuple[cv2.DMatch, ...]:
    if left is None or right is None or len(left) < 2 or len(right) < 2:
        return ()
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    candidates = matcher.knnMatch(left, right, k=2)
    accepted = [
        first
        for pair in candidates
        if len(pair) == 2
        for first, second in [pair]
        if first.distance < ratio * second.distance
    ]
    return tuple(sorted(accepted, key=lambda item: (item.queryIdx, item.trainIdx)))


def _fundamental_inliers(
    left: np.ndarray,
    right: np.ndarray,
    config: VideoTrackingConfig,
) -> np.ndarray:
    if len(left) < 8:
        return np.zeros(len(left), dtype=bool)
    cv2.setRNGSeed(0)
    _fundamental, mask = cv2.findFundamentalMat(
        left,
        right,
        cv2.FM_RANSAC,
        config.ransac_reprojection_threshold_px,
        0.99,
    )
    return (
        mask.ravel().astype(bool)
        if mask is not None
        else np.zeros(len(left), dtype=bool)
    )


def _homography_residual(
    left: np.ndarray,
    right: np.ndarray,
    config: VideoTrackingConfig,
) -> float:
    if len(left) < 4:
        return 0.0
    cv2.setRNGSeed(0)
    homography, _mask = cv2.findHomography(
        left,
        right,
        cv2.RANSAC,
        config.ransac_reprojection_threshold_px,
    )
    if homography is None:
        return _median_distance(left, right)
    projected = cv2.perspectiveTransform(left.reshape(-1, 1, 2), homography).reshape(
        -1, 2
    )
    return _median_distance(projected, right)


def _median_distance(left: np.ndarray, right: np.ndarray) -> float:
    if len(left) == 0:
        return 0.0
    return float(np.median(np.linalg.norm(right - left, axis=1)))


def _track_coverage(
    left: np.ndarray,
    right: np.ndarray,
    image_size_px: tuple[int, int],
) -> float:
    if len(left) < 3:
        return 0.0
    image_area = float(image_size_px[0] * image_size_px[1])
    left_area = float(cv2.contourArea(cv2.convexHull(left)))
    right_area = float(cv2.contourArea(cv2.convexHull(right)))
    return min(left_area, right_area) / image_area if image_area > 0 else 0.0


def _rejection_reasons(
    left_keypoints: int,
    right_keypoints: int,
    matches: int,
    inliers: int,
    inlier_ratio: float,
    motion_fraction: float,
    parallax_fraction: float,
    coverage_fraction: float,
    config: VideoTrackingConfig,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if min(left_keypoints, right_keypoints) < config.minimum_keypoints_per_frame:
        reasons.append("low_keypoint_yield")
    if matches < config.minimum_matches:
        reasons.append("too_few_matches")
    if inliers < config.minimum_fundamental_inliers:
        reasons.append("too_few_geometric_inliers")
    if inlier_ratio < config.minimum_fundamental_inlier_ratio:
        reasons.append("low_inlier_ratio")
    if motion_fraction < config.minimum_motion_fraction:
        reasons.append("insufficient_image_motion")
    if parallax_fraction < config.minimum_parallax_fraction:
        reasons.append("homography_dominant_or_low_parallax")
    if coverage_fraction < config.minimum_coverage_fraction:
        reasons.append("poor_frame_coverage")
    return tuple(reasons)


def _empty_diagnostics(identifier: str) -> VideoTrackDiagnostics:
    return VideoTrackDiagnostics(
        identifier=identifier,
        analyzed_pairs=0,
        eligible_pairs=0,
        eligible_pair_ratio=0.0,
        median_keypoints=0.0,
        median_matches=0.0,
        median_fundamental_inliers=0.0,
        median_motion_px=0.0,
        median_parallax_px=0.0,
        median_coverage_fraction=0.0,
        rejection_reason_counts=(("too_few_frames", 1),),
        accepted_for_relative_vo=False,
    )


def _validate_config(config: VideoTrackingConfig) -> None:
    if config.maximum_pair_count <= 0 or config.resize_max_dimension_px <= 0:
        raise ValueError("video tracking pair and image bounds must be positive")
    if config.orb_feature_count <= 0 or config.orb_fast_threshold < 0:
        raise ValueError("video ORB settings are invalid")
    fractions = (
        config.ratio_test,
        config.minimum_fundamental_inlier_ratio,
        config.minimum_motion_fraction,
        config.minimum_parallax_fraction,
        config.minimum_coverage_fraction,
        config.minimum_eligible_pair_ratio,
    )
    if any(not 0 < value <= 1 for value in fractions):
        raise ValueError("video tracking ratios must be in (0, 1]")
