import numpy as np
import pytest

from cozmo_floorplan.recon.record3d_openings import detect_record3d_openings
from cozmo_floorplan.recon.record3d_planes import (
    HorizontalPlaneLevels,
    ManhattanRoomCandidate,
)


def _room_candidate() -> ManhattanRoomCandidate:
    return ManhattanRoomCandidate(
        levels=HorizontalPlaneLevels(
            floor_y_m=0.0,
            ceiling_y_m=2.8,
            floor_support_points=1000,
            ceiling_support_points=1000,
        ),
        yaw_degrees=0.0,
        walls=(),
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
        vertical_support_columns=200,
    )


def _room_points(*, include_gaps: bool = True) -> np.ndarray:
    y_values = np.arange(0.05, 2.80, 0.05)
    x_values = np.arange(-2.0, 2.001, 0.025)
    z_values = np.arange(-1.5, 1.501, 0.025)
    points: list[tuple[float, float, float]] = []
    for x in x_values:
        for y in y_values:
            door_gap = -0.50 <= x <= 0.40 and y < 2.10
            if not include_gaps or not door_gap:
                points.append((float(x), float(y), -1.5))
            points.append((float(x), float(y), 1.5))
    for z in z_values:
        for y in y_values:
            window_gap = -0.50 <= z <= 0.50 and 0.80 <= y < 2.00
            points.append((-2.0, float(y), float(z)))
            if not include_gaps or not window_gap:
                points.append((2.0, float(y), float(z)))
    return np.asarray(points)


def test_detects_floor_reaching_door_and_sill_supported_window():
    openings = detect_record3d_openings(_room_points(), _room_candidate())

    assert [(opening.wall_index, opening.kind) for opening in openings] == [
        (0, "door"),
        (1, "window"),
    ]
    door, window = openings
    assert door.width_m == pytest.approx(0.90, abs=0.08)
    assert door.height_m == pytest.approx(2.10, abs=0.08)
    assert window.width_m == pytest.approx(1.00, abs=0.08)
    assert window.height_m == pytest.approx(1.20, abs=0.08)
    assert door.lintel_support_points > 0


def test_solid_walls_do_not_create_phantom_openings():
    openings = detect_record3d_openings(
        _room_points(include_gaps=False), _room_candidate()
    )

    assert openings == ()


def test_wide_floor_reaching_gap_is_a_cased_opening_not_a_door():
    y_values = np.arange(0.05, 2.80, 0.05)
    x_values = np.arange(-2.0, 2.001, 0.025)
    points: list[tuple[float, float, float]] = []
    for x in x_values:
        for y in y_values:
            wide_gap = -1.0 <= x <= 1.0 and y < 2.20
            if not wide_gap:
                points.append((float(x), float(y), -1.5))
            points.append((float(x), float(y), 1.5))
    z_values = np.arange(-1.5, 1.501, 0.025)
    for z in z_values:
        for y in y_values:
            points.append((-2.0, float(y), float(z)))
            points.append((2.0, float(y), float(z)))

    openings = detect_record3d_openings(np.asarray(points), _room_candidate())

    assert len(openings) == 1
    assert openings[0].kind == "cased_opening"
    assert openings[0].width_m == pytest.approx(2.0, abs=0.12)
