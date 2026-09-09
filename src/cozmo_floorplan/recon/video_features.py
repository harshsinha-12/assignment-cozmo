"""Reusable ORB observations and robust two-frame correspondences."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from cozmo_floorplan.recon.video_config import VideoTrackingConfig


@dataclass(frozen=True, slots=True)
class FrameFeatures:
    """ORB observations cached once for one normalized video sample."""

    keypoints: tuple[cv2.KeyPoint, ...]
    descriptors: np.ndarray | None
    image_size_px: tuple[int, int]


@dataclass(frozen=True, slots=True)
class PairCorrespondences:
    """Ratio-tested matches plus the robust fundamental-matrix support set."""

    left_points_px: np.ndarray
    right_points_px: np.ndarray
    fundamental_matrix: np.ndarray | None
    fundamental_inliers: np.ndarray

    @property
    def match_count(self) -> int:
        return len(self.left_points_px)


def extract_frame_features(
    frame_rgb: np.ndarray,
    config: VideoTrackingConfig,
) -> FrameFeatures:
    """Resize one RGB frame deterministically and extract bounded ORB features."""

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


def match_frame_features(
    left: FrameFeatures,
    right: FrameFeatures,
    config: VideoTrackingConfig,
) -> PairCorrespondences:
    """Match two feature sets and estimate a seeded robust fundamental matrix."""

    matches = _ratio_matches(left.descriptors, right.descriptors, config.ratio_test)
    if matches:
        left_points = np.float32([left.keypoints[item.queryIdx].pt for item in matches])
        right_points = np.float32(
            [right.keypoints[item.trainIdx].pt for item in matches]
        )
    else:
        left_points = np.empty((0, 2), dtype=np.float32)
        right_points = np.empty((0, 2), dtype=np.float32)
    fundamental, inliers = _fundamental_inliers(left_points, right_points, config)
    return PairCorrespondences(left_points, right_points, fundamental, inliers)


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
) -> tuple[np.ndarray | None, np.ndarray]:
    if len(left) < 8:
        return None, np.zeros(len(left), dtype=bool)
    cv2.setRNGSeed(0)
    fundamental, mask = cv2.findFundamentalMat(
        left,
        right,
        cv2.FM_RANSAC,
        config.ransac_reprojection_threshold_px,
        0.99,
    )
    inliers = (
        mask.ravel().astype(bool)
        if mask is not None
        else np.zeros(len(left), dtype=bool)
    )
    if fundamental is None or fundamental.shape != (3, 3):
        return None, np.zeros(len(left), dtype=bool)
    return fundamental, inliers
