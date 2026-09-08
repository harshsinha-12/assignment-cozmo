"""Stable package configuration shared across CLI and pipeline modules."""

from enum import IntEnum

FLOORPLAN_SCHEMA_VERSION = "0.2.0"
EVAL_REPORT_VERSION = "0.1.0"
MANIFEST_FILENAME = "manifest.yaml"
OUTPUT_FILENAME = "floorplan.json"
SVG_OUTPUT_FILENAME = "floorplan.svg"
EVAL_OUTPUT_FILENAME = "eval.json"
PIPELINE_NAME = "cozmo-floorplan/t13-cli-stub"
SCHEMA_ENV_VAR = "COZMO_FLOORPLAN_SCHEMA"

SUPPORTED_TIERS = frozenset({"photos", "video", "lidar", "synthetic", "mixed"})
TIER_INPUT_DIRECTORIES = {
    "photos": "photos",
    "video": "video",
    "lidar": "lidar",
}


class ExitCode(IntEnum):
    """Process exit codes exposed by the local command."""

    OK = 0
    INTERNAL_ERROR = 1
    STRUCTURED_FAILURE = 2
    EVALUATION_FAILED = 3
