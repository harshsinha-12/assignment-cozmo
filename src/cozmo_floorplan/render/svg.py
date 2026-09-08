"""Compose a self-contained, deterministic whole-property SVG."""

from math import atan2, degrees, hypot
from typing import Any
from xml.etree import ElementTree as ET

from cozmo_floorplan.render.config import DEFAULT_STYLE, RenderStyle
from cozmo_floorplan.render.layout import SvgLayout, build_layout, room_label_point

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NAMESPACE)


def render_floorplan_svg(
    document: dict[str, Any],
    style: RenderStyle = DEFAULT_STYLE,
) -> str:
    """Render FloorPlan v0.2 data without estimating any new dimensions."""

    layout = build_layout(document, style)
    root = ET.Element(
        _tag("svg"),
        {
            "viewBox": f"0 0 {_number(layout.canvas_width)} {_number(layout.canvas_height)}",
            "role": "img",
            "aria-labelledby": "plan-title plan-description",
        },
    )
    ET.SubElement(root, _tag("title"), {"id": "plan-title"}).text = _title(document)
    ET.SubElement(root, _tag("desc"), {"id": "plan-description"}).text = (
        "Dimensioned whole-property plan in centimetres with rooms, walls, openings, and confidence intervals."
    )
    _add_style(root, style)
    ET.SubElement(
        root,
        _tag("rect"),
        {
            "class": "background",
            "width": "100%",
            "height": "100%",
        },
    )
    _add_header(root, document, style)
    plan_group = ET.SubElement(root, _tag("g"), {"id": "property-plan"})
    _add_rooms(plan_group, document, layout, style)
    _add_walls(plan_group, document, layout)
    _add_openings(plan_group, document, layout)
    _add_wall_dimensions(plan_group, document, layout)
    if not document.get("rooms") and not document.get("walls"):
        _add_empty_state(plan_group, layout, style)
    _add_sidebar(root, document, layout, style)
    _add_scale_bar(root, layout, style)
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"


def _add_style(root: ET.Element, style: RenderStyle) -> None:
    rules = f"""
        .background {{ fill: {style.background}; }}
        text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: {style.ink}; }}
        .title {{ font-size: 23px; font-weight: 700; }}
        .subtitle, .meta {{ font-size: 12px; fill: {style.muted}; }}
        .room {{ stroke: {style.wall}; stroke-width: {style.room_stroke_width}; }}
        .wall {{ stroke: {style.wall}; stroke-width: {style.wall_width}; stroke-linecap: square; }}
        .opening-gap {{ stroke: {style.background}; stroke-width: {style.opening_width + 3}; }}
        .opening {{ stroke: {style.opening}; stroke-width: {style.opening_width}; stroke-linecap: butt; }}
        .room-label {{ font-size: 18px; font-weight: 700; text-anchor: middle; }}
        .room-meta {{ font-size: 11px; fill: {style.muted}; text-anchor: middle; }}
        .dimension {{ font-size: 11px; text-anchor: middle; paint-order: stroke; stroke: {style.background}; stroke-width: 4px; stroke-linejoin: round; }}
        .sidebar-heading {{ font-size: 14px; font-weight: 700; }}
        .status-warning {{ fill: {style.warning}; font-weight: 700; }}
        .scale {{ stroke: {style.ink}; stroke-width: 2; }}
    """
    ET.SubElement(root, _tag("style")).text = rules


def _add_header(root: ET.Element, document: dict[str, Any], style: RenderStyle) -> None:
    title = ET.SubElement(root, _tag("text"), {"class": "title", "x": _number(style.padding), "y": "33"})
    title.text = _title(document)
    subtitle = ET.SubElement(root, _tag("text"), {"class": "subtitle", "x": _number(style.padding), "y": "52"})
    subtitle.text = "Whole-property plan · all dimensions in cm · intervals shown at stated confidence"


