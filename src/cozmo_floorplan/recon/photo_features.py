"""Reusable deterministic feature evidence for unordered room photos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from cozmo_floorplan.recon.photos_config import PhotoOverlapConfig


@dataclass(frozen=True, slots=True)
class PhotoFeatures:
    """Bounded ORB observations for one decoded photo."""

    path: Path
    keypoints: tuple[cv2.KeyPoint, ...]
    descriptors: np.ndarray | None
    image_size_px: tuple[int, int]


@dataclass(frozen=True, slots=True)
class PhotoMatchEvidence:
    """Mutual ratio matches and robust two-view geometric support."""

    matches: int
    homography_inliers: int
    fundamental_inliers: int
    geometric_inliers: int
    geometric_model: str
    geometric_inlier_ratio: float
    coverage_fraction: float


def extract_photo_features(path: Path, config: PhotoOverlapConfig) -> PhotoFeatures:
    """Decode, resize, and describe a photo using bounded ORB features."""

    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise ValueError(f"Could not decode photo for feature extraction: {path}")
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
    return PhotoFeatures(path, tuple(keypoints), descriptors, (width, height))


def match_photo_features(
    left: PhotoFeatures,
    right: PhotoFeatures,
    config: PhotoOverlapConfig,
) -> PhotoMatchEvidence:
    """Measure mutual descriptor and homography/fundamental support."""

    matches = _mutual_ratio_matches(
        left.descriptors,
        right.descriptors,
        config.ratio_test,
    )
    if not matches:
        return PhotoMatchEvidence(0, 0, 0, 0, "none", 0.0, 0.0)
    left_points = np.float32([left.keypoints[item[0]].pt for item in matches])
    right_points = np.float32([right.keypoints[item[1]].pt for item in matches])
    homography_mask = _homography_inliers(left_points, right_points, config)
    fundamental_mask = _fundamental_inliers(left_points, right_points, config)
    homography_count = int(np.count_nonzero(homography_mask))
    fundamental_count = int(np.count_nonzero(fundamental_mask))
    if homography_count >= fundamental_count:
        model = "homography"
        geometric_mask = homography_mask
    else:
        model = "fundamental"
        geometric_mask = fundamental_mask
    geometric_count = int(np.count_nonzero(geometric_mask))
    coverage = _coverage(
        left_points[geometric_mask],
        right_points[geometric_mask],
        left.image_size_px,
        right.image_size_px,
    )
    return PhotoMatchEvidence(
        matches=len(matches),
        homography_inliers=homography_count,
        fundamental_inliers=fundamental_count,
        geometric_inliers=geometric_count,
        geometric_model=model,
        geometric_inlier_ratio=geometric_count / len(matches),
        coverage_fraction=coverage,
    )


def _mutual_ratio_matches(
    left: np.ndarray | None,
    right: np.ndarray | None,
    ratio: float,
) -> tuple[tuple[int, int], ...]:
    if left is None or right is None or len(left) < 2 or len(right) < 2:
        return ()
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    forward = _ratio_map(matcher.knnMatch(left, right, k=2), ratio)
    reverse = _ratio_map(matcher.knnMatch(right, left, k=2), ratio)
    return tuple(
        sorted(
            (left_index, right_index)
            for left_index, right_index in forward.items()
            if reverse.get(right_index) == left_index
        )
    )


def _ratio_map(candidates: tuple | list, ratio: float) -> dict[int, int]:
    return {
        first.queryIdx: first.trainIdx
        for pair in candidates
        if len(pair) == 2
        for first, second in [pair]
        if first.distance < ratio * second.distance
    }


def _homography_inliers(
    left: np.ndarray,
    right: np.ndarray,
    config: PhotoOverlapConfig,
) -> np.ndarray:
    if len(left) < 4:
        return np.zeros(len(left), dtype=bool)
    cv2.setRNGSeed(0)
    _homography, mask = cv2.findHomography(
        left,
        right,
        cv2.RANSAC,
        config.ransac_reprojection_threshold_px,
    )
    return mask.ravel().astype(bool) if mask is not None else np.zeros(len(left), bool)


def _fundamental_inliers(
    left: np.ndarray,
    right: np.ndarray,
    config: PhotoOverlapConfig,
) -> np.ndarray:
    if len(left) < 8:
        return np.zeros(len(left), dtype=bool)
    cv2.setRNGSeed(0)
    fundamental, mask = cv2.findFundamentalMat(
        left,
        right,
        cv2.FM_RANSAC,
        config.ransac_reprojection_threshold_px,
        0.99,
    )
    if fundamental is None or fundamental.shape != (3, 3) or mask is None:
        return np.zeros(len(left), dtype=bool)
    return mask.ravel().astype(bool)


def _coverage(
    left: np.ndarray,
    right: np.ndarray,
    left_size: tuple[int, int],
    right_size: tuple[int, int],
) -> float:
    if len(left) < 3:
        return 0.0
    left_area = float(cv2.contourArea(cv2.convexHull(left)))
    right_area = float(cv2.contourArea(cv2.convexHull(right)))
    left_fraction = left_area / float(left_size[0] * left_size[1])
    right_fraction = right_area / float(right_size[0] * right_size[1])
    return min(left_fraction, right_fraction)
