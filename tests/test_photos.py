import json
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job, load_job
from cozmo_floorplan.io.photos import load_photo_rooms
from cozmo_floorplan.pipeline import run_job
import cozmo_floorplan.pipeline as pipeline_module
from cozmo_floorplan.recon.photo_image import load_resized_gray
from cozmo_floorplan.recon.photos import reconstruct_photos
from cozmo_floorplan.recon.photos_config import PhotoOverlapConfig
from cozmo_floorplan.schema import validate_floorplan
from cozmo_floorplan.utils.images import load_display_oriented_bgr


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


def _write_exif_oriented_jpeg(
    path: Path, display_rgb: np.ndarray, orientation: int
) -> None:
    """Store pixels rotated so EXIF orientation restores `display_rgb`."""

    visual = Image.fromarray(display_rgb)
    stored = {
        1: visual,
        3: visual.transpose(Image.Transpose.ROTATE_180),
        6: visual.transpose(Image.Transpose.ROTATE_90),
        8: visual.transpose(Image.Transpose.ROTATE_270),
    }[orientation]
    exif = Image.Exif()
    exif[0x0112] = orientation
    path.parent.mkdir(parents=True, exist_ok=True)
    stored.save(path, format="JPEG", quality=95, exif=exif)


def test_exif_orientation_is_applied_before_photo_ingest(tmp_path):
    photos_dir = tmp_path / "photos"
    display = np.zeros((120, 80, 3), dtype=np.uint8)
    display[:20] = (0, 255, 0)
    display[-12:] = (255, 0, 0)
    _write_photo(photos_dir / "room_a" / "01.jpg")
    _write_exif_oriented_jpeg(photos_dir / "room_a" / "02.jpg", display, 6)

    rooms = load_photo_rooms(photos_dir)
    oriented = load_display_oriented_bgr(photos_dir / "room_a" / "02.jpg")
    gray = load_resized_gray(photos_dir / "room_a" / "02.jpg", 900)

    assert rooms[0].frames[1].width_px == 80
    assert rooms[0].frames[1].height_px == 120
    assert oriented is not None
    assert oriented.shape[0] == 120
    assert oriented.shape[1] == 80
    assert gray.shape[0] > gray.shape[1]
    top_bgr = oriented[:20].mean(axis=(0, 1))
    bottom_bgr = oriented[-12:].mean(axis=(0, 1))
    assert top_bgr[1] > top_bgr[0] + 100
    assert top_bgr[1] > top_bgr[2] + 100
    assert bottom_bgr[2] > bottom_bgr[0] + 100
    assert bottom_bgr[2] > bottom_bgr[1] + 100


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


def test_connected_planar_overlap_still_refuses_guessed_centimetres(tmp_path):
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

    assert raised.value.warning_code == "low_confidence"
    assert "overlap graph is eligible" in str(raised.value)
    assert "centimetres will not be guessed" in str(raised.value).lower()


