from pathlib import Path

import numpy as np
import pytest

import cozmo_floorplan.recon.record3d_points as points_module
from cozmo_floorplan.geom.rotations import quaternion_xyzw_matrix
from cozmo_floorplan.io.record3d import (
    Record3DCapture,
    Record3DFrame,
    Record3DMetadata,
)
from cozmo_floorplan.recon.record3d_config import Record3DPointCloudConfig
from cozmo_floorplan.recon.record3d_points import build_metric_point_cloud
from cozmo_floorplan.utils.sampling import evenly_spaced_indices


def _capture() -> Record3DCapture:
    return Record3DCapture(
        source=Path("synthetic.r3d"),
        metadata=Record3DMetadata(
            color_width_px=2,
            color_height_px=2,
            depth_width_px=2,
            depth_height_px=2,
            fps=60.0,
            timestamps_s=(0.0, 1 / 60),
            poses=(
                (0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0, 1.0, 10.0, 0.0, 0.0),
            ),
            intrinsics=((1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0)),
        ),
        frame_indices=(0, 1),
    )


def test_evenly_spaced_indices_include_both_ends_without_duplicates():
    assert evenly_spaced_indices(10, 4) == (0, 3, 6, 9)
    assert evenly_spaced_indices(2, 10) == (0, 1)
    assert evenly_spaced_indices(0, 3) == ()


def test_quaternion_matrix_normalizes_xyzw_and_rotates_points():
    half_root = np.sqrt(0.5)
    rotation = quaternion_xyzw_matrix((0.0, 0.0, half_root, half_root))

    rotated = rotation @ np.asarray([1.0, 0.0, 0.0])

    assert rotated == pytest.approx([0.0, 1.0, 0.0])
    assert rotation @ rotation.T == pytest.approx(np.eye(3))


def test_metric_point_cloud_back_projects_and_applies_camera_pose(monkeypatch):
    depth = np.ones((2, 2), dtype=np.float32)
    confidence = np.full((2, 2), 2, dtype=np.uint8)

    def fake_read_frame(_capture, index):
        return Record3DFrame(
            index=index,
            color_size_px=(2, 2),
            depth_m=depth,
            confidence=confidence,
        )

    monkeypatch.setattr(points_module, "read_record3d_frame", fake_read_frame)
    config = Record3DPointCloudConfig(
        sampled_frame_count=2,
        pixel_stride=1,
        minimum_confidence=1,
        minimum_depth_m=0.1,
        maximum_depth_m=2.0,
        voxel_size_m=0.01,
    )

    cloud = build_metric_point_cloud(_capture(), config=config)

    assert cloud.observed_depth_pixels == 8
    assert cloud.accepted_depth_pixels == 8
    assert len(cloud.points_m) == 8
    minimum, maximum = cloud.bounds_m
    assert minimum == pytest.approx((0.0, -1.0, -1.0))
    assert maximum == pytest.approx((11.0, 0.0, -1.0))


def test_metric_point_cloud_rejects_invalid_sampling_config():
    with pytest.raises(ValueError, match="pixel_stride"):
        build_metric_point_cloud(
            _capture(),
            config=Record3DPointCloudConfig(pixel_stride=0),
        )
