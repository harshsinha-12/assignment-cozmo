"""Deterministically match predicted entities to truth without trusting array order."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from math import atan2, hypot, pi
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

Entity = dict[str, Any]
CostFunction = Callable[[Entity, Entity], float]


@dataclass(frozen=True, slots=True)
class EntityMatches:
    """Matched pairs plus truth misses and prediction phantoms."""

    pairs: tuple[tuple[Entity, Entity], ...]
    missed_truth: tuple[Entity, ...]
    phantom_predictions: tuple[Entity, ...]


def match_entities(
    predictions: Sequence[Entity],
    truths: Sequence[Entity],
    *,
    fallback_cost: CostFunction | None = None,
    maximum_cost: float = float("inf"),
) -> EntityMatches:
    """Match IDs first, then optionally use a Hungarian fallback for remaining entities."""

    truth_by_id = {entity["id"]: entity for entity in truths}
    prediction_by_id = {entity["id"]: entity for entity in predictions}
    shared_ids = sorted(prediction_by_id.keys() & truth_by_id.keys())
    pairs = [(prediction_by_id[entity_id], truth_by_id[entity_id]) for entity_id in shared_ids]
    remaining_predictions = [entity for entity in predictions if entity["id"] not in shared_ids]
    remaining_truths = [entity for entity in truths if entity["id"] not in shared_ids]

    matched_prediction_indexes: set[int] = set()
    matched_truth_indexes: set[int] = set()
    if fallback_cost and remaining_predictions and remaining_truths:
        costs = np.array(
            [
                [fallback_cost(prediction, truth) for truth in remaining_truths]
                for prediction in remaining_predictions
            ],
            dtype=float,
        )
        prediction_indexes, truth_indexes = linear_sum_assignment(costs)
        for prediction_index, truth_index in zip(prediction_indexes, truth_indexes, strict=True):
            if costs[prediction_index, truth_index] <= maximum_cost:
                pairs.append((remaining_predictions[prediction_index], remaining_truths[truth_index]))
                matched_prediction_indexes.add(int(prediction_index))
                matched_truth_indexes.add(int(truth_index))

    missed = tuple(
        truth for index, truth in enumerate(remaining_truths) if index not in matched_truth_indexes
    )
    phantoms = tuple(
        prediction
        for index, prediction in enumerate(remaining_predictions)
        if index not in matched_prediction_indexes
    )
    return EntityMatches(tuple(pairs), missed, phantoms)


def wall_cost(prediction: Entity, truth: Entity) -> float:
    """Cost based on midpoint, direction, and length for non-identical wall IDs."""

    pred_midpoint = _midpoint(prediction)
    truth_midpoint = _midpoint(truth)
    midpoint_distance = hypot(
        pred_midpoint[0] - truth_midpoint[0], pred_midpoint[1] - truth_midpoint[1]
    )
    angle_distance = _undirected_angle_difference(_angle(prediction), _angle(truth))
    length_distance = abs(
        float(prediction["length"]["value"]) - float(truth["length"]["value"])
    )
    return midpoint_distance + 50.0 * angle_distance + 0.25 * length_distance


def room_cost(prediction: Entity, truth: Entity) -> float:
    """Cost based on polygon centroid and reported area."""

    pred_centroid = _polygon_centroid(prediction["polygon"])
    truth_centroid = _polygon_centroid(truth["polygon"])
    centroid_distance = hypot(
        pred_centroid[0] - truth_centroid[0], pred_centroid[1] - truth_centroid[1]
    )
    area_distance = abs(
        float(prediction["area"]["value"]) - float(truth["area"]["value"])
    )
    return centroid_distance + 0.001 * area_distance


def opening_cost(
    prediction: Entity,
    truth: Entity,
    predicted_to_truth_wall_ids: dict[str, str],
) -> float:
    """Match openings by kind, supporting wall, offset, and width."""

    if prediction["kind"] != truth["kind"]:
        return 1_000_000.0
    mapped_wall_id = predicted_to_truth_wall_ids.get(
        str(prediction["wall_id"]), str(prediction["wall_id"])
    )
    wall_penalty = 0.0 if mapped_wall_id == truth["wall_id"] else 1_000.0
    width_distance = abs(
        float(prediction["width"]["value"]) - float(truth["width"]["value"])
    )
    if "offset_along_wall" in prediction and "offset_along_wall" in truth:
        offset_distance = abs(
            float(prediction["offset_along_wall"]["value"])
            - float(truth["offset_along_wall"]["value"])
        )
    else:
        offset_distance = 0.0
    return wall_penalty + offset_distance + 0.25 * width_distance


def _midpoint(wall: Entity) -> tuple[float, float]:
    return (
        (float(wall["a"][0]) + float(wall["b"][0])) / 2,
        (float(wall["a"][1]) + float(wall["b"][1])) / 2,
    )


def _angle(wall: Entity) -> float:
    return atan2(
        float(wall["b"][1]) - float(wall["a"][1]),
        float(wall["b"][0]) - float(wall["a"][0]),
    )


def _undirected_angle_difference(left: float, right: float) -> float:
    difference = abs(left - right) % pi
    return min(difference, pi - difference)


def _polygon_centroid(points: Sequence[Sequence[float]]) -> tuple[float, float]:
    return (
        sum(float(point[0]) for point in points) / len(points),
        sum(float(point[1]) for point in points) / len(points),
    )
