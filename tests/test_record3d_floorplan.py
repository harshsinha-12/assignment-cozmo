import json
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
    assert "uncalibrated" in document["warnings"][0]["message"]


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
