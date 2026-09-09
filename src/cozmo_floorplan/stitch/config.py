"""Immutable settings for plane-anchored multi-room drift correction."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DriftConfig:
    method: str = "plane_anchored"
    residual_half_width_cm: float = 2.5
    residual_confidence: float = 0.80


DEFAULT_DRIFT_CONFIG = DriftConfig()
