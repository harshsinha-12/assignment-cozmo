"""Parse the documented portable RoomPlan JSON interchange format."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.geom.transforms import SurfacePose, parse_surface_pose


@dataclass(frozen=True, slots=True)
class RoomPlanSurface:
    identifier: str
    kind: str
    dimensions_m: tuple[float, float, float]
    pose: SurfacePose
    confidence: str
    wall_identifier: str | None = None
    connects_room_ids: tuple[str, ...] = ()
    room_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RoomPlanRoom:
    identifier: str
    label: str | None
    walls: tuple[RoomPlanSurface, ...]
    openings: tuple[RoomPlanSurface, ...]


@dataclass(frozen=True, slots=True)
class RoomPlanCapture:
    source: Path
    rooms: tuple[RoomPlanRoom, ...]


def load_roomplan_capture(path: str | Path) -> RoomPlanCapture:
    """Load one CapturedRoom or portable multi-room wrapper."""

    source = Path(path).resolve()
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReconstructionError(f"Could not read RoomPlan JSON {source}: {exc}") from exc
    if not isinstance(document, dict):
        raise ReconstructionError("RoomPlan JSON root must be an object")

    raw_rooms = document.get("rooms")
    if raw_rooms is None:
        raw_rooms = [document]
    if not isinstance(raw_rooms, list) or not raw_rooms:
        raise ReconstructionError("RoomPlan JSON must contain at least one room")

    rooms = tuple(_parse_room(raw_room, index) for index, raw_room in enumerate(raw_rooms))
    return RoomPlanCapture(source=source, rooms=rooms)


def _parse_room(raw_room: Any, index: int) -> RoomPlanRoom:
    if not isinstance(raw_room, dict):
        raise ReconstructionError(f"RoomPlan room at index {index} must be an object")
    identifier = _identifier(raw_room, f"room_{index}")
    walls = _surface_list(raw_room.get("walls", []), "wall")
    if len(walls) < 3:
        raise ReconstructionError(f"RoomPlan room {identifier!r} needs at least three walls")
    openings = tuple(
        surface
        for key, kind in (("doors", "door"), ("windows", "window"), ("openings", "cased_opening"))
        for surface in _surface_list(raw_room.get(key, []), kind)
    )
    label_value = raw_room.get("label")
    return RoomPlanRoom(
        identifier=identifier,
        label=str(label_value) if label_value is not None else None,
        walls=walls,
        openings=openings,
    )


def _surface_list(value: Any, kind: str) -> tuple[RoomPlanSurface, ...]:
    if not isinstance(value, list):
        raise ReconstructionError(f"RoomPlan {kind} collection must be an array")
    return tuple(_parse_surface(surface, kind, index) for index, surface in enumerate(value))


def _parse_surface(raw: Any, kind: str, index: int) -> RoomPlanSurface:
    if not isinstance(raw, dict):
        raise ReconstructionError(f"RoomPlan {kind} at index {index} must be an object")
    dimensions = _dimensions(raw.get("dimensions"))
    confidence = str(raw.get("confidence", "medium")).lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "medium"
    connects = raw.get("connectsRoomIds", raw.get("connects_room_ids", []))
    room_ids = raw.get("roomIds", raw.get("room_ids", []))
    return RoomPlanSurface(
        identifier=_identifier(raw, f"{kind}_{index}"),
        kind=kind,
        dimensions_m=dimensions,
        pose=parse_surface_pose(raw),
        confidence=confidence,
        wall_identifier=_optional_string(raw.get("wallIdentifier", raw.get("wall_id"))),
        connects_room_ids=_string_tuple(connects, "connectsRoomIds"),
        room_ids=_string_tuple(room_ids, "roomIds"),
    )


def _dimensions(value: Any) -> tuple[float, float, float]:
    if isinstance(value, list) and len(value) == 3:
        dimensions = tuple(float(component) for component in value)
    elif isinstance(value, dict) and all(axis in value for axis in ("x", "y", "z")):
        dimensions = float(value["x"]), float(value["y"]), float(value["z"])
    else:
        raise ReconstructionError("RoomPlan surface dimensions must be a 3-vector")
    if dimensions[0] <= 0 or dimensions[1] <= 0:
        raise ReconstructionError("RoomPlan surface width and height must be positive")
    return dimensions  # type: ignore[return-value]


def _identifier(value: dict[str, Any], fallback: str) -> str:
    identifier = value.get("identifier", value.get("id", fallback))
    return str(identifier)


def _optional_string(value: Any) -> str | None:
    return str(value) if value is not None else None


def _string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ReconstructionError(f"RoomPlan field {field!r} must be an array")
    return tuple(str(item) for item in value)