def _lookat_camera(eye, target, image_size, focal_fraction=0.9):
    forward = np.asarray(target, dtype=np.float64) - np.asarray(eye, dtype=np.float64)
    forward /= np.linalg.norm(forward)
    down = np.array([0.0, -1.0, 0.0])
    down = down - forward * float(np.dot(down, forward))
    down /= np.linalg.norm(down)
    right = np.cross(down, forward)
    right /= np.linalg.norm(right)
    rotation = np.vstack((right, down, forward))
    translation = -rotation @ np.asarray(eye, dtype=np.float64)
    width, height = image_size
    focal = focal_fraction * max(width, height)
    intrinsic = np.array(
        [[focal, 0.0, width / 2.0], [0.0, focal, height / 2.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    return intrinsic, rotation, translation


def _face_texture(seed: int, size: int = 256) -> np.ndarray:
    rng = np.random.default_rng(seed)
    image = rng.integers(40, 220, (size, size, 3), dtype=np.uint8)
    for index in range(24):
        color = tuple(int(value) for value in rng.integers(0, 255, 3))
        center = (
            int(rng.integers(16, size - 16)),
            int(rng.integers(16, size - 16)),
        )
        cv2.circle(image, center, int(rng.integers(6, 22)), color, -1)
        top_left = (
            int(rng.integers(0, size - 40)),
            int(rng.integers(0, size - 40)),
        )
        cv2.rectangle(
            image,
            top_left,
            (top_left[0] + 28, top_left[1] + 12),
            color,
            2,
        )
        cv2.putText(
            image,
            str(index),
            (center[0] - 8, center[1] + 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
    return image


def _project_points(points, intrinsic, rotation, translation):
    camera = (rotation @ points.T).T + translation
    projected = (intrinsic @ camera.T).T
    valid = camera[:, 2] > 0.15
    pixels = np.full((len(points), 2), np.nan)
    pixels[valid] = projected[valid, :2] / projected[valid, 2:3]
    return pixels, camera[:, 2]


def _render_room_view(eye, target, image_size=(480, 360)) -> np.ndarray:
    width, height = image_size
    intrinsic, rotation, translation = _lookat_camera(eye, target, image_size)
    room_w, room_h, room_d = 4.0, 2.7, 3.2
    faces = {
        "floor": (
            np.array(
                [[0, 0, 0], [room_w, 0, 0], [room_w, 0, room_d], [0, 0, room_d]],
                dtype=np.float64,
            ),
            _face_texture(1),
        ),
        "ceiling": (
            np.array(
                [
                    [0, room_h, 0],
                    [0, room_h, room_d],
                    [room_w, room_h, room_d],
                    [room_w, room_h, 0],
                ],
                dtype=np.float64,
            ),
            _face_texture(2),
        ),
        "z0": (
            np.array(
                [[0, 0, 0], [0, room_h, 0], [room_w, room_h, 0], [room_w, 0, 0]],
                dtype=np.float64,
            ),
            _face_texture(3),
        ),
        "z1": (
            np.array(
                [
                    [0, 0, room_d],
                    [room_w, 0, room_d],
                    [room_w, room_h, room_d],
                    [0, room_h, room_d],
                ],
                dtype=np.float64,
            ),
            _face_texture(4),
        ),
        "x0": (
            np.array(
                [[0, 0, 0], [0, 0, room_d], [0, room_h, room_d], [0, room_h, 0]],
                dtype=np.float64,
            ),
            _face_texture(5),
        ),
        "x1": (
            np.array(
                [
                    [room_w, 0, 0],
                    [room_w, room_h, 0],
                    [room_w, room_h, room_d],
                    [room_w, 0, room_d],
                ],
                dtype=np.float64,
            ),
            _face_texture(6),
        ),
    }
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    painted = []
    for corners, texture in faces.values():
        pixels, depths = _project_points(corners, intrinsic, rotation, translation)
        if not np.all(np.isfinite(pixels)):
            continue
        mean_depth = float(np.mean(depths))
        src = np.float32(
            [
                [0, 0],
                [texture.shape[1] - 1, 0],
                [texture.shape[1] - 1, texture.shape[0] - 1],
                [0, texture.shape[0] - 1],
            ]
        )
        homography = cv2.getPerspectiveTransform(src, pixels.astype(np.float32))
        warped = cv2.warpPerspective(texture, homography, (width, height))
        mask = cv2.warpPerspective(
            np.full(texture.shape[:2], 255, dtype=np.uint8),
            homography,
            (width, height),
        )
        painted.append((mean_depth, warped, mask))
    for _depth, warped, mask in sorted(painted, key=lambda item: -item[0]):
        visible = mask > 0
        canvas[visible] = warped[visible]
    return canvas


def test_overlapping_metric_stills_emit_a_partial_photo_floorplan(tmp_path):
    job_dir = tmp_path / "metric_stills"
    photos_dir = _write_job(job_dir)
    target = (2.0, 1.25, 3.0)
    cameras = (
        (1.35, 1.45, 1.05),
        (2.00, 1.45, 1.15),
        (2.65, 1.45, 1.05),
        (2.00, 1.48, 1.55),
    )
    room_dir = photos_dir / "kitchen"
    room_dir.mkdir(parents=True)
    for index, eye in enumerate(cameras, start=1):
        image = _render_room_view(eye, target)
        assert cv2.imwrite(str(room_dir / f"{index:02d}.jpg"), image)

    document = reconstruct_photos(
        load_job(job_dir),
        overlap_config=PhotoOverlapConfig(enable_sift_fallback=False),
    )

    assert document["status"] in {"ok", "partial"}
    assert document["provenance"]["tier"] == "photos"
    assert document["provenance"]["scale_source"] == "known_length"
    assert len(document["rooms"]) == 1
    assert len(document["walls"]) == 4
    widths = [wall["length"]["value"] for wall in document["walls"]]
    assert all(value > 80 for value in widths)
    assert document["rooms"][0]["ceiling_height"]["value"] > 200
    validate_floorplan(document)


def test_pipeline_forwards_a_successful_photo_reconstruction(monkeypatch, tmp_path):
    expected = json.loads(
        (Path(__file__).parents[1] / "data/fixtures/synthetic_two_room/ground_truth.json").read_text(
            encoding="utf-8"
        )
    )
    expected["status"] = "partial"
    expected["provenance"]["tier"] = "photos"
    job = Job(
        root=tmp_path,
        job_id="photo-job",
        tier="photos",
        device="iPhone 15",
        manifest={"job_id": "photo-job", "tier": "photos"},
        input_refs=("manifest.yaml", "photos/room-a/01.jpg"),
    )
    monkeypatch.setattr(pipeline_module, "reconstruct_photos", lambda _job: expected)
    monkeypatch.setattr(
        pipeline_module, "apply_drift_correction", lambda document, enabled: document
    )
    monkeypatch.setattr(
        pipeline_module, "enrich_floorplan", lambda _job, document: document
    )

    document, ablation = pipeline_module.run_loaded_job(job)

    assert document is expected
    assert document["provenance"]["tier"] == "photos"
    assert ablation is expected
