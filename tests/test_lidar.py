import json
from pathlib import Path

import jsonschema

from cozmo_floorplan.cli import main
from cozmo_floorplan.eval.evaluator import evaluate_floorplans
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.pipeline import run_job

ROOT = Path(__file__).resolve().parents[1]
JOB_DIR = ROOT / "data" / "fixtures" / "roomplan_two_room"
TRUTH_PATH = ROOT / "data" / "fixtures" / "synthetic_two_room" / "ground_truth.json"
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"


def _gate(report, name: str):
    return next(gate for gate in report.gates if gate.name == name)


def test_roomplan_fixture_loads_as_a_lidar_job():
    job = load_job(JOB_DIR)

    assert job.tier == "lidar"
    assert job.input_refs == ("manifest.yaml", "lidar/roomplan.json")


def test_roomplan_two_room_reconstructs_metric_floorplan():
    document = run_job(JOB_DIR)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=document, schema=schema)

    assert document["status"] == "partial"
    assert document["provenance"]["tier"] == "lidar"
    assert document["provenance"]["scale_source"] == "lidar"
    assert len(document["rooms"]) == 2
    assert len(document["walls"]) == 8
    assert len(document["openings"]) == 1
    assert document["rooms"][0]["area"]["value"] == 120000
    assert document["rooms"][1]["area"]["value"] == 98000
    assert document["openings"][0]["width"]["value"] == 80
    assert document["openings"][0]["height"]["value"] == 210
    assert document["openings"][0]["offset_along_wall"]["value"] == 150
    assert document["stitch"]["drift_correction"] == {
        "enabled": False,
        "method": "none",
        "notes": "T6 preserves global RoomPlan transforms; T9 adds correction and ablation.",
    }


def test_roomplan_geometry_passes_available_metric_gates():
    prediction = run_job(JOB_DIR)
    truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))

    report = evaluate_floorplans(prediction, truth)

    assert report.summary["wall_median_error_cm"] == 0
    assert report.summary["area_median_relative_error"] == 0
    assert _gate(report, "opening_widths").status == "pass"
    assert _gate(report, "ceiling_height").status == "pass"
    assert _gate(report, "interval_calibration").status == "pass"
    assert _gate(report, "repeatability").status == "missing_evidence"
    assert _gate(report, "drift_accountability").status == "missing_evidence"


def test_single_captured_room_root_is_supported_without_stitch_warning(tmp_path):
    fixture = json.loads(
        (JOB_DIR / "lidar" / "roomplan.json").read_text(encoding="utf-8")
    )
    single_room = fixture["rooms"][0]
    single_room["doors"] = []
    job_dir = tmp_path / "single_room"
    lidar_dir = job_dir / "lidar"
    lidar_dir.mkdir(parents=True)
    (job_dir / "manifest.yaml").write_text(
        "job_id: single_room\ntier: lidar\ndevice: iPhone Pro\n",
        encoding="utf-8",
    )
    (lidar_dir / "captured_room.json").write_text(
        json.dumps(single_room),
        encoding="utf-8",
    )

    document = run_job(job_dir)

    assert document["status"] == "ok"
    assert len(document["rooms"]) == 1
    assert "stitch" not in document


def test_run_cli_writes_dimensioned_partial_lidar_output(tmp_path):
    exit_code = main(["run", str(JOB_DIR), "--out", str(tmp_path)])

    assert exit_code == 2
    document = json.loads((tmp_path / "floorplan.json").read_text(encoding="utf-8"))
    assert document["status"] == "partial"
    assert document["walls"][0]["length"]["unit"] == "cm"
    assert document["walls"][0]["length"]["interval"]["confidence"] == 0.95


def test_missing_roomplan_export_is_a_structured_failure(tmp_path):
    job_dir = tmp_path / "missing_export"
    (job_dir / "lidar").mkdir(parents=True)
    (job_dir / "manifest.yaml").write_text(
        "job_id: missing_export\ntier: lidar\ndevice: iPhone Pro\n",
        encoding="utf-8",
    )

    document = run_job(job_dir)

    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "incomplete_scan"
    assert "RoomPlan JSON" in document["warnings"][0]["message"]


def test_record3d_export_is_detected_without_fake_geometry(tmp_path):
    job_dir = tmp_path / "record3d_export"
    lidar_dir = job_dir / "lidar"
    lidar_dir.mkdir(parents=True)
    (job_dir / "manifest.yaml").write_text(
        "job_id: record3d_export\ntier: lidar\ndevice: iPhone Pro\n",
        encoding="utf-8",
    )
    (lidar_dir / "metadata.json").write_text('{"poses": [], "K": []}', encoding="utf-8")

    document = run_job(job_dir)

    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "unsupported_tier"
    assert "Record3D" in document["warnings"][0]["message"]
