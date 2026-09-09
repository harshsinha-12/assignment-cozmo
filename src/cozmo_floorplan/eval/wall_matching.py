"""Match room walls without assuming a shared scan coordinate frame."""

from collections import defaultdict
from collections.abc import Sequence
from math import atan2
from typing import Any

from cozmo_floorplan.eval.matching import EntityMatches, match_entities, wall_cost

Entity = dict[str, Any]


def match_room_walls(
    predictions: Sequence[Entity],
    truths: Sequence[Entity],
    room_matches: EntityMatches,
) -> EntityMatches:
    """Match room-local wall cycles before using the co-framed fallback.

    Independently reconstructed rooms may be translated, rotated, or reflected,
    and generated wall IDs are not semantic identities.  A room's cyclic wall
    topology and side lengths survive those frame changes, so they are the safe
    primary evidence for single-owner walls.
    """

    prediction_groups = _single_room_groups(predictions)
    truth_groups = _single_room_groups(truths)
    pairs: list[tuple[Entity, Entity]] = []
    used_predictions: set[int] = set()
    used_truths: set[int] = set()

    for prediction_room, truth_room in room_matches.pairs:
        predicted = prediction_groups.get(str(prediction_room["id"]), ())
        expected = truth_groups.get(str(truth_room["id"]), ())
        if not predicted or len(predicted) != len(expected):
            continue
        room_pairs = _best_cyclic_pairs(predicted, expected)
        pairs.extend(room_pairs)
        used_predictions.update(id(wall) for wall, _ in room_pairs)
        used_truths.update(id(wall) for _, wall in room_pairs)

    remaining_predictions = [wall for wall in predictions if id(wall) not in used_predictions]
    remaining_truths = [wall for wall in truths if id(wall) not in used_truths]
    fallback = match_entities(
        remaining_predictions,
        remaining_truths,
        fallback_cost=wall_cost,
        maximum_cost=250.0,
    )
    return EntityMatches(
        pairs=tuple(pairs) + fallback.pairs,
        missed_truth=fallback.missed_truth,
        phantom_predictions=fallback.phantom_predictions,
    )


def _single_room_groups(walls: Sequence[Entity]) -> dict[str, tuple[Entity, ...]]:
    groups: dict[str, list[Entity]] = defaultdict(list)
    for wall in walls:
        room_ids = wall.get("room_ids", [])
        if len(room_ids) == 1:
            groups[str(room_ids[0])].append(wall)
    return {room_id: _walls_around_centroid(group) for room_id, group in groups.items()}


def _walls_around_centroid(walls: Sequence[Entity]) -> tuple[Entity, ...]:
    midpoints = [_midpoint(wall) for wall in walls]
    centroid_x = sum(point[0] for point in midpoints) / len(midpoints)
    centroid_y = sum(point[1] for point in midpoints) / len(midpoints)
    return tuple(
        wall
        for _, wall in sorted(
            zip(
                (
                    atan2(point[1] - centroid_y, point[0] - centroid_x)
                    for point in midpoints
                ),
                walls,
                strict=True,
            ),
            key=lambda item: (item[0], str(item[1]["id"])),
        )
    )


def _best_cyclic_pairs(
    predictions: Sequence[Entity], truths: Sequence[Entity]
) -> tuple[tuple[Entity, Entity], ...]:
    candidates: list[tuple[tuple[float, int, int, int], tuple[tuple[Entity, Entity], ...]]] = []
    count = len(predictions)
    for reflected in (0, 1):
        for shift in range(count):
            truth_indexes = [
                (shift - index) % count if reflected else (shift + index) % count
                for index in range(count)
            ]
            pairs = tuple(
                (prediction, truths[truth_index])
                for prediction, truth_index in zip(predictions, truth_indexes, strict=True)
            )
            length_cost = sum(
                abs(_length(prediction) - _length(truth)) for prediction, truth in pairs
            )
            id_mismatches = sum(
                prediction["id"] != truth["id"] for prediction, truth in pairs
            )
            candidates.append(((length_cost, id_mismatches, reflected, shift), pairs))
    return min(candidates, key=lambda candidate: candidate[0])[1]


def _midpoint(wall: Entity) -> tuple[float, float]:
    return (
        (float(wall["a"][0]) + float(wall["b"][0])) / 2,
        (float(wall["a"][1]) + float(wall["b"][1])) / 2,
    )


def _length(wall: Entity) -> float:
    return float(wall["length"]["value"])
