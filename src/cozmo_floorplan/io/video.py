"""Discover walkthrough files and sample display-oriented RGB frames."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_INGEST,
    POSE_SIDECAR_NAMES,
    POSE_SIDECAR_SUFFIXES,
    VIDEO_EXTENSIONS,
    VideoIngestConfig,
)
from cozmo_floorplan.utils.images import rotate_quarter_turns_clockwise


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Container and display metadata needed before visual reconstruction."""

    source: Path
    native_size_px: tuple[int, int]
    display_size_px: tuple[int, int]
    native_fps: float
    frame_count: int
    duration_s: float
    rotation_degrees_clockwise: int


@dataclass(frozen=True, slots=True)
class SampledVideo:
    """One identified walkthrough plus normalized RGB samples."""

    identifier: str
    metadata: VideoMetadata
    frames: tuple[np.ndarray, ...]
    source_frame_indices: tuple[int, ...] = ()
    timestamps_s: tuple[float, ...] = ()


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


def find_pose_sidecar(
    video_dir: Path,
    *,
    video_stem: str | None = None,
    allow_global: bool = True,
) -> Path | None:
    """Return the sidecar belonging to one video, then an allowed global file."""

    if video_stem is not None:
        for suffix in POSE_SIDECAR_SUFFIXES:
            candidate = video_dir / f"{video_stem}{suffix}"
            if candidate.is_file():
                return candidate

    if allow_global:
        for name in POSE_SIDECAR_NAMES:
            candidate = video_dir / name
            if candidate.is_file():
                return candidate
    return None


def sample_video(
    path: Path,
    *,
    config: VideoIngestConfig = DEFAULT_VIDEO_INGEST,
) -> SampledVideo:
    """Read bounded RGB samples after explicitly applying display rotation."""

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise OSError(f"Could not open video file: {path}")

    auto_rotation_disabled = _disable_backend_auto_rotation(capture)
    metadata = _metadata(capture, path, config)
    if metadata.rotation_degrees_clockwise and not auto_rotation_disabled:
        capture.release()
        raise OSError(f"Could not disable backend auto-rotation for video file: {path}")
    stride = 1
    if metadata.native_fps > 0 and config.sample_fps > 0:
        stride = max(1, round(metadata.native_fps / config.sample_fps))

    frames: list[np.ndarray] = []
    source_frame_indices: list[int] = []
    timestamps_s: list[float] = []
    index = 0
    try:
        while len(frames) < config.max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            if index % stride == 0:
                oriented = rotate_quarter_turns_clockwise(
                    frame,
                    metadata.rotation_degrees_clockwise,
                )
                frames.append(cv2.cvtColor(oriented, cv2.COLOR_BGR2RGB))
                source_frame_indices.append(index)
                timestamp_ms = float(capture.get(cv2.CAP_PROP_POS_MSEC) or 0.0)
                timestamp_s = timestamp_ms / 1000.0
                if index > 0 and timestamp_s <= 0 and metadata.native_fps > 0:
                    timestamp_s = index / metadata.native_fps
                timestamps_s.append(timestamp_s)
            index += 1
    finally:
        capture.release()
    return SampledVideo(
        identifier=path.stem,
        metadata=metadata,
        frames=tuple(frames),
        source_frame_indices=tuple(source_frame_indices),
        timestamps_s=tuple(timestamps_s),
    )


def sample_video_frames(
    path: Path,
    *,
    config: VideoIngestConfig = DEFAULT_VIDEO_INGEST,
) -> list[np.ndarray]:
    """Compatibility wrapper returning normalized RGB frame arrays."""

    return list(sample_video(path, config=config).frames)


def _disable_backend_auto_rotation(capture: cv2.VideoCapture) -> bool:
    property_id = getattr(cv2, "CAP_PROP_ORIENTATION_AUTO", None)
    return property_id is None or bool(capture.set(property_id, 0))


def _metadata(
    capture: cv2.VideoCapture,
    path: Path,
    config: VideoIngestConfig,
) -> VideoMetadata:
    native_width = max(0, round(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
    native_height = max(0, round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    native_fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = max(0, round(capture.get(cv2.CAP_PROP_FRAME_COUNT)))
    raw_rotation = _capture_rotation(capture)
    rotation = _normalize_rotation(raw_rotation, config.rotation_tolerance_degrees)
    if rotation in {90, 270}:
        display_size = (native_height, native_width)
    else:
        display_size = (native_width, native_height)
    duration = frame_count / native_fps if native_fps > 0 else 0.0
    return VideoMetadata(
        source=path,
        native_size_px=(native_width, native_height),
        display_size_px=display_size,
        native_fps=native_fps,
        frame_count=frame_count,
        duration_s=duration,
        rotation_degrees_clockwise=rotation,
    )


def _capture_rotation(capture: cv2.VideoCapture) -> float:
    property_id = getattr(cv2, "CAP_PROP_ORIENTATION_META", None)
    return float(capture.get(property_id) or 0.0) if property_id is not None else 0.0


def _normalize_rotation(raw_degrees: float, tolerance_degrees: float) -> int:
    normalized = raw_degrees % 360.0
    closest = int(round(normalized / 90.0) * 90) % 360
    circular_error = abs((normalized - closest + 180.0) % 360.0 - 180.0)
    if circular_error > tolerance_degrees:
        raise OSError(
            f"Unsupported video display rotation {raw_degrees:g} degrees; "
            "expected a quarter turn."
        )
    return closest
