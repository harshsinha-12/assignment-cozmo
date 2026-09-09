"""Reusable deterministic feature evidence for unordered room photos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from cozmo_floorplan.recon.photo_image import load_resized_gray
from cozmo_floorplan.recon.photos_config import PhotoOverlapConfig


@dataclass(frozen=True, slots=True)
class PhotoFeatures:
    """Bounded ORB observations for one decoded photo."""

    path: Path
    keypoints: tuple[cv2.KeyPoint, ...]
    descriptors: np.ndarray | None
    image_size_px: tuple[int, int]
    method: str = "orb"
    norm_type: int = cv2.NORM_HAMMING


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

    gray = load_resized_gray(path, config.resize_max_dimension_px)
    height, width = gray.shape
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

    if left.method != right.method or left.norm_type != right.norm_type:
        raise ValueError("photo feature methods must match")
    ratio_test = (
        config.sift_ratio_test if left.method == "sift_clahe" else config.ratio_test
    )
    matches = _mutual_ratio_matches(
        left.descriptors,
        right.descriptors,
        ratio_test,
        left.norm_type,
    )
    if not matches:
        return PhotoMatchEvidence(0, 0, 0, 0, "none", 0.0, 0.0)
    left_points = np.float32([left.keypoints[item[0]].pt for item in matches])
    right_points = np.float32([right.keypoints[item[1]].pt for item in matches])
    threshold = (
        config.sift_ransac_reprojection_threshold_px
        if left.method == "sift_clahe"
        else config.ransac_reprojection_threshold_px
    )
    homography_mask = _homography_inliers(left_points, right_points, threshold)
    fundamental_mask = _fundamental_inliers(left_points, right_points, threshold)
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
    norm_type: int,
) -> tuple[tuple[int, int], ...]:
    if left is None or right is None or len(left) < 2 or len(right) < 2:
        return ()
    matcher = cv2.BFMatcher(norm_type)
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
    threshold_px: float,
) -> np.ndarray:
    if len(left) < 4:
        return np.zeros(len(left), dtype=bool)
    cv2.setRNGSeed(0)
    _homography, mask = cv2.findHomography(
        left,
        right,
        cv2.RANSAC,
        threshold_px,
    )
    return mask.ravel().astype(bool) if mask is not None else np.zeros(len(left), bool)


def _fundamental_inliers(
    left: np.ndarray,
    right: np.ndarray,
    threshold_px: float,
) -> np.ndarray:
    if len(left) < 8:
        return np.zeros(len(left), dtype=bool)
    cv2.setRNGSeed(0)
    fundamental, mask = cv2.findFundamentalMat(
        left,
        right,
        cv2.FM_RANSAC,
        threshold_px,
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
