import json
from pathlib import Path

import cv2
import numpy as np
import pytest

import cozmo_floorplan.io.video as video_module
import cozmo_floorplan.recon.video as recon_video_module
from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.io.video import find_video_files, sample_video, sample_video_frames
from cozmo_floorplan.io.video_poses import (
    MetricCameraIntrinsics,
    MetricCameraPose,
    MetricPoseSidecar,
)
from cozmo_floorplan.pipeline import run_job
from cozmo_floorplan.recon.video_pose_alignment import (
    MetricSegmentAlignment,
    MetricTrajectoryAlignment,
)
from cozmo_floorplan.recon.video_rooms import VideoRoomCandidate
from cozmo_floorplan.recon.video_surfaces import VideoPlaneCandidate
from cozmo_floorplan.recon.video_trajectory import (
    RelativeCameraPose,
    TrajectorySegment,
    VideoTrajectoryDiagnostics,
)
from cozmo_floorplan.recon.video import reconstruct_video
from cozmo_floorplan.recon.video_config import VideoIngestConfig
from cozmo_floorplan.utils.images import rotate_quarter_turns_clockwise


def _write_manifest(job_dir: Path) -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "manifest.yaml").write_text(
        "job_id: video_fixture\ntier: video\ndevice: iPhone 17 Pro\n",
        encoding="utf-8",
    )
    (job_dir / "video").mkdir(exist_ok=True)


