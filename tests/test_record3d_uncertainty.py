"""Tests for support-conditioned Record3D measurement intervals."""

import numpy as np
import pytest

from cozmo_floorplan.recon.record3d_planes import (
    HorizontalPlaneLevels,
    ManhattanRoomCandidate,
    WallPlaneCandidate,
)
from cozmo_floorplan.recon.record3d_uncertainty import estimate_record3d_uncertainty


def _room() -> ManhattanRoomCandidate:
    return ManhattanRoomCandidate(
        levels=HorizontalPlaneLevels(-1.0, 1.8, 100, 100),
        yaw_degrees=0.0,
        walls=(
            WallPlaneCandidate("x", -2.0, 20),
            WallPlaneCandidate("x", 2.0, 20),
            WallPlaneCandidate("z", -1.5, 20),
            WallPlaneCandidate("z", 1.5, 20),
        ),
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
        vertical_support_columns=80,
    )


def _supported_points() -> np.ndarray:
    along_x = np.linspace(-2.0, 2.0, 21)
    along_z = np.linspace(-1.5, 1.5, 21)
    heights = np.linspace(-0.8, 1.6, 13)
    points = []
    for residual in (-0.08, -0.04, 0.0, 0.04, 0.08):
        for height in heights:
            points.extend(((-2.0 + residual, height, z) for z in along_z))
            points.extend(((2.0 + residual, height, z) for z in along_z))
            points.extend(((x, height, -1.5 + residual) for x in along_x))
            points.extend(((x, height, 1.5 + residual) for x in along_x))
        points.extend(((x, -1.0 + residual, z) for x, z in zip(along_x, along_z)))
        points.extend(((x, 1.8 + residual, z) for x, z in zip(along_x, along_z)))
    return np.asarray(points, dtype=float)


def test_support_residuals_expand_candidate_intervals_without_moving_geometry():
    uncertainty = estimate_record3d_uncertainty(_supported_points(), _room())

    assert uncertainty.x_span_half_width_cm == pytest.approx(16.0)
    assert uncertainty.z_span_half_width_cm == pytest.approx(16.0)
    assert uncertainty.ceiling_half_width_cm == pytest.approx(16.0)
    assert uncertainty.area_relative_half_width > 0.08
    assert uncertainty.polygon_wall_half_widths_cm == pytest.approx((16, 16, 16, 16))


def test_fixed_candidate_floors_apply_when_plane_support_is_tighter():
    points = _supported_points()
    room = _room()
    for axis, coordinate in ((0, -2.0), (0, 2.0), (2, -1.5), (2, 1.5)):
        near = np.abs(points[:, axis] - coordinate) <= 0.10
        points[near, axis] = coordinate
    near_floor = np.abs(points[:, 1] - room.levels.floor_y_m) <= 0.10
    near_ceiling = np.abs(points[:, 1] - room.levels.ceiling_y_m) <= 0.10
    points[near_floor, 1] = room.levels.floor_y_m
    points[near_ceiling, 1] = room.levels.ceiling_y_m

    uncertainty = estimate_record3d_uncertainty(points, room)

    assert uncertainty.x_span_half_width_cm == 5.0
    assert uncertainty.z_span_half_width_cm == 5.0
    assert uncertainty.ceiling_half_width_cm == 2.5
