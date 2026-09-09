import numpy as np
import pytest

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.recon.video_config import VideoSurfaceConfig
from cozmo_floorplan.recon.video_rooms import fit_video_room_candidate


def _rotated_room(yaw_degrees: float = 20.0) -> tuple[np.ndarray, np.ndarray]:
    x_values = np.linspace(-2.0, 2.0, 24)
    z_values = np.linspace(-1.5, 1.5, 20)
    heights = np.linspace(0.05, 2.75, 22)
    floor_x, floor_z = np.meshgrid(x_values, z_values)
    floor = np.column_stack((floor_x.ravel(), np.zeros(floor_x.size), floor_z.ravel()))
    ceiling = floor.copy()
    ceiling[:, 1] = 2.8
    walls = []
    for x in (-2.0, 2.0):
        wall_z, wall_y = np.meshgrid(z_values, heights)
        walls.append(
            np.column_stack((np.full(wall_z.size, x), wall_y.ravel(), wall_z.ravel()))
        )
    for z in (-1.5, 1.5):
        wall_x, wall_y = np.meshgrid(x_values, heights)
        walls.append(
            np.column_stack((wall_x.ravel(), wall_y.ravel(), np.full(wall_x.size, z)))
        )
    local = np.vstack((floor, ceiling, *walls))
    angle = np.deg2rad(yaw_degrees)
    rotation = np.asarray(
        [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]
    )
    world = local.copy()
    world[:, (0, 2)] = local[:, (0, 2)] @ rotation
    cameras = np.asarray([[-0.5, 1.4, -0.2], [0.0, 1.4, 0.0], [0.5, 1.4, 0.2]])
    cameras[:, (0, 2)] = cameras[:, (0, 2)] @ rotation
    return world, cameras


def test_rotated_sparse_points_produce_camera_bracketing_room():
    points, cameras = _rotated_room()

    room = fit_video_room_candidate(
        points,
        cameras,
        surface_config=VideoSurfaceConfig(
            coordinate_bin_m=0.08,
            minimum_support_points=20,
            minimum_support_fraction=0.01,
            maximum_candidates_per_axis=6,
            minimum_candidate_separation_m=0.3,
        ),
    )

    assert room.yaw_degrees == pytest.approx(20.0, abs=1.0)
    assert room.width_m == pytest.approx(4.0, abs=0.1)
    assert room.depth_m == pytest.approx(3.0, abs=0.1)
    assert room.ceiling_height_m == pytest.approx(2.8, abs=0.05)
    assert len(room.polygon_xz_m) == 4


def test_incomplete_plane_support_is_rejected_instead_of_dimensioned():
    points, cameras = _rotated_room()
    points = points[points[:, 1] < 2.0]

    with pytest.raises(ReconstructionError, match="ceiling") as raised:
        fit_video_room_candidate(points, cameras)

    assert raised.value.warning_code == "low_confidence"
