"""Apply accumulated SE(2) poses to FloorPlan geometry."""

from copy import deepcopy
from typing import Any

from shapely.geometry import Polygon

from cozmo_floorplan.geom.se2 import IDENTITY, Rigid2D
from cozmo_floorplan.recon.measurements import derived_diagnostic


def transform_document(document: dict[str, Any], poses: dict[str, Rigid2D]) -> dict[str, Any]:
    """Return a copy whose room/wall vertices have been rigidly moved."""

    result = deepcopy(document)
    room_by_id = {str(room["id"]): room for room in result.get("rooms", [])}
    for room_id, pose in poses.items():
        if pose == IDENTITY or room_id not in room_by_id:
            continue
        room = room_by_id[room_id]
        room["polygon"] = [pose.apply(point) for point in room["polygon"]]

    for wall in result.get("walls", []):
        pose = _dominant_pose(wall.get("room_ids", []), poses)
        if pose == IDENTITY:
            continue
        wall["a"] = pose.apply(wall["a"])
        wall["b"] = pose.apply(wall["b"])
    return result


def rebuild_stitch_edges(
    document: dict[str, Any],
    *,
    residual_cm: float,
    half_width: float,
) -> list[dict[str, Any]]:
    """Refresh centroid-to-centroid stitch diagnostics after correction."""

    centroids = {
        str(room["id"]): _centroid(room["polygon"])
        for room in document.get("rooms", [])
    }
    edges: list[dict[str, Any]] = []
    for opening in document.get("openings", []):
        connected = [str(room_id) for room_id in opening.get("connects_room_ids", [])]
        if len(connected) != 2 or any(room_id not in centroids for room_id in connected):
            continue
        left_room, right_room = connected
        left = centroids[left_room]
        right = centroids[right_room]
        evidence = f"opening:{opening['id']}"
        edges.append(
            {
                "left_room": left_room,
                "right_room": right_room,
                "via": str(opening["id"]),
                "dx": derived_diagnostic(right[0] - left[0], "cm", evidence, half_width=half_width),
                "dy": derived_diagnostic(right[1] - left[1], "cm", evidence, half_width=half_width),
                "dtheta": derived_diagnostic(0.0, "deg", evidence, half_width=1.0),
                "residual": derived_diagnostic(residual_cm, "cm", evidence, half_width=half_width),
            }
        )
    return edges


def _dominant_pose(room_ids: list[Any], poses: dict[str, Rigid2D]) -> Rigid2D:
    for room_id in room_ids:
        pose = poses.get(str(room_id))
        if pose is not None and pose != IDENTITY:
            return pose
    return IDENTITY


def _centroid(polygon: list[list[float]]) -> tuple[float, float]:
    shape = Polygon(polygon)
    return (float(shape.centroid.x), float(shape.centroid.y))
