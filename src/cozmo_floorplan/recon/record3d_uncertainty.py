"""Estimate Record3D candidate intervals from raw plane support."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_OUTPUT,
    DEFAULT_RECORD3D_UNCERTAINTY,
    Record3DOutputConfig,
    Record3DUncertaintyConfig,
)
from cozmo_floorplan.recon.record3d_planes import (
    ManhattanRoomCandidate,
    _planar_rotation,
)


@dataclass(frozen=True, slots=True)
class Record3DUncertainty:
    """Support-conditioned half-widths and their audit diagnostics."""

    x_span_half_width_cm: float
    z_span_half_width_cm: float
    ceiling_half_width_cm: float
    area_relative_half_width: float
    wall_residual_quantile_cm: tuple[float, float, float, float]
    floor_residual_quantile_cm: float
    ceiling_residual_quantile_cm: float

    @property
    def polygon_wall_half_widths_cm(self) -> tuple[float, float, float, float]:
        """Return intervals in polygon edge order: z-low, x-high, z-high, x-low."""

        return (
            self.z_span_half_width_cm,
            self.x_span_half_width_cm,
            self.z_span_half_width_cm,
            self.x_span_half_width_cm,
        )


def estimate_record3d_uncertainty(
    points_m: np.ndarray,
    room: ManhattanRoomCandidate,
    *,
    config: Record3DUncertaintyConfig = DEFAULT_RECORD3D_UNCERTAINTY,
    output_config: Record3DOutputConfig = DEFAULT_RECORD3D_OUTPUT,
) -> Record3DUncertainty:
    """Estimate conservative span/height intervals without benchmark truth."""

    _validate(points_m, room, config)
    rotation = _planar_rotation(room.yaw_degrees)
    local_xz = points_m[:, (0, 2)] @ rotation.T
    vertical = (
        points_m[:, 1] >= room.levels.floor_y_m + config.vertical_margin_m
    ) & (points_m[:, 1] <= room.levels.ceiling_y_m - config.vertical_margin_m)
    wall_residuals = tuple(
        _residual_quantile(
            local_xz[vertical, 0 if wall.axis == "x" else 1],
            wall.coordinate_m,
            config,
        )
        for wall in room.walls
    )
    if len(wall_residuals) != 4 or [wall.axis for wall in room.walls] != [
        "x",
        "x",
        "z",
        "z",
    ]:
        raise ReconstructionError(
            "Record3D uncertainty requires x-low/x-high/z-low/z-high wall candidates."
        )

    floor_residual = _residual_quantile(
        points_m[:, 1], room.levels.floor_y_m, config
    )
    ceiling_residual = _residual_quantile(
        points_m[:, 1], room.levels.ceiling_y_m, config
    )
    x_half_width_cm = max(
        output_config.wall_half_width_cm,
        (wall_residuals[0] + wall_residuals[1]) * 100.0,
    )
    z_half_width_cm = max(
        output_config.wall_half_width_cm,
        (wall_residuals[2] + wall_residuals[3]) * 100.0,
    )
    ceiling_half_width_cm = max(
        output_config.ceiling_half_width_cm,
        (floor_residual + ceiling_residual) * 100.0,
    )
    x_relative = x_half_width_cm / (room.width_m * 100.0)
    z_relative = z_half_width_cm / (room.depth_m * 100.0)
    area_relative_half_width = max(
        output_config.area_relative_half_width,
        x_relative + z_relative + x_relative * z_relative,
    )
    return Record3DUncertainty(
        x_span_half_width_cm=x_half_width_cm,
        z_span_half_width_cm=z_half_width_cm,
        ceiling_half_width_cm=ceiling_half_width_cm,
        area_relative_half_width=area_relative_half_width,
        wall_residual_quantile_cm=tuple(value * 100.0 for value in wall_residuals),
        floor_residual_quantile_cm=floor_residual * 100.0,
        ceiling_residual_quantile_cm=ceiling_residual * 100.0,
    )


def _residual_quantile(
    values: np.ndarray,
    coordinate_m: float,
    config: Record3DUncertaintyConfig,
) -> float:
    residuals = np.abs(values - coordinate_m)
    support = residuals[residuals <= config.support_window_m]
    if len(support) == 0:
        raise ReconstructionError(
            "Record3D candidate plane has no points inside the uncertainty support window."
        )
    return float(np.quantile(support, config.residual_quantile))


def _validate(
    points_m: np.ndarray,
    room: ManhattanRoomCandidate,
    config: Record3DUncertaintyConfig,
) -> None:
    if points_m.ndim != 2 or points_m.shape[1] != 3 or not np.all(np.isfinite(points_m)):
        raise ReconstructionError("Record3D uncertainty requires finite N x 3 points.")
    if config.support_window_m <= 0 or config.vertical_margin_m < 0:
        raise ValueError("Record3D uncertainty distances must be positive.")
    if not 0 < config.residual_quantile < 1:
        raise ValueError("Record3D residual_quantile must be between zero and one.")
    if room.width_m <= 0 or room.depth_m <= 0:
        raise ReconstructionError("Record3D uncertainty requires positive room spans.")
