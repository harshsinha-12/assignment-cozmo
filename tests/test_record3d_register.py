from dataclasses import replace

from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.record3d_planes import (
    HorizontalPlaneLevels,
    ManhattanRoomCandidate,
)
from cozmo_floorplan.recon.record3d_register import associate_record3d_openings


def _room(*, polygon: tuple[tuple[float, float], ...]) -> ManhattanRoomCandidate:
    xs = [point[0] for point in polygon]
    zs = [point[1] for point in polygon]
    return ManhattanRoomCandidate(
        levels=HorizontalPlaneLevels(
            floor_y_m=0.0,
            ceiling_y_m=2.8,
            floor_support_points=100,
            ceiling_support_points=100,
        ),
        yaw_degrees=0.0,
        walls=(),
        polygon_xz_m=polygon,
        width_m=max(xs) - min(xs),
        depth_m=max(zs) - min(zs),
        vertical_support_columns=50,
    )


def _door(*, wall_index: int, offset_m: float, width_m: float = 0.80) -> Record3DOpeningCandidate:
    return Record3DOpeningCandidate(
        wall_index=wall_index,
        kind="door",
        offset_m=offset_m,
        width_m=width_m,
        height_m=2.00,
        sparse_profile_bins=16,
        lintel_support_points=40,
    )


def test_facing_doors_in_a_shared_world_frame_are_associated():
    left = _room(polygon=((0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)))
    right = _room(polygon=((4.1, 0.0), (8.1, 0.0), (8.1, 3.0), (4.1, 3.0)))
    left_door = _door(wall_index=1, offset_m=1.1)
    right_door = _door(wall_index=3, offset_m=1.1)

    associations = associate_record3d_openings((left, right), ((left_door,), (right_door,)))

    assert len(associations) == 1
    assert associations[0].left_room_index == 0
    assert associations[0].right_room_index == 1
    assert associations[0].center_distance_m < 0.2


def test_distant_or_mismatched_openings_are_not_associated():
    left = _room(polygon=((0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)))
    far = _room(polygon=((20.0, 0.0), (24.0, 0.0), (24.0, 3.0), (20.0, 3.0)))
    wide = replace(_door(wall_index=1, offset_m=1.1), width_m=2.0)

    distant = associate_record3d_openings(
        (left, far),
        ((_door(wall_index=1, offset_m=1.1),), (_door(wall_index=3, offset_m=1.1),)),
    )
    mismatched = associate_record3d_openings(
        (left, _room(polygon=((4.1, 0.0), (8.1, 0.0), (8.1, 3.0), (4.1, 3.0)))),
        ((_door(wall_index=1, offset_m=1.1),), (wide,)),
    )

    assert distant == ()
    assert mismatched == ()
