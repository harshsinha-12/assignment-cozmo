"""Evaluate FloorPlan predictions against the official numerical gates."""

from typing import Any

from cozmo_floorplan.eval.config import GateThresholds, OFFICIAL_THRESHOLDS
from cozmo_floorplan.eval.geometry import adjacency_pairs, footprint_area, room_overlap_area
from cozmo_floorplan.eval.matching import (
    EntityMatches,
    match_entities,
    opening_cost,
    room_cost,
    wall_cost,
)
from cozmo_floorplan.eval.measurements import summarize_interval_coverage, value
from cozmo_floorplan.eval.metrics import (
    absolute_errors,
    median_or_none,
    percentile_or_none,
    relative_errors,
)
from cozmo_floorplan.eval.models import EvaluationReport, GateResult

FloorPlan = dict[str, Any]


def evaluate_floorplans(
    prediction: FloorPlan,
    truth: FloorPlan,
    *,
    repeat_prediction: FloorPlan | None = None,
    ablation_off_prediction: FloorPlan | None = None,
    incumbent_prediction: FloorPlan | None = None,
    thresholds: GateThresholds = OFFICIAL_THRESHOLDS,
) -> EvaluationReport:
    """Evaluate one prediction and optional repeat/ablation evidence."""

    wall_matches = _wall_matches(prediction, truth)
    room_matches = _room_matches(prediction, truth)
    opening_matches = _opening_matches(prediction, truth, wall_matches)
    gates = (
        _yield_gate(prediction),
        _opening_gate(opening_matches, thresholds),
        _ceiling_gate(room_matches, repeat_prediction, thresholds),
        _repeatability_gate(prediction, truth, repeat_prediction, thresholds),
        _drift_gate(prediction, ablation_off_prediction),
        _photo_stitch_gate(prediction, truth, room_matches, thresholds),
        _tier_wall_gate(prediction, wall_matches, thresholds),
        _calibration_gate(wall_matches, room_matches, opening_matches, thresholds),
        _head_to_head_gate(prediction, truth, incumbent_prediction, thresholds),
    )
    return EvaluationReport(
        tier=str(prediction["provenance"]["tier"]),
        prediction_status=str(prediction["status"]),
        gates=gates,
        summary=_summary(wall_matches, room_matches, opening_matches),
    )


def _yield_gate(prediction: FloorPlan) -> GateResult:
    passed = prediction["status"] == "ok"
    return GateResult(
        name="pipeline_yield",
        status="pass" if passed else "fail",
        threshold="prediction status must be ok",
        metrics={"prediction_status": prediction["status"]},
        detail="A partial or failed job is counted in yield and cannot pass the benchmark row.",
    )


def _opening_gate(matches: EntityMatches, thresholds: GateThresholds) -> GateResult:
    total = len(matches.pairs) + len(matches.missed_truth) + len(matches.phantom_predictions)
    errors = absolute_errors(
        (value(prediction["width"]), value(truth["width"]))
        for prediction, truth in matches.pairs
    )
    accurate = sum(error <= thresholds.opening_error_cm for error in errors)
    success_rate = accurate / total if total else None
    passed = total > 0 and success_rate is not None and success_rate >= thresholds.opening_success_rate
    return GateResult(
        name="opening_widths",
        status="pass" if passed else "fail",
        threshold=(
            f"absolute width error <= {thresholds.opening_error_cm:g} cm on >= "
            f"{thresholds.opening_success_rate:.0%}; misses and phantoms count"
        ),
        metrics={
            "truth_count": len(matches.pairs) + len(matches.missed_truth),
            "prediction_count": len(matches.pairs) + len(matches.phantom_predictions),
            "matched_count": len(matches.pairs),
            "accurate_count": accurate,
            "success_rate": success_rate,
            "median_error_cm": median_or_none(errors),
            "p95_error_cm": percentile_or_none(errors, 0.95),
        },
        detail="Unmatched truth openings and unmatched predictions are scored as failures.",
    )


