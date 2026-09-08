import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest
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
    assert door["width"]["value"] == 80
    assert door["width"]["unit"] == "cm"
    assert door["width"]["interval"] == {"low": 80, "high": 80, "confidence": 1.0}
    assert instance["units"] == "cm"


def test_manifest_door_matches_ground_truth():
    manifest = yaml.safe_load(MANIFEST.read_text())
    door = next(x for x in manifest["known_lengths_cm"] if x["kind"] == "door_width")
    instance = json.loads(FIXTURE.read_text())
    gt_door = next(o for o in instance["openings"] if o["kind"] == "door")
    assert door["cm"] == gt_door["width"]["value"]


def test_claims_arrays_are_present_even_when_empty():
    instance = json.loads(FIXTURE.read_text())
    assert instance["damage"] == []
    assert instance["concealed_flags"] == []
    assert instance["scope"] == []


def test_all_fixture_measurements_have_intervals():
    instance = json.loads(FIXTURE.read_text())
    measurements = []
    for room in instance["rooms"]:
        measurements.extend([room["ceiling_height"], room["area"]])
    for wall in instance["walls"]:
        measurements.append(wall["length"])
    for opening in instance["openings"]:
        measurements.append(opening["width"])
        measurements.extend(opening[key] for key in ("height", "offset_along_wall") if key in opening)
    for edge in instance["stitch"]["edges"]:
        measurements.extend(edge[key] for key in ("dx", "dy", "dtheta", "residual") if key in edge)

    for measurement in measurements:
        interval = measurement["interval"]
        assert interval["low"] <= measurement["value"] <= interval["high"]


def test_schema_rejects_a_dimension_without_an_interval():
    schema = json.loads(SCHEMA_PATH.read_text())
    instance = json.loads(FIXTURE.read_text())
    del instance["walls"][0]["length"]["interval"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=instance, schema=schema)


def test_claims_contract_requires_rule_id_and_quantity_interval():
    schema = json.loads(SCHEMA_PATH.read_text())
    instance = json.loads(FIXTURE.read_text())
    instance["damage"] = [
        {
            "id": "damage_1",
            "surface": {"kind": "wall", "id": "a_north"},
            "class": "water_stain",
            "extent": {
                "value": 1200,
                "unit": "cm2",
                "interval": {"low": 1000, "high": 1400, "confidence": 0.95},
            },
            "evidence_refs": ["frame_001.jpg"],
            "confidence": 0.9,
        }
    ]
    instance["concealed_flags"] = [
        {
            "id": "flag_1",
            "surface": {"kind": "wall", "id": "a_north"},
            "rule_id": "water_below_visible_stain_v1",
            "status": "suspected",
            "damage_ids": ["damage_1"],
            "evidence_refs": ["frame_001.jpg"],
        }
    ]
    instance["scope"] = [
        {
            "id": "scope_1",
            "surface": {"kind": "wall", "id": "a_north"},
            "action": "inspect affected drywall",
            "quantity": {
                "value": 1200,
                "unit": "cm2",
                "interval": {"low": 1000, "high": 1400, "confidence": 0.95},
            },
            "quantity_source": "damage_extent",
            "damage_ids": ["damage_1"],
            "concealed_flag_ids": ["flag_1"],
        }
    ]

    jsonschema.validate(instance=instance, schema=schema)

    missing_rule = deepcopy(instance)
    del missing_rule["concealed_flags"][0]["rule_id"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=missing_rule, schema=schema)

    missing_quantity_interval = deepcopy(instance)
    del missing_quantity_interval["scope"][0]["quantity"]["interval"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=missing_quantity_interval, schema=schema)
