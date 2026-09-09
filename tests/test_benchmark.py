import json
from pathlib import Path

import pytest

import cozmo_floorplan.benchmark.runner as runner_module
from cozmo_floorplan.benchmark.manifest import load_benchmark_manifest
from cozmo_floorplan.benchmark.runner import run_benchmark
from cozmo_floorplan.cli import main

ROOT = Path(__file__).resolve().parents[1]
TRUTH_PATH = ROOT / "data" / "fixtures" / "synthetic_two_room" / "ground_truth.json"


def test_missing_capture_root_writes_pending_report(tmp_path):
    capture_root = tmp_path / "not-captured-yet"
    output = tmp_path / "output"

    report = run_benchmark(capture_root, output)

    assert report["status"] == "pending_inputs"
    assert "capture_root" in report["pending_inputs"]
    assert "ground_truth" in report["pending_inputs"]
    assert all(item["status"] == "pending" for item in report["evaluations"])
    assert (output / "benchmark-status.json").is_file()
    assert (output / "benchmark-summary.md").is_file()


def test_benchmark_manifest_rejects_path_escape(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "benchmark.yaml").write_text(
        """schema_version: '1.0.0'
benchmark_id: unsafe
jobs:
  photos: ../outside
  video: benchmark-video
  lidar: benchmark-lidar
ground_truth: ground_truth.json
repeats: {lidar: benchmark-lidar-repeat}
incumbent: incumbent/floorplan.json
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="escapes capture root"):
        load_benchmark_manifest(tmp_path)


def test_complete_manifest_runs_every_tier_and_writes_evaluations(
    monkeypatch, tmp_path
):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    truth_text = TRUTH_PATH.read_text(encoding="utf-8")
    truth = json.loads(truth_text)
    (capture_root / "ground_truth.json").write_text(truth_text, encoding="utf-8")
    incumbent = capture_root / "incumbent" / "floorplan.json"
    incumbent.parent.mkdir()
    incumbent.write_text(truth_text, encoding="utf-8")
    for name in (
        "benchmark-photos",
        "benchmark-video",
        "benchmark-lidar",
        "benchmark-lidar-repeat",
    ):
        job = capture_root / name
        job.mkdir()
        (job / "manifest.yaml").write_text(
            f"job_id: {name}\ntier: lidar\n", encoding="utf-8"
        )
    (capture_root / "benchmark-lidar" / "damage_observations.json").write_text(
        "[]\n", encoding="utf-8"
    )
    template = (ROOT / "data" / "templates" / "benchmark.yaml").read_text(
        encoding="utf-8"
    )
    (capture_root / "benchmark.yaml").write_text(template, encoding="utf-8")
    monkeypatch.setattr(
        runner_module,
        "run_job_with_ablation",
        lambda _job: (truth, None),
    )

    report = run_benchmark(capture_root, tmp_path / "output")

    assert report["status"] == "complete"
    assert not report["pending_inputs"]
    assert len(report["runs"]) == 4
    assert all(item["status"] == "complete" for item in report["runs"])
    assert all(item["status"] == "complete" for item in report["evaluations"])


def test_benchmark_cli_treats_pending_as_a_successful_audit(tmp_path):
    output = tmp_path / "output"

    exit_code = main(
        ["benchmark", str(tmp_path / "missing-captures"), "--out", str(output)]
    )

    assert exit_code == 0
    report = json.loads((output / "benchmark-status.json").read_text(encoding="utf-8"))
    assert report["status"] == "pending_inputs"
