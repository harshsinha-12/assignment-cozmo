import json
from pathlib import Path

import jsonschema

from cozmo_floorplan.cli import main
from cozmo_floorplan.eval.evaluator import evaluate_floorplans
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.pipeline import run_job, run_job_with_ablation
from cozmo_floorplan.recon.lidar import reconstruct_lidar
from cozmo_floorplan.stitch import apply_drift_correction
from cozmo_floorplan.stitch.constraints import mean_opening_gap, opening_constraints

ROOT = Path(__file__).resolve().parents[1]
JOB_DIR = ROOT / "data" / "fixtures" / "roomplan_two_room"
TRUTH_PATH = ROOT / "data/fixtures/synthetic_two_room/ground_truth.json"
SCHEMA_PATH = ROOT / "docs/schemas/floorplan.schema.json"
ROOMPLAN_PATH = JOB_DIR / "lidar" / "roomplan.json"


def _gate(report, name: str):
    return next(gate for gate in report.gates if gate.name == name)


def _warning_codes(document: dict) -> list[str]:
    return [str(warning.get("code")) for warning in document.get("warnings", [])]


def test_default_run_enables_plane_anchored_correction():
    document, ablation = run_job_with_ablation(JOB_DIR)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=document, schema=schema)
    jsonschema.validate(instance=ablation, schema=schema)

    assert document["status"] in {"ok", "partial"}
    assert document["status"] != "failed"
    assert document["stitch"]["drift_correction"]["enabled"] is True
    assert document["stitch"]["drift_correction"]["method"] == "plane_anchored"
    assert ablation is not None
    assert ablation["status"] == "ok"
    assert ablation["stitch"]["drift_correction"]["enabled"] is False
    assert ablation["stitch"]["drift_correction"]["method"] == "none"


def test_geometry_correction_is_ok_before_claims_enrichment():
    raw = reconstruct_lidar(load_job(JOB_DIR))
    corrected = apply_drift_correction(raw, enabled=True)

    assert corrected["status"] == "ok"
    assert corrected["stitch"]["drift_correction"]["method"] == "plane_anchored"
    assert corrected["stitch"]["drift_correction"]["residual_after"]["value"] < 1


def test_correction_is_not_claimed_without_opening_constraints():
    raw = reconstruct_lidar(load_job(JOB_DIR))
    raw["openings"] = []

    corrected = apply_drift_correction(raw, enabled=True)

    assert corrected["status"] == "partial"
    assert corrected["stitch"]["drift_correction"]["enabled"] is False
    assert corrected["stitch"]["drift_correction"]["method"] == "none"
    assert "disconnected_rooms" in _warning_codes(corrected)


def test_drift_gate_passes_with_regenerable_ablation():
    raw = reconstruct_lidar(load_job(JOB_DIR))
    prediction = apply_drift_correction(raw, enabled=True)
    ablation = apply_drift_correction(raw, enabled=False)
    truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))

    report = evaluate_floorplans(prediction, truth, ablation_off_prediction=ablation)

    assert _gate(report, "drift_accountability").status == "pass"
    assert _gate(report, "pipeline_yield").status == "pass"
    assert _gate(report, "opening_widths").status == "pass"


def test_pipeline_ablation_is_accepted_by_the_drift_gate():
    prediction, ablation = run_job_with_ablation(JOB_DIR)
    truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))

    report = evaluate_floorplans(prediction, truth, ablation_off_prediction=ablation)

    assert _gate(report, "drift_accountability").status == "pass"
    assert _gate(report, "opening_widths").status == "pass"


def test_cli_writes_ablation_off_artifact(tmp_path):
    exit_code = main(["run", str(JOB_DIR), "--out", str(tmp_path)])

    assert exit_code in {0, 2}
    on = json.loads((tmp_path / "floorplan.json").read_text(encoding="utf-8"))
    off = json.loads((tmp_path / "floorplan.ablation-off.json").read_text(encoding="utf-8"))
    assert on["status"] in {"ok", "partial"}
    assert on["stitch"]["drift_correction"]["method"] == "plane_anchored"
    assert off["stitch"]["drift_correction"]["method"] == "none"


def test_no_drift_correction_flag_is_poses_as_is(tmp_path):
    exit_code = main(["run", str(JOB_DIR), "--out", str(tmp_path), "--no-drift-correction"])

    assert exit_code in {0, 2}
    document = json.loads((tmp_path / "floorplan.json").read_text(encoding="utf-8"))
    assert document["stitch"]["drift_correction"]["method"] == "none"
    assert not (tmp_path / "floorplan.ablation-off.json").exists()


def test_plane_anchor_closes_injected_opening_gap(tmp_path):
    fixture = json.loads(ROOMPLAN_PATH.read_text(encoding="utf-8"))
    for surface in fixture["rooms"][1]["walls"]:
        surface["transform"][12] += 0.20
    job_dir = tmp_path / "drifted"
    lidar_dir = job_dir / "lidar"
    lidar_dir.mkdir(parents=True)
    (job_dir / "manifest.yaml").write_text(
        "job_id: drifted\ntier: lidar\ndevice: iPhone 17 Pro\n",
        encoding="utf-8",
    )
    (lidar_dir / "roomplan.json").write_text(json.dumps(fixture), encoding="utf-8")
    job = load_job(job_dir)
    raw = reconstruct_lidar(job)
    gap_before = mean_opening_gap(opening_constraints(raw))
    corrected = apply_drift_correction(raw, enabled=True)
    gap_after = mean_opening_gap(opening_constraints(corrected))
    a_east = next(wall for wall in corrected["walls"] if wall["id"] == "a_east")
    b_west = next(wall for wall in corrected["walls"] if wall["id"] == "b_west")

    assert gap_before > 10
    assert gap_after < 1
    assert a_east["a"][0] == 400.0
    assert b_west["a"][0] == 400.0
    assert corrected["stitch"]["drift_correction"]["residual_before"]["value"] > 10
    assert corrected["stitch"]["drift_correction"]["residual_after"]["value"] < 1
    enriched = run_job(job_dir)
    assert enriched["status"] in {"ok", "partial"}
    assert "incomplete_scan" not in _warning_codes(enriched)
