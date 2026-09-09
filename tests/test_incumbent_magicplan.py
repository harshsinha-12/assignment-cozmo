import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
INCUMBENT = ROOT / "data" / "private" / "benchmark-incumbent" / "floorplan.json"
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"
NOTES = (
    ROOT
    / "data"
    / "private"
    / "benchmark-incumbent"
    / "raw"
    / "magicplan-version-here"
    / "notes.txt"
)


@pytest.mark.skipif(not INCUMBENT.is_file(), reason="private Magicplan incumbent is absent")
def test_magicplan_incumbent_encodes_displayed_my_room_and_traced_pooja_walls():
    document = json.loads(INCUMBENT.read_text(encoding="utf-8"))
    jsonschema.validate(
        instance=document,
        schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
    )

    my_walls = [wall for wall in document["walls"] if wall["room_ids"] == ["my-room"]]
    pooja_walls = [wall for wall in document["walls"] if wall["room_ids"] == ["pooja-room"]]
    my_lengths = sorted(wall["length"]["value"] for wall in my_walls)
    pooja_lengths = sorted(wall["length"]["value"] for wall in pooja_walls)
    assert my_lengths == [329, 329, 420, 420]
    assert pooja_lengths == pytest.approx(
        [61.42027, 142.345438, 156.871533, 299.216971, 370.182573, 431.602843],
        abs=1e-5,
    )
    areas = {room["id"]: room["area"]["value"] for room in document["rooms"]}
    assert areas["my-room"] == 126400
    assert areas["pooja-room"] == 120400
    notes = document["provenance"]["notes"]
    assert "2026.35.0" in notes
    assert "12.04 m2" in notes


@pytest.mark.skipif(not NOTES.is_file(), reason="private Magicplan notes are absent")
def test_magicplan_notes_record_app_store_version():
    text = NOTES.read_text(encoding="utf-8")
    assert "Exact version: 2026.35.0" in text
    assert "427424432" in text
