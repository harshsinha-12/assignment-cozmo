from pathlib import Path

import numpy as np
import pytest

from cozmo_floorplan.geom.rotations import (
    matrix_to_quaternion_xyzw,
    quaternion_xyzw_matrix,
)
from cozmo_floorplan.io.video import SampledVideo, VideoMetadata
from cozmo_floorplan.recon.video_native_scale import (
    NATIVE_SCALE_SOURCE,
    apply_handheld_height_scale,
    build_native_unit_sidecar,
    estimate_handheld_height_scale,
)
from cozmo_floorplan.recon.video_trajectory import (
    RelativeCameraPose,
    TrajectorySegment,
    VideoTrajectoryDiagnostics,
)


def _identity_pose(index: int, x: float) -> RelativeCameraPose:
    return RelativeCameraPose(
        frame_index=index,
        position_unitless=(x, 0.0, 0.0),
        rotation_camera_to_segment=tuple(float(value) for value in np.eye(3).ravel()),
    )


def test_handheld_height_scale_recovers_disclosed_camera_height():
    cameras = np.array([[0.0, 0.5, 0.0], [1.0, 0.5, 0.0], [2.0, 0.52, 0.0]])
    rng = np.random.default_rng(4)
    floor = np.column_stack(
        (
            rng.uniform(-0.5, 2.5, 24),
            np.full(24, 0.02),
            rng.uniform(-0.4, 0.4, 24),
        )
    )

    scale = estimate_handheld_height_scale(cameras, floor)

    assert scale is not None
    assert abs(scale.camera_height_m - 1.45) < 1e-9
    assert abs((0.5 - scale.floor_y) * scale.scale_m_per_unit - 1.45) < 0.05


def test_missing_floor_support_does_not_invent_scale():
    cameras = np.array([[0.0, 1.4, 0.0], [1.0, 1.4, 0.0], [2.0, 1.4, 0.0]])
    points = np.array([[0.0, 1.3, 4.0], [0.2, 1.35, 4.2], [0.4, 1.2, 3.8]])

    assert estimate_handheld_height_scale(cameras, points) is None


def test_native_unit_sidecar_uses_y_up_and_exact_frame_times(tmp_path):
    source = tmp_path / "room-a.mp4"
    video = SampledVideo(
        identifier="room-a",
        metadata=VideoMetadata(
            source=source,
            native_size_px=(80, 48),
            display_size_px=(80, 48),
            native_fps=2.0,
            frame_count=3,
            duration_s=0.2,
            rotation_degrees_clockwise=0,
        ),
        frames=(np.zeros((48, 80, 3), dtype=np.uint8),) * 3,
        source_frame_indices=(0, 4, 8),
        timestamps_s=(0.0, 0.2, 0.4),
    )
    trajectory = VideoTrajectoryDiagnostics(
        identifier="room-a",
        selected_frames=3,
        attempted_edges=2,
        accepted_edges=2,
        segment_breaks=0,
        segment_restarts=0,
        assumed_focal_length_px=72.0,
        intrinsics_source="test",
        segments=(
            TrajectorySegment(
                0,
                (
                    _identity_pose(0, 0.0),
                    _identity_pose(1, 1.0),
                    _identity_pose(2, 2.0),
                ),
            ),
        ),
        edges=(),
    )

    sidecar = build_native_unit_sidecar(video, trajectory)

    assert sidecar is not None
    assert sidecar.scale_source == NATIVE_SCALE_SOURCE
    assert sidecar.world_frame_id == "native-video-assumed-up:room-a"
    assert sidecar.intrinsics.image_size_px == (80, 48)
    assert sidecar.intrinsics.fx_px == pytest.approx(0.9 * 80)
    assert sidecar.intrinsics.cx_px == 40.0
    assert [pose.source_frame_index for pose in sidecar.poses] == [0, 4, 8]
    assert sidecar.poses[1].position_m[0] == 1.0
    assert sidecar.poses[1].position_m[1] == 0.0
    first_rotation = quaternion_xyzw_matrix(sidecar.poses[0].rotation_xyzw)
    assert np.linalg.det(first_rotation) == np.float64(1.0)
    assert np.allclose(first_rotation, np.diag([1.0, -1.0, -1.0]))


def test_apply_handheld_height_puts_floor_at_zero():
    cameras = np.array([[0.0, 0.5, 0.0], [1.0, 0.5, 0.0], [2.0, 0.5, 0.0]])
    points = np.array([[0.0, 0.0, 1.0], [0.5, 0.0, 1.2], [1.0, 0.0, 0.8]] + [[0.1, 0.0, 0.9]] * 8)
    scale = estimate_handheld_height_scale(cameras, points)
    assert scale is not None
    from cozmo_floorplan.io.video_poses import (
        MetricCameraIntrinsics,
        MetricCameraPose,
        MetricPoseSidecar,
    )

    sidecar = MetricPoseSidecar(
        source=Path("room-a.native-height.poses.json"),
        poses=tuple(
            MetricCameraPose(index, index * 0.1, tuple(position), (0.0, 0.0, 0.0, 1.0))
            for index, position in enumerate(cameras)
        ),
        schema_version="1.2.0",
        intrinsics=MetricCameraIntrinsics(70.0, 70.0, 40.0, 24.0, (80, 48)),
        camera_axes="x_right_y_down_z_forward",
        world_frame_id="native-video-assumed-up:room-a",
        scale_source=NATIVE_SCALE_SOURCE,
    )
    scaled_sidecar, scaled_points = apply_handheld_height_scale(sidecar, points, scale)

    assert abs(float(np.median(scaled_points[:, 1]))) < 0.05
    assert abs(float(np.median([pose.position_m[1] for pose in scaled_sidecar.poses])) - 1.45) < 0.05


def test_rotation_matrix_quaternion_round_trip():
    original = np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
        ]
    )
    recovered = quaternion_xyzw_matrix(matrix_to_quaternion_xyzw(original))
    assert np.allclose(recovered, original)
