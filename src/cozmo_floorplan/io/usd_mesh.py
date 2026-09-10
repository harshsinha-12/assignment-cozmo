"""Read semantic room meshes exported as USD, USDA, or USDZ."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.geom.transforms import SurfacePose
from cozmo_floorplan.io.roomplan import RoomPlanCapture, RoomPlanRoom, RoomPlanSurface

USD_EXTENSIONS = (".usd", ".usda", ".usdz")

_MESH_PATTERN = re.compile(r'\bdef\s+Mesh\s+"([^"]+)"')
_EXTENT_PATTERN = re.compile(
    r"extent\s*=\s*\[\s*\(([^)]*)\)\s*,\s*\(([^)]*)\)\s*\]",
    re.DOTALL,
)
_TRANSFORM_PATTERN = re.compile(
    r"matrix4d\s+xformOp:transform\s*=\s*\(\s*"
    r"\(([^)]*)\)\s*,\s*\(([^)]*)\)\s*,\s*"
    r"\(([^)]*)\)\s*,\s*\(([^)]*)\)\s*\)",
    re.DOTALL,
)


def discover_usd_room_meshes(lidar_dir: Path) -> tuple[Path, ...]:
    """Return supported USD room exports in deterministic order."""

    return tuple(
        sorted(
            path
            for path in lidar_dir.iterdir()
            if path.is_file() and path.suffix.lower() in USD_EXTENSIONS
        )
    )


def load_usd_room_capture(
    path: str | Path,
    *,
    room_identifier: str,
) -> RoomPlanCapture:
    """Convert semantic Wall/Door/Window meshes into RoomPlan-like surfaces."""

    source = Path(path).resolve()
    text = _read_usda(source)
    walls: list[RoomPlanSurface] = []
    openings: list[RoomPlanSurface] = []
    for name, block in _mesh_blocks(text):
        kind = _semantic_kind(name)
        if kind is None:
            continue
        surface = _parse_surface(name, kind, block)
        if kind == "wall":
            walls.append(surface)
        else:
            openings.append(surface)

    if len(walls) < 3:
        raise ReconstructionError(
            f"USD room mesh {source.name!r} needs at least three named Wall meshes"
        )
    return RoomPlanCapture(
        source=source,
        rooms=(
            RoomPlanRoom(
                identifier=room_identifier,
                label=room_identifier.replace("-", " ").title(),
                walls=tuple(walls),
                openings=tuple(openings),
            ),
        ),
    )


def _read_usda(source: Path) -> str:
    if source.suffix.lower() == ".usda":
        try:
            return source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ReconstructionError(f"Could not read USDA {source}: {exc}") from exc

    usdcat = shutil.which("usdcat")
    if usdcat is None:
        raise ReconstructionError(
            "Binary USD/USDZ export requires Pixar usdcat on PATH; export ASCII USDA "
            "or RoomPlan JSON when usdcat is unavailable.",
            warning_code="unsupported_tier",
        )
    try:
        completed = subprocess.run(
            [usdcat, source.as_posix()],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReconstructionError(f"Could not decode USD export {source}: {exc}") from exc
    return completed.stdout


def _mesh_blocks(text: str) -> tuple[tuple[str, str], ...]:
    blocks: list[tuple[str, str]] = []
    for match in _MESH_PATTERN.finditer(text):
        opening = text.find("{", match.end())
        if opening < 0:
            continue
        depth = 0
        for index in range(opening, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append((match.group(1), text[opening + 1 : index]))
                    break
    return tuple(blocks)


def _semantic_kind(name: str) -> str | None:
    lowered = name.lower()
    if lowered.startswith("wall"):
        return "wall"
    if lowered.startswith("door"):
        return "door"
    if lowered.startswith("window"):
        return "window"
    return None


def _parse_surface(name: str, kind: str, block: str) -> RoomPlanSurface:
    extent_match = _EXTENT_PATTERN.search(block)
    transform_match = _TRANSFORM_PATTERN.search(block)
    if extent_match is None or transform_match is None:
        raise ReconstructionError(
            f"Semantic USD mesh {name!r} needs extent and xformOp:transform"
        )
    minimum = _numbers(extent_match.group(1), expected=3, field=f"{name} extent")
    maximum = _numbers(extent_match.group(2), expected=3, field=f"{name} extent")
    rows = tuple(
        _numbers(transform_match.group(index), expected=4, field=f"{name} transform")
        for index in range(1, 5)
    )
    dimensions = tuple(maximum[index] - minimum[index] for index in range(3))
    if dimensions[0] <= 0 or dimensions[1] <= 0:
        raise ReconstructionError(f"Semantic USD mesh {name!r} has invalid dimensions")
    return RoomPlanSurface(
        identifier=name,
        kind=kind,
        dimensions_m=dimensions,
        pose=SurfacePose(
            center_m=(rows[3][0], rows[3][1], rows[3][2]),
            x_axis=(rows[0][0], rows[0][1], rows[0][2]),
        ),
        confidence="medium",
    )


def _numbers(value: str, *, expected: int, field: str) -> tuple[float, ...]:
    try:
        numbers = tuple(float(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise ReconstructionError(f"USD {field} contains a non-numeric value") from exc
    if len(numbers) != expected:
        raise ReconstructionError(f"USD {field} must contain {expected} numbers")
    return numbers
