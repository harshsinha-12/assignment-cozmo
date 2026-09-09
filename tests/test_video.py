from pathlib import Path

import cv2
import numpy as np
import pytest

import cozmo_floorplan.io.video as video_module
from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.io.video import find_video_files, sample_video, sample_video_frames
from cozmo_floorplan.pipeline import run_job
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
    (job_dir / "video" / "poses.json").write_text("[]", encoding="utf-8")

    files = find_video_files(job_dir / "video")
    frames = sample_video_frames(
        files[0], config=VideoIngestConfig(sample_fps=2.0, max_frames=40, min_frames=8)
    )
    document = run_job(job_dir)

    assert files == [video_path]
    assert len(frames) >= 8
    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "unsupported_tier"
    assert "Sampled" in document["warnings"][0]["message"]
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
    (job_dir / "video" / "my-room.poses.json").write_text("[]", encoding="utf-8")
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


def test_quarter_turn_rotation_rejects_non_right_angle():
    with pytest.raises(ValueError, match="multiple of 90"):
        rotate_quarter_turns_clockwise(np.zeros((2, 3, 3), dtype=np.uint8), 45)
