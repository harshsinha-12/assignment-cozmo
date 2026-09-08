"""Map centimetre floor coordinates into a readable SVG canvas."""

from dataclasses import dataclass
from math import isfinite
from typing import Any

from shapely.geometry import Polygon

from cozmo_floorplan.render.config import DEFAULT_STYLE, RenderStyle

Point = tuple[float, float]


@dataclass(frozen=True)
class SvgLayout:
    """Canvas dimensions and the y-up floor to y-down SVG transform."""

    min_x: float
    max_y: float
    x_offset: float
    y_offset: float
    canvas_width: float
    canvas_height: float
    plan_area_right: float

    def point(self, coordinates: list[float] | tuple[float, float]) -> Point:
        """Convert one FloorPlan point without changing its metric scale."""

        return (
            self.x_offset + float(coordinates[0]) - self.min_x,
            self.y_offset + self.max_y - float(coordinates[1]),
        )


def build_layout(document: dict[str, Any], style: RenderStyle = DEFAULT_STYLE) -> SvgLayout:
    """Fit all plan geometry into a canvas with a fixed information sidebar."""

    points = _geometry_points(document)
    if points:
        xs, ys = zip(*points, strict=True)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
    else:
        min_x = min_y = 0.0
        max_x = max_y = 0.0

    geometry_width = max_x - min_x
    geometry_height = max_y - min_y
    plan_width = max(geometry_width, style.min_plan_width)
    plan_height = max(geometry_height, style.min_plan_height)
    x_offset = style.padding + (plan_width - geometry_width) / 2.0
    y_offset = style.header_height + style.padding + (plan_height - geometry_height) / 2.0
    plan_area_right = style.padding * 2.0 + plan_width
    canvas_width = plan_area_right + style.sidebar_gap + style.sidebar_width
    canvas_height = style.header_height + style.padding * 2.0 + plan_height
    return SvgLayout(
        min_x=min_x,
        max_y=max_y,
        x_offset=x_offset,
        y_offset=y_offset,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        plan_area_right=plan_area_right,
    )


def room_label_point(room: dict[str, Any], layout: SvgLayout) -> Point:
    """Choose a label point guaranteed to lie inside a valid room polygon."""

    shape = Polygon(room["polygon"])
    representative = shape.representative_point()
    return layout.point((representative.x, representative.y))


def _geometry_points(document: dict[str, Any]) -> list[Point]:
    raw_points: list[list[float]] = []
    for room in document.get("rooms", []):
        raw_points.extend(room.get("polygon", []))
    for wall in document.get("walls", []):
        raw_points.extend((wall.get("a", []), wall.get("b", [])))
    return [
        (float(point[0]), float(point[1]))
        for point in raw_points
        if len(point) == 2 and all(isfinite(float(value)) for value in point)
    ]
