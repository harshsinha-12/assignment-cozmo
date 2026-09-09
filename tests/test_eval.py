import json
from copy import deepcopy
from pathlib import Path

from cozmo_floorplan.cli import main
from cozmo_floorplan.eval.evaluator import evaluate_floorplans
from cozmo_floorplan.floorplan import build_failed_floorplan

ROOT = Path(__file__).resolve().parents[1]
TRUTH_PATH = ROOT / "data" / "fixtures" / "synthetic_two_room" / "ground_truth.json"


def _truth() -> dict:
    return json.loads(TRUTH_PATH.read_text(encoding="utf-8"))


def _gate(report, name: str):
    return next(gate for gate in report.gates if gate.name == name)


def _ablation_off(document: dict) -> dict:
    ablation = deepcopy(document)
    ablation["stitch"]["drift_correction"] = {"enabled": False, "method": "none"}
    return ablation


def test_empty_prediction_reports_explicit_red_gates():
    prediction = build_failed_floorplan(
        job_id="synthetic_two_room",
        tier="synthetic",
        warning_code="unsupported_tier",
        message="adapter missing",
    )

    report = evaluate_floorplans(prediction, _truth())

    assert report.passed is False
    assert _gate(report, "pipeline_yield").status == "fail"
    assert _gate(report, "opening_widths").status == "fail"
    assert _gate(report, "ceiling_height").status == "fail"
    assert _gate(report, "repeatability").status == "missing_evidence"
    assert _gate(report, "drift_accountability").status == "missing_evidence"
    assert _gate(report, "interval_calibration").status == "fail"


def test_perfect_synthetic_prediction_passes_with_required_evidence():
    truth = _truth()

    report = evaluate_floorplans(
        truth,
        truth,
        repeat_prediction=truth,
        ablation_off_prediction=_ablation_off(truth),
    )

    assert report.passed is True
    assert all(
        gate.status in {"pass", "not_applicable"}
        for gate in report.gates
    )
    assert report.summary["wall_median_error_cm"] == 0
    assert _gate(report, "opening_widths").metrics["success_rate"] == 1


def test_missed_opening_counts_as_a_detection_failure():
    prediction = _truth()
    prediction["openings"] = []

    gate = _gate(evaluate_floorplans(prediction, _truth()), "opening_widths")

    assert gate.status == "fail"
    assert gate.metrics["truth_count"] == 1
    assert gate.metrics["prediction_count"] == 0
    assert gate.metrics["success_rate"] == 0


def test_phantom_opening_is_added_to_detection_denominator():
    prediction = _truth()
    phantom = deepcopy(prediction["openings"][0])
    phantom["id"] = "phantom_door"
    prediction["openings"].append(phantom)

    gate = _gate(evaluate_floorplans(prediction, _truth()), "opening_widths")

    assert gate.status == "fail"
    assert gate.metrics["truth_count"] == 1
    assert gate.metrics["prediction_count"] == 2
    assert gate.metrics["success_rate"] == 0.5


def test_photo_stitch_and_wall_gates_pass_on_exact_geometry():
    truth = _truth()
    prediction = deepcopy(truth)
    prediction["provenance"]["tier"] = "photos"
    prediction["provenance"]["scale_source"] = "known_length"
    prediction["provenance"]["pipeline"] = "test-photo-adapter"

    report = evaluate_floorplans(prediction, truth)

    assert _gate(report, "photo_whole_property_stitch").status == "pass"
    assert _gate(report, "tier_wall_accuracy").status == "pass"


def test_photo_adjacency_uses_geometry_matches_when_room_ids_differ():
    truth = _truth()
    prediction = deepcopy(truth)
    prediction["provenance"]["tier"] = "photos"
    prediction["provenance"]["scale_source"] = "known_length"
    prediction["rooms"][0]["id"] = "predicted_a"
    prediction["rooms"][1]["id"] = "predicted_b"
    prediction["stitch"]["edges"][0]["left_room"] = "predicted_a"
    prediction["stitch"]["edges"][0]["right_room"] = "predicted_b"

    gate = _gate(evaluate_floorplans(prediction, truth), "photo_whole_property_stitch")

    assert gate.status == "pass"
    assert gate.metrics["adjacency_matches"] is True


def test_lidar_head_to_head_reports_wins_against_incumbent():
    truth = _truth()
    prediction = deepcopy(truth)
    prediction["provenance"]["tier"] = "lidar"
    prediction["provenance"]["scale_source"] = "lidar"
    incumbent = deepcopy(prediction)
    incumbent["walls"][0]["length"]["value"] += 10

    report = evaluate_floorplans(prediction, truth, incumbent_prediction=incumbent)
    gate = _gate(report, "head_to_head")

    assert gate.status == "pass"
    assert gate.metrics["shared_dimensions"] == 13
    assert gate.metrics["win_rate"] == 1


def test_eval_cli_writes_red_eval_json(tmp_path):
    prediction = build_failed_floorplan(
        job_id="synthetic_two_room",
        tier="synthetic",
        warning_code="unsupported_tier",
        message="adapter missing",
    )
    prediction_path = tmp_path / "prediction.json"
    prediction_path.write_text(json.dumps(prediction), encoding="utf-8")
    out_dir = tmp_path / "evaluation"

    exit_code = main(
        [
            "eval",
            "--pred",
            str(prediction_path),
            "--truth",
            str(TRUTH_PATH),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 3
    report = json.loads((out_dir / "eval.json").read_text(encoding="utf-8"))
    assert report["passed"] is False
    assert report["version"] == "0.1.0"
    assert {gate["name"] for gate in report["gates"]} >= {
        "opening_widths",
        "ceiling_height",
        "repeatability",
        "drift_accountability",
        "interval_calibration",
    }
