"""Plane-anchored drift correction and regenerable poses-as-is ablation."""

from copy import deepcopy
from typing import Any

from cozmo_floorplan.recon.measurements import derived_diagnostic
from cozmo_floorplan.stitch.apply import rebuild_stitch_edges, transform_document
from cozmo_floorplan.stitch.config import DEFAULT_DRIFT_CONFIG, DriftConfig
from cozmo_floorplan.stitch.constraints import mean_opening_gap, opening_constraints
from cozmo_floorplan.stitch.pose_graph import room_poses

FloorPlan = dict[str, Any]


def apply_drift_correction(
    document: FloorPlan,
    *,
    enabled: bool = True,
    config: DriftConfig = DEFAULT_DRIFT_CONFIG,
) -> FloorPlan:
    """Snap rooms through shared openings, or stamp poses-as-is metadata."""

    result = deepcopy(document)
    rooms = [str(room["id"]) for room in result.get("rooms", [])]
    if len(rooms) < 2:
        result.pop("stitch", None)
        return _drop_drift_warning(result)

    constraints = opening_constraints(result)
    residual_before = mean_opening_gap(constraints)
    if enabled and constraints:
        poses = room_poses(rooms, constraints)
        result = transform_document(result, poses)
        residual_after = mean_opening_gap(opening_constraints(result))
        method = config.method
    else:
        residual_after = residual_before
        method = "none" if not enabled else config.method

    result["stitch"] = {
        "edges": rebuild_stitch_edges(
            result,
            residual_cm=residual_after,
            half_width=config.residual_half_width_cm,
        ),
        "drift_correction": {
            "enabled": bool(enabled and method != "none"),
            "method": method if enabled else "none",
            "residual_before": derived_diagnostic(
                residual_before,
                "cm",
                "stitch:opening-gap",
                half_width=config.residual_half_width_cm,
                confidence=config.residual_confidence,
            ),
            "residual_after": derived_diagnostic(
                residual_after,
                "cm",
                "stitch:opening-gap",
                half_width=config.residual_half_width_cm,
                confidence=config.residual_confidence,
            ),
            "notes": (
                "Plane-anchored opening snap: fix the first room and rigidly align each "
                "reachable neighbor so shared door/window frames coincide. Ablate with "
                "--no-drift-correction."
            ),
        },
    }
    result = _drop_drift_warning(result)
    if enabled and len(constraints) < len(rooms) - 1:
        result.setdefault("warnings", []).append(
            {
                "code": "disconnected_rooms",
                "message": "Opening constraints do not connect every reconstructed room.",
                "refs": [],
            }
        )
    if not result.get("warnings"):
        result["status"] = "ok"
        result.pop("warnings", None)
    else:
        result["status"] = "partial"
    return result


def _drop_drift_warning(document: FloorPlan) -> FloorPlan:
    warnings = [
        warning
        for warning in document.get("warnings", [])
        if "T9" not in str(warning.get("message", ""))
        and "used as-is" not in str(warning.get("message", ""))
    ]
    document["warnings"] = warnings
    return document