def _add_rooms(
    parent: ET.Element,
    document: dict[str, Any],
    layout: SvgLayout,
    style: RenderStyle,
) -> None:
    for index, room in enumerate(document.get("rooms", [])):
        points = " ".join(_point_text(layout.point(point)) for point in room["polygon"])
        ET.SubElement(
            parent,
            _tag("polygon"),
            {
                "class": "room",
                "id": f"room-{room['id']}",
                "points": points,
                "fill": style.room_fills[index % len(style.room_fills)],
                "fill-opacity": "0.72",
            },
        )
        x, y = room_label_point(room, layout)
        label = ET.SubElement(parent, _tag("text"), {"class": "room-label", "x": _number(x), "y": _number(y - 4)})
        label.text = str(room.get("label") or room["id"])
        metadata = ET.SubElement(parent, _tag("text"), {"class": "room-meta", "x": _number(x), "y": _number(y + 15)})
        metadata.text = f"{_measurement(room['area'])} · ceiling {_measurement(room['ceiling_height'])}"


def _add_walls(parent: ET.Element, document: dict[str, Any], layout: SvgLayout) -> None:
    for wall in document.get("walls", []):
        start = layout.point(wall["a"])
        end = layout.point(wall["b"])
        ET.SubElement(parent, _tag("line"), _line_attributes(start, end, "wall", f"wall-{wall['id']}"))


def _add_openings(parent: ET.Element, document: dict[str, Any], layout: SvgLayout) -> None:
    walls = {wall["id"]: wall for wall in document.get("walls", [])}
    for opening in document.get("openings", []):
        wall = walls.get(opening["wall_id"])
        if wall is None:
            continue
        start, end = _opening_segment(opening, wall, layout)
        ET.SubElement(parent, _tag("line"), _line_attributes(start, end, "opening-gap"))
        opening_line = ET.SubElement(
            parent,
            _tag("line"),
            _line_attributes(start, end, f"opening opening-{opening['kind']}", f"opening-{opening['id']}"),
        )
        ET.SubElement(opening_line, _tag("title")).text = (
            f"{opening['kind'].replace('_', ' ').title()}: {_measurement(opening['width'], include_interval=True)}"
        )


def _add_wall_dimensions(parent: ET.Element, document: dict[str, Any], layout: SvgLayout) -> None:
    seen: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    for wall in document.get("walls", []):
        floor_start = (float(wall["a"][0]), float(wall["a"][1]))
        floor_end = (float(wall["b"][0]), float(wall["b"][1]))
        key = tuple(sorted((floor_start, floor_end)))
        if key in seen:
            continue
        seen.add(key)
        start = layout.point(wall["a"])
        end = layout.point(wall["b"])
        dx, dy = end[0] - start[0], end[1] - start[1]
        segment_length = hypot(dx, dy)
        if segment_length <= 1e-9:
            continue
        normal_x, normal_y = -dy / segment_length, dx / segment_length
        x = (start[0] + end[0]) / 2.0 + normal_x * 16.0
        y = (start[1] + end[1]) / 2.0 + normal_y * 16.0
        angle = degrees(atan2(dy, dx))
        if angle > 90 or angle < -90:
            angle += 180
        label = ET.SubElement(
            parent,
            _tag("text"),
            {
                "class": "dimension",
                "x": _number(x),
                "y": _number(y),
                "transform": f"rotate({_number(angle)} {_number(x)} {_number(y)})",
            },
        )
        label.text = _measurement(wall["length"], include_interval=True)


def _add_sidebar(root: ET.Element, document: dict[str, Any], layout: SvgLayout, style: RenderStyle) -> None:
    x = layout.plan_area_right + style.sidebar_gap
    y = style.header_height + style.padding
    status = str(document.get("status", "unknown"))
    heading = ET.SubElement(root, _tag("text"), {"class": "sidebar-heading", "x": _number(x), "y": _number(y)})
    heading.text = "Plan summary"
    lines = [
        ("Status", status.upper()),
        ("Rooms", str(len(document.get("rooms", [])))),
        ("Walls", str(len(document.get("walls", [])))),
        ("Openings", str(len(document.get("openings", [])))),
        ("Damage regions", str(len(document.get("damage", [])))),
        ("Scope lines", str(len(document.get("scope", [])))),
        ("Capture tier", str(document.get("provenance", {}).get("tier", "unknown"))),
        ("Scale source", str(document.get("provenance", {}).get("scale_source", "unknown"))),
    ]
    for index, (key, value) in enumerate(lines, start=1):
        line_y = y + index * 24
        item = ET.SubElement(root, _tag("text"), {"class": "meta", "x": _number(x), "y": _number(line_y)})
        item.text = f"{key}: "
        value_span = ET.SubElement(item, _tag("tspan"), {"class": "status-warning" if key == "Status" and status != "ok" else ""})
        value_span.text = value
    warning_count = len(document.get("warnings", []))
    if warning_count:
        warning = ET.SubElement(root, _tag("text"), {"class": "meta status-warning", "x": _number(x), "y": _number(y + (len(lines) + 2) * 24)})
        warning.text = f"{warning_count} warning{'s' if warning_count != 1 else ''} — see floorplan.json"


