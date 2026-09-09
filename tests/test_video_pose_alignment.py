import json
from pathlib import Path

import numpy as np
import pytest

from cozmo_floorplan.io.video import SampledVideo, VideoMetadata
from cozmo_floorplan.io.video_poses import load_metric_pose_sidecar
from cozmo_floorplan.recon.video_pose_alignment import (
    align_trajectory_to_metric_poses,
)
from cozmo_floorplan.recon.video_trajectory import (
    RelativeCameraPose,
    TrajectorySegment,
    VideoTrajectoryDiagnostics,
)


def _sidecar_document(
    positions: list[tuple[float, float, float]],
    *,
    timestamp_offset: float = 0.0,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "units": "m",
        "transform": "camera_to_world",
        "coordinate_system": "right_handed_y_up",
        "timestamp_origin": "video_start",
        "poses": [
            {
                "source_frame_index": frame_index,
                "timestamp_s": sample_index * 0.5 + timestamp_offset,
                "position_m": list(position),
                "rotation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
            for sample_index, (frame_index, position) in enumerate(
                zip((0, 10, 20, 30), positions, strict=True)
            )
        ],
    }


def _write_sidecar(path: Path, document: dict) -> Path:
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _trajectory_fixture() -> tuple[
    SampledVideo, VideoTrajectoryDiagnostics, np.ndarray
]:
    unitless = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]]
    )
    poses = tuple(
        RelativeCameraPose(
            frame_index=index,
            position_unitless=tuple(position),
            rotation_camera_to_segment=tuple(np.eye(3).ravel()),
        )
        for index, position in enumerate(unitless)
    )
    segment = TrajectorySegment(0, poses)
    trajectory = VideoTrajectoryDiagnostics(
        identifier="room",
        selected_frames=4,
        attempted_edges=3,
        accepted_edges=3,
        segment_breaks=0,
        segment_restarts=0,
        assumed_focal_length_px=300.0,
        intrinsics_source="image_size_focal_prior_unvalidated",
        segments=(segment,),
        edges=(),
    )
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    video = SampledVideo(
        identifier="room",
        metadata=VideoMetadata(
            source=Path("room.mp4"),
            native_size_px=(10, 10),
            display_size_px=(10, 10),
            native_fps=20.0,
            frame_count=31,
            duration_s=1.5,
            rotation_degrees_clockwise=0,
        ),
        frames=(frame, frame, frame, frame),
        source_frame_indices=(0, 10, 20, 30),
        timestamps_s=(0.0, 0.5, 1.0, 1.5),
    )
    return video, trajectory, unitless


def test_metric_sidecar_parses_strict_versioned_camera_poses(tmp_path):
    positions = [(0.0, 0.0, 0.0), (0.4, 0.0, 0.0), (0.4, 0.4, 0.0), (0.8, 0.4, 0.0)]
    path = _write_sidecar(tmp_path / "room.poses.json", _sidecar_document(positions))

    sidecar = load_metric_pose_sidecar(path)

    assert len(sidecar.poses) == 4
    assert sidecar.poses[2].source_frame_index == 20
    assert sidecar.poses[2].timestamp_s == 1.0
    assert sidecar.units == "m"
    assert sidecar.intrinsics is None


def test_metric_sidecar_v12_adds_shared_frame_and_scale_source(tmp_path):
    document = _sidecar_document([(0.0, 0.0, 0.0)] * 4)
    document.update(
        schema_version="1.2.0",
        camera_axes="x_right_y_down_z_forward",
        world_frame_id="walkthrough-session-a",
        scale_source="arkit_poses",
        intrinsics={
            "fx_px": 600.0,
            "fy_px": 602.0,
            "cx_px": 320.0,
            "cy_px": 240.0,
            "image_size_px": [640, 480],
        },
    )

    sidecar = load_metric_pose_sidecar(
        _write_sidecar(tmp_path / "calibrated.poses.json", document)
    )

    assert sidecar.schema_version == "1.2.0"
    assert sidecar.camera_axes == "x_right_y_down_z_forward"
    assert sidecar.world_frame_id == "walkthrough-session-a"
    assert sidecar.scale_source == "arkit_poses"
    assert sidecar.intrinsics is not None
    assert sidecar.intrinsics.image_size_px == (640, 480)


