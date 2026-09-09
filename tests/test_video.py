from pathlib import Path

import cv2
import numpy as np
import pytest

from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.io.video import find_video_files, sample_video_frames
from cozmo_floorplan.pipeline import run_job
from cozmo_floorplan.recon.video import reconstruct_video
from cozmo_floorplan.recon.video_config import VideoIngestConfig
from cozmo_floorplan.errors import ReconstructionError


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
    assert writer.isOpened(), "OpenCV could not write a synthetic mp4 in this environment"
    for index in range(frames):
        shade = int((index * 11) % 255)
        frame = np.full((size[1], size[0], 3), shade, dtype=np.uint8)
        cv2.putText(frame, str(index), (8, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
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
    frames = sample_video_frames(files[0], config=VideoIngestConfig(sample_fps=2.0, max_frames=40, min_frames=8))
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
        reconstruct_video(load_job(job_dir), config=VideoIngestConfig(min_frames=8, sample_fps=6.0, max_frames=40))

    assert raised.value.warning_code == "incomplete_scan"
    assert "frames" in str(raised.value)
