import copy
from pathlib import Path
from xml.etree import ElementTree as ET

from cozmo_floorplan.floorplan import build_failed_floorplan
from cozmo_floorplan.pipeline import run_job
from cozmo_floorplan.render import render_floorplan_svg

ROOT = Path(__file__).resolve().parents[1]
ROOMPLAN_JOB = ROOT / "data" / "fixtures" / "roomplan_two_room"
SVG_NAMESPACE = {"svg": "http://www.w3.org/2000/svg"}


def _roomplan_document() -> dict:
    return run_job(ROOMPLAN_JOB)


def test_renderer_outputs_parseable_whole_property_svg():
    svg = render_floorplan_svg(_roomplan_document())
    root = ET.fromstring(svg)

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.find("svg:g[@id='property-plan']", SVG_NAMESPACE) is not None
    assert root.find("svg:g/svg:polygon[@id='room-room_a']", SVG_NAMESPACE) is not None
    assert root.find("svg:g/svg:polygon[@id='room-room_b']", SVG_NAMESPACE) is not None
    assert root.find("svg:g/svg:line[@id='opening-door_ab']", SVG_NAMESPACE) is not None
    assert "Room A" in svg
    assert "400 cm [399–401; 95%]" in svg
    assert "OK" in svg


def test_renderer_is_deterministic_and_escapes_labels():
    document = _roomplan_document()
    document = copy.deepcopy(document)
    document["rooms"][0]["label"] = "Kitchen <north> & hall"

    first = render_floorplan_svg(document)
    second = render_floorplan_svg(document)

    assert first == second
    assert "Kitchen &lt;north&gt; &amp; hall" in first
    assert "Kitchen <north> & hall" not in first
    ET.fromstring(first)


def test_failed_floorplan_renders_explanatory_placeholder():
    document = build_failed_floorplan(
        job_id="missing_capture",
        tier="photos",
        warning_code="incomplete_scan",
        message="No input images found.",
    )

    svg = render_floorplan_svg(document)

    assert "No geometry available" in svg
    assert "FAILED" in svg
    assert "1 warning" in svg
    ET.fromstring(svg)
