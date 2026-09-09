import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pytest
from PIL import Image

import cozmo_floorplan.recon.record3d_validation as validation_module
from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.record3d import (
    Record3DFrame,
    load_record3d_capture,
    read_record3d_frame,
)
from cozmo_floorplan.recon.record3d_validation import validate_record3d_capture
from cozmo_floorplan.utils import lzfse as lzfse_module


def _write_record3d_archive(path: Path, *, omit: str | None = None) -> None:
    metadata = {
        "w": 4,
        "h": 3,
        "dw": 2,
        "dh": 2,
        "fps": 60,
        "frameTimestamps": [0.0, 1 / 60],
        "poses": [
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 2, 3],
        ],
        "perFrameIntrinsicCoeffs": [
            [100, 100, 2, 1.5],
            [100, 100, 2, 1.5],
        ],
    }
    color = BytesIO()
    Image.new("RGB", (4, 3), color=(20, 40, 60)).save(color, format="JPEG")
    depth = np.asarray([1.0, 2.0, np.nan, 4.0], dtype="<f4").tobytes()
    confidence = bytes([0, 1, 2, 2])
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("metadata", json.dumps(metadata))
        for index in range(2):
            entries = {
                f"rgbd/{index}.jpg": color.getvalue(),
                f"rgbd/{index}.depth": depth,
                f"rgbd/{index}.conf": confidence,
            }
            for name, payload in entries.items():
                if name != omit:
                    archive.writestr(name, payload)


def test_record3d_archive_indexes_metadata_and_decodes_typed_frame(tmp_path):
    path = tmp_path / "room.r3d"
    _write_record3d_archive(path)

    capture = load_record3d_capture(path)
    frame = read_record3d_frame(capture, 0, decoder=lambda payload: payload)

    assert capture.metadata.frame_count == 2
    assert capture.metadata.depth_width_px == 2
    assert capture.metadata.intrinsics[0] == (100.0, 100.0, 2.0, 1.5)
    assert capture.frame_indices == (0, 1)
    assert frame.color_size_px == (4, 3)
    assert frame.depth_m.shape == (2, 2)
    assert frame.depth_m[0, 1] == 2.0
    assert np.isnan(frame.depth_m[1, 0])
    assert frame.confidence.tolist() == [[0, 1], [2, 2]]


def test_record3d_archive_rejects_unmatched_modalities(tmp_path):
    path = tmp_path / "room.r3d"
    _write_record3d_archive(path, omit="rgbd/1.depth")

    with pytest.raises(ReconstructionError, match="mismatched depth frames"):
        load_record3d_capture(path)


def test_record3d_validation_samples_depth_and_camera_trajectory(tmp_path, monkeypatch):
    path = tmp_path / "room.r3d"
    _write_record3d_archive(path)
    capture = load_record3d_capture(path)

    def fake_read_frame(_capture, index):
        return Record3DFrame(
            index=index,
            color_size_px=(4, 3),
            depth_m=np.asarray([[1.0, 2.0], [np.nan, 25.0]], dtype=np.float32),
            confidence=np.asarray([[0, 1], [2, 2]], dtype=np.uint8),
        )

    monkeypatch.setattr(validation_module, "read_record3d_frame", fake_read_frame)

    summary = validate_record3d_capture(capture)

    assert summary.sampled_frame_indices == (0, 1)
    assert summary.valid_depth_fraction == 0.5
    assert summary.depth_range_m == (1.0, 2.0)
    assert summary.trajectory_extent_m == (1.0, 2.0, 3.0)


def test_lzfse_decoder_checks_exact_output_size(monkeypatch):
    monkeypatch.setattr(
        lzfse_module, "_python_lzfse_decoder", lambda: lambda _data: b"x"
    )

    with pytest.raises(lzfse_module.LzfseDecodeError, match="expected exactly 4"):
        lzfse_module.decompress_lzfse(b"payload", expected_size=4)
