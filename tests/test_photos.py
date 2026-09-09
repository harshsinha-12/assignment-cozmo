from pathlib import Path

import cv2
import numpy as np
import pytest

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.io.photos import load_photo_rooms
from cozmo_floorplan.pipeline import run_job
from cozmo_floorplan.recon.photos import reconstruct_photos


def _write_job(job_dir: Path) -> Path:
    job_dir.mkdir(parents=True)
    (job_dir / "manifest.yaml").write_text(
        "job_id: photo_fixture\ntier: photos\ndevice: iPhone 17 Pro\n",
        encoding="utf-8",
    )
    photos_dir = job_dir / "photos"
    photos_dir.mkdir()
    return photos_dir


def _write_photo(path: Path, *, shade: int = 80) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = np.full((96, 128, 3), shade, dtype=np.uint8)
    cv2.line(image, (8, 80), (120, 20), (255, 255, 255), 3)
    assert cv2.imwrite(str(path), image)


def test_empty_photo_root_requires_room_folders(tmp_path):
    job_dir = tmp_path / "empty"
    _write_job(job_dir)

    document = run_job(job_dir)

    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "incomplete_scan"
    assert "room folders" in document["warnings"][0]["message"]


@pytest.mark.parametrize("count", [1, 9])
def test_room_enforces_official_two_to_eight_photo_count(tmp_path, count):
    job_dir = tmp_path / f"count_{count}"
    photos_dir = _write_job(job_dir)
    for index in range(count):
        _write_photo(photos_dir / "room_a" / f"{index:02d}.jpg", shade=30 + index)

    with pytest.raises(ReconstructionError) as raised:
        reconstruct_photos(load_job(job_dir))

    assert raised.value.warning_code == "incomplete_scan"
    assert f"contains {count}" in str(raised.value)


def test_corrupt_photo_is_rejected_before_reconstruction(tmp_path):
    job_dir = tmp_path / "corrupt"
    photos_dir = _write_job(job_dir)
    _write_photo(photos_dir / "room_a" / "01.jpg")
    (photos_dir / "room_a" / "02.jpg").write_text("not a jpeg", encoding="utf-8")

    with pytest.raises(ReconstructionError) as raised:
        load_photo_rooms(photos_dir)

    assert "Could not decode" in str(raised.value)


def test_multi_room_photos_are_validated_without_inventing_centimetres(tmp_path):
    job_dir = tmp_path / "multi_room"
    photos_dir = _write_job(job_dir)
    for room in ("hallway", "room_a"):
        for index in range(2):
            _write_photo(photos_dir / room / f"{index + 1:02d}.jpg", shade=60 + index)

    rooms = load_photo_rooms(photos_dir)
    document = run_job(job_dir)

    assert [room.identifier for room in rooms] == ["hallway", "room_a"]
    assert [len(room.frames) for room in rooms] == [2, 2]
    assert document["status"] == "failed"
    assert document["warnings"][0]["code"] == "insufficient_overlap"
    assert "Validated 4 decodable photos" in document["warnings"][0]["message"]
    assert "overlap graph is disconnected" in document["warnings"][0]["message"]
    assert (
        "centimetres will not be guessed" in document["warnings"][0]["message"].lower()
    )


def test_connected_rooms_reach_metric_sfm_boundary(tmp_path):
    job_dir = tmp_path / "connected_rooms"
    photos_dir = _write_job(job_dir)
    rng = np.random.default_rng(17)
    base = rng.integers(0, 256, (360, 480, 3), dtype=np.uint8)
    base = cv2.GaussianBlur(base, (3, 3), 0)
    for room in ("room_a", "room_b"):
        for index in range(2):
            transform = np.float32([[1.0, 0.0, index * 8.0], [0.0, 1.0, index * 3.0]])
            image = cv2.warpAffine(base, transform, (480, 360))
            path = photos_dir / room / f"{index + 1:02d}.jpg"
            path.parent.mkdir(parents=True, exist_ok=True)
            assert cv2.imwrite(str(path), image)

    with pytest.raises(ReconstructionError) as raised:
        reconstruct_photos(load_job(job_dir))

    assert raised.value.warning_code == "unsupported_tier"
    assert "overlap graph is eligible" in str(raised.value)
    assert "Metric SfM" in str(raised.value)
