"""Stable names required by the fix-loop reproduction bundle."""

MANIFEST_FILENAME = "manifest.json"
REQUIRED_BEFORE_ARTIFACTS = frozenset(
    {
        "before/eval.json",
        "before/floorplan.ablation-off.json",
        "before/floorplan.json",
        "before/floorplan.svg",
    }
)
