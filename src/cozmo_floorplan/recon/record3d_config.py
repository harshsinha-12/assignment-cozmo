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


@dataclass(frozen=True, slots=True)
class Record3DPlaneConfig:
    """Geometric thresholds for conservative Manhattan-room candidates."""

    horizontal_bin_m: float = 0.025
    horizontal_smoothing_bins: int = 5
    camera_level_clearance_m: float = 0.50
    level_refine_half_width_m: float = 0.05
    wall_vertical_margin_m: float = 0.08
    wall_column_bin_m: float = 0.05
    minimum_column_points: int = 4
    minimum_column_vertical_span_m: float = 1.50
    yaw_step_degrees: float = 0.50
    wall_histogram_bin_m: float = 0.05
    yaw_peak_count: int = 4
    camera_bracket_quantile: float = 0.10
    camera_wall_margin_m: float = 0.05
    outer_wall_support_ratio: float = 1.0
    max_clutter_offset_m: float = 0.32
    minimum_room_span_m: float = 1.50
    maximum_room_span_m: float = 12.0
    minimum_ceiling_height_m: float = 2.0
    maximum_ceiling_height_m: float = 4.5


DEFAULT_RECORD3D_PLANES = Record3DPlaneConfig()


@dataclass(frozen=True, slots=True)
class Record3DUncertaintyConfig:
    """Raw-support policy for candidate-stage measurement intervals."""

    support_window_m: float = 0.10
    residual_quantile: float = 0.95
    vertical_margin_m: float = 0.10


DEFAULT_RECORD3D_UNCERTAINTY = Record3DUncertaintyConfig()


@dataclass(frozen=True, slots=True)
class Record3DOpeningConfig:
    """Occupancy-profile thresholds for supported wall-opening candidates."""

    wall_normal_tolerance_m: float = 0.10
    profile_bin_m: float = 0.05
    wall_end_margin_m: float = 0.15
    door_band_low_m: float = 0.15
    door_band_high_m: float = 1.80
    sill_band_high_m: float = 0.65
    window_band_low_m: float = 0.85
    window_band_high_m: float = 1.90
    lintel_band_low_m: float = 2.05
    ceiling_margin_m: float = 0.10
    sparse_ratio: float = 0.22
    supported_ratio: float = 0.30
    minimum_band_points: int = 3
    maximum_interruption_bins: int = 1
    minimum_door_width_m: float = 0.65
    maximum_door_width_m: float = 1.40
    minimum_cased_opening_width_m: float = 1.40
    maximum_cased_opening_width_m: float = 2.40
    minimum_window_width_m: float = 0.40
    maximum_window_width_m: float = 2.40
    minimum_opening_height_m: float = 1.75
    height_bin_m: float = 0.05
    height_support_ratio: float = 0.15
    height_support_run_bins: int = 2


DEFAULT_RECORD3D_OPENINGS = Record3DOpeningConfig()


@dataclass(frozen=True, slots=True)
class Record3DOutputConfig:
    """Uncalibrated interval policy for Record3D candidate geometry."""

    confidence: float = 0.80
    opening_confidence: float = 0.60
    wall_half_width_cm: float = 5.0
    ceiling_half_width_cm: float = 2.5
    opening_width_half_width_cm: float = 5.0
    opening_height_half_width_cm: float = 7.5
    area_relative_half_width: float = 0.08


DEFAULT_RECORD3D_OUTPUT = Record3DOutputConfig()


@dataclass(frozen=True, slots=True)
class Record3DRegisterConfig:
    """Shared-world opening pairing without inventing a new pose frame."""

    maximum_center_distance_m: float = 1.25
    maximum_width_delta_m: float = 0.25
    maximum_height_delta_m: float = 0.40


DEFAULT_RECORD3D_REGISTER = Record3DRegisterConfig()
