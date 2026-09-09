"""Accumulate room poses from opening-plane constraints."""

from collections import defaultdict, deque

from cozmo_floorplan.geom.se2 import IDENTITY, Rigid2D, align_frames
from cozmo_floorplan.stitch.constraints import OpeningConstraint


def room_poses(
    room_ids: list[str],
    constraints: list[OpeningConstraint],
) -> dict[str, Rigid2D]:
    """Fix the first room and BFS-snap every reachable neighbor through openings."""

    poses = {room_id: IDENTITY for room_id in room_ids}
    if not room_ids:
        return poses

    adjacency: dict[str, list[OpeningConstraint]] = defaultdict(list)
    for constraint in constraints:
        adjacency[constraint.left_room].append(constraint)
        adjacency[constraint.right_room].append(_flipped(constraint))

    root = room_ids[0]
    visited = {root}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        for constraint in adjacency[current]:
            neighbor = constraint.right_room
            if neighbor in visited or neighbor not in poses:
                continue
            local = align_frames(
                constraint.right_origin,
                constraint.right_angle,
                constraint.left_origin,
                constraint.left_angle,
            )
            poses[neighbor] = poses[current].compose(local)
            visited.add(neighbor)
            queue.append(neighbor)
    return poses


def _flipped(constraint: OpeningConstraint) -> OpeningConstraint:
    return OpeningConstraint(
        left_room=constraint.right_room,
        right_room=constraint.left_room,
        via=constraint.via,
        left_origin=constraint.right_origin,
        left_angle=constraint.right_angle,
        right_origin=constraint.left_origin,
        right_angle=constraint.left_angle,
    )
