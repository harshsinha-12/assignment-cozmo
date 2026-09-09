import numpy as np
import pytest

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.recon.record3d_planes import extract_manhattan_room_candidate


def _rotate_local_xz(local_xz: np.ndarray, yaw_degrees: float) -> np.ndarray:
    angle = np.deg2rad(yaw_degrees)
    rotation = np.asarray(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )
    return local_xz @ rotation.T


def _rectangular_room(
    *,
    width_m: float = 4.0,
    depth_m: float = 3.0,
    height_m: float = 2.8,
    yaw_degrees: float = 20.0,
    include_ceiling: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    x_values = np.arange(-width_m / 2, width_m / 2 + 0.001, 0.05)
    z_values = np.arange(-depth_m / 2, depth_m / 2 + 0.001, 0.05)
    y_values = np.arange(0.1, height_m, 0.1)

    wall_x = np.concatenate(
        [
            np.column_stack(
                (
                    np.full(len(z_values) * len(y_values), x),
                    np.tile(z_values, len(y_values)),
                    np.repeat(y_values, len(z_values)),
                )
            )
            for x in (-width_m / 2, width_m / 2)
        ]
    )
    wall_z = np.concatenate(
        [
            np.column_stack(
                (
                    np.tile(x_values, len(y_values)),
                    np.full(len(x_values) * len(y_values), z),
                    np.repeat(y_values, len(x_values)),
                )
            )
            for z in (-depth_m / 2, depth_m / 2)
        ]
    )
    horizontal_x, horizontal_z = np.meshgrid(x_values, z_values)
    floor = np.column_stack(
        (
            horizontal_x.ravel(),
            horizontal_z.ravel(),
            np.zeros(horizontal_x.size),
        )
    )
    horizontal = [floor]
    if include_ceiling:
        ceiling = floor.copy()
        ceiling[:, 2] = height_m
        horizontal.append(ceiling)

    # A low interior box exercises furniture rejection by vertical persistence.
    furniture_y = np.arange(0.05, 0.8, 0.05)
    furniture = np.column_stack(
        (
            np.full(len(furniture_y), 0.65),
            np.full(len(furniture_y), 0.35),
            furniture_y,
        )
    )
    local_xyz = np.concatenate([wall_x, wall_z, *horizontal, furniture])
    world_xz = _rotate_local_xz(local_xyz[:, :2], yaw_degrees)
    points = np.column_stack((world_xz[:, 0], local_xyz[:, 2], world_xz[:, 1]))

    camera_local_xz = np.asarray([[-0.5, -0.3], [0.0, 0.0], [0.6, 0.4], [0.2, -0.4]])
    camera_world_xz = _rotate_local_xz(camera_local_xz, yaw_degrees)
    cameras = np.column_stack(
        (
            camera_world_xz[:, 0],
            np.full(len(camera_world_xz), 1.4),
            camera_world_xz[:, 1],
        )
    )
    return points, cameras


def test_extracts_horizontal_levels_and_rotated_manhattan_walls():
    points, cameras = _rectangular_room()

    candidate = extract_manhattan_room_candidate(points, cameras)

    assert candidate.levels.floor_y_m == pytest.approx(0.0, abs=0.03)
    assert candidate.levels.ceiling_y_m == pytest.approx(2.8, abs=0.03)
    assert candidate.levels.ceiling_height_m == pytest.approx(2.8, abs=0.05)
    assert sorted((candidate.width_m, candidate.depth_m)) == pytest.approx(
        [3.0, 4.0], abs=0.08
    )
    assert candidate.yaw_degrees == pytest.approx(20.0, abs=1.0)
    assert len(candidate.polygon_xz_m) == 4
    assert [wall.axis for wall in candidate.walls] == ["x", "x", "z", "z"]
    assert candidate.vertical_support_columns > 100


def test_low_furniture_does_not_replace_room_walls():
    points, cameras = _rectangular_room(width_m=5.0, depth_m=3.5)

    candidate = extract_manhattan_room_candidate(points, cameras)

    assert sorted((candidate.width_m, candidate.depth_m)) == pytest.approx(
        [3.5, 5.0], abs=0.08
    )


def test_tall_inward_wardrobe_does_not_replace_outer_wall():
    points, cameras = _rectangular_room(width_m=5.0, depth_m=3.5, yaw_degrees=0.0)
    y_values = np.arange(0.1, 1.8, 0.05)
    z_values = np.arange(-1.6, 1.61, 0.04)
    wardrobe = np.column_stack(
        (
            np.full(len(y_values) * len(z_values), 2.20),
            np.repeat(y_values, len(z_values)),
            np.tile(z_values, len(y_values)),
        )
    )
    candidate = extract_manhattan_room_candidate(
        np.concatenate([points, wardrobe]), cameras
    )

    assert sorted((candidate.width_m, candidate.depth_m)) == pytest.approx(
        [3.5, 5.0], abs=0.12
    )


def test_far_adjacent_room_wall_does_not_expand_the_envelope():
    points, cameras = _rectangular_room(width_m=5.0, depth_m=3.5, yaw_degrees=0.0)
    y_values = np.arange(0.1, 1.8, 0.05)
    z_values = np.arange(-1.6, 1.61, 0.05)
    next_room = np.column_stack(
        (
            np.full(len(y_values) * len(z_values), 4.40),
            np.repeat(y_values, len(z_values)),
            np.tile(z_values, len(y_values)),
        )
    )
    candidate = extract_manhattan_room_candidate(
        np.concatenate([points, next_room]), cameras
    )

    assert sorted((candidate.width_m, candidate.depth_m)) == pytest.approx(
        [3.5, 5.0], abs=0.12
    )


def test_rejects_capture_without_a_ceiling_candidate():
    points, cameras = _rectangular_room(include_ceiling=False)
    points = points[points[:, 1] < 1.9]

    with pytest.raises(ReconstructionError, match="floor and ceiling"):
        extract_manhattan_room_candidate(points, cameras)


def test_rejects_non_finite_geometry():
    points, cameras = _rectangular_room()
    points[0, 0] = np.nan

    with pytest.raises(ReconstructionError, match="finite"):
        extract_manhattan_room_candidate(points, cameras)
