"""Audit final benchmark inputs without interpreting missing evidence as zero."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cozmo_floorplan.benchmark.config import TIERS
from cozmo_floorplan.benchmark.manifest import BenchmarkManifest


def audit_benchmark_inputs(manifest: BenchmarkManifest) -> list[dict[str, Any]]:
    """Return deterministic ready/pending checks for every required input class."""

    checks = [
        _check(
            "capture_root",
            manifest.root,
            manifest.root.is_dir(),
            "Create the capture root and copy the benchmark templates into it.",
        ),
        _check(
            "benchmark_manifest",
            manifest.manifest_path,
            manifest.manifest_present,
            "Copy data/templates/benchmark.yaml into the capture root and edit it.",
        ),
    ]
    checks.extend(
        _check(
            f"job_{tier}",
            manifest.jobs[tier],
            (manifest.jobs[tier] / "manifest.yaml").is_file(),
            f"Add the {tier} job directory with manifest.yaml.",
        )
        for tier in TIERS
    )
    checks.append(
        _check(
            "ground_truth",
            manifest.truth,
            manifest.truth.is_file(),
            "Add tape/laser ground_truth.json in FloorPlan schema format.",
        )
    )
    lidar_repeat = manifest.repeats.get("lidar")
    checks.append(
        _check(
            "repeat_lidar",
            lidar_repeat or manifest.root / "benchmark-lidar-repeat",
            lidar_repeat is not None and (lidar_repeat / "manifest.yaml").is_file(),
            "Add the required second LiDAR capture job.",
        )
    )
    checks.append(
        _check(
            "incumbent",
            manifest.incumbent,
            manifest.incumbent.is_file(),
            "Add normalized Polycam or magicplan FloorPlan evidence for two rooms.",
        )
    )
    damage_files = [
        path / "damage_observations.json"
        for path in manifest.jobs.values()
        if (path / "damage_observations.json").is_file()
    ]
    checks.append(
        _check(
            "damage_evidence",
            damage_files[0]
            if damage_files
            else manifest.root / "damage_observations.json",
            bool(damage_files),
            "Add staged damage observations with image evidence to at least one job.",
        )
    )
    return checks


def _check(
    identifier: str,
    path: Path,
    ready: bool,
    pending_detail: str,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "status": "ready" if ready else "pending",
        "path": path.as_posix(),
        "detail": "Input found." if ready else pending_detail,
    }
