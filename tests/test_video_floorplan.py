import json
from pathlib import Path

import jsonschema

import cozmo_floorplan.pipeline as pipeline_module
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.recon.video_floorplan import (
    VideoRoomReconstruction,
    build_video_floorplan,
)
from cozmo_floorplan.recon.video_rooms import VideoRoomCandidate
from cozmo_floorplan.recon.video_surfaces import VideoPlaneCandidate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"


def _job(root: Path) -> Job:
    return Job(
        root=root,
        job_id="video-job",
        tier="video",
        device="iPhone Pro",
        manifest={"job_id": "video-job", "tier": "video"},
        input_refs=("manifest.yaml", "video/room-a.mp4", "video/room-a.poses.json"),
    )


def _reconstruction(root: Path, name: str = "room-a") -> VideoRoomReconstruction:
    floor = VideoPlaneCandidate("horizontal", "y", 0.0, 120, 0.2)
    ceiling = VideoPlaneCandidate("horizontal", "y", 2.8, 110, 0.18)
    wall = VideoPlaneCandidate("wall", "x", -2.0, 100, 0.16)
    room = VideoRoomCandidate(
        floor=floor,
        ceiling=ceiling,
        walls=(wall, wall, wall, wall),
        yaw_degrees=0.0,
        polygon_xz_m=((-2.0, -1.5), (2.0, -1.5), (2.0, 1.5), (-2.0, 1.5)),
        width_m=4.0,
        depth_m=3.0,
    )
    return VideoRoomReconstruction(
        source=root / "video" / f"{name}.mp4",
        pose_sidecar=root / "video" / f"{name}.poses.json",
        world_frame_id="walkthrough-session-a",
        scale_source="arkit_poses",
        room=room,
        sampled_frames=80,
        metric_voxel_count=4_000,
        accepted_pair_count=30,
    )


def test_video_room_converts_to_schema_valid_interval_floorplan(tmp_path):
    document = build_video_floorplan(_job(tmp_path), (_reconstruction(tmp_path),))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    jsonschema.validate(instance=document, schema=schema)
    assert document["status"] == "partial"
    assert document["provenance"]["tier"] == "video"
    assert document["provenance"]["scale_source"] == "arkit_poses"
    assert document["rooms"][0]["area"]["value"] == 120_000
    assert document["rooms"][0]["ceiling_height"]["value"] == 280
    assert len(document["walls"]) == 4
    assert document["walls"][0]["length"]["value"] == 400
    assert document["walls"][0]["length"]["interval"]["confidence"] == 0.70
    assert document["openings"] == []
    assert "uncalibrated" in document["warnings"][0]["message"]


def test_multiple_video_rooms_require_one_shared_world_frame(tmp_path):
    first = _reconstruction(tmp_path, "room-a")
    second = _reconstruction(tmp_path, "room-b")
    second = VideoRoomReconstruction(
        source=second.source,
        pose_sidecar=second.pose_sidecar,
        world_frame_id="different-session",
        scale_source=second.scale_source,
        room=second.room,
        sampled_frames=second.sampled_frames,
        metric_voxel_count=second.metric_voxel_count,
        accepted_pair_count=second.accepted_pair_count,
    )

    try:
        build_video_floorplan(_job(tmp_path), (first, second))
    except ValueError as exc:
        assert "world_frame_id" in str(exc)
    else:
        raise AssertionError("unrelated video world frames must be rejected")


def test_pipeline_returns_successful_video_adapter_document(monkeypatch, tmp_path):
    expected = build_video_floorplan(_job(tmp_path), (_reconstruction(tmp_path),))
    monkeypatch.setattr(pipeline_module, "reconstruct_video", lambda _job: expected)
    monkeypatch.setattr(
        pipeline_module, "enrich_floorplan", lambda _job, document: document
    )

    document, ablation = pipeline_module.run_loaded_job(_job(tmp_path))

    assert document["provenance"]["tier"] == "video"
    assert document["rooms"][0]["id"] == "room-a"
    assert ablation is None
