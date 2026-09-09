"""Immutable settings for video ingest. Reconstruction stays metric-honest."""

from dataclasses import dataclass


VIDEO_EXTENSIONS = (".mp4", ".mov", ".m4v", ".avi")
POSE_SIDECAR_NAMES = ("poses.json", "arkit_poses.json", "cameras.json")
POSE_SIDECAR_SUFFIXES = (".poses.json", ".arkit_poses.json", ".cameras.json")


@dataclass(frozen=True, slots=True)
class VideoIngestConfig:
    sample_fps: float = 2.0
    max_frames: int = 240
    min_frames: int = 8
    rotation_tolerance_degrees: float = 1.0


DEFAULT_VIDEO_INGEST = VideoIngestConfig()
