from pathlib import Path

import numpy as np
import pytest

import cozmo_floorplan.recon.video_triangulation as triangulation_module
from cozmo_floorplan.io.video import SampledVideo, VideoMetadata
from cozmo_floorplan.io.video_poses import (
    MetricCameraIntrinsics,
    MetricCameraPose,
    MetricPoseSidecar,
)
from cozmo_floorplan.recon.video_config import (
    VideoSurfaceConfig,
    VideoTriangulationConfig,
)
from cozmo_floorplan.recon.video_surfaces import diagnose_video_planes
from cozmo_floorplan.recon.video_features import FrameFeatures, PairCorrespondences
from cozmo_floorplan.recon.video_pose_alignment import (
    MetricSegmentAlignment,
    MetricTrajectoryAlignment,
)
from cozmo_floorplan.recon.video_triangulation import (
    triangulate_aligned_video_segments,
    triangulate_metric_correspondences,
)
from cozmo_floorplan.recon.video_trajectory import (
    RelativeCameraPose,
    TrajectorySegment,
    VideoTrajectoryDiagnostics,
)


INTRINSICS = MetricCameraIntrinsics(500.0, 500.0, 320.0, 240.0, (640, 480))
LEFT_POSE = MetricCameraPose(0, 0.0, (-0.25, 1.4, 0.0), (0.0, 0.0, 0.0, 1.0))
RIGHT_POSE = MetricCameraPose(1, 0.1, (0.25, 1.4, 0.0), (0.0, 0.0, 0.0, 1.0))


def _project(points: np.ndarray, pose: MetricCameraPose) -> np.ndarray:
    camera = points - np.asarray(pose.position_m)
    return np.column_stack(
        (
            INTRINSICS.fx_px * camera[:, 0] / camera[:, 2] + INTRINSICS.cx_px,
            INTRINSICS.fy_px * camera[:, 1] / camera[:, 2] + INTRINSICS.cy_px,
        )
    )


def test_calibrated_metric_triangulation_recovers_known_world_points():
    points = np.asarray(
        [
            [-1.0, 0.2, 3.0],
            [0.0, 0.0, 3.5],
            [1.0, 0.5, 4.0],
            [-0.8, 2.4, 4.5],
            [0.2, 2.6, 5.0],
            [1.2, 1.4, 5.5],
        ],
        dtype=np.float64,
    )
    config = VideoTriangulationConfig(minimum_pair_inliers=4)

    recovered = triangulate_metric_correspondences(
        _project(points, LEFT_POSE),
        _project(points, RIGHT_POSE),
        LEFT_POSE,
        RIGHT_POSE,
        INTRINSICS,
        config=config,
    )

    assert recovered == pytest.approx(points, abs=1e-7)


def test_triangulation_rejects_large_reprojection_outlier():
    points = np.asarray(
        [[-0.8, 0.3, 3.0], [0.0, 0.6, 3.5], [0.7, 1.0, 4.0], [1.0, 1.8, 4.5]]
    )
    left = _project(points, LEFT_POSE)
    right = _project(points, RIGHT_POSE)
    right[-1] += (80.0, -60.0)

    recovered = triangulate_metric_correspondences(
        left,
        right,
        LEFT_POSE,
        RIGHT_POSE,
        INTRINSICS,
        config=VideoTriangulationConfig(minimum_pair_inliers=4),
    )

    assert len(recovered) == 3
    assert recovered == pytest.approx(points[:3], abs=1e-7)


