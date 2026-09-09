from pathlib import Path

import cv2
import numpy as np

from cozmo_floorplan.io.video import SampledVideo, VideoMetadata
from cozmo_floorplan.recon.video_tracks import analyze_video_tracks


def _sampled_video(identifier: str, frames: list[np.ndarray]) -> SampledVideo:
    height, width = frames[0].shape[:2]
    return SampledVideo(
        identifier=identifier,
        metadata=VideoMetadata(
            source=Path(f"{identifier}.mp4"),
            native_size_px=(width, height),
            display_size_px=(width, height),
            native_fps=2.0,
            frame_count=len(frames),
            duration_s=len(frames) / 2.0,
            rotation_degrees_clockwise=0,
        ),
        frames=tuple(frames),
    )


def _two_depth_motion_frames() -> list[np.ndarray]:
    rng = np.random.default_rng(7)
    base = rng.integers(0, 256, (360, 480), dtype=np.uint8)
    base = cv2.GaussianBlur(base, (3, 3), 0)
    frames: list[np.ndarray] = []
    for index in range(8):
        left = np.roll(base[:, :240], index * 2, axis=1)
        right = np.roll(base[:, 240:], index * 7, axis=1)
        gray = np.column_stack((left, right))
        frames.append(cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB))
    return frames


def _homography_only_frames() -> list[np.ndarray]:
    rng = np.random.default_rng(11)
    base = rng.integers(0, 256, (360, 480), dtype=np.uint8)
    base = cv2.GaussianBlur(base, (3, 3), 0)
    frames: list[np.ndarray] = []
    for index in range(8):
        transform = cv2.getRotationMatrix2D((240, 180), index * 0.8, 1.0)
        transformed = cv2.warpAffine(base, transform, (480, 360))
        frames.append(cv2.cvtColor(transformed, cv2.COLOR_GRAY2RGB))
    return frames


def test_two_depth_motion_has_eligible_relative_vo_pairs():
    diagnostics = analyze_video_tracks(
        _sampled_video("parallax", _two_depth_motion_frames())
    )

    assert diagnostics.accepted_for_relative_vo is True
    assert diagnostics.eligible_pairs > 0
    assert diagnostics.median_matches >= 24
    assert diagnostics.median_fundamental_inliers >= 16
    assert diagnostics.median_parallax_px > 0
    assert diagnostics.median_coverage_fraction >= 0.08


def test_homography_only_motion_is_rejected_as_low_parallax():
    diagnostics = analyze_video_tracks(
        _sampled_video("rotation", _homography_only_frames())
    )

    assert diagnostics.accepted_for_relative_vo is False
    assert diagnostics.median_motion_px > 0
    assert diagnostics.median_parallax_px < 1.0
    assert (
        dict(diagnostics.rejection_reason_counts)["homography_dominant_or_low_parallax"]
        > 0
    )


def test_featureless_frames_are_rejected_without_crashing():
    blank = np.zeros((240, 320, 3), dtype=np.uint8)

    diagnostics = analyze_video_tracks(
        _sampled_video("blank", [blank.copy() for _ in range(4)])
    )

    assert diagnostics.accepted_for_relative_vo is False
    assert diagnostics.eligible_pairs == 0
    assert diagnostics.median_keypoints == 0
    assert diagnostics.median_matches == 0
    assert dict(diagnostics.rejection_reason_counts)["low_keypoint_yield"] == 3
