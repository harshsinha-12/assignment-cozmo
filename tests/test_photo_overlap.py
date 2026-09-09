from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from cozmo_floorplan.io.photos import load_photo_rooms
from cozmo_floorplan.recon.photo_overlap import analyze_photo_overlap


def _write_room(
    photos_dir: Path,
    room: str,
    images: list[np.ndarray],
) -> None:
    room_dir = photos_dir / room
    room_dir.mkdir(parents=True)
    for index, image in enumerate(images):
        assert cv2.imwrite(str(room_dir / f"{index:02d}.jpg"), image)


def _textured_image(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    image = rng.integers(0, 256, (360, 480, 3), dtype=np.uint8)
    return cv2.GaussianBlur(image, (3, 3), 0)


def _translated_views(seed: int, count: int) -> list[np.ndarray]:
    base = _textured_image(seed)
    return [
        cv2.warpAffine(
            base,
            np.float32([[1.0, 0.0, index * 8.0], [0.0, 1.0, index * 3.0]]),
            (480, 360),
        )
        for index in range(count)
    ]


def _write_exif_oriented_jpeg(
    path: Path, display_bgr: np.ndarray, orientation: int
) -> None:
    visual = Image.fromarray(cv2.cvtColor(display_bgr, cv2.COLOR_BGR2RGB))
    stored = {
        1: visual,
        6: visual.transpose(Image.Transpose.ROTATE_90),
    }[orientation]
    exif = Image.Exif()
    exif[0x0112] = orientation
    stored.save(path, format="JPEG", quality=95, exif=exif)


def test_exif_oriented_pair_still_builds_within_room_edge(tmp_path):
    photos_dir = tmp_path / "photos"
    views = _translated_views(7, 2)
    room_dir = photos_dir / "room-a"
    room_dir.mkdir(parents=True)
    assert cv2.imwrite(str(room_dir / "00.jpg"), views[0])
    _write_exif_oriented_jpeg(room_dir / "01.jpg", views[1], 6)

    diagnostics = analyze_photo_overlap(load_photo_rooms(photos_dir))

    assert diagnostics.rooms[0].connected is True
    assert diagnostics.rooms[0].eligible_edges == 1


def test_within_room_overlap_builds_connected_graph(tmp_path):
    photos_dir = tmp_path / "photos"
    _write_room(photos_dir, "room-a", _translated_views(7, 3))

    diagnostics = analyze_photo_overlap(load_photo_rooms(photos_dir))

    room = diagnostics.rooms[0]
    assert room.connected is True
    assert room.component_count == 1
    assert len(room.components[0]) == 3
    assert room.eligible_edges >= 2
    assert all(pair.geometric_inliers >= 12 for pair in diagnostics.pairs)


def test_unrelated_rooms_do_not_create_cross_room_candidate(tmp_path):
    photos_dir = tmp_path / "photos"
    _write_room(photos_dir, "room-a", _translated_views(11, 2))
    _write_room(photos_dir, "room-b", _translated_views(29, 2))

    diagnostics = analyze_photo_overlap(load_photo_rooms(photos_dir))

    assert all(room.connected for room in diagnostics.rooms)
    assert diagnostics.cross_room_candidates == ()
    cross_pairs = [
        pair for pair in diagnostics.pairs if pair.relationship == "cross_room"
    ]
    assert len(cross_pairs) == 4
    assert not any(pair.eligible for pair in cross_pairs)


def test_featureless_image_remains_visible_as_disconnected_component(tmp_path):
    photos_dir = tmp_path / "photos"
    images = _translated_views(41, 2)
    images.append(np.zeros((360, 480, 3), dtype=np.uint8))
    _write_room(photos_dir, "room-a", images)

    diagnostics = analyze_photo_overlap(load_photo_rooms(photos_dir))

    room = diagnostics.rooms[0]
    assert room.connected is False
    assert room.component_count == 2
    assert ("02.jpg",) in room.components
    blank_pairs = [pair for pair in diagnostics.pairs if pair.right_image == "02.jpg"]
    assert blank_pairs
    assert all("low_keypoint_yield" in pair.rejection_reasons for pair in blank_pairs)


def test_sift_fallback_connects_low_contrast_translated_views(tmp_path):
    photos_dir = tmp_path / "photos"
    base = np.full((480, 640, 3), 118, dtype=np.uint8)
    rng = np.random.default_rng(73)
    for _ in range(180):
        center = tuple(int(value) for value in rng.integers([20, 20], [620, 460]))
        shade = int(rng.integers(105, 132))
        cv2.circle(base, center, int(rng.integers(2, 7)), (shade,) * 3, -1)
    views = [
        cv2.warpAffine(
            base,
            np.float32([[1.0, 0.0, offset], [0.0, 1.0, offset / 3]]),
            (640, 480),
        )
        for offset in (0, 14, 28)
    ]
    _write_room(photos_dir, "room-a", views)

    diagnostics = analyze_photo_overlap(load_photo_rooms(photos_dir))

    assert diagnostics.rooms[0].connected is True
    assert any(
        pair.geometric_model.startswith("sift_clahe:")
        for pair in diagnostics.pairs
        if pair.eligible
    )
