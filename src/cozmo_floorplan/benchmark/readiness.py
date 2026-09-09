"""Audit final benchmark inputs without interpreting missing evidence as zero."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cozmo_floorplan.benchmark.config import TIERS
from cozmo_floorplan.benchmark.evidence import (
    find_damage_evidence,
    floorplan_evidence_ready,
)
from cozmo_floorplan.benchmark.manifest import BenchmarkManifest
from cozmo_floorplan.benchmark.repeat import find_repeat_evidence


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
    truth_ready, truth_problem = floorplan_evidence_ready(manifest.truth)
    checks.append(
        _check(
            "ground_truth",
            manifest.truth,
            truth_ready,
            "Add valid tape/laser ground_truth.json in FloorPlan schema format "
            f"({truth_problem}).",
        )
    )
    repeat, repeat_problem = find_repeat_evidence(manifest)
    checks.append(
        _check(
            "repeat_capture",
            repeat.path if repeat is not None else manifest.root,
            repeat is not None,
            "Add one same-room repeat at any tier with repeat_of_job_id and "
            f"repeat_room_ids ({repeat_problem}).",
        )
    )
    incumbent_ready, incumbent_problem = floorplan_evidence_ready(
        manifest.incumbent, minimum_rooms=2
    )
    checks.append(
        _check(
            "incumbent",
            manifest.incumbent,
            incumbent_ready,
            "Add normalized Polycam or magicplan FloorPlan evidence for two rooms "
            f"({incumbent_problem}).",
        )
    )
    damage_path, damage_problem = find_damage_evidence(list(manifest.jobs.values()))
    checks.append(
        _check(
            "damage_evidence",
            damage_path or manifest.root / "damage_observations.json",
            damage_path is not None,
            "Add two-class staged damage observations with local image evidence "
            f"({damage_problem}).",
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