def _ceiling_gate(
    matches: EntityMatches,
    repeat_prediction: FloorPlan | None,
    thresholds: GateThresholds,
) -> GateResult:
    errors = absolute_errors(
        (value(prediction["ceiling_height"]), value(truth["ceiling_height"]))
        for prediction, truth in matches.pairs
    )
    accuracy_passed = bool(matches.pairs) and not matches.missed_truth and all(
        error <= thresholds.ceiling_error_cm for error in errors
    )
    repeat_spreads: list[float] = []
    if repeat_prediction is not None:
        repeat_matches = match_entities(
            [prediction for prediction, _ in matches.pairs],
            repeat_prediction.get("rooms", []),
            fallback_cost=room_cost,
            maximum_cost=500.0,
        )
        repeat_spreads = absolute_errors(
            (value(first["ceiling_height"]), value(second["ceiling_height"]))
            for first, second in repeat_matches.pairs
        )
        repeat_passed = (
            not repeat_matches.missed_truth
            and not repeat_matches.phantom_predictions
            and all(spread <= thresholds.ceiling_repeat_spread_cm for spread in repeat_spreads)
        )
    else:
        repeat_passed = True

    passed = accuracy_passed and repeat_passed
    return GateResult(
        name="ceiling_height",
        status="pass" if passed else "fail",
        threshold=(
            f"error <= {thresholds.ceiling_error_cm:g} cm per room; repeat spread <= "
            f"{thresholds.ceiling_repeat_spread_cm:g} cm when supplied"
        ),
        metrics={
            "matched_rooms": len(matches.pairs),
            "missed_rooms": len(matches.missed_truth),
            "max_error_cm": max(errors) if errors else None,
            "max_repeat_spread_cm": max(repeat_spreads) if repeat_spreads else None,
        },
        detail="Accuracy and repeat spread are reported separately to expose bias versus instability.",
    )


def _repeatability_gate(
    prediction: FloorPlan,
    truth: FloorPlan,
    repeat_prediction: FloorPlan | None,
    thresholds: GateThresholds,
) -> GateResult:
    threshold_text = (
        f"per-wall spread <= max({thresholds.repeatability_absolute_cm:g} cm, "
        f"{thresholds.repeatability_relative:.1%} of wall length)"
    )
    if repeat_prediction is None:
        return GateResult(
            name="repeatability",
            status="missing_evidence",
            threshold=threshold_text,
            detail="Pass --repeat with a second capture of the same room.",
        )

    first_truth_matches = _wall_matches(prediction, truth)
    repeat_truth_matches = _wall_matches(repeat_prediction, truth)
    repeated_matches = _wall_matches(prediction, repeat_prediction)
    spreads: list[float] = []
    tolerances: list[float] = []
    for first, second in repeated_matches.pairs:
        reference_length = (value(first["length"]) + value(second["length"])) / 2
        spreads.append(abs(value(first["length"]) - value(second["length"])))
        tolerances.append(
            max(
                thresholds.repeatability_absolute_cm,
                thresholds.repeatability_relative * reference_length,
            )
        )
    complete = (
        bool(repeated_matches.pairs)
        and not first_truth_matches.missed_truth
        and not first_truth_matches.phantom_predictions
        and not repeat_truth_matches.missed_truth
        and not repeat_truth_matches.phantom_predictions
        and not repeated_matches.missed_truth
        and not repeated_matches.phantom_predictions
    )
    passed = complete and all(spread <= tolerance for spread, tolerance in zip(spreads, tolerances))
    return GateResult(
        name="repeatability",
        status="pass" if passed else "fail",
        threshold=threshold_text,
        metrics={
            "matched_walls": len(repeated_matches.pairs),
            "max_spread_cm": max(spreads) if spreads else None,
            "failing_walls": sum(
                spread > tolerance for spread, tolerance in zip(spreads, tolerances)
            ),
        },
        detail="Both captures must also cover every ground-truth wall; repeatable omissions do not pass.",
    )


def _drift_gate(prediction: FloorPlan, ablation_off: FloorPlan | None) -> GateResult:
    threshold = "correction enabled plus a supplied correction-off ablation"
    if ablation_off is None:
        return GateResult(
            name="drift_accountability",
            status="missing_evidence",
            threshold=threshold,
            detail="Pass --ablation-off with the regenerable poses-as-is output.",
        )

    correction = prediction.get("stitch", {}).get("drift_correction", {})
    off_correction = ablation_off.get("stitch", {}).get("drift_correction", {})
    correction_on = bool(correction.get("enabled")) and correction.get("method") != "none"
    correction_off = not bool(off_correction.get("enabled")) or off_correction.get("method") == "none"
    passed = correction_on and correction_off
    on_area = footprint_area(prediction)
    off_area = footprint_area(ablation_off)
    return GateResult(
        name="drift_accountability",
        status="pass" if passed else "fail",
        threshold=threshold,
        metrics={
            "on_method": correction.get("method"),
            "off_method": off_correction.get("method"),
            "footprint_on_cm2": on_area,
            "footprint_off_cm2": off_area,
            "absolute_footprint_delta_cm2": abs(on_area - off_area),
        },
        detail="This gate proves the ablation exists; downstream reports must also interpret its delta.",
    )