def _write_synthetic_mp4(path: Path, *, frames: int = 72, fps: float = 12.0) -> None:
    size = (80, 48)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    assert writer.isOpened(), (
        "OpenCV could not write a synthetic mp4 in this environment"
    )
    for index in range(frames):
        shade = int((index * 11) % 255)
        frame = np.full((size[1], size[0], 3), shade, dtype=np.uint8)
        cv2.putText(
            frame,
            str(index),
            (8, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            1,
        )
        writer.write(frame)
    writer.release()


def _write_metric_sidecar(path: Path) -> None:
    document = {
        "schema_version": "1.0.0",
        "units": "m",
        "transform": "camera_to_world",
        "coordinate_system": "right_handed_y_up",
        "timestamp_origin": "video_start",
        "poses": [
            {
                "source_frame_index": index * 6,
                "timestamp_s": index * 0.5,
                "position_m": [index * 0.1, 0.0, 0.0],
                "rotation_xyzw": [0.0, 0.0, 0.0, 1.0],
            }
            for index in range(3)
        ],
    }
    path.write_text(json.dumps(document), encoding="utf-8")


def test_empty_video_directory_is_incomplete_scan(tmp_path):
    job_dir = tmp_path / "empty_video"
    _write_manifest(job_dir)

    document = run_job(job_dir)

    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "incomplete_scan"
    assert "MP4/MOV" in document["warnings"][0]["message"]


def test_synthetic_walkthrough_is_sampled_without_inventing_centimetres(tmp_path):
    job_dir = tmp_path / "sampled_video"
    _write_manifest(job_dir)
    video_path = job_dir / "video" / "walkthrough.mp4"
    _write_synthetic_mp4(video_path)
    _write_metric_sidecar(job_dir / "video" / "poses.json")

    files = find_video_files(job_dir / "video")
    ingest_config = VideoIngestConfig(sample_fps=2.0, max_frames=40, min_frames=8)
    sampled = sample_video(files[0], config=ingest_config)
    frames = sample_video_frames(
        files[0],
        config=ingest_config,
    )
    document = run_job(job_dir)

    assert files == [video_path]
    assert len(frames) >= 8
    assert len(sampled.source_frame_indices) == len(sampled.frames)
    assert len(sampled.timestamps_s) == len(sampled.frames)
    assert sampled.source_frame_indices[0] == 0
    assert all(
        right > left
        for left, right in zip(
            sampled.source_frame_indices,
            sampled.source_frame_indices[1:],
            strict=False,
        )
    )
    assert all(
        right > left
        for left, right in zip(
            sampled.timestamps_s,
            sampled.timestamps_s[1:],
            strict=False,
        )
    )
    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "insufficient_overlap"
    assert "samples from" in document["warnings"][0]["message"]
    assert "poses.json" in document["warnings"][0]["message"]
    assert "not be guessed" in document["warnings"][0]["message"]


def test_short_clip_is_incomplete_scan(tmp_path):
    job_dir = tmp_path / "short_video"
    _write_manifest(job_dir)
    _write_synthetic_mp4(job_dir / "video" / "clip.mp4", frames=3, fps=6.0)

    with pytest.raises(ReconstructionError) as raised:
        reconstruct_video(
            load_job(job_dir),
            config=VideoIngestConfig(min_frames=8, sample_fps=6.0, max_frames=40),
        )

    assert raised.value.warning_code == "incomplete_scan"
    assert "frames" in str(raised.value)


def test_multiple_walkthroughs_keep_identity_and_named_sidecars(tmp_path):
    job_dir = tmp_path / "multiple_videos"
    _write_manifest(job_dir)
    _write_synthetic_mp4(job_dir / "video" / "my-room.mp4")
    _write_synthetic_mp4(job_dir / "video" / "pooja-room.mp4")
    _write_metric_sidecar(job_dir / "video" / "my-room.poses.json")
    (job_dir / "video" / "poses.json").write_text("[]", encoding="utf-8")

    with pytest.raises(ReconstructionError) as raised:
        reconstruct_video(load_job(job_dir))

    message = str(raised.value)
    assert "2 room walkthrough(s)" in message
    assert "my-room:" in message
    assert "pooja-room:" in message
    assert "my-room.poses.json" in message
    assert "global pose sidecar is ambiguous" in message


def test_sample_video_applies_container_rotation_explicitly(monkeypatch, tmp_path):
    raw_frame = np.arange(2 * 3 * 3, dtype=np.uint8).reshape((2, 3, 3))

    class FakeCapture:
        def __init__(self, _path):
            self.read_count = 0
            self.auto_rotation = None

        def isOpened(self):
            return True

        def set(self, property_id, value):
            if property_id == cv2.CAP_PROP_ORIENTATION_AUTO:
                self.auto_rotation = value
            return True

        def get(self, property_id):
            values = {
                cv2.CAP_PROP_FRAME_WIDTH: 3,
                cv2.CAP_PROP_FRAME_HEIGHT: 2,
                cv2.CAP_PROP_FPS: 1,
                cv2.CAP_PROP_FRAME_COUNT: 1,
                cv2.CAP_PROP_ORIENTATION_META: 90,
            }
            return values.get(property_id, 0)

        def read(self):
            self.read_count += 1
            return (True, raw_frame.copy()) if self.read_count == 1 else (False, None)

        def release(self):
            return None

    fake_capture = FakeCapture("unused")
    monkeypatch.setattr(video_module.cv2, "VideoCapture", lambda _path: fake_capture)

    sampled = sample_video(
        tmp_path / "portrait.mp4",
        config=VideoIngestConfig(sample_fps=1, max_frames=2, min_frames=1),
    )

    expected_bgr = rotate_quarter_turns_clockwise(raw_frame, 90)
    expected_rgb = cv2.cvtColor(expected_bgr, cv2.COLOR_BGR2RGB)
    assert fake_capture.auto_rotation == 0
    assert sampled.identifier == "portrait"
    assert sampled.metadata.native_size_px == (3, 2)
    assert sampled.metadata.display_size_px == (2, 3)
    assert sampled.metadata.rotation_degrees_clockwise == 90
    assert sampled.frames[0] == pytest.approx(expected_rgb)
    assert sampled.source_frame_indices == (0,)
    assert sampled.timestamps_s == (0.0,)


def test_quarter_turn_rotation_rejects_non_right_angle():
    with pytest.raises(ValueError, match="multiple of 90"):
        rotate_quarter_turns_clockwise(np.zeros((2, 3, 3), dtype=np.uint8), 45)


def test_calibrated_supported_room_returns_video_floorplan(monkeypatch, tmp_path):
    job_dir = tmp_path / "calibrated_video"
    _write_manifest(job_dir)
    source = job_dir / "video" / "room-a.mp4"
    source.touch()
    sidecar_path = job_dir / "video" / "room-a.poses.json"
    sidecar_path.touch()
    frame = np.zeros((48, 80, 3), dtype=np.uint8)
    sampled = video_module.SampledVideo(
        identifier="room-a",
        metadata=video_module.VideoMetadata(
            source=source,
            native_size_px=(80, 48),
            display_size_px=(80, 48),
            native_fps=10.0,
            frame_count=3,
            duration_s=0.2,
            rotation_degrees_clockwise=0,
        ),
        frames=(frame, frame, frame),
        source_frame_indices=(0, 1, 2),
        timestamps_s=(0.0, 0.1, 0.2),
    )
    relative_poses = tuple(
        RelativeCameraPose(index, (float(index), 0.0, 0.0), tuple(np.eye(3).ravel()))
        for index in range(3)
    )
    segment = TrajectorySegment(0, relative_poses)
    trajectory = VideoTrajectoryDiagnostics(
        identifier="room-a",
        selected_frames=3,
        attempted_edges=2,
        accepted_edges=2,
        segment_breaks=0,
        segment_restarts=0,
        assumed_focal_length_px=72.0,
        intrinsics_source="test",
        segments=(segment,),
        edges=(),
    )
    positions = ((-0.3, 1.4, 0.0), (0.0, 1.4, 0.0), (0.3, 1.4, 0.0))
    poses = tuple(
        MetricCameraPose(index, index * 0.1, position, (0.0, 0.0, 0.0, 1.0))
        for index, position in enumerate(positions)
    )
    sidecar = MetricPoseSidecar(
        source=sidecar_path,
        poses=poses,
        schema_version="1.2.0",
        intrinsics=MetricCameraIntrinsics(70.0, 70.0, 40.0, 24.0, (80, 48)),
        camera_axes="x_right_y_down_z_forward",
        world_frame_id="session-a",
        scale_source="arkit_poses",
    )
    accepted = MetricSegmentAlignment(0, 3, 0, True, None, 0.3, 0.0, positions)
    alignment = MetricTrajectoryAlignment(sidecar_path.name, 3, 1, (accepted,))
    plane = VideoPlaneCandidate("wall", "x", -2.0, 50, 0.1)
    room = VideoRoomCandidate(
        floor=VideoPlaneCandidate("horizontal", "y", 0.0, 50, 0.1),
        ceiling=VideoPlaneCandidate("horizontal", "y", 2.8, 50, 0.1),
        walls=(plane, plane, plane, plane),
        yaw_degrees=0.0,
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
    )
    tracks = type(
        "Tracks",
        (),
        {
            # A low aggregate ratio is diagnostic only when locally connected,
            # individually gated pose edges still form a usable segment.
            "accepted_for_relative_vo": False,
            "eligible_pairs": 2,
            "analyzed_pairs": 2,
            "median_keypoints": 200.0,
            "median_matches": 100.0,
            "median_fundamental_inliers": 80.0,
            "median_motion_px": 10.0,
            "median_parallax_px": 2.0,
            "median_coverage_fraction": 0.2,
            "rejection_reason_counts": (),
        },
    )()
    cloud = type(
        "Cloud",
        (),
        {
            "points_m": np.zeros((100, 3)),
            "accepted_pairs": 2,
            "attempted_pairs": 2,
        },
    )()
    monkeypatch.setattr(recon_video_module, "find_video_files", lambda _path: [source])
    monkeypatch.setattr(
        recon_video_module, "sample_video", lambda *_args, **_kwargs: sampled
    )
    monkeypatch.setattr(
        recon_video_module, "find_pose_sidecar", lambda *_args, **_kwargs: sidecar_path
    )
    monkeypatch.setattr(
        recon_video_module, "load_metric_pose_sidecar", lambda _path: sidecar
    )
    monkeypatch.setattr(
        recon_video_module, "analyze_video_tracks", lambda *_args, **_kwargs: tracks
    )
    monkeypatch.setattr(
        recon_video_module,
        "recover_scale_free_trajectory",
        lambda *_args, **_kwargs: trajectory,
    )
    monkeypatch.setattr(
        recon_video_module,
        "align_trajectory_to_metric_poses",
        lambda *_args, **_kwargs: alignment,
    )
    monkeypatch.setattr(
        recon_video_module,
        "triangulate_aligned_video_segments",
        lambda *_args, **_kwargs: cloud,
    )
    monkeypatch.setattr(
        recon_video_module, "fit_video_room_candidate", lambda *_args, **_kwargs: room
    )

    document = reconstruct_video(
        load_job(job_dir),
        config=VideoIngestConfig(min_frames=3),
    )

    assert document["status"] == "partial"
    assert document["provenance"]["tier"] == "video"
    assert document["rooms"][0]["id"] == "room-a"
    assert len(document["walls"]) == 4


def test_partial_job_keeps_successful_room_when_another_fails(monkeypatch, tmp_path):
    job_dir = tmp_path / "partial_video"
    _write_manifest(job_dir)
    first = job_dir / "video" / "room-a.mp4"
    second = job_dir / "video" / "room-b.mp4"
    first.touch()
    second.touch()
    sidecar_a = job_dir / "video" / "room-a.poses.json"
    sidecar_b = job_dir / "video" / "room-b.poses.json"
    sidecar_a.touch()
    sidecar_b.touch()

    def _sampled(source):
        identifier = source.stem
        frame = np.zeros((48, 80, 3), dtype=np.uint8)
        return video_module.SampledVideo(
            identifier=identifier,
            metadata=video_module.VideoMetadata(
                source=source,
                native_size_px=(80, 48),
                display_size_px=(80, 48),
                native_fps=10.0,
                frame_count=3,
                duration_s=0.2,
                rotation_degrees_clockwise=0,
            ),
            frames=(frame, frame, frame),
            source_frame_indices=(0, 1, 2),
            timestamps_s=(0.0, 0.1, 0.2),
        )

    relative_poses = tuple(
        RelativeCameraPose(index, (float(index), 0.0, 0.0), tuple(np.eye(3).ravel()))
        for index in range(3)
    )
    trajectory = VideoTrajectoryDiagnostics(
        identifier="room",
        selected_frames=3,
        attempted_edges=2,
        accepted_edges=2,
        segment_breaks=0,
        segment_restarts=0,
        assumed_focal_length_px=72.0,
        intrinsics_source="test",
        segments=(TrajectorySegment(0, relative_poses),),
        edges=(),
    )
    positions = ((-0.3, 1.4, 0.0), (0.0, 1.4, 0.0), (0.3, 1.4, 0.0))
    poses = tuple(
        MetricCameraPose(index, index * 0.1, position, (0.0, 0.0, 0.0, 1.0))
        for index, position in enumerate(positions)
    )

    def _sidecar(path):
        return MetricPoseSidecar(
            source=path,
            poses=poses,
            schema_version="1.2.0",
            intrinsics=MetricCameraIntrinsics(70.0, 70.0, 40.0, 24.0, (80, 48)),
            camera_axes="x_right_y_down_z_forward",
            world_frame_id="session-a",
            scale_source="arkit_poses",
        )

    accepted = MetricSegmentAlignment(0, 3, 0, True, None, 0.3, 0.0, positions)
    alignment = MetricTrajectoryAlignment("sidecar", 3, 1, (accepted,))
    plane = VideoPlaneCandidate("wall", "x", -2.0, 50, 0.1)
    room = VideoRoomCandidate(
        floor=VideoPlaneCandidate("horizontal", "y", 0.0, 50, 0.1),
        ceiling=VideoPlaneCandidate("horizontal", "y", 2.8, 50, 0.1),
        walls=(plane, plane, plane, plane),
        yaw_degrees=0.0,
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
    )
    tracks = type(
        "Tracks",
        (),
        {
            "accepted_for_relative_vo": True,
            "eligible_pairs": 2,
            "analyzed_pairs": 2,
            "median_keypoints": 200.0,
            "median_matches": 100.0,
            "median_fundamental_inliers": 80.0,
            "median_motion_px": 10.0,
            "median_parallax_px": 2.0,
            "median_coverage_fraction": 0.2,
            "rejection_reason_counts": (),
        },
    )()
    cloud = type(
        "Cloud",
        (),
        {
            "points_m": np.zeros((100, 3)),
            "accepted_pairs": 2,
            "attempted_pairs": 2,
        },
    )()

    def _fit(points, cameras, **_kwargs):
        if getattr(_fit, "calls", 0) == 0:
            _fit.calls = 1
            return room
        raise ReconstructionError(
            "Sparse video points do not support a camera-bracketing x-high wall candidate.",
            warning_code="low_confidence",
        )

    monkeypatch.setattr(
        recon_video_module, "find_video_files", lambda _path: [first, second]
    )
    monkeypatch.setattr(
        recon_video_module, "sample_video", lambda source, **_kwargs: _sampled(source)
    )
    monkeypatch.setattr(
        recon_video_module,
        "find_pose_sidecar",
        lambda _dir, video_stem=None, allow_global=True: (
            sidecar_a if video_stem == "room-a" else sidecar_b
        ),
    )
    monkeypatch.setattr(
        recon_video_module, "load_metric_pose_sidecar", lambda path: _sidecar(path)
    )
    monkeypatch.setattr(
        recon_video_module, "analyze_video_tracks", lambda *_args, **_kwargs: tracks
    )
    monkeypatch.setattr(
        recon_video_module,
        "recover_scale_free_trajectory",
        lambda *_args, **_kwargs: trajectory,
    )
    monkeypatch.setattr(
        recon_video_module,
        "align_trajectory_to_metric_poses",
        lambda *_args, **_kwargs: alignment,
    )
    monkeypatch.setattr(
        recon_video_module,
        "triangulate_aligned_video_segments",
        lambda *_args, **_kwargs: cloud,
    )
    monkeypatch.setattr(recon_video_module, "fit_video_room_candidate", _fit)
    monkeypatch.setattr(
        recon_video_module, "detect_video_openings", lambda *_args, **_kwargs: ()
    )

    document = reconstruct_video(
        load_job(job_dir),
        config=VideoIngestConfig(min_frames=3),
    )

    assert document["status"] == "partial"
    assert [room["id"] for room in document["rooms"]] == ["room-a"]
    assert any("room-b" in warning["message"] for warning in document["warnings"])


def test_malformed_metric_pose_sidecar_fails_structurally(tmp_path):
    job_dir = tmp_path / "malformed_sidecar"
    _write_manifest(job_dir)
    _write_synthetic_mp4(job_dir / "video" / "walkthrough.mp4")
    (job_dir / "video" / "walkthrough.poses.json").write_text(
        '{"units":"cm","poses":[]}',
        encoding="utf-8",
    )

    with pytest.raises(ReconstructionError) as raised:
        reconstruct_video(load_job(job_dir))

    assert raised.value.warning_code == "incomplete_scan"
    assert "schema_version" in str(raised.value)
