"""Visual constants for the whole-property SVG artifact."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderStyle:
    """One immutable visual theme, expressed in SVG user units."""

    background: str = "#f7f5f0"
    ink: str = "#17202a"
    muted: str = "#667085"
    wall: str = "#253238"
    opening: str = "#168aad"
    warning: str = "#c2410c"
    room_fills: tuple[str, ...] = ("#dbeafe", "#dcfce7", "#fef3c7", "#f3e8ff")
    wall_width: float = 8.0
    opening_width: float = 10.0
    room_stroke_width: float = 1.5
    padding: float = 44.0
    header_height: float = 64.0
    sidebar_width: float = 220.0
    sidebar_gap: float = 36.0
    min_plan_width: float = 400.0
    min_plan_height: float = 260.0


DEFAULT_STYLE = RenderStyle()
