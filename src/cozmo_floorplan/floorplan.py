"""Factories for schema-valid FloorPlan documents."""

from typing import Any

from cozmo_floorplan.config import FLOORPLAN_SCHEMA_VERSION, PIPELINE_NAME, SUPPORTED_TIERS


def build_failed_floorplan(
    *,
    job_id: str,
    tier: str,
    warning_code: str,
    message: str,
    input_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Build the stable failure shape used before and between adapters."""

    safe_tier = tier if tier in SUPPORTED_TIERS else "mixed"
    return {
        "version": FLOORPLAN_SCHEMA_VERSION,
        "units": "cm",
        "status": "failed",
        "warnings": [{"code": warning_code, "message": message}],
        "floor_id": job_id or "unknown_job",
        "origin": {"frame": "job-floor-plane", "up": [0, 0, 1]},
        "rooms": [],
        "walls": [],
        "openings": [],
        "damage": [],
        "concealed_flags": [],
        "scope": [],
        "provenance": {
            "tier": safe_tier,
            "scale_source": "none",
            "gravity_source": "unknown",
            "pipeline": PIPELINE_NAME,
            "inputs": list(input_refs),
            "notes": "Structured T13 stub output; reconstruction adapters are not implemented yet.",
        },
    }
