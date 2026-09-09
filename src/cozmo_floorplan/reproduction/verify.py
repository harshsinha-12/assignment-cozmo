"""Assertions over the generated synthetic reproduction artifacts."""

import json
from pathlib import Path
from typing import Any

from cozmo_floorplan.reproduction.config import (
    EXPECTED_MISSING_GATES,
    EXPECTED_PASS_GATES,
    REQUIRED_ARTIFACTS,
)
from cozmo_floorplan.schema import validate_floorplan


class ReproductionArtifactError(ValueError):
    """Generated artifacts do not match the public synthetic contract."""


def verify_reproduction_artifacts(output_dir: str | Path) -> dict[str, Any]:
    """Validate output files, FloorPlan shape, and expected synthetic gates."""

    root = Path(output_dir)
    missing = [name for name in REQUIRED_ARTIFACTS if not (root / name).is_file()]
    if missing:
        raise ReproductionArtifactError(f"Missing reproduction artifacts: {missing}")

    plan = _read_json(root / "floorplan.json")
    report = _read_json(root / "eval.json")
    validate_floorplan(plan)
    if plan.get("status") != "ok":
        raise ReproductionArtifactError("Synthetic FloorPlan status must be ok")

    expected_counts = {
        "rooms": 2,
        "walls": 8,
        "openings": 1,
        "damage": 2,
        "concealed_flags": 1,
        "scope": 2,
    }
    for key, expected in expected_counts.items():
        if len(plan.get(key, [])) != expected:
            raise ReproductionArtifactError(f"Expected {expected} {key}")

    gates = {gate.get("name"): gate for gate in report.get("gates", [])}
    _require_gate_statuses(gates, EXPECTED_PASS_GATES, "pass")
    _require_gate_statuses(gates, EXPECTED_MISSING_GATES, "missing_evidence")
    return {"plan": plan, "report": report}


def _require_gate_statuses(
    gates: dict[str | None, Any],
    names: tuple[str, ...],
    expected: str,
) -> None:
    for name in names:
        gate = gates.get(name)
        if not isinstance(gate, dict) or gate.get("status") != expected:
            raise ReproductionArtifactError(f"Expected {name}={expected}")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReproductionArtifactError(f"Could not read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReproductionArtifactError(f"Expected a JSON object: {path}")
    return value
