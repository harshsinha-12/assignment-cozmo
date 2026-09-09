"""Occupancy-profile openings for sparse metric video rooms."""

from __future__ import annotations

from cozmo_floorplan.recon.record3d_config import Record3DOpeningConfig
from cozmo_floorplan.recon.record3d_openings import (
    Record3DOpeningCandidate,
    detect_occupancy_openings,
)
from cozmo_floorplan.recon.video_rooms import VideoRoomCandidate

DEFAULT_VIDEO_OPENINGS = Record3DOpeningConfig(
    wall_normal_tolerance_m=0.18,
    profile_bin_m=0.12,
    wall_end_margin_m=0.20,
    door_band_low_m=0.15,
    door_band_high_m=1.80,
    sill_band_high_m=0.65,
    window_band_low_m=0.85,
    window_band_high_m=1.90,
    lintel_band_low_m=2.05,
    ceiling_margin_m=0.10,
    sparse_ratio=0.20,
    supported_ratio=0.25,
    minimum_band_points=2,
    maximum_interruption_bins=2,
    minimum_door_width_m=0.55,
    maximum_door_width_m=1.40,
    minimum_window_width_m=0.40,
    maximum_window_width_m=2.40,
    minimum_opening_height_m=1.75,
    height_bin_m=0.08,
    height_support_ratio=0.15,
    height_support_run_bins=2,
)


def detect_video_openings(
    points_m,
    room: VideoRoomCandidate,
    *,
    config: Record3DOpeningConfig = DEFAULT_VIDEO_OPENINGS,
) -> tuple[Record3DOpeningCandidate, ...]:
    """Reuse occupancy-profile gaps; do not invent openings without lintel support."""

    return detect_occupancy_openings(
        points_m,
        room.polygon_xz_m,
        room.floor.coordinate_m,
        room.ceiling_height_m,
        config=config,
    )
