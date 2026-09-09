import numpy as np
import pytest

from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.video_openings import detect_video_openings
from cozmo_floorplan.recon.video_rooms import VideoRoomCandidate
from cozmo_floorplan.recon.video_surfaces import VideoPlaneCandidate


def _room() -> VideoRoomCandidate:
    wall = VideoPlaneCandidate("wall", "x", -2.0, 80, 0.1)
    return VideoRoomCandidate(
        floor=VideoPlaneCandidate("horizontal", "y", 0.0, 80, 0.1),
        ceiling=VideoPlaneCandidate("horizontal", "y", 2.8, 80, 0.1),
        walls=(wall, wall, wall, wall),
        yaw_degrees=0.0,
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
    )


def _room_points(*, include_gaps: bool = True) -> np.ndarray:
    y_values = np.arange(0.05, 2.80, 0.08)
    x_values = np.arange(-2.0, 2.001, 0.04)
    z_values = np.arange(-1.5, 1.501, 0.04)
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


def test_video_openings_detect_supported_door_and_window():
    openings = detect_video_openings(_room_points(), _room())

    assert [(opening.wall_index, opening.kind) for opening in openings] == [
        (0, "door"),
        (1, "window"),
    ]
    door, window = openings
    assert isinstance(door, Record3DOpeningCandidate)
    assert door.width_m == pytest.approx(0.90, abs=0.16)
    assert window.width_m == pytest.approx(1.00, abs=0.16)
    assert door.lintel_support_points > 0


def test_solid_video_walls_do_not_invent_openings():
    assert detect_video_openings(_room_points(include_gaps=False), _room()) == ()
