"""Build and persist the complete artifact pair for one pipeline run."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cozmo_floorplan.config import OUTPUT_FILENAME, SVG_OUTPUT_FILENAME
from cozmo_floorplan.io.output import write_json_atomic, write_text_atomic
from cozmo_floorplan.render import render_floorplan_svg
from cozmo_floorplan.schema import validate_floorplan


@dataclass(frozen=True)
class ArtifactPaths:
    """Locations produced by one successful artifact write."""

    floorplan_json: Path
    floorplan_svg: Path


def write_run_artifacts(document: dict[str, Any], out_dir: str | Path) -> ArtifactPaths:
    """Validate once, render in memory, then atomically write JSON and SVG."""

    validate_floorplan(document)
    svg = render_floorplan_svg(document)
    destination = Path(out_dir)
    json_path = write_json_atomic(document, destination / OUTPUT_FILENAME)
    svg_path = write_text_atomic(svg, destination / SVG_OUTPUT_FILENAME)
    return ArtifactPaths(floorplan_json=json_path, floorplan_svg=svg_path)
