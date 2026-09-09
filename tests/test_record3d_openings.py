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


def test_corner_door_keeps_full_width_instead_of_wall_end_margin():
    y_values = np.arange(0.05, 2.80, 0.05)
    x_values = np.arange(-2.0, 2.001, 0.025)
    z_values = np.arange(-1.5, 1.501, 0.025)
    points: list[tuple[float, float, float]] = []
    for x in x_values:
        for y in y_values:
            door_gap = x <= -1.20 and y < 2.10
            if not door_gap:
                points.append((float(x), float(y), -1.5))
            points.append((float(x), float(y), 1.5))
    for z in z_values:
        for y in y_values:
            points.append((-2.0, float(y), float(z)))
            points.append((2.0, float(y), float(z)))

    openings = detect_record3d_openings(np.asarray(points), _room_candidate())
    doors = [opening for opening in openings if opening.kind == "door"]

    assert len(doors) == 1
    assert doors[0].wall_index == 0
    assert doors[0].width_m == pytest.approx(0.80, abs=0.08)
    assert doors[0].offset_m == pytest.approx(0.0, abs=0.08)


def test_emptier_cased_opening_wins_over_a_lintel_heavier_partial_gap():
    from cozmo_floorplan.recon.record3d_openings import (
        Record3DOpeningCandidate,
        _limit_kind,
    )

    occupied = Record3DOpeningCandidate(
        wall_index=3,
        kind="cased_opening",
        offset_m=1.05,
        width_m=1.70,
        height_m=2.00,
        sparse_profile_bins=34,
        lintel_support_points=6700,
        gap_occupancy_points=1191,
    )
    empty = Record3DOpeningCandidate(
        wall_index=2,
        kind="cased_opening",
        offset_m=0.20,
        width_m=1.95,
        height_m=2.15,
        sparse_profile_bins=39,
        lintel_support_points=5762,
        gap_occupancy_points=46,
    )

    limited = _limit_kind((occupied, empty), "cased_opening")

    assert limited == (empty,)


def test_gap_at_door_cased_boundary_is_cased_opening_not_both():
    y_values = np.arange(0.05, 2.80, 0.05)
    x_values = np.arange(-2.0, 2.001, 0.025)
    z_values = np.arange(-1.5, 1.501, 0.025)
    points: list[tuple[float, float, float]] = []
    for x in x_values:
        for y in y_values:
            boundary_gap = -0.70 <= x <= 0.70 and y < 2.20
            if not boundary_gap:
                points.append((float(x), float(y), -1.5))
            points.append((float(x), float(y), 1.5))
    for z in z_values:
        for y in y_values:
            points.append((-2.0, float(y), float(z)))
            points.append((2.0, float(y), float(z)))

    openings = detect_record3d_openings(np.asarray(points), _room_candidate())

    assert [opening.kind for opening in openings] == ["cased_opening"]
    assert openings[0].width_m == pytest.approx(1.40, abs=0.10)


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