def test_sparse_surface_diagnostics_find_supported_floor_and_walls():
    along = np.linspace(-1.8, 1.8, 12)
    heights = np.linspace(0.1, 2.6, 12)
    depths = np.linspace(2.0, 5.8, 12)
    floor = np.column_stack((along, np.zeros(12), depths))
    ceiling = np.column_stack((along, np.full(12, 2.8), depths))
    left_wall = np.column_stack((np.full(12, -2.0), heights, depths))
    right_wall = np.column_stack((np.full(12, 2.0), heights, depths))
    back_wall = np.column_stack((along, heights, np.full(12, 6.0)))
    points = np.vstack((floor, ceiling, left_wall, right_wall, back_wall))

    candidates = diagnose_video_planes(
        points,
        config=VideoSurfaceConfig(
            coordinate_bin_m=0.1,
            minimum_support_points=8,
            minimum_support_fraction=0.05,
            maximum_candidates_per_axis=4,
            minimum_candidate_separation_m=0.3,
        ),
    )

    coordinates = {(item.kind, item.axis): [] for item in candidates}
    for item in candidates:
        coordinates[(item.kind, item.axis)].append(item.coordinate_m)
    assert coordinates[("horizontal", "y")] == pytest.approx([0.0, 2.8], abs=0.05)
    assert coordinates[("wall", "x")] == pytest.approx([-2.0, 2.0], abs=0.05)
    assert coordinates[("wall", "z")] == pytest.approx([6.0], abs=0.05)


def test_segment_triangulation_requires_calibration_and_accepted_alignment(monkeypatch):
    points = np.asarray(
        [[-0.8, 0.3, 3.0], [0.0, 0.6, 3.5], [0.7, 1.0, 4.0], [1.0, 1.8, 4.5]]
    )
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    video = SampledVideo(
        identifier="room",
        metadata=VideoMetadata(
            source=Path("room.mp4"),
            native_size_px=(640, 480),
            display_size_px=(640, 480),
            native_fps=10.0,
            frame_count=2,
            duration_s=0.1,
            rotation_degrees_clockwise=0,
        ),
        frames=(frame, frame),
        source_frame_indices=(0, 1),
        timestamps_s=(0.0, 0.1),
    )
    relative_poses = tuple(
        RelativeCameraPose(index, (float(index), 0.0, 0.0), tuple(np.eye(3).ravel()))
        for index in range(2)
    )
    trajectory = VideoTrajectoryDiagnostics(
        identifier="room",
        selected_frames=2,
        attempted_edges=1,
        accepted_edges=1,
        segment_breaks=0,
        segment_restarts=0,
        assumed_focal_length_px=500.0,
        intrinsics_source="test",
        segments=(TrajectorySegment(0, relative_poses),),
        edges=(),
    )
    accepted_segment = MetricSegmentAlignment(
        segment_id=0,
        matched_pose_count=2,
        timestamp_mismatch_count=0,
        accepted=True,
        rejection_reason=None,
        scale_m_per_unit=0.5,
        rmse_m=0.0,
        aligned_positions_m=(LEFT_POSE.position_m, RIGHT_POSE.position_m),
    )
    alignment = MetricTrajectoryAlignment("room.poses.json", 2, 1, (accepted_segment,))
    sidecar = MetricPoseSidecar(
        source=Path("room.poses.json"),
        poses=(LEFT_POSE, RIGHT_POSE),
        schema_version="1.2.0",
        intrinsics=INTRINSICS,
        camera_axes="x_right_y_down_z_forward",
        world_frame_id="walkthrough-session-a",
        scale_source="arkit_poses",
    )
    features = FrameFeatures((), None, (640, 480))
    correspondences = PairCorrespondences(
        _project(points, LEFT_POSE),
        _project(points, RIGHT_POSE),
        np.eye(3),
        np.ones(len(points), dtype=bool),
    )
    monkeypatch.setattr(
        triangulation_module, "extract_frame_features", lambda *_args: features
    )
    monkeypatch.setattr(
        triangulation_module, "match_frame_features", lambda *_args: correspondences
    )

    cloud = triangulate_aligned_video_segments(
        video,
        trajectory,
        alignment,
        sidecar,
        config=VideoTriangulationConfig(minimum_pair_inliers=4, voxel_size_m=0.01),
    )

    assert cloud is not None
    assert cloud.accepted_pairs == 1
    assert cloud.points_m == pytest.approx(points, abs=1e-7)
    assert (
        triangulate_aligned_video_segments(
            video,
            trajectory,
            alignment,
            MetricPoseSidecar(Path("v1.poses.json"), (LEFT_POSE, RIGHT_POSE)),
        )
        is None
    )
