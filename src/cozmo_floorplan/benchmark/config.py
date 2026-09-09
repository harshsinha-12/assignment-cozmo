"""Stable names and default paths for the final benchmark bundle."""

BENCHMARK_MANIFEST_NAME = "benchmark.yaml"
BENCHMARK_REPORT_NAME = "benchmark-status.json"
BENCHMARK_SUMMARY_NAME = "benchmark-summary.md"
BENCHMARK_SCHEMA_VERSION = "1.0.0"

TIERS = ("photos", "video", "lidar")
DEFAULT_JOB_PATHS = {
    "photos": "benchmark-photos",
    "video": "benchmark-video",
    "lidar": "benchmark-lidar",
}
DEFAULT_TRUTH_PATH = "ground_truth.json"
DEFAULT_LIDAR_REPEAT_PATH = "benchmark-lidar-repeat"
DEFAULT_INCUMBENT_PATH = "incumbent/floorplan.json"
