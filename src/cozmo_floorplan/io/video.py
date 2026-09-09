"""Discover walkthrough files and sample frames without inventing geometry."""

from pathlib import Path

import cv2
import numpy as np

from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_INGEST,
    POSE_SIDECAR_NAMES,
    VIDEO_EXTENSIONS,
    VideoIngestConfig,
)


def find_video_files(video_dir: Path) -> list[Path]:
    """Return walkthrough files in a stable order."""

    if not video_dir.is_dir():
        return []
    files = [
        path
        for path in video_dir.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    ]
    return sorted(files, key=lambda path: path.name.lower())


def find_pose_sidecar(video_dir: Path) -> Path | None:
    """Return an optional metric-camera sidecar if the capture app wrote one."""

    for name in POSE_SIDECAR_NAMES:
        candidate = video_dir / name
        if candidate.is_file():
            return candidate
    return None


def sample_video_frames(
    path: Path,
    *,
    config: VideoIngestConfig = DEFAULT_VIDEO_INGEST,
) -> list[np.ndarray]:
    """Sample RGB frames at a bounded rate. Does not estimate camera motion."""

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise OSError(f"Could not open video file: {path}")

    native_fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    stride = 1
    if native_fps > 0 and config.sample_fps > 0:
        stride = max(1, round(native_fps / config.sample_fps))

    frames: list[np.ndarray] = []
    index = 0
    try:
        while len(frames) < config.max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            if index % stride == 0:
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            index += 1
    finally:
        capture.release()
    return frames
