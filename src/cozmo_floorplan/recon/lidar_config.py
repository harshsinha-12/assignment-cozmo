"""LiDAR confidence mapping and interval widths kept out of adapter logic."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LidarUncertainty:
    score: float
    length_half_width_cm: float
    area_relative_half_width: float


LIDAR_UNCERTAINTY = {
    "high": LidarUncertainty(0.95, 1.0, 0.02),
    "medium": LidarUncertainty(0.80, 2.5, 0.05),
    "low": LidarUncertainty(0.60, 5.0, 0.10),
}

ROOMPLAN_FILENAMES = (
    "roomplan.json",
    "captured_room.json",
    "captured_structure.json",
)
