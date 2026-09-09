"""Stable names and holdout policy for the cold walk-in rehearsal."""

WALKIN_MANIFEST_NAME = "walkin.yaml"
WALKIN_REPORT_NAME = "walkin-status.json"
WALKIN_SUMMARY_NAME = "walkin-summary.md"
WALKIN_SCHEMA_VERSION = "1.0.0"
TWO_PHOTO_TIER = "photos_2still"

TIERS = ("photos", "video", "lidar")
DEFAULT_JOB_PATHS = {
    "photos": "walkin-photos",
    "video": "walkin-video",
    "lidar": "walkin-lidar",
}
DEFAULT_TRUTH_PATH = "ground_truth.json"
DEFAULT_ROOM_ID = "holdout-room"

# Benchmark rooms already used for scored eval. A walk-in that reuses them is
# not a cold room.
DEFAULT_FORBIDDEN_ROOM_IDS = (
    "drawing-room",
    "my-room",
    "pooja-room",
    "connector",
)
PLACEHOLDER_PREFIX = "replace-me"
