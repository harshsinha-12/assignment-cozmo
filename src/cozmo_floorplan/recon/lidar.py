"""Convert RoomPlan JSON surfaces into the shared FloorPlan IR."""

from math import hypot
from pathlib import Path
from statistics import median
from typing import Any

from shapely.geometry import Polygon

from cozmo_floorplan.config import FLOORPLAN_SCHEMA_VERSION
from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.geom.polygons import polygon_from_wall_segments
from cozmo_floorplan.geom.transforms import floor_segment_cm
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.roomplan import RoomPlanCapture, RoomPlanRoom, RoomPlanSurface, load_roomplan_capture
from cozmo_floorplan.recon.lidar_config import LIDAR_UNCERTAINTY, ROOMPLAN_FILENAMES
from cozmo_floorplan.recon.measurements import derived_diagnostic, lidar_area, lidar_length

FloorPlan = dict[str, Any]


def reconstruct_lidar(job: Job) -> FloorPlan:
    """Detect a supported LiDAR export and convert it into FloorPlan v0.2."""

    lidar_dir = job.root / "lidar"
    source = _find_roomplan_json(lidar_dir)
    capture = load_roomplan_capture(source)
    return _capture_to_floorplan(job, capture)


def _capture_to_floorplan(job: Job, capture: RoomPlanCapture) -> FloorPlan:
    rooms: list[dict[str, Any]] = []
    walls: list[dict[str, Any]] = []
    openings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    room_centroids: dict[str, tuple[float, float]] = {}
    seen_opening_ids: set[str] = set()
    evidence_file = capture.source.relative_to(job.root).as_posix()

    for room in capture.rooms:
        built_walls, segments = _build_walls(room, evidence_file)
        polygon, is_closed = polygon_from_wall_segments(segments)
        if len(polygon) < 3:
            raise ReconstructionError(f"Could not construct a polygon for room {room.identifier!r}")
        if not is_closed:
            warnings.append(
                {
                    "code": "incomplete_scan",
                    "message": f"Room {room.identifier!r} wall loop was open; polygon uses a convex hull.",
                    "refs": [evidence_file],
                }
            )
        confidence = _lowest_confidence(surface.confidence for surface in room.walls)
        polygon_shape = Polygon(polygon)
        room_centroids[room.identifier] = (
            float(polygon_shape.centroid.x),
            float(polygon_shape.centroid.y),
        )
        rooms.append(
            {
                "id": room.identifier,
                **({"label": room.label} if room.label else {}),
                "polygon": polygon,
                "ceiling_height": lidar_length(
                    median(surface.dimensions_m[1] for surface in room.walls) * 100.0,
                    confidence,
                    evidence_file,
                ),
                "area": lidar_area(float(polygon_shape.area), confidence, evidence_file),
                "confidence": LIDAR_UNCERTAINTY[confidence].score,
            }
        )
        walls.extend(built_walls)
        openings.extend(
            _build_openings(
                room,
                built_walls,
                evidence_file,
                seen_opening_ids,
            )
        )

    stitch_edges = _build_stitch_edges(openings, room_centroids, evidence_file)
    multi_room_without_drift_fix = len(rooms) > 1
    if multi_room_without_drift_fix:
        warnings.append(
            {
                "code": "low_confidence",
                "message": "Multi-room RoomPlan transforms are used as-is; T9 drift correction is not implemented.",
                "refs": [evidence_file],
            }
        )
        if len(stitch_edges) < len(rooms) - 1:
            warnings.append(
                {
                    "code": "disconnected_rooms",
                    "message": "RoomPlan openings do not connect every reconstructed room.",
                    "refs": [evidence_file],
                }
            )

    document: FloorPlan = {
        "version": FLOORPLAN_SCHEMA_VERSION,
        "units": "cm",
        "status": "partial" if warnings else "ok",
        "warnings": warnings,
        "floor_id": job.job_id,
        "origin": {"frame": "roomplan-world-xz", "up": [0, 1, 0]},
        "rooms": rooms,
        "walls": walls,
        "openings": openings,
        "damage": [],
        "concealed_flags": [],
        "scope": [],
        "provenance": {
            "tier": "lidar",
            "scale_source": "lidar",
            "gravity_source": "device",
            "pipeline": "cozmo-floorplan/roomplan-json-v1",
            "inputs": list(job.input_refs),
            "notes": "Metric RoomPlan surfaces projected from world x-z onto the floor plane.",
        },
    }
    if len(rooms) > 1:
        document["stitch"] = {
            "edges": stitch_edges,
            "drift_correction": {
                "enabled": False,
                "method": "none",
                "notes": "T6 preserves global RoomPlan transforms; T9 adds correction and ablation.",
            },
        }
    return document


def _build_walls(
    room: RoomPlanRoom,
    evidence_file: str,
) -> tuple[list[dict[str, Any]], list[tuple[list[float], list[float]]]]:
    walls: list[dict[str, Any]] = []
    segments: list[tuple[list[float], list[float]]] = []
    for surface in room.walls:
        start, end = floor_segment_cm(surface.pose, surface.dimensions_m[0])
        evidence_ref = f"{evidence_file}#surface:{surface.identifier}"
        room_ids = list(dict.fromkeys((room.identifier, *surface.room_ids)))
        wall = {
            "id": surface.identifier,
            "room_ids": room_ids,
            "a": start,
            "b": end,
            "length": lidar_length(
                surface.dimensions_m[0] * 100.0,
                surface.confidence,
                evidence_ref,
            ),
            "confidence": LIDAR_UNCERTAINTY[surface.confidence].score,
        }
        if surface.dimensions_m[2] > 0:
            wall["thickness"] = lidar_length(
                surface.dimensions_m[2] * 100.0,
                surface.confidence,
                evidence_ref,
            )
        walls.append(wall)
        segments.append((start, end))
    return walls, segments