def _photo_stitch_gate(
    prediction: FloorPlan,
    truth: FloorPlan,
    room_matches: EntityMatches,
    thresholds: GateThresholds,
) -> GateResult:
    threshold = (
        "correct adjacency, no room overlap, and footprint relative error <= "
        f"{thresholds.photo_footprint_relative_error:.0%}"
    )
    if prediction["provenance"]["tier"] != "photos":
        return GateResult(
            name="photo_whole_property_stitch",
            status="not_applicable",
            threshold=threshold,
            detail="This gate applies only to photo-tier predictions.",
        )

    truth_area = footprint_area(truth)
    prediction_area = footprint_area(prediction)
    footprint_error = abs(prediction_area - truth_area) / truth_area if truth_area else None
    overlap = room_overlap_area(prediction)
    mapped_predicted_adjacency = _mapped_adjacency_pairs(prediction, room_matches)
    truth_adjacency = adjacency_pairs(truth)
    passed = (
        bool(room_matches.pairs)
        and not room_matches.missed_truth
        and not room_matches.phantom_predictions
        and mapped_predicted_adjacency == truth_adjacency
        and overlap <= thresholds.overlap_area_tolerance_cm2
        and footprint_error is not None
        and footprint_error <= thresholds.photo_footprint_relative_error
    )
    return GateResult(
        name="photo_whole_property_stitch",
        status="pass" if passed else "fail",
        threshold=threshold,
        metrics={
            "matched_rooms": len(room_matches.pairs),
            "missed_rooms": len(room_matches.missed_truth),
            "phantom_rooms": len(room_matches.phantom_predictions),
            "adjacency_matches": mapped_predicted_adjacency == truth_adjacency,
            "overlap_area_cm2": overlap,
            "footprint_relative_error": footprint_error,
        },
    )


def _tier_wall_gate(
    prediction: FloorPlan,
    matches: EntityMatches,
    thresholds: GateThresholds,
) -> GateResult:
    tier = prediction["provenance"]["tier"]
    limit = {
        "photos": thresholds.photo_wall_relative_error,
        "video": thresholds.video_wall_relative_error,
    }.get(tier)
    if limit is None:
        return GateResult(
            name="tier_wall_accuracy",
            status="not_applicable",
            threshold="photos <= 8%; video <= 3% relative wall-length error",
            detail=f"The official prompt does not give this percentage gate for tier {tier!r}.",
        )

    errors = relative_errors(
        (value(prediction_wall["length"]), value(truth_wall["length"]))
        for prediction_wall, truth_wall in matches.pairs
    )
    passed = (
        bool(matches.pairs)
        and not matches.missed_truth
        and not matches.phantom_predictions
        and all(error <= limit for error in errors)
    )
    return GateResult(
        name="tier_wall_accuracy",
        status="pass" if passed else "fail",
        threshold=f"every matched wall relative error <= {limit:.0%}",
        metrics={
            "matched_walls": len(matches.pairs),
            "missed_walls": len(matches.missed_truth),
            "phantom_walls": len(matches.phantom_predictions),
            "median_relative_error": median_or_none(errors),
            "p95_relative_error": percentile_or_none(errors, 0.95),
        },
    )


def _calibration_gate(
    wall_matches: EntityMatches,
    room_matches: EntityMatches,
    opening_matches: EntityMatches,
    thresholds: GateThresholds,
) -> GateResult:
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    pairs.extend((prediction["length"], truth["length"]) for prediction, truth in wall_matches.pairs)
    for prediction, truth in room_matches.pairs:
        pairs.extend(
            [
                (prediction["ceiling_height"], truth["ceiling_height"]),
                (prediction["area"], truth["area"]),
            ]
        )
    for prediction, truth in opening_matches.pairs:
        for field in ("width", "height", "offset_along_wall"):
            if field in prediction and field in truth:
                pairs.append((prediction[field], truth[field]))

    metrics = summarize_interval_coverage(pairs)
    coverage = metrics["coverage"]
    declared = metrics["mean_declared_confidence"]
    passed = (
        isinstance(coverage, float)
        and isinstance(declared, float)
        and coverage + thresholds.calibration_coverage_tolerance >= declared
    )
    return GateResult(
        name="interval_calibration",
        status="pass" if passed else "fail",
        threshold=(
            "empirical coverage must not trail mean declared confidence by more than "
            f"{thresholds.calibration_coverage_tolerance:.0%} (explicit internal policy)"
        ),
        metrics=metrics,
        detail="Calibration is scored at every tier; this policy is explicit until a published method is supplied.",
    )


