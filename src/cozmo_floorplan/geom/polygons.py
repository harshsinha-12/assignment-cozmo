"""Construct room polygons from unordered wall segments."""

from collections.abc import Sequence

from shapely.geometry import LineString, MultiPoint, Polygon
from shapely.ops import polygonize, unary_union

Segment = tuple[Sequence[float], Sequence[float]]


def polygon_from_wall_segments(segments: Sequence[Segment]) -> tuple[list[list[float]], bool]:
    """Return a room polygon and whether a closed wall loop was recovered."""

    lines = [LineString([start, end]) for start, end in segments]
    polygons = list(polygonize(unary_union(lines)))
    if polygons:
        polygon = max(polygons, key=lambda candidate: candidate.area)
        return _exterior_coordinates(polygon), True

    points = [tuple(float(value) for value in point) for segment in segments for point in segment]
    hull = MultiPoint(points).convex_hull
    if not isinstance(hull, Polygon) or hull.is_empty or hull.area <= 0:
        return [], False
    return _exterior_coordinates(hull), False


def _exterior_coordinates(polygon: Polygon) -> list[list[float]]:
    return [[_clean(x), _clean(y)] for x, y in list(polygon.exterior.coords)[:-1]]


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
