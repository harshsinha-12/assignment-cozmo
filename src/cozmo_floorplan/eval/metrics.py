"""Small numerical summaries shared by evaluation gates."""

from collections.abc import Iterable, Sequence
from math import ceil
from statistics import median


def absolute_errors(pairs: Iterable[tuple[float, float]]) -> list[float]:
    return [abs(prediction - truth) for prediction, truth in pairs]


def relative_errors(pairs: Iterable[tuple[float, float]]) -> list[float]:
    errors: list[float] = []
    for prediction, truth in pairs:
        errors.append(abs(prediction - truth) / abs(truth) if truth else float("inf"))
    return errors


def median_or_none(values: Sequence[float]) -> float | None:
    return float(median(values)) if values else None


def percentile_or_none(values: Sequence[float], percentile: float) -> float | None:
    """Return a deterministic nearest-rank percentile without another model dependency."""

    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, ceil(percentile * len(ordered)))
    return float(ordered[rank - 1])
