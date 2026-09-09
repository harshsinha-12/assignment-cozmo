"""Tests for frame-invariant, room-local wall matching."""

from copy import deepcopy

from cozmo_floorplan.eval.matching import EntityMatches
from cozmo_floorplan.eval.wall_matching import match_room_walls


def _room(room_id: str) -> dict:
    return {"id": room_id}


def _wall(wall_id: str, room_id: str, a: tuple[float, float], b: tuple[float, float]) -> dict:
    length = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
    return {
        "id": wall_id,
        "room_ids": [room_id],
        "a": list(a),
        "b": list(b),
        "length": {"value": length},
    }


def _rectangle(room_id: str, prefix: str, width: float, height: float) -> list[dict]:
    return [
        _wall(f"{prefix}-1", room_id, (0, 0), (width, 0)),
        _wall(f"{prefix}-2", room_id, (width, 0), (width, height)),
        _wall(f"{prefix}-3", room_id, (width, height), (0, height)),
        _wall(f"{prefix}-4", room_id, (0, height), (0, 0)),
    ]


def test_matches_room_wall_cycle_across_rotation_translation_and_new_ids():
    truths = _rectangle("truth-room", "truth", 400, 300)
    predictions = _rectangle("pred-room", "pred", 400, 300)
    for wall in predictions:
        wall["a"] = [-wall["a"][1] + 900, wall["a"][0] - 250]
        wall["b"] = [-wall["b"][1] + 900, wall["b"][0] - 250]
    predictions.reverse()
    room_matches = EntityMatches(
        pairs=((_room("pred-room"), _room("truth-room")),),
        missed_truth=(),
        phantom_predictions=(),
    )

    matches = match_room_walls(predictions, truths, room_matches)

    assert not matches.missed_truth
    assert not matches.phantom_predictions
    assert sorted(
        (prediction["length"]["value"], truth["length"]["value"])
        for prediction, truth in matches.pairs
    ) == [(300, 300), (300, 300), (400, 400), (400, 400)]


def test_length_evidence_overrides_reused_but_shifted_generated_ids():
    truths = _rectangle("room", "room-wall", 400, 300)
    predictions = deepcopy(truths)
    shifted_ids = [wall["id"] for wall in predictions[1:] + predictions[:1]]
    for wall, shifted_id in zip(predictions, shifted_ids, strict=True):
        wall["id"] = shifted_id
    room = _room("room")
    room_matches = EntityMatches(
        pairs=((room, room),), missed_truth=(), phantom_predictions=()
    )

    matches = match_room_walls(predictions, truths, room_matches)

    assert all(
        prediction["length"]["value"] == truth["length"]["value"]
        for prediction, truth in matches.pairs
    )
