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
    jobs = {
        "benchmark-photos": "photos",
        "benchmark-video": "video",
        "benchmark-lidar": "lidar",
        "benchmark-photos-repeat": "photos",
    }
    for name, tier in jobs.items():
        job = capture_root / name
        job.mkdir()
        (job / "manifest.yaml").write_text(
            f"job_id: {name}\ntier: {tier}\n", encoding="utf-8"
        )
    (capture_root / "benchmark-photos-repeat" / "manifest.yaml").write_text(
        "job_id: benchmark-photos-repeat\n"
        "tier: photos\n"
        "repeat_of_job_id: benchmark-photos\n"
        "repeat_room_ids: [room_a]\n",
        encoding="utf-8",
    )
    damage_job = capture_root / "benchmark-lidar"
    (damage_job / "damage-a.jpg").write_bytes(b"evidence-a")
    (damage_job / "damage-b.jpg").write_bytes(b"evidence-b")
    (damage_job / "damage_observations.json").write_text(
        json.dumps(
            {
                "version": "1.0",
                "observations": [
                    {
                        "id": "damage-a",
                        "surface": {"kind": "wall", "id": "a_south"},
                        "fallback_class": "crack",
                        "confidence": 0.9,
                        "extent": {
                            "value": 10,
                            "unit": "cm2",
                            "interval": {"low": 9, "high": 11, "confidence": 0.9},
                        },
                        "evidence_refs": ["damage-a.jpg"],
                    },
                    {
                        "id": "damage-b",
                        "surface": {"kind": "wall", "id": "b_south"},
                        "fallback_class": "impact_damage",
                        "confidence": 0.9,
                        "extent": {
                            "value": 12,
                            "unit": "cm2",
                            "interval": {"low": 11, "high": 13, "confidence": 0.9},
                        },
                        "evidence_refs": ["damage-b.jpg"],
                    },
                ],
            }
        ),
        encoding="utf-8",
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


def test_any_same_tier_repeat_satisfies_readiness(tmp_path):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    (capture_root / "benchmark.yaml").write_text(
        """schema_version: '1.0.0'
benchmark_id: photo-repeat
jobs:
  photos: benchmark-photos
  video: benchmark-video
  lidar: benchmark-lidar
ground_truth: ground_truth.json
repeats: {photos: benchmark-photos-repeat}
incumbent: incumbent/floorplan.json
""",
        encoding="utf-8",
    )
    primary = capture_root / "benchmark-photos"
    repeat = capture_root / "benchmark-photos-repeat"
    primary.mkdir()
    repeat.mkdir()
    (primary / "manifest.yaml").write_text(
        "job_id: primary-photos\ntier: photos\n", encoding="utf-8"
    )
    (repeat / "manifest.yaml").write_text(
        "job_id: repeat-photos\n"
        "tier: photos\n"
        "repeat_of_job_id: primary-photos\n"
        "repeat_room_ids: [my-room]\n",
        encoding="utf-8",
    )

    report = run_benchmark(capture_root, tmp_path / "output")

    repeat_check = next(
        item for item in report["inputs"] if item["id"] == "repeat_capture"
    )
    assert repeat_check["status"] == "ready"


def test_repeat_must_link_to_primary_job(tmp_path):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    (capture_root / "benchmark.yaml").write_text(
        """schema_version: '1.0.0'
benchmark_id: bad-repeat
jobs:
  photos: benchmark-photos
  video: benchmark-video
  lidar: benchmark-lidar
ground_truth: ground_truth.json
repeats: {photos: benchmark-photos-repeat}
incumbent: incumbent/floorplan.json
""",
        encoding="utf-8",
    )
    primary = capture_root / "benchmark-photos"
    repeat = capture_root / "benchmark-photos-repeat"
    primary.mkdir()
    repeat.mkdir()
    (primary / "manifest.yaml").write_text(
        "job_id: primary-photos\ntier: photos\n", encoding="utf-8"
    )
    (repeat / "manifest.yaml").write_text(
        "job_id: repeat-photos\n"
        "tier: photos\n"
        "repeat_of_job_id: another-job\n"
        "repeat_room_ids: [my-room]\n",
        encoding="utf-8",
    )

    report = run_benchmark(capture_root, tmp_path / "output")

    repeat_check = next(
        item for item in report["inputs"] if item["id"] == "repeat_capture"
    )
    assert repeat_check["status"] == "pending"
    assert "repeat_of_job_id" in repeat_check["detail"]


def test_benchmark_cli_treats_pending_as_a_successful_audit(tmp_path):
    output = tmp_path / "output"

    exit_code = main(
        ["benchmark", str(tmp_path / "missing-captures"), "--out", str(output)]
    )

    assert exit_code == 0
    report = json.loads((output / "benchmark-status.json").read_text(encoding="utf-8"))
    assert report["status"] == "pending_inputs"