def test_metric_sidecar_v11_rejects_missing_intrinsics(tmp_path):
    document = _sidecar_document([(0.0, 0.0, 0.0)] * 4)
    document.update(
        schema_version="1.1.0",
        camera_axes="x_right_y_down_z_forward",
    )

    with pytest.raises(ValueError, match="intrinsics must be an object"):
        load_metric_pose_sidecar(
            _write_sidecar(tmp_path / "uncalibrated.poses.json", document)
        )


def test_metric_sidecar_v11_remains_valid_without_v12_output_fields(tmp_path):
    document = _sidecar_document([(0.0, 0.0, 0.0)] * 4)
    document.update(
        schema_version="1.1.0",
        camera_axes="x_right_y_down_z_forward",
        intrinsics={
            "fx_px": 600.0,
            "fy_px": 602.0,
            "cx_px": 320.0,
            "cy_px": 240.0,
            "image_size_px": [640, 480],
        },
    )

    sidecar = load_metric_pose_sidecar(
        _write_sidecar(tmp_path / "v11.poses.json", document)
    )

    assert sidecar.intrinsics is not None
    assert sidecar.world_frame_id is None
    assert sidecar.scale_source is None


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda document: document.update(units="cm"), "requires units='m'"),
        (
            lambda document: document["poses"][1].update(source_frame_index=0),
            "unique and increasing",
        ),
        (
            lambda document: document["poses"][0].update(
                rotation_xyzw=[0.0, 0.0, 0.0, 2.0]
            ),
            "unit norm",
        ),
    ],
)
def test_metric_sidecar_rejects_ambiguous_scale_or_correspondence(
    tmp_path, mutation, message
):
    document = _sidecar_document([(0.0, 0.0, 0.0)] * 4)
    mutation(document)
    path = _write_sidecar(tmp_path / "bad.poses.json", document)

    with pytest.raises(ValueError, match=message):
        load_metric_pose_sidecar(path)


def test_similarity_alignment_recovers_metric_scale_and_positions(tmp_path):
    video, trajectory, unitless = _trajectory_fixture()
    angle = np.deg2rad(30.0)
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    metric = 0.4 * (unitless @ rotation.T) + np.array([2.0, 1.0, -0.5])
    path = _write_sidecar(
        tmp_path / "room.poses.json",
        _sidecar_document([tuple(position) for position in metric]),
    )

    result = align_trajectory_to_metric_poses(
        video,
        trajectory,
        load_metric_pose_sidecar(path),
    )

    segment = result.segments[0]
    assert result.aligned_segment_count == 1
    assert segment.accepted is True
    assert segment.scale_m_per_unit == pytest.approx(0.4)
    assert segment.rmse_m == pytest.approx(0.0, abs=1e-12)
    assert np.asarray(segment.aligned_positions_m) == pytest.approx(metric)


def test_timestamp_mismatch_prevents_metric_alignment(tmp_path):
    video, trajectory, _unitless = _trajectory_fixture()
    document = _sidecar_document(
        [(0.0, 0.0, 0.0)] * 4,
        timestamp_offset=0.1,
    )
    sidecar = load_metric_pose_sidecar(
        _write_sidecar(tmp_path / "room.poses.json", document)
    )

    result = align_trajectory_to_metric_poses(video, trajectory, sidecar)

    segment = result.segments[0]
    assert result.aligned_segment_count == 0
    assert segment.accepted is False
    assert segment.timestamp_mismatch_count == 4
    assert segment.rejection_reason == "insufficient_exact_frame_time_matches"
