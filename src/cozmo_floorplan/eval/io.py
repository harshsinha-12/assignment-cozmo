"""Read validated FloorPlans and write deterministic evaluation artifacts."""

import json
from pathlib import Path
from typing import Any

from cozmo_floorplan.config import EVAL_OUTPUT_FILENAME
from cozmo_floorplan.errors import EvaluationInputError, OutputValidationError
from cozmo_floorplan.io.output import write_json_atomic
from cozmo_floorplan.schema import validate_floorplan


def load_floorplan(path: str | Path) -> dict[str, Any]:
    """Read and validate one FloorPlan input."""

    resolved = Path(path).resolve()
    try:
        document = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationInputError(f"Could not read FloorPlan {resolved}: {exc}") from exc
    if not isinstance(document, dict):
        raise EvaluationInputError(f"FloorPlan must be a JSON object: {resolved}")
    try:
        validate_floorplan(document)
    except OutputValidationError as exc:
        raise EvaluationInputError(f"Invalid FloorPlan {resolved}: {exc}") from exc
    return document


def write_evaluation(report: dict[str, Any], out_dir: str | Path) -> Path:
    """Atomically write ``eval.json``."""

    return write_json_atomic(report, Path(out_dir) / EVAL_OUTPUT_FILENAME)
