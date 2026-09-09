import json
from dataclasses import replace
from pathlib import Path

import jsonschema

from cozmo_floorplan.io.job import Job
from cozmo_floorplan.recon.record3d_floorplan import (
    Record3DRoomReconstruction,
    build_record3d_floorplan,
)
from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.record3d_planes import (
    HorizontalPlaneLevels,
    ManhattanRoomCandidate,
)
from cozmo_floorplan.recon.record3d_uncertainty import Record3DUncertainty
from cozmo_floorplan.stitch import apply_drift_correction

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"


def _reconstruction(root: Path, name: str = "room-a") -> Record3DRoomReconstruction:
    source = root / "lidar" / f"{name}.r3d"
    room = ManhattanRoomCandidate(
        levels=HorizontalPlaneLevels(
            floor_y_m=-1.0,
            ceiling_y_m=1.8,
            floor_support_points=1000,
            ceiling_support_points=900,
        ),
        yaw_degrees=0.0,
        walls=(),
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
        vertical_support_columns=200,
    )
    opening = Record3DOpeningCandidate(
        wall_index=0,
        kind="door",
        offset_m=1.2,
        width_m=0.9,
        height_m=2.1,
        sparse_profile_bins=18,
        lintel_support_points=250,
    )
    return Record3DRoomReconstruction(
        source=source,
        room=room,
        openings=(opening,),
        frame_count=120,
        sampled_frame_count=61,
        metric_voxel_count=50_000,
    )


def _job(root: Path) -> Job:
    return Job(
        root=root,
        job_id="record3d-job",
        tier="lidar",
        device="iPhone Pro",
        manifest={"job_id": "record3d-job", "tier": "lidar"},
        input_refs=("manifest.yaml", "lidar/room-a.r3d"),
    )


def test_record3d_candidate_converts_to_interval_bearing_floorplan(tmp_path):
    document = build_record3d_floorplan(_job(tmp_path), (_reconstruction(tmp_path),))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    jsonschema.validate(instance=document, schema=schema)
    assert document["status"] == "partial"
    assert document["provenance"]["scale_source"] == "lidar"
    assert document["origin"]["frame"] == "record3d-world-xz"
    assert len(document["rooms"]) == 1
    assert len(document["walls"]) == 4
    assert len(document["openings"]) == 1
    assert document["rooms"][0]["area"]["value"] == 120_000
    assert document["rooms"][0]["ceiling_height"]["value"] == 280
    assert document["walls"][0]["length"]["value"] == 400
    assert document["openings"][0]["width"]["value"] == 90
    assert document["openings"][0]["offset_along_wall"]["value"] == 120
    assert document["openings"][0]["connects_room_ids"] == ["room-a"]
    assert document["openings"][0]["confidence"] == 0.60
    assert "independent holdout validation" in document["warnings"][0]["message"]


def test_multiple_archives_remain_explicitly_unregistered(tmp_path):
    first = _reconstruction(tmp_path, "room-a")
    second = _reconstruction(tmp_path, "room-b")

    document = build_record3d_floorplan(_job(tmp_path), (first, second))

    assert len(document["rooms"]) == 2
    assert any(
        warning["code"] == "disconnected_rooms"
        and "no shared opening association" in warning["message"]
        for warning in document["warnings"]
    )

    corrected = apply_drift_correction(document)

    assert (
        sum(
            warning["code"] == "disconnected_rooms" for warning in corrected["warnings"]
        )
        == 1
    )


def test_support_conditioned_intervals_reach_floorplan_measurements(tmp_path):
    uncertainty = Record3DUncertainty(
        x_span_half_width_cm=10.0,
        z_span_half_width_cm=20.0,
        ceiling_half_width_cm=7.0,
        area_relative_half_width=0.12,
        wall_residual_quantile_cm=(4.0, 6.0, 9.0, 11.0),
        floor_residual_quantile_cm=3.0,
        ceiling_residual_quantile_cm=4.0,
    )
    reconstruction = replace(_reconstruction(tmp_path), uncertainty=uncertainty)

    document = build_record3d_floorplan(_job(tmp_path), (reconstruction,))

    wall_half_widths = [
        wall["length"]["interval"]["high"] - wall["length"]["value"]
        for wall in document["walls"]
    ]
    ceiling = document["rooms"][0]["ceiling_height"]
    area = document["rooms"][0]["area"]
    assert wall_half_widths == [20.0, 10.0, 20.0, 10.0]
    assert ceiling["interval"]["high"] - ceiling["value"] == 7.0
    assert (area["interval"]["high"] - area["value"]) / area["value"] == 0.12
