"""Whole-property geometry metrics used by stitch gates."""

from itertools import combinations
from typing import Any

from shapely.geometry import Polygon
from shapely.ops import unary_union


def footprint_area(document: dict[str, Any]) -> float:
    """Return the union area of all valid room polygons in square centimetres."""

    polygons = _room_polygons(document)
    return float(unary_union(polygons).area) if polygons else 0.0


def room_overlap_area(document: dict[str, Any]) -> float:
    """Return total pairwise interior overlap across room polygons."""

    polygons = _room_polygons(document)
    return float(sum(left.intersection(right).area for left, right in combinations(polygons, 2)))


def adjacency_pairs(document: dict[str, Any]) -> set[tuple[str, str]]:
    """Return unordered room pairs declared by stitch edges."""

    edges = document.get("stitch", {}).get("edges", [])
    return {
        tuple(sorted((str(edge["left_room"]), str(edge["right_room"]))))
        for edge in edges
    }


def _room_polygons(document: dict[str, Any]) -> list[Polygon]:
    polygons: list[Polygon] = []
    for room in document.get("rooms", []):
        polygon = Polygon(room["polygon"])
        if polygon.is_valid and not polygon.is_empty:
            polygons.append(polygon)
    return polygons
