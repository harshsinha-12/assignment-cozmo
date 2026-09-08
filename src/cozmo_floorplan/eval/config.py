"""Official thresholds and explicit internal calibration policy."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GateThresholds:
    """Numerical gates copied from the official prompt unless noted."""

    opening_error_cm: float = 2.0
    opening_success_rate: float = 0.85
    ceiling_error_cm: float = 1.5
    ceiling_repeat_spread_cm: float = 1.0
    repeatability_absolute_cm: float = 1.0
    repeatability_relative: float = 0.005
    photo_wall_relative_error: float = 0.08
    video_wall_relative_error: float = 0.03
    photo_footprint_relative_error: float = 0.08
    head_to_head_win_rate: float = 0.70
    overlap_area_tolerance_cm2: float = 1.0
    calibration_coverage_tolerance: float = 0.05


OFFICIAL_THRESHOLDS = GateThresholds()
