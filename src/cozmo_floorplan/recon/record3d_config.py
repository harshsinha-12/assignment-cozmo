"""Configuration for bounded Record3D capture validation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Record3DValidationConfig:
    sample_frame_count: int = 3
    minimum_depth_m: float = 0.05
    maximum_depth_m: float = 20.0


DEFAULT_RECORD3D_VALIDATION = Record3DValidationConfig()


@dataclass(frozen=True, slots=True)
class Record3DPointCloudConfig:
    """Bounded, deterministic sampling for metric point generation."""

    sampled_frame_count: int = 61
    pixel_stride: int = 2
    minimum_confidence: int = 1
    minimum_depth_m: float = 0.10
    maximum_depth_m: float = 8.0
    voxel_size_m: float = 0.025


DEFAULT_RECORD3D_POINT_CLOUD = Record3DPointCloudConfig()
