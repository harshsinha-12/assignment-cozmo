import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
INCUMBENT = ROOT / "data" / "private" / "benchmark-incumbent" / "floorplan.json"
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"


@pytest.mark.skipif(not INCUMBENT.is_file(), reason="private Magicplan incumbent is absent")
def test_magicplan_incumbent_encodes_displayed_my_room_walls_not_pooja_walls():
    document = json.loads(INCUMBENT.read_text(encoding="utf-8"))
    jsonschema.validate(
        instance=document,
        schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
    )

    my_walls = [wall for wall in document["walls"] if wall["room_ids"] == ["my-room"]]
    lengths = sorted(wall["length"]["value"] for wall in my_walls)
    assert lengths == [329, 329, 420, 420]
    assert all("pooja-room" not in wall["id"] for wall in document["walls"])
    areas = {room["id"]: room["area"]["value"] for room in document["rooms"]}
    assert areas["my-room"] == 126400
    assert areas["pooja-room"] == 120400