def _add_scale_bar(root: ET.Element, layout: SvgLayout, style: RenderStyle) -> None:
    x = style.padding
    y = layout.canvas_height - 22.0
    ET.SubElement(root, _tag("line"), _line_attributes((x, y), (x + 100.0, y), "scale"))
    for tick_x in (x, x + 100.0):
        ET.SubElement(root, _tag("line"), _line_attributes((tick_x, y - 5.0), (tick_x, y + 5.0), "scale"))
    label = ET.SubElement(root, _tag("text"), {"class": "meta", "x": _number(x), "y": _number(y - 9.0)})
    label.text = "100 cm"


def _add_empty_state(parent: ET.Element, layout: SvgLayout, style: RenderStyle) -> None:
    x = style.padding + (layout.plan_area_right - style.padding * 2.0) / 2.0
    y = style.header_height + (layout.canvas_height - style.header_height) / 2.0
    message = ET.SubElement(parent, _tag("text"), {"class": "room-label", "x": _number(x), "y": _number(y)})
    message.text = "No geometry available"
    detail = ET.SubElement(parent, _tag("text"), {"class": "room-meta", "x": _number(x), "y": _number(y + 22.0)})
    detail.text = "See floorplan.json warnings and capture provenance."


def _opening_segment(
    opening: dict[str, Any],
    wall: dict[str, Any],
    layout: SvgLayout,
) -> tuple[tuple[float, float], tuple[float, float]]:
    ax, ay = float(wall["a"][0]), float(wall["a"][1])
    bx, by = float(wall["b"][0]), float(wall["b"][1])
    dx, dy = bx - ax, by - ay
    wall_length = hypot(dx, dy)
    if wall_length <= 1e-9:
        point = layout.point((ax, ay))
        return point, point
    center = float(opening.get("offset_along_wall", {}).get("value", wall_length / 2.0))
    half_width = float(opening["width"]["value"]) / 2.0
    start_offset = max(0.0, center - half_width)
    end_offset = min(wall_length, center + half_width)
    unit_x, unit_y = dx / wall_length, dy / wall_length
    return (
        layout.point((ax + unit_x * start_offset, ay + unit_y * start_offset)),
        layout.point((ax + unit_x * end_offset, ay + unit_y * end_offset)),
    )


def _measurement(measurement: dict[str, Any], *, include_interval: bool = False) -> str:
    value = _number(float(measurement["value"]))
    unit = "cm²" if measurement["unit"] == "cm2" else str(measurement["unit"])
    if not include_interval:
        return f"{value} {unit}"
    interval = measurement["interval"]
    confidence = _number(float(interval["confidence"]) * 100.0)
    return f"{value} {unit} [{_number(float(interval['low']))}–{_number(float(interval['high']))}; {confidence}%]"


def _title(document: dict[str, Any]) -> str:
    return f"Floor plan · {document.get('floor_id', 'unnamed job')}"


def _line_attributes(
    start: tuple[float, float],
    end: tuple[float, float],
    css_class: str,
    identifier: str | None = None,
) -> dict[str, str]:
    attributes = {
        "class": css_class,
        "x1": _number(start[0]),
        "y1": _number(start[1]),
        "x2": _number(end[0]),
        "y2": _number(end[1]),
    }
    if identifier is not None:
        attributes["id"] = identifier
    return attributes


def _point_text(point: tuple[float, float]) -> str:
    return f"{_number(point[0])},{_number(point[1])}"


def _number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _tag(local_name: str) -> str:
    return f"{{{SVG_NAMESPACE}}}{local_name}"
