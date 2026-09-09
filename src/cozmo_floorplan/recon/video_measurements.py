"""Candidate-stage interval measurements for calibrated video geometry."""

from __future__ import annotations

from typing import Any

from cozmo_floorplan.recon.video_config import DEFAULT_VIDEO_OUTPUT, VideoOutputConfig


def video_length(
    value_cm: float,
    evidence_ref: str,
    *,
    ceiling: bool = False,
    config: VideoOutputConfig = DEFAULT_VIDEO_OUTPUT,
) -> dict[str, Any]:
    relative = value_cm * config.length_relative_half_width
    minimum = (
        config.minimum_ceiling_half_width_cm
        if ceiling
        else config.minimum_length_half_width_cm
    )
    return _measurement(
        value_cm,
        "cm",
        max(minimum, relative),
        evidence_ref,
        config.confidence,
        config.method,
    )


def video_area(
    value_cm2: float,
    evidence_ref: str,
    *,
    config: VideoOutputConfig = DEFAULT_VIDEO_OUTPUT,
) -> dict[str, Any]:
    return _measurement(
        value_cm2,
        "cm2",
        value_cm2 * config.area_relative_half_width,
        evidence_ref,
        config.confidence,
        config.method,
    )


def _measurement(
    value: float,
    unit: str,
    half_width: float,
    evidence_ref: str,
    confidence: float,
    method: str,
) -> dict[str, Any]:
    return {
        "value": _clean(value),
        "unit": unit,
        "interval": {
            "low": _clean(max(0.0, value - half_width)),
            "high": _clean(value + half_width),
            "confidence": confidence,
        },
        "method": method,
        "evidence_refs": [evidence_ref],
    }


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
