"""Cozmo Capture ZIP packages must unpack into the CLI job-folder contract."""

from pathlib import Path
from zipfile import ZipFile

import pytest

from cozmo_floorplan.errors import JobLoadError
from cozmo_floorplan.io.capture_package import (
    extract_capture_zip,
    inspect_capture_zip,
    open_job_directory,
    validate_capture_zip,
)
from cozmo_floorplan.io.job import load_job

FIXTURE_ROOMPLAN = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "fixtures"
    / "roomplan_two_room"
    / "lidar"
    / "roomplan.json"
)

MANIFEST = """job_id: cozmo-capture-test
tier: lidar
device: iPhone 17 Pro
capture_tool: Cozmo Capture 0.1.0
capture_format: roomplan-json-v1+record3d-r3d
"""


def _write_zip(path: Path, members: dict[str, bytes]) -> Path:
    with ZipFile(path, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return path


def _complete_members(*, wrapped: bool = True) -> dict[str, bytes]:
    prefix = "cozmo-capture-test/" if wrapped else ""
    return {
        f"{prefix}manifest.yaml": MANIFEST.encode("utf-8"),
        f"{prefix}lidar/roomplan.json": FIXTURE_ROOMPLAN.read_bytes(),
        f"{prefix}lidar/kitchen.r3d": b"r3d-placeholder",
    }


def test_inspect_strips_single_wrapper_folder(tmp_path):
    archive = _write_zip(tmp_path / "job.zip", _complete_members(wrapped=True))

    assert inspect_capture_zip(archive) == (
        "lidar/kitchen.r3d",
        "lidar/roomplan.json",
        "manifest.yaml",
    )


def test_extract_wrapped_zip_loads_as_lidar_job(tmp_path):
    archive = _write_zip(tmp_path / "job.zip", _complete_members(wrapped=True))
    job_dir = extract_capture_zip(archive, tmp_path / "unpacked")
    job = load_job(job_dir)

    assert job.tier == "lidar"
    assert job.job_id == "cozmo-capture-test"
    assert job.device == "iPhone 17 Pro"
    assert "lidar/roomplan.json" in job.input_refs
    assert "lidar/kitchen.r3d" in job.input_refs


def test_extract_root_layout_zip_loads_as_lidar_job(tmp_path):
    archive = _write_zip(tmp_path / "job.zip", _complete_members(wrapped=False))
    job = load_job(extract_capture_zip(archive, tmp_path / "unpacked"))

    assert job.tier == "lidar"
    assert (job.root / "lidar" / "roomplan.json").is_file()


def test_missing_manifest_is_rejected(tmp_path):
    archive = _write_zip(
        tmp_path / "job.zip",
        {"cozmo-capture-test/lidar/roomplan.json": FIXTURE_ROOMPLAN.read_bytes()},
    )

    with pytest.raises(JobLoadError, match="missing manifest.yaml"):
        validate_capture_zip(archive)


def test_missing_roomplan_is_rejected(tmp_path):
    archive = _write_zip(
        tmp_path / "job.zip",
        {"cozmo-capture-test/manifest.yaml": MANIFEST.encode("utf-8")},
    )

    with pytest.raises(JobLoadError, match="missing lidar/roomplan.json"):
        validate_capture_zip(archive)


def test_empty_rooms_are_rejected(tmp_path):
    archive = _write_zip(
        tmp_path / "job.zip",
        {
            "manifest.yaml": MANIFEST.encode("utf-8"),
            "lidar/roomplan.json": b'{"format":"roomplan-json-v1","rooms":[]}',
        },
    )

    with pytest.raises(JobLoadError, match="has no rooms"):
        extract_capture_zip(archive, tmp_path / "unpacked")


def test_zip_slip_member_is_rejected(tmp_path):
    archive = _write_zip(
        tmp_path / "job.zip",
        {
            **_complete_members(wrapped=False),
            "lidar/../../escape.yaml": b"job_id: stolen\n",
        },
    )

    with pytest.raises(JobLoadError, match="escapes destination"):
        extract_capture_zip(archive, tmp_path / "unpacked")


def test_open_job_directory_rejects_non_zip_files(tmp_path):
    payload = tmp_path / "notes.txt"
    payload.write_text("not a job\n", encoding="utf-8")

    with pytest.raises(JobLoadError, match="directory or .zip"):
        open_job_directory(payload)
