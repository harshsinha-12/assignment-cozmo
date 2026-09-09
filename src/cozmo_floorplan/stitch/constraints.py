"""Opening-plane constraints between adjacent rooms."""

from math import hypot
from typing import Any, NamedTuple

from cozmo_floorplan.geom.se2 import point_angle


class OpeningConstraint(NamedTuple):
    """One shared opening used to snap a neighbor room onto a root-side room."""

    left_room: str
    right_room: str
    via: str
    left_origin: tuple[float, float]
    left_angle: float
    right_origin: tuple[float, float]
    right_angle: float


def opening_constraints(document: dict[str, Any]) -> list[OpeningConstraint]:
    """Build pairwise opening frames from reconstructed walls."""

    walls_by_id = {str(wall["id"]): wall for wall in document.get("walls", [])}
    walls_by_room = _walls_by_room(document)
    constraints: list[OpeningConstraint] = []
    for opening in document.get("openings", []):
        connected = [str(room_id) for room_id in opening.get("connects_room_ids", [])]
        if len(connected) != 2:
            continue
        left_room, right_room = connected
        parent = walls_by_id.get(str(opening["wall_id"]))
        parent_origin = _offset_origin(parent, opening) if parent is not None else None
        left_wall = _wall_for_room(parent, left_room, walls_by_room.get(left_room, []), parent_origin)
        right_wall = _wall_for_room(parent, right_room, walls_by_room.get(right_room, []), parent_origin)
        if left_wall is None or right_wall is None:
            continue
        left_origin = _frame_origin(left_wall, opening, parent_origin)
        right_origin = _frame_origin(right_wall, opening, parent_origin)
        constraints.append(
            OpeningConstraint(
                left_room=left_room,
                right_room=right_room,
                via=str(opening["id"]),
                left_origin=left_origin,
                left_angle=point_angle(left_wall["a"], left_wall["b"]),
                right_origin=right_origin,
                right_angle=point_angle(right_wall["a"], right_wall["b"]),
            )
        )
    return constraints


def mean_opening_gap(constraints: list[OpeningConstraint]) -> float:
    """Mean distance between paired opening origins, in centimetres."""

    if not constraints:
        return 0.0
    return sum(
        hypot(
            constraint.left_origin[0] - constraint.right_origin[0],
            constraint.left_origin[1] - constraint.right_origin[1],
        )
        for constraint in constraints
    ) / len(constraints)


def _walls_by_room(document: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {str(room["id"]): [] for room in document.get("rooms", [])}
    for wall in document.get("walls", []):
        for room_id in wall.get("room_ids", []):
            grouped.setdefault(str(room_id), []).append(wall)
    return grouped


def _wall_for_room(
    parent: dict[str, Any] | None,
    room_id: str,
    room_walls: list[dict[str, Any]],
    parent_origin: tuple[float, float] | None,
) -> dict[str, Any] | None:
    parent_ids = [str(item) for item in parent.get("room_ids", [])] if parent is not None else []
    if parent is not None and parent_ids and parent_ids[0] == room_id:
        return parent
    if not room_walls:
        return None
    origin = parent_origin or (0.0, 0.0)
    exclusive = [wall for wall in room_walls if [str(item) for item in wall.get("room_ids", [])] == [room_id]]
    candidates = exclusive or room_walls
    return min(candidates, key=lambda wall: _point_segment_distance(origin, wall["a"], wall["b"]))


def _frame_origin(
    wall: dict[str, Any],
    opening: dict[str, Any],
    parent_origin: tuple[float, float] | None,
) -> tuple[float, float]:
    if str(wall.get("id")) == str(opening.get("wall_id")):
        return _offset_origin(wall, opening)
    if parent_origin is None:
        return _midpoint(wall)
    return _closest_point(parent_origin, wall["a"], wall["b"])


def _offset_origin(wall: dict[str, Any], opening: dict[str, Any]) -> tuple[float, float]:
    start_x, start_y = float(wall["a"][0]), float(wall["a"][1])
    delta_x = float(wall["b"][0]) - start_x
    delta_y = float(wall["b"][1]) - start_y
    length = hypot(delta_x, delta_y)
    if length <= 1e-9:
        return (start_x, start_y)
    offset = float(opening["offset_along_wall"]["value"]) if "offset_along_wall" in opening else length / 2.0
    ratio = max(0.0, min(1.0, offset / length))
    return (start_x + ratio * delta_x, start_y + ratio * delta_y)


def _midpoint(wall: dict[str, Any]) -> tuple[float, float]:
    return (
        (float(wall["a"][0]) + float(wall["b"][0])) / 2.0,
        (float(wall["a"][1]) + float(wall["b"][1])) / 2.0,
    )


def _closest_point(
    point: tuple[float, float],
    start: list[float],
    end: list[float],
) -> tuple[float, float]:
    start_x, start_y = float(start[0]), float(start[1])
    delta_x = float(end[0]) - start_x
    delta_y = float(end[1]) - start_y
    length_sq = delta_x * delta_x + delta_y * delta_y
    if length_sq <= 1e-12:
        return (start_x, start_y)
    ratio = max(0.0, min(1.0, ((point[0] - start_x) * delta_x + (point[1] - start_y) * delta_y) / length_sq))
    return (start_x + ratio * delta_x, start_y + ratio * delta_y)


def _point_segment_distance(
    point: tuple[float, float],
    start: list[float],
    end: list[float],
) -> float:
    closest = _closest_point(point, start, end)
    return hypot(point[0] - closest[0], point[1] - closest[1])
