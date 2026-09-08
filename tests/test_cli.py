import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from cozmo_floorplan.cli import main

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"


def _write_manifest(job_dir: Path, *, tier: str = "photos") -> None:
    job_dir.mkdir()
    (job_dir / "manifest.yaml").write_text(
        f"job_id: test_job\ntier: {tier}\ndevice: iPhone 17 Pro\n",
        encoding="utf-8",
    )


def _read_and_validate(output_path: Path) -> dict:
    document = json.loads(output_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=document, schema=schema)
    return document


def test_run_writes_schema_valid_structured_adapter_failure(tmp_path):
    job_dir = tmp_path / "job"
    out_dir = tmp_path / "out"
    _write_manifest(job_dir)
    photos_dir = job_dir / "photos"
    photos_dir.mkdir()
    (photos_dir / "room_a_01.jpg").write_bytes(b"fixture-placeholder")

    exit_code = main(["run", str(job_dir), "--out", str(out_dir)])

    assert exit_code == 2
    document = _read_and_validate(out_dir / "floorplan.json")
    assert document["status"] == "failed"
    assert document["provenance"]["tier"] == "photos"
    assert document["provenance"]["inputs"] == ["manifest.yaml", "photos/room_a_01.jpg"]
    assert document["warnings"][0]["code"] == "unsupported_tier"


def test_missing_manifest_still_writes_structured_failure(tmp_path):
    job_dir = tmp_path / "job_without_manifest"
    out_dir = tmp_path / "out"
    job_dir.mkdir()

    exit_code = main(["run", str(job_dir), "--out", str(out_dir)])

    assert exit_code == 2
    document = _read_and_validate(out_dir / "floorplan.json")
    assert document["warnings"][0]["code"] == "incomplete_scan"
    assert "manifest" in document["warnings"][0]["message"].lower()


def test_missing_tier_directory_is_a_structured_failure(tmp_path):
    job_dir = tmp_path / "job"
    out_dir = tmp_path / "out"
    _write_manifest(job_dir, tier="video")

    exit_code = main(["run", str(job_dir), "--out", str(out_dir)])

    assert exit_code == 2
    document = _read_and_validate(out_dir / "floorplan.json")
    assert document["warnings"][0]["code"] == "incomplete_scan"
    assert "video/" in document["warnings"][0]["message"]


def test_exact_module_command_is_runnable(tmp_path):
    job_dir = tmp_path / "job"
    out_dir = tmp_path / "out"
    _write_manifest(job_dir, tier="lidar")
    (job_dir / "lidar").mkdir()

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "cozmo_floorplan", "run", str(job_dir), "--out", str(out_dir)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "status=failed" in result.stdout
    _read_and_validate(out_dir / "floorplan.json")
