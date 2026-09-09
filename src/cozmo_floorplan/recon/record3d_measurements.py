"""Build explicitly uncalibrated measurements for Record3D candidates."""

from __future__ import annotations

from typing import Any

from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_OUTPUT,
    Record3DOutputConfig,
)


def record3d_length(
    value_cm: float,
    evidence_ref: str,
    *,
    half_width_cm: float,
    config: Record3DOutputConfig = DEFAULT_RECORD3D_OUTPUT,
) -> dict[str, Any]:
    """Return a metric length with a disclosed candidate-stage interval."""

    return _measurement(
        value_cm,
        "cm",
        max(0.0, value_cm - half_width_cm),
        value_cm + half_width_cm,
        config.confidence,
        evidence_ref,
    )


def record3d_area(
    value_cm2: float,
    evidence_ref: str,
    *,
    relative_half_width: float | None = None,
    config: Record3DOutputConfig = DEFAULT_RECORD3D_OUTPUT,
) -> dict[str, Any]:
    """Return polygon area with the uncalibrated relative interval policy."""

    half_width = value_cm2 * (
        config.area_relative_half_width
        if relative_half_width is None
        else relative_half_width
    )
    return _measurement(
        value_cm2,
        "cm2",
        max(0.0, value_cm2 - half_width),
        value_cm2 + half_width,
        config.confidence,
        evidence_ref,
    )


def _measurement(
    value: float,
    unit: str,
    low: float,
    high: float,
    confidence: float,
    evidence_ref: str,
) -> dict[str, Any]:
    return {
        "value": _clean(value),
        "unit": unit,
        "interval": {
            "low": _clean(low),
            "high": _clean(high),
            "confidence": confidence,
        },
        "method": "record3d_manhattan_candidate_uncalibrated",
        "evidence_refs": [evidence_ref],
    }


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
