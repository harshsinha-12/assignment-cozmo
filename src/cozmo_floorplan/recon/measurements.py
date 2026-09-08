"""Construct interval-bearing measurements from capture confidence."""

from typing import Any

from cozmo_floorplan.recon.lidar_config import LIDAR_UNCERTAINTY


def lidar_length(value_cm: float, confidence: str, evidence_ref: str) -> dict[str, Any]:
    uncertainty = LIDAR_UNCERTAINTY[confidence]
    half_width = uncertainty.length_half_width_cm
    return _measurement(
        value_cm,
        "cm",
        max(0.0, value_cm - half_width),
        value_cm + half_width,
        uncertainty.score,
        "roomplan_surface",
        evidence_ref,
    )


def lidar_area(value_cm2: float, confidence: str, evidence_ref: str) -> dict[str, Any]:
    uncertainty = LIDAR_UNCERTAINTY[confidence]
    half_width = value_cm2 * uncertainty.area_relative_half_width
    return _measurement(
        value_cm2,
        "cm2",
        max(0.0, value_cm2 - half_width),
        value_cm2 + half_width,
        uncertainty.score,
        "roomplan_polygon",
        evidence_ref,
    )


def derived_diagnostic(
    value: float,
    unit: str,
    evidence_ref: str,
    *,
    half_width: float,
    confidence: float = 0.80,
) -> dict[str, Any]:
    return _measurement(
        value,
        unit,
        value - half_width,
        value + half_width,
        confidence,
        "derived_roomplan_transform",
        evidence_ref,
    )


def _measurement(
    value: float,
    unit: str,
    low: float,
    high: float,
    confidence: float,
    method: str,
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
        "method": method,
        "evidence_refs": [evidence_ref],
    }


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
