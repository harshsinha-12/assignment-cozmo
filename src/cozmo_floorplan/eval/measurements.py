"""Read FloorPlan v0.2 measurements and evaluate interval coverage."""

from collections.abc import Iterable
from typing import Any


def value(measurement: dict[str, Any]) -> float:
    """Return a measurement point estimate as a float."""

    return float(measurement["value"])


def interval_contains(measurement: dict[str, Any], truth_value: float) -> bool:
    """Return whether an interval contains the ground-truth point."""

    interval = measurement["interval"]
    return float(interval["low"]) <= truth_value <= float(interval["high"])


def interval_confidence(measurement: dict[str, Any]) -> float:
    """Return the declared interval coverage level."""

    return float(measurement["interval"]["confidence"])


def summarize_interval_coverage(
    measurement_pairs: Iterable[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, float | int | None]:
    """Summarize empirical coverage for paired prediction/truth measurements."""

    pairs = list(measurement_pairs)
    if not pairs:
        return {"count": 0, "covered": 0, "coverage": None, "mean_declared_confidence": None}

    covered = sum(interval_contains(prediction, value(truth)) for prediction, truth in pairs)
    return {
        "count": len(pairs),
        "covered": covered,
        "coverage": covered / len(pairs),
        "mean_declared_confidence": sum(interval_confidence(prediction) for prediction, _ in pairs)
        / len(pairs),
    }
