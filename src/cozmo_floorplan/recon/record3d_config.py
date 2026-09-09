"""Configuration for bounded Record3D capture validation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Record3DValidationConfig:
    sample_frame_count: int = 3
    minimum_depth_m: float = 0.05
    maximum_depth_m: float = 20.0


DEFAULT_RECORD3D_VALIDATION = Record3DValidationConfig()
