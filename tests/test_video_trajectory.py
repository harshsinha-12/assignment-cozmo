from pathlib import Path

import numpy as np

import cozmo_floorplan.recon.video_trajectory as trajectory_module
from cozmo_floorplan.io.video import SampledVideo, VideoMetadata
from cozmo_floorplan.recon.video_config import VideoTrajectoryConfig
from cozmo_floorplan.recon.video_features import FrameFeatures, PairCorrespondences
from cozmo_floorplan.recon.video_tracks import PairTrackDiagnostics
from cozmo_floorplan.recon.video_trajectory import (
    RelativePoseEstimate,
    recover_relative_pose_from_points,
    recover_scale_free_trajectory,
)


def _project(points: np.ndarray, intrinsic: np.ndarray) -> np.ndarray:
    pixels = (intrinsic @ points.T).T
    return pixels[:, :2] / pixels[:, 2, None]


def _blank_video(frame_count: int) -> SampledVideo:
    frames = tuple(np.zeros((240, 320, 3), dtype=np.uint8) for _ in range(frame_count))
    return SampledVideo(
        identifier="trajectory-fixture",
        metadata=VideoMetadata(
            source=Path("trajectory-fixture.mp4"),
            native_size_px=(320, 240),
            display_size_px=(320, 240),
            native_fps=2.0,
            frame_count=frame_count,
            duration_s=frame_count / 2.0,
            rotation_degrees_clockwise=0,
        ),
        frames=frames,
    )


def test_two_view_pose_recovers_rotation_and_translation_direction():
    rng = np.random.default_rng(23)
    points = np.column_stack(
        (
            rng.uniform(-1.8, 1.8, 80),
            rng.uniform(-1.2, 1.2, 80),
            rng.uniform(4.0, 9.0, 80),
        )
    )
    angle = np.deg2rad(4.0)
    rotation = np.array(
        [
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)],
        ]
    )
    translation = np.array([0.35, 0.02, 0.08])
    intrinsic = np.array([[576.0, 0.0, 320.0], [0.0, 576.0, 240.0], [0, 0, 1]])
    left = _project(points, intrinsic)
    right = _project((rotation @ points.T).T + translation, intrinsic)

    estimate = recover_relative_pose_from_points(
        left,
        right,
        (640, 480),
        config=VideoTrajectoryConfig(
            minimum_pose_inliers=8,
            minimum_cheirality_ratio=0.5,
        ),
    )

    assert estimate is not None
    assert estimate.pose_inliers >= 8
    assert np.trace(estimate.rotation_left_to_right @ rotation.T) > 2.95
    expected_direction = translation / np.linalg.norm(translation)
    assert (
        np.dot(estimate.translation_direction_left_to_right, expected_direction) > 0.95
    )


def test_failed_feature_edge_breaks_and_restarts_trajectory(monkeypatch):
    def fake_extract(_frame, _config):
        marker = fake_extract.index
        fake_extract.index += 1
        return FrameFeatures((), np.array([[marker]], dtype=np.uint8), (320, 240))

    fake_extract.index = 0

    def fake_match(left, _right, _config):
        marker = int(left.descriptors[0, 0])
        points = np.full((12, 2), marker, dtype=np.float32)
        return PairCorrespondences(points, points, np.eye(3), np.ones(12, dtype=bool))

    def fake_track(index, _left, _right, _config, _correspondences):
        eligible = index != 1
        return PairTrackDiagnostics(
            index,
            index + 1,
            100,
            100,
            40,
            30,
            0.75,
            8.0,
            2.0,
            0.2,
            eligible,
            () if eligible else ("poor_frame_coverage",),
        )

    estimate = RelativePoseEstimate(
        rotation_left_to_right=np.eye(3),
        translation_direction_left_to_right=np.array([1.0, 0.0, 0.0]),
        pose_inliers=24,
        cheirality_ratio=0.9,
    )

    monkeypatch.setattr(trajectory_module, "extract_frame_features", fake_extract)
    monkeypatch.setattr(trajectory_module, "match_frame_features", fake_match)
    monkeypatch.setattr(trajectory_module, "analyze_feature_pair", fake_track)
    monkeypatch.setattr(
        trajectory_module,
        "_recover_relative_pose",
        lambda *_args: (estimate, ()),
    )

    result = recover_scale_free_trajectory(
        _blank_video(5),
        trajectory_config=VideoTrajectoryConfig(maximum_frame_count=5, maximum_edge_span=1),
    )

    assert result.accepted_edges == 3
    assert result.segment_breaks == 1
    assert result.segment_restarts == 1
    assert [
        tuple(pose.frame_index for pose in segment.poses) for segment in result.segments
    ] == [
        (0, 1),
        (2, 3, 4),
    ]
    assert result.segments[0].poses[1].position_unitless == (-1.0, 0.0, 0.0)
    assert result.intrinsics_source == "image_size_focal_prior_unvalidated"


def test_skip_span_pose_uses_real_pair_instead_of_interpolating(monkeypatch):
    def fake_extract(_frame, _config):
        marker = fake_extract.index
        fake_extract.index += 1
        return FrameFeatures((), np.array([[marker]], dtype=np.uint8), (320, 240))

    fake_extract.index = 0

    def fake_match(left, _right, _config):
        marker = int(left.descriptors[0, 0])
        points = np.full((12, 2), marker, dtype=np.float32)
        return PairCorrespondences(points, points, np.eye(3), np.ones(12, dtype=bool))

    def fake_track(_index, left, right, _config, _correspondences):
        left_marker = int(left.descriptors[0, 0])
        right_marker = int(right.descriptors[0, 0])
        eligible = not (left_marker == 1 and right_marker == 2)
        return PairTrackDiagnostics(
            left_marker,
            right_marker,
            100,
            100,
            40,
            30,
            0.75,
            8.0,
            2.0,
            0.2,
            eligible,
            () if eligible else ("poor_frame_coverage",),
        )

    estimate = RelativePoseEstimate(
        rotation_left_to_right=np.eye(3),
        translation_direction_left_to_right=np.array([1.0, 0.0, 0.0]),
        pose_inliers=24,
        cheirality_ratio=0.9,
    )

    monkeypatch.setattr(trajectory_module, "extract_frame_features", fake_extract)
    monkeypatch.setattr(trajectory_module, "match_frame_features", fake_match)
    monkeypatch.setattr(trajectory_module, "analyze_feature_pair", fake_track)
    monkeypatch.setattr(
        trajectory_module,
        "_recover_relative_pose",
        lambda *_args: (estimate, ()),
    )

    result = recover_scale_free_trajectory(
        _blank_video(5),
        trajectory_config=VideoTrajectoryConfig(maximum_frame_count=5, maximum_edge_span=2),
    )

    assert [(edge.left_index, edge.right_index, edge.accepted) for edge in result.edges] == [
        (0, 1, True),
        (1, 2, False),
        (1, 3, True),
        (3, 4, True),
    ]
    assert result.segment_breaks == 0
    assert [tuple(pose.frame_index for pose in segment.poses) for segment in result.segments] == [
        (0, 1, 3, 4)
    ]
    assert result.segments[0].poses[2].position_unitless == (-3.0, 0.0, 0.0)


def test_single_frame_returns_no_metric_or_pose_claim():
    result = recover_scale_free_trajectory(_blank_video(1))

    assert result.attempted_edges == 0
    assert result.segments == ()
    assert result.assumed_focal_length_px == 0.0
