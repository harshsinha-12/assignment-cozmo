"""Parse portable RoomPlan surface transforms into world-space axes."""

from dataclasses import dataclass
from math import sqrt
from typing import Any

from cozmo_floorplan.errors import ReconstructionError


@dataclass(frozen=True, slots=True)
class SurfacePose:
    """World-space centre and normalized local x-axis for one surface."""

    center_m: tuple[float, float, float]
    x_axis: tuple[float, float, float]


def parse_surface_pose(surface: dict[str, Any]) -> SurfacePose:
    """Read either explicit pose fields or a 4x4 column-major transform."""

    if "center" in surface and "xAxis" in surface:
        center = _vector3(surface["center"], "center")
        x_axis = _normalize(_vector3(surface["xAxis"], "xAxis"))
        return SurfacePose(center, x_axis)

    transform = surface.get("transform")
    if isinstance(transform, list) and len(transform) == 16:
        values = tuple(float(value) for value in transform)
        return SurfacePose(
            center_m=(values[12], values[13], values[14]),
            x_axis=_normalize((values[0], values[1], values[2])),
        )
    if (
        isinstance(transform, list)
        and len(transform) == 4
        and all(isinstance(row, list) and len(row) == 4 for row in transform)
    ):
        rows = [[float(value) for value in row] for row in transform]
        return SurfacePose(
            center_m=(rows[0][3], rows[1][3], rows[2][3]),
            x_axis=_normalize((rows[0][0], rows[1][0], rows[2][0])),
        )
    raise ReconstructionError(
        "RoomPlan surface needs center+xAxis or a 16-value column-major/4x4 row-major transform"
    )


def floor_segment_cm(pose: SurfacePose, width_m: float) -> tuple[list[float], list[float]]:
    """Project a surface's local width axis onto the world x-z floor plane."""

    horizontal_x, horizontal_z = pose.x_axis[0], pose.x_axis[2]
    magnitude = sqrt(horizontal_x * horizontal_x + horizontal_z * horizontal_z)
    if magnitude <= 1e-9:
        raise ReconstructionError("RoomPlan surface width axis is vertical; cannot form a floor-plan wall")
    horizontal_x /= magnitude
    horizontal_z /= magnitude
    half_width_cm = width_m * 100.0 / 2.0
    center_x_cm = pose.center_m[0] * 100.0
    center_z_cm = pose.center_m[2] * 100.0
    return (
        [center_x_cm - horizontal_x * half_width_cm, center_z_cm - horizontal_z * half_width_cm],
        [center_x_cm + horizontal_x * half_width_cm, center_z_cm + horizontal_z * half_width_cm],
    )


def _vector3(value: Any, field: str) -> tuple[float, float, float]:
    if isinstance(value, list) and len(value) == 3:
        return tuple(float(component) for component in value)  # type: ignore[return-value]
    if isinstance(value, dict) and all(axis in value for axis in ("x", "y", "z")):
        return float(value["x"]), float(value["y"]), float(value["z"])
    raise ReconstructionError(f"RoomPlan field {field!r} must be a 3-vector")


def _normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    magnitude = sqrt(sum(component * component for component in vector))
    if magnitude <= 1e-9:
        raise ReconstructionError("RoomPlan transform contains a zero-length x-axis")
    return tuple(component / magnitude for component in vector)  # type: ignore[return-value]