def _head_to_head_gate(
    prediction: FloorPlan,
    truth: FloorPlan,
    incumbent: FloorPlan | None,
    thresholds: GateThresholds,
) -> GateResult:
    threshold = f"beat or tie incumbent error on >= {thresholds.head_to_head_win_rate:.0%} shared dimensions"
    if prediction["provenance"]["tier"] != "lidar":
        return GateResult(
            name="head_to_head",
            status="not_applicable",
            threshold=threshold,
            detail="The official comparison applies to LiDAR output on two benchmark rooms.",
        )
    if incumbent is None:
        return GateResult(
            name="head_to_head",
            status="missing_evidence",
            threshold=threshold,
            detail="Pass --incumbent with the normalized Polycam or magicplan FloorPlan export.",
        )

    ours = _dimension_errors_by_truth_key(prediction, truth)
    theirs = _dimension_errors_by_truth_key(incumbent, truth)
    shared = sorted(ours.keys() & theirs.keys())
    wins = sum(ours[key] <= theirs[key] for key in shared)
    win_rate = wins / len(shared) if shared else None
    passed = win_rate is not None and win_rate >= thresholds.head_to_head_win_rate
    return GateResult(
        name="head_to_head",
        status="pass" if passed else "fail",
        threshold=threshold,
        metrics={"shared_dimensions": len(shared), "wins_or_ties": wins, "win_rate": win_rate},
        detail="Shared dimensions include wall lengths, opening widths, and ceiling heights.",
    )


def _summary(
    wall_matches: EntityMatches,
    room_matches: EntityMatches,
    opening_matches: EntityMatches,
) -> dict[str, Any]:
    wall_errors = absolute_errors(
        (value(prediction["length"]), value(truth["length"]))
        for prediction, truth in wall_matches.pairs
    )
    area_errors = relative_errors(
        (value(prediction["area"]), value(truth["area"]))
        for prediction, truth in room_matches.pairs
    )
    opening_errors = absolute_errors(
        (value(prediction["width"]), value(truth["width"]))
        for prediction, truth in opening_matches.pairs
    )
    return {
        "wall_median_error_cm": median_or_none(wall_errors),
        "wall_p95_error_cm": percentile_or_none(wall_errors, 0.95),
        "wall_count": len(wall_matches.pairs),
        "area_median_relative_error": median_or_none(area_errors),
        "opening_median_error_cm": median_or_none(opening_errors),
    }


def _wall_matches(prediction: FloorPlan, truth: FloorPlan) -> EntityMatches:
    return match_entities(
        prediction.get("walls", []),
        truth.get("walls", []),
        fallback_cost=wall_cost,
        maximum_cost=250.0,
    )


def _room_matches(prediction: FloorPlan, truth: FloorPlan) -> EntityMatches:
    return match_entities(
        prediction.get("rooms", []),
        truth.get("rooms", []),
        fallback_cost=room_cost,
        maximum_cost=500.0,
    )


def _opening_matches(
    prediction: FloorPlan,
    truth: FloorPlan,
    wall_matches: EntityMatches | None = None,
) -> EntityMatches:
    wall_id_map = {
        str(prediction_wall["id"]): str(truth_wall["id"])
        for prediction_wall, truth_wall in (wall_matches.pairs if wall_matches else ())
    }
    return match_entities(
        prediction.get("openings", []),
        truth.get("openings", []),
        fallback_cost=lambda prediction_opening, truth_opening: opening_cost(
            prediction_opening, truth_opening, wall_id_map
        ),
        maximum_cost=100.0,
    )


def _mapped_adjacency_pairs(
    prediction: FloorPlan,
    room_matches: EntityMatches,
) -> set[tuple[str, str]]:
    room_id_map = {
        str(prediction_room["id"]): str(truth_room["id"])
        for prediction_room, truth_room in room_matches.pairs
    }
    return {
        tuple(
            sorted(
                (
                    room_id_map.get(left, left),
                    room_id_map.get(right, right),
                )
            )
        )
        for left, right in adjacency_pairs(prediction)
    }


def _dimension_errors_by_truth_key(document: FloorPlan, truth: FloorPlan) -> dict[str, float]:
    errors: dict[str, float] = {}
    wall_matches = _wall_matches(document, truth)
    room_matches = _room_matches(document, truth)
    opening_matches = _opening_matches(document, truth, wall_matches)
    for prediction_wall, truth_wall in wall_matches.pairs:
        errors[f"wall:{truth_wall['id']}:length"] = abs(
            value(prediction_wall["length"]) - value(truth_wall["length"])
        )
    for prediction_room, truth_room in room_matches.pairs:
        errors[f"room:{truth_room['id']}:ceiling_height"] = abs(
            value(prediction_room["ceiling_height"]) - value(truth_room["ceiling_height"])
        )
    for prediction_opening, truth_opening in opening_matches.pairs:
        errors[f"opening:{truth_opening['id']}:width"] = abs(
            value(prediction_opening["width"]) - value(truth_opening["width"])
        )
    return errors
