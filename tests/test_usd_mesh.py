from pathlib import Path

from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.io.usd_mesh import discover_usd_room_meshes, load_usd_room_capture
from cozmo_floorplan.pipeline import run_job
from cozmo_floorplan.walkin.runner import job_has_capture_media


def _mesh(name: str, width: float, center: tuple[float, float, float], x_axis: tuple[float, float, float]) -> str:
    return f'''def Mesh "{name}"
{{
    float3[] extent = [({-width / 2}, -1.25, -0.05), ({width / 2}, 1.25, 0.05)]
    matrix4d xformOp:transform = ( ({x_axis[0]}, {x_axis[1]}, {x_axis[2]}, 0), (0, 1, 0, 0), (0, 0, 1, 0), ({center[0]}, {center[1]}, {center[2]}, 1) )
}}
'''


def _write_usda_job(root: Path) -> Path:
    lidar = root / "lidar"
    lidar.mkdir(parents=True)
    (root / "manifest.yaml").write_text(
        "job_id: usd-room\ntier: lidar\ndevice: iPhone Pro\nrooms:\n  - guest-room\n",
        encoding="utf-8",
    )
    text = "#usda 1.0\n" + "\n".join(
        (
            _mesh("Wall0", 4.0, (2.0, 1.25, 0.0), (1.0, 0.0, 0.0)),
            _mesh("Wall1", 3.0, (4.0, 1.25, 1.5), (0.0, 0.0, 1.0)),
            _mesh("Wall2", 4.0, (2.0, 1.25, 3.0), (-1.0, 0.0, 0.0)),
            _mesh("Wall3", 3.0, (0.0, 1.25, 1.5), (0.0, 0.0, -1.0)),
            _mesh("Door0", 0.8, (4.0, 1.05, 1.5), (0.0, 0.0, 1.0)),
            _mesh("Chair0", 0.5, (1.0, 0.5, 1.0), (1.0, 0.0, 0.0)),
        )
    )
    (lidar / "room.usda").write_text(text, encoding="utf-8")
    return root


def test_semantic_usda_surfaces_convert_to_floorplan(tmp_path):
    job_dir = _write_usda_job(tmp_path / "job")

    document = run_job(job_dir)

    assert document["status"] == "ok"
    assert document["provenance"]["scale_source"] == "lidar"
    assert "semantic-usd-mesh" in document["provenance"]["pipeline"]
    assert [room["id"] for room in document["rooms"]] == ["guest-room"]
    assert len(document["walls"]) == 4
    assert len(document["openings"]) == 1
    assert document["openings"][0]["width"]["value"] == 80
    assert document["rooms"][0]["ceiling_height"]["value"] == 250


def test_usd_discovery_and_walkin_media_audit(tmp_path):
    job_dir = _write_usda_job(tmp_path / "job")
    (job_dir / "lidar" / "secondary.usdz").write_bytes(b"fixture")

    sources = discover_usd_room_meshes(job_dir / "lidar")

    assert [path.name for path in sources] == ["room.usda", "secondary.usdz"]
    assert job_has_capture_media(job_dir, "lidar") is True


def test_usda_parser_ignores_non_semantic_object_meshes(tmp_path):
    job_dir = _write_usda_job(tmp_path / "job")
    capture = load_usd_room_capture(
        job_dir / "lidar" / "room.usda",
        room_identifier="guest-room",
    )

    assert [surface.identifier for surface in capture.rooms[0].walls] == [
        "Wall0",
        "Wall1",
        "Wall2",
        "Wall3",
    ]
    assert [surface.identifier for surface in capture.rooms[0].openings] == ["Door0"]
    assert load_job(job_dir).input_refs[-1] == "lidar/room.usda"