def _build_openings(
    room: RoomPlanRoom,
    room_walls: list[dict[str, Any]],
    evidence_file: str,
    seen_ids: set[str],
) -> list[dict[str, Any]]:
    openings: list[dict[str, Any]] = []
    walls_by_id = {wall["id"]: wall for wall in room_walls}
    for surface in room.openings:
        if surface.identifier in seen_ids:
            continue
        wall_id = surface.wall_identifier
        if wall_id not in walls_by_id:
            wall_id = _nearest_wall_id(surface, room_walls)
        wall = walls_by_id[wall_id]
        center = [surface.pose.center_m[0] * 100.0, surface.pose.center_m[2] * 100.0]
        evidence_ref = f"{evidence_file}#surface:{surface.identifier}"
        opening = {
            "id": surface.identifier,
            "kind": surface.kind,
            "wall_id": wall_id,
            "width": lidar_length(
                surface.dimensions_m[0] * 100.0,
                surface.confidence,
                evidence_ref,
            ),
            "height": lidar_length(
                surface.dimensions_m[1] * 100.0,
                surface.confidence,
                evidence_ref,
            ),
            "offset_along_wall": lidar_length(
                _offset_along_wall(center, wall),
                surface.confidence,
                evidence_ref,
            ),
            "connects_room_ids": list(surface.connects_room_ids),
            "confidence": LIDAR_UNCERTAINTY[surface.confidence].score,
        }
        openings.append(opening)
        seen_ids.add(surface.identifier)
    return openings


def _build_stitch_edges(
    openings: list[dict[str, Any]],
    room_centroids: dict[str, tuple[float, float]],
    evidence_file: str,
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for opening in openings:
        connected = opening.get("connects_room_ids", [])
        if len(connected) != 2 or any(room_id not in room_centroids for room_id in connected):
            continue
        left_room, right_room = connected
        left_center = room_centroids[left_room]
        right_center = room_centroids[right_room]
        edges.append(
            {
                "left_room": left_room,
                "right_room": right_room,
                "via": opening["id"],
                "dx": derived_diagnostic(
                    right_center[0] - left_center[0],
                    "cm",
                    evidence_file,
                    half_width=2.5,
                ),
                "dy": derived_diagnostic(
                    right_center[1] - left_center[1],
                    "cm",
                    evidence_file,
                    half_width=2.5,
                ),
                "dtheta": derived_diagnostic(
                    0.0,
                    "deg",
                    evidence_file,
                    half_width=1.0,
                ),
                "residual": derived_diagnostic(
                    0.0,
                    "cm",
                    evidence_file,
                    half_width=2.5,
                ),
            }
        )
    return edges


def _nearest_wall_id(surface: RoomPlanSurface, walls: list[dict[str, Any]]) -> str:
    center = (surface.pose.center_m[0] * 100.0, surface.pose.center_m[2] * 100.0)
    if not walls:
        raise ReconstructionError(f"Opening {surface.identifier!r} has no wall to attach to")
    return min(walls, key=lambda wall: _point_segment_distance(center, wall["a"], wall["b"]))["id"]


def _offset_along_wall(point: list[float], wall: dict[str, Any]) -> float:
    start_x, start_y = float(wall["a"][0]), float(wall["a"][1])
    delta_x = float(wall["b"][0]) - start_x
    delta_y = float(wall["b"][1]) - start_y
    length = hypot(delta_x, delta_y)
    if length <= 1e-9:
        return 0.0
    return max(0.0, min(length, ((point[0] - start_x) * delta_x + (point[1] - start_y) * delta_y) / length))


def _point_segment_distance(
    point: tuple[float, float],
    start: list[float],
    end: list[float],
) -> float:
    offset = _offset_along_wall([point[0], point[1]], {"a": start, "b": end})
    length = hypot(float(end[0]) - float(start[0]), float(end[1]) - float(start[1]))
    if length <= 1e-9:
        return hypot(point[0] - float(start[0]), point[1] - float(start[1]))
    ratio = offset / length
    closest_x = float(start[0]) + ratio * (float(end[0]) - float(start[0]))
    closest_y = float(start[1]) + ratio * (float(end[1]) - float(start[1]))
    return hypot(point[0] - closest_x, point[1] - closest_y)


def _lowest_confidence(confidences: Any) -> str:
    ranks = {"low": 0, "medium": 1, "high": 2}
    return min(confidences, key=lambda confidence: ranks[confidence])


def _find_roomplan_json(lidar_dir: Path) -> Path:
    for filename in ROOMPLAN_FILENAMES:
        candidate = lidar_dir / filename
        if candidate.is_file():
            return candidate

    if any(lidar_dir.glob("*.usdz")):
        raise ReconstructionError(
            "USDZ LiDAR export detected, but T6 requires RoomPlan JSON alongside it.",
            warning_code="unsupported_tier",
        )
    if (lidar_dir / "metadata").is_file() or (lidar_dir / "metadata.json").is_file() or any(
        lidar_dir.glob("*.r3d")
    ):
        raise ReconstructionError(
            "Record3D depth/pose export detected; raw depth fusion awaits a real capture fixture. "
            "Export RoomPlan JSON alongside it for the current adapter.",
            warning_code="unsupported_tier",
        )
    raise ReconstructionError(
        f"No supported RoomPlan JSON found in {lidar_dir}; expected one of {ROOMPLAN_FILENAMES}"
    )
