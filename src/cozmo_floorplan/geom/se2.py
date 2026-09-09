"""Planar rigid transforms used by multi-room drift correction."""

from dataclasses import dataclass
from math import atan2, cos, hypot, sin, pi


@dataclass(frozen=True, slots=True)
class Rigid2D:
    """SE(2) transform: rotate by theta, then translate by (dx, dy)."""

    dx: float
    dy: float
    theta: float

    def apply(self, point: list[float] | tuple[float, float]) -> list[float]:
        cosine = cos(self.theta)
        sine = sin(self.theta)
        x = float(point[0])
        y = float(point[1])
        return [_clean(cosine * x - sine * y + self.dx), _clean(sine * x + cosine * y + self.dy)]

    def compose(self, other: "Rigid2D") -> "Rigid2D":
        cosine = cos(self.theta)
        sine = sin(self.theta)
        return Rigid2D(
            dx=_clean(cosine * other.dx - sine * other.dy + self.dx),
            dy=_clean(sine * other.dx + cosine * other.dy + self.dy),
            theta=_wrap_angle(self.theta + other.theta),
        )


IDENTITY = Rigid2D(0.0, 0.0, 0.0)


def align_frames(
    source_origin: tuple[float, float],
    source_angle: float,
    target_origin: tuple[float, float],
    target_angle: float,
) -> Rigid2D:
    """Return the rigid map that sends the source frame onto the target frame."""

    theta = _parallel_delta(target_angle, source_angle)
    cosine = cos(theta)
    sine = sin(theta)
    rotated_x = cosine * source_origin[0] - sine * source_origin[1]
    rotated_y = sine * source_origin[0] + cosine * source_origin[1]
    return Rigid2D(
        dx=_clean(target_origin[0] - rotated_x),
        dy=_clean(target_origin[1] - rotated_y),
        theta=theta,
    )


def point_angle(start: list[float], end: list[float]) -> float:
    return atan2(float(end[1]) - float(start[1]), float(end[0]) - float(start[0]))


def point_distance(left: tuple[float, float], right: tuple[float, float]) -> float:
    return hypot(left[0] - right[0], left[1] - right[1])


def _parallel_delta(target: float, source: float) -> float:
    """Smallest rotation that makes the source direction parallel to the target."""

    delta = _wrap_angle(target - source)
    flipped = _wrap_angle(delta + pi)
    return delta if abs(delta) <= abs(flipped) else flipped


def _wrap_angle(theta: float) -> float:
    wrapped = (theta + pi) % (2 * pi) - pi
    return 0.0 if abs(wrapped) < 1e-12 else wrapped


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
