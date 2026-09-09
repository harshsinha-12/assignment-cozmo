"""Stable inputs and assertions for the public synthetic reproduction."""

FIXTURE_RELATIVE = "data/fixtures/roomplan_two_room"
TRUTH_RELATIVE = "data/fixtures/synthetic_two_room/ground_truth.json"
FIX_LOOP_RELATIVE = "data/fix-loop"

REQUIRED_ARTIFACTS = (
    "floorplan.json",
    "floorplan.svg",
    "floorplan.ablation-off.json",
    "eval.json",
)

EXPECTED_PASS_GATES = (
    "pipeline_yield",
    "opening_widths",
    "ceiling_height",
    "drift_accountability",
    "interval_calibration",
)

EXPECTED_MISSING_GATES = (
    "repeatability",
    "head_to_head",
)
