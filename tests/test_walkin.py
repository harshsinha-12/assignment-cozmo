import json
from pathlib import Path

import cv2
import numpy as np
import pytest

import cozmo_floorplan.walkin.runner as runner_module
from cozmo_floorplan.cli import main
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.walkin.manifest import load_walkin_manifest
from cozmo_floorplan.walkin.runner import run_walkin
from cozmo_floorplan.walkin.subset import materialize_two_photo_job

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "data" / "templates" / "walkin"
TRUTH_PATH = ROOT / "data" / "fixtures" / "synthetic_two_room" / "ground_truth.json"


def _write_photo(path: Path, *, shade: int = 80) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = np.full((96, 128, 3), shade, dtype=np.uint8)
    cv2.line(image, (8, 80), (120, 20), (255, 255, 255), 3)
    assert cv2.imwrite(str(path), image)


def _write_job(job_dir: Path, *, tier: str, room_id: str = "holdout-room") -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "manifest.yaml").write_text(
        f"job_id: {job_dir.name}\ntier: {tier}\nrooms:\n  - {room_id}\n",
        encoding="utf-8",
    )
    (job_dir / tier).mkdir(exist_ok=True)


def test_missing_capture_root_writes_pending_report(tmp_path):
    output = tmp_path / "output"

    report = run_walkin(tmp_path / "not-captured-yet", output)

    assert report["status"] == "pending_inputs"
    assert "capture_root" in report["pending_inputs"]
    assert "ground_truth" in report["pending_inputs"]
    assert all(item["status"] == "pending" for item in report["evaluations"])
    assert (output / "walkin-status.json").is_file()
    assert (output / "walkin-summary.md").is_file()


def test_walkin_manifest_rejects_path_escape(tmp_path):
    (tmp_path / "walkin.yaml").write_text(
        """schema_version: '1.0.0'
walkin_id: unsafe
room_id: kitchen
jobs:
  photos: ../outside
  video: walkin-video
  lidar: walkin-lidar
ground_truth: ground_truth.json
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="escapes capture root"):
        load_walkin_manifest(tmp_path)


def test_forbidden_benchmark_room_refuses_to_score(tmp_path):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    (capture_root / "walkin.yaml").write_text(
        TEMPLATE_ROOT.joinpath("walkin.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    photos = capture_root / "walkin-photos"
    _write_job(photos, tier="photos", room_id="my-room")
    _write_photo(photos / "photos" / "my-room" / "01.jpg")
    _write_photo(photos / "photos" / "my-room" / "02.jpg")
    _write_job(capture_root / "walkin-video", tier="video")
    _write_job(capture_root / "walkin-lidar", tier="lidar")

    report = run_walkin(capture_root, tmp_path / "output")

    assert report["status"] == "invalid_holdout"
    assert "my-room" in report["forbidden_collisions"]
    assert all(item["status"] == "skipped" for item in report["runs"])


def test_complete_holdout_runs_every_tier_and_records_timing(monkeypatch, tmp_path):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    truth_text = TRUTH_PATH.read_text(encoding="utf-8")
    (capture_root / "ground_truth.json").write_text(truth_text, encoding="utf-8")
    (capture_root / "walkin.yaml").write_text(
        """schema_version: '1.0.0'
walkin_id: kitchen-holdout
room_id: kitchen
jobs:
  photos: walkin-photos
  video: walkin-video
  lidar: walkin-lidar
ground_truth: ground_truth.json
""",
        encoding="utf-8",
    )
    for name, tier in (
        ("walkin-photos", "photos"),
        ("walkin-video", "video"),
        ("walkin-lidar", "lidar"),
    ):
        _write_job(capture_root / name, tier=tier, room_id="kitchen")
    truth = json.loads(truth_text)
    monkeypatch.setattr(
        runner_module,
        "run_job_with_ablation",
        lambda _job: (truth, None),
    )

    report = run_walkin(capture_root, tmp_path / "output")

    assert report["status"] == "complete"
    assert not report["pending_inputs"]
    assert report["observed_rooms"] == ["kitchen"]
    assert not report["forbidden_collisions"]
    timed_runs = [item for item in report["runs"] if item["tier"] != "photos_2still"]
    assert len(timed_runs) == 3
    assert all(item["status"] == "complete" for item in timed_runs)
    assert all(isinstance(item["elapsed_s"], float) for item in timed_runs)
    assert all(item["status"] == "complete" for item in report["evaluations"])


def test_two_photo_subset_crash_tests_the_official_floor(tmp_path):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    (capture_root / "walkin.yaml").write_text(
        """schema_version: '1.0.0'
walkin_id: kitchen-holdout
room_id: kitchen
jobs:
  photos: walkin-photos
  video: walkin-video
  lidar: walkin-lidar
ground_truth: ground_truth.json
""",
        encoding="utf-8",
    )
    photos = capture_root / "walkin-photos"
    _write_job(photos, tier="photos", room_id="kitchen")
    for index in range(3):
        _write_photo(photos / "photos" / "kitchen" / f"{index:02d}.jpg", shade=40 + index)

    report = run_walkin(capture_root, tmp_path / "output")
    subset = next(item for item in report["runs"] if item["tier"] == "photos_2still")
    subset_room = tmp_path / "output" / "photos-2still" / "job" / "photos" / "kitchen"

    assert report["status"] == "pending_inputs"
    assert subset["status"] == "complete"
    assert subset["pipeline_status"] in {"failed", "partial", "ok"}
    assert sorted(path.name for path in subset_room.iterdir()) == ["00.jpg", "01.jpg"]


def test_two_photo_materialize_keeps_first_two_stills(tmp_path):
    source = tmp_path / "source"
    _write_job(source, tier="photos", room_id="kitchen")
    for index in range(4):
        _write_photo(source / "photos" / "kitchen" / f"{index:02d}.jpg", shade=50 + index)

    destination = materialize_two_photo_job(source, tmp_path / "subset")

    assert destination is not None
    names = sorted(path.name for path in (destination / "photos" / "kitchen").iterdir())
    assert names == ["00.jpg", "01.jpg"]


def test_walkin_templates_load_as_declared_tiers() -> None:
    for tier, folder in (
        ("photos", "walkin-photos"),
        ("video", "walkin-video"),
        ("lidar", "walkin-lidar"),
    ):
        job = load_job(TEMPLATE_ROOT / folder)
        assert job.tier == tier
        assert job.manifest["rooms"] == ["holdout-room"]


def test_walkin_cli_treats_pending_as_a_successful_audit(tmp_path):
    output = tmp_path / "output"

    exit_code = main(["walkin", str(tmp_path / "missing-captures"), "--out", str(output)])

    assert exit_code == 0
    report = json.loads((output / "walkin-status.json").read_text(encoding="utf-8"))
    assert report["status"] == "pending_inputs"


def test_walkin_cli_rejects_benchmark_room_reuse(tmp_path):
    capture_root = tmp_path / "capture"
    capture_root.mkdir()
    (capture_root / "walkin.yaml").write_text(
        TEMPLATE_ROOT.joinpath("walkin.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    photos = capture_root / "walkin-photos"
    _write_job(photos, tier="photos", room_id="pooja-room")
    _write_photo(photos / "photos" / "pooja-room" / "01.jpg")
    _write_photo(photos / "photos" / "pooja-room" / "02.jpg")
    output = tmp_path / "output"

    exit_code = main(["walkin", str(capture_root), "--out", str(output)])

    assert exit_code == 2
    report = json.loads((output / "walkin-status.json").read_text(encoding="utf-8"))
    assert report["status"] == "invalid_holdout"
    assert "pooja-room" in report["forbidden_collisions"]
