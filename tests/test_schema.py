import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "floorplan.schema.json"
FIXTURE = ROOT / "data" / "fixtures" / "synthetic_two_room" / "ground_truth.json"
MANIFEST = ROOT / "data" / "fixtures" / "synthetic_two_room" / "manifest.yaml"


def test_schema_file_is_json():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["title"] == "Cozmo FloorPlan IR"


def test_synthetic_ground_truth_validates():
    schema = json.loads(SCHEMA_PATH.read_text())
    instance = json.loads(FIXTURE.read_text())
    jsonschema.validate(instance=instance, schema=schema)


def test_synthetic_door_is_80cm():
    instance = json.loads(FIXTURE.read_text())
    door = next(o for o in instance["openings"] if o["id"] == "door_ab")
    assert door["width"] == 80
    assert instance["units"] == "cm"


def test_manifest_door_matches_ground_truth():
    manifest = yaml.safe_load(MANIFEST.read_text())
    door = next(x for x in manifest["known_lengths_cm"] if x["kind"] == "door_width")
    instance = json.loads(FIXTURE.read_text())
    gt_door = next(o for o in instance["openings"] if o["kind"] == "door")
    assert door["cm"] == gt_door["width"]
