"""Associate openings across Record3D rooms that already share a world frame."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_REGISTER,
    Record3DRegisterConfig,
)
from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.record3d_planes import ManhattanRoomCandidate

COMPATIBLE_KINDS = {
    "door": frozenset({"door", "cased_opening"}),
    "cased_opening": frozenset({"door", "cased_opening"}),
    "window": frozenset({"window"}),
}


@dataclass(frozen=True, slots=True)
class OpeningAssociation:
    """One mutual nearest-neighbor opening pair in a shared world frame."""

    left_room_index: int
    left_opening_index: int
    right_room_index: int
    right_opening_index: int
    center_distance_m: float
    width_delta_m: float


def associate_record3d_openings(
    rooms: tuple[ManhattanRoomCandidate, ...],
    openings_by_room: tuple[tuple[Record3DOpeningCandidate, ...], ...],
    *,
    config: Record3DRegisterConfig = DEFAULT_RECORD3D_REGISTER,
) -> tuple[OpeningAssociation, ...]:
    """Pair facing openings only when each side's nearest partner is unique."""

    if len(rooms) != len(openings_by_room):
        raise ValueError("Each Record3D room must supply its own opening tuple")
    located: list[tuple[int, int, Record3DOpeningCandidate, tuple[float, float]]] = []
    for room_index, (room, openings) in enumerate(zip(rooms, openings_by_room, strict=True)):
        for opening_index, opening in enumerate(openings):
            located.append(
                (
                    room_index,
                    opening_index,
                    opening,
                    _opening_center_xz(room, opening),
                )
            )

    candidates: list[OpeningAssociation] = []
    for left_index, (left_room, left_opening_index, left, left_center) in enumerate(located):
        for right_room, right_opening_index, right, right_center in located[left_index + 1 :]:
            if left_room == right_room:
                continue
            if right.kind not in COMPATIBLE_KINDS.get(left.kind, frozenset()):
                continue
            width_delta = abs(left.width_m - right.width_m)
            height_delta = abs(left.height_m - right.height_m)
            if width_delta > config.maximum_width_delta_m:
                continue
            if height_delta > config.maximum_height_delta_m:
                continue
            distance = hypot(
                left_center[0] - right_center[0],
                left_center[1] - right_center[1],
            )
            if distance > config.maximum_center_distance_m:
                continue
            candidates.append(
                OpeningAssociation(
                    left_room_index=left_room,
                    left_opening_index=left_opening_index,
                    right_room_index=right_room,
                    right_opening_index=right_opening_index,
                    center_distance_m=distance,
                    width_delta_m=width_delta,
                )
            )

    return tuple(_mutual_unique_pairs(candidates))


def connected_room_ids(
    room_ids: tuple[str, ...],
    associations: tuple[OpeningAssociation, ...],
) -> set[frozenset[str]]:
    """Return connected components implied by accepted opening pairs."""

    parent = {room_id: room_id for room_id in room_ids}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for association in associations:
        union(room_ids[association.left_room_index], room_ids[association.right_room_index])
    components: dict[str, set[str]] = {}
    for room_id in room_ids:
        components.setdefault(find(room_id), set()).add(room_id)
    return {frozenset(group) for group in components.values()}


def _opening_center_xz(
    room: ManhattanRoomCandidate,
    opening: Record3DOpeningCandidate,
) -> tuple[float, float]:
    start = room.polygon_xz_m[opening.wall_index]
    end = room.polygon_xz_m[(opening.wall_index + 1) % len(room.polygon_xz_m)]
    length = hypot(end[0] - start[0], end[1] - start[1])
    if length <= 1e-9:
        return start
    along = min(length, max(0.0, opening.offset_m + 0.5 * opening.width_m))
    ratio = along / length
    return (
        start[0] + ratio * (end[0] - start[0]),
        start[1] + ratio * (end[1] - start[1]),
    )


def _mutual_unique_pairs(
    candidates: list[OpeningAssociation],
) -> list[OpeningAssociation]:
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda item: (item.center_distance_m, item.width_delta_m))
    used_openings: set[tuple[int, int]] = set()
    accepted: list[OpeningAssociation] = []
    for association in ordered:
        left = (association.left_room_index, association.left_opening_index)
        right = (association.right_room_index, association.right_opening_index)
        if left in used_openings or right in used_openings:
            continue
        used_openings.add(left)
        used_openings.add(right)
        accepted.append(association)
    return accepted
