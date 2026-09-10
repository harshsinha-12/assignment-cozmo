"""Run the three-tier walk-in rehearsal and emit an honest status bundle."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from cozmo_floorplan.benchmark.evidence import floorplan_evidence_ready
from cozmo_floorplan.config import ABLATION_OFF_FILENAME, MANIFEST_FILENAME
from cozmo_floorplan.errors import CozmoFloorPlanError
from cozmo_floorplan.eval.evaluator import evaluate_floorplans
from cozmo_floorplan.eval.io import load_floorplan, write_evaluation
from cozmo_floorplan.io.artifacts import write_run_artifacts
from cozmo_floorplan.io.output import write_json_atomic, write_text_atomic
from cozmo_floorplan.io.usd_mesh import USD_EXTENSIONS
from cozmo_floorplan.pipeline import run_job_with_ablation
from cozmo_floorplan.recon.lidar_config import ROOMPLAN_FILENAMES
from cozmo_floorplan.recon.photos_config import DEFAULT_PHOTO_INGEST, PHOTO_EXTENSIONS
from cozmo_floorplan.recon.video_config import VIDEO_EXTENSIONS
from cozmo_floorplan.schema import validate_floorplan
from cozmo_floorplan.walkin.config import (
    TIERS,
    TWO_PHOTO_TIER,
    WALKIN_REPORT_NAME,
    WALKIN_SCHEMA_VERSION,
    WALKIN_SUMMARY_NAME,
)
from cozmo_floorplan.walkin.manifest import WalkinManifest, is_placeholder, load_walkin_manifest
from cozmo_floorplan.walkin.report import render_walkin_summary
from cozmo_floorplan.walkin.rooms import collect_observed_room_ids, forbidden_collisions
from cozmo_floorplan.walkin.subset import materialize_two_photo_job


def run_walkin(
    capture_root: str | Path,
    output_dir: str | Path,
    *,
    tiers: tuple[str, ...] = TIERS,
) -> dict[str, Any]:
    """Time present tiers and refuse a recapture of the scored benchmark rooms."""

    if not tiers or any(tier not in TIERS for tier in tiers) or len(set(tiers)) != len(tiers):
        raise ValueError(f"walk-in tiers must be unique values from {', '.join(TIERS)}")
    manifest = load_walkin_manifest(capture_root)
    output = Path(output_dir).resolve()
    observed = collect_observed_room_ids(manifest, tiers)
    collisions = forbidden_collisions(manifest, tiers)
    inputs = audit_walkin_inputs(manifest, tiers=tiers)
    runs: list[dict[str, Any]] = []
    plans: dict[str, dict[str, Any]] = {}

    if collisions:
        report = _report(
            manifest,
            status="invalid_holdout",
            inputs=inputs,
            observed=observed,
            collisions=collisions,
            runs=[
                {
                    "tier": tier,
                    "status": "skipped",
                    "job": manifest.jobs[tier].as_posix(),
                    "detail": (
                        "Refused to score a walk-in that reuses benchmark rooms: "
                        + ", ".join(collisions)
                    ),
                }
                for tier in tiers
            ],
            evaluations=[
                _pending_evaluation(
                    tier,
                    "Holdout room collided with the scored benchmark; evaluation skipped.",
                )
                for tier in tiers
            ],
            selected_tiers=tiers,
        )
        _write_report(report, output)
        return report

    for tier in tiers:
        result, plan = _run_timed_job(tier, manifest.jobs[tier], output / tier)
        runs.append(result)
        if plan is not None:
            plans[tier] = plan

    if "photos" in tiers:
        subset_result, subset_plan = _run_two_photo_subset(
            manifest.jobs["photos"], output / "photos-2still"
        )
        if subset_result is not None:
            runs.append(subset_result)
            if subset_plan is not None:
                plans[TWO_PHOTO_TIER] = subset_plan

    truth, truth_error = _load_optional_floorplan(manifest.truth)
    evaluations = [
        _evaluate_tier(tier, plans.get(tier), truth, truth_error, output / tier)
        for tier in tiers
    ]
    pending_inputs = [item["id"] for item in inputs if item["status"] == "pending"]
    report = _report(
        manifest,
        status="pending_inputs" if pending_inputs else "complete",
        inputs=inputs,
        observed=observed,
        collisions=collisions,
        runs=runs,
        evaluations=evaluations,
        pending_inputs=pending_inputs,
        selected_tiers=tiers,
    )
    _write_report(report, output)
    return report


def audit_walkin_inputs(
    manifest: WalkinManifest,
    *,
    tiers: tuple[str, ...] = TIERS,
) -> list[dict[str, Any]]:
    """Return ready/pending checks for the holdout capture, not the benchmark."""

    room_ready = bool(manifest.room_id) and not is_placeholder(manifest.room_id)
    checks = [
        _check(
            "capture_root",
            manifest.root,
            manifest.root.is_dir(),
            "Copy data/templates/walkin into a gitignored holdout folder.",
        ),
        _check(
            "walkin_manifest",
            manifest.manifest_path,
            manifest.manifest_present,
            "Copy data/templates/walkin/walkin.yaml into the capture root and edit it.",
        ),
        _check(
            "declared_room",
            manifest.manifest_path,
            room_ready,
            "Set room_id to the new room. Do not reuse drawing-room, my-room, "
            "pooja-room, or connector.",
        ),
    ]
    checks.extend(
        _check(
            f"job_{tier}",
            manifest.jobs[tier],
            job_has_capture_media(manifest.jobs[tier], tier),
            f"Add original {tier} capture files under {tier}/. Empty templates are not a walk-in.",
        )
        for tier in tiers
    )
    truth_ready, truth_problem = floorplan_evidence_ready(manifest.truth, minimum_rooms=1)
    checks.append(
        _check(
            "ground_truth",
            manifest.truth,
            truth_ready,
            "Add tape/laser ground_truth.json for the holdout room "
            f"({truth_problem}).",
        )
    )
    return checks


def _run_two_photo_subset(
    photo_job: Path, output_dir: Path
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    subset_job = output_dir / "job"
    materialized = materialize_two_photo_job(photo_job, subset_job)
    if materialized is None:
        return None, None
    return _run_timed_job(TWO_PHOTO_TIER, materialized, output_dir)


def job_has_capture_media(job_path: Path, tier: str) -> bool:
    """Return True when the job has original capture files, not only a template."""

    if not (job_path / MANIFEST_FILENAME).is_file():
        return False
    if tier == "photos":
        photos_dir = job_path / "photos"
        if not photos_dir.is_dir():
            return False
        for room_dir in photos_dir.iterdir():
            if not room_dir.is_dir() or room_dir.name.startswith("."):
                continue
            images = [
                path
                for path in room_dir.iterdir()
                if path.is_file() and path.suffix.lower() in PHOTO_EXTENSIONS
            ]
            if len(images) >= DEFAULT_PHOTO_INGEST.min_photos_per_room:
                return True
        return False
    if tier == "video":
        video_dir = job_path / "video"
        if not video_dir.is_dir():
            return False
        return any(
            path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
            for path in video_dir.iterdir()
        )
    if tier == "lidar":
        lidar_dir = job_path / "lidar"
        if not lidar_dir.is_dir():
            return False
        names = {name.lower() for name in ROOMPLAN_FILENAMES}
        return any(
            path.is_file()
            and path.name != ".gitkeep"
            and (
                path.suffix.lower() == ".r3d"
                or path.suffix.lower() in USD_EXTENSIONS
                or path.name.lower() in names
            )
            for path in lidar_dir.iterdir()
        )
    return False


def _run_timed_job(
    tier: str,
    job_path: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    media_tier = "photos" if tier == TWO_PHOTO_TIER else tier
    if not job_has_capture_media(job_path, media_tier):
        detail = (
            "Job manifest is not available."
            if not (job_path / MANIFEST_FILENAME).is_file()
            else "Capture files are not available yet."
        )
        return (
            {
                "tier": tier,
                "status": "pending",
                "job": job_path.as_posix(),
                "elapsed_s": None,
                "detail": detail,
            },
            None,
        )
    started = time.perf_counter()
    try:
        plan, ablation = run_job_with_ablation(job_path)
        artifacts = write_run_artifacts(plan, output_dir)
        if ablation is not None:
            validate_floorplan(ablation)
            write_json_atomic(ablation, output_dir / ABLATION_OFF_FILENAME)
    except (CozmoFloorPlanError, OSError, ValueError) as exc:
        return (
            {
                "tier": tier,
                "status": "error",
                "job": job_path.as_posix(),
                "elapsed_s": round(time.perf_counter() - started, 3),
                "detail": str(exc),
            },
            None,
        )
    elapsed = round(time.perf_counter() - started, 3)
    return (
        {
            "tier": tier,
            "status": "complete",
            "job": job_path.as_posix(),
            "pipeline_status": plan["status"],
            "geometry_ready": bool(plan.get("rooms")) and bool(plan.get("walls")),
            "warning_codes": sorted(
                {
                    str(warning.get("code", "other"))
                    for warning in plan.get("warnings", [])
                    if isinstance(warning, dict)
                }
            ),
            "next_action": _next_action(media_tier, plan),
            "elapsed_s": elapsed,
            "output": artifacts.floorplan_json.as_posix(),
            "detail": "Public run path timed; inspect pipeline_status and evaluation gates.",
        },
        plan,
    )


def _evaluate_tier(
    tier: str,
    prediction: dict[str, Any] | None,
    truth: dict[str, Any] | None,
    truth_error: str | None,
    eval_dir: Path,
) -> dict[str, Any]:
    if prediction is None:
        return _pending_evaluation(tier, "Tier prediction is not available.")
    if truth is None:
        return _pending_evaluation(tier, truth_error or "Ground truth is not available.")
    report = evaluate_floorplans(prediction, truth)
    eval_path = write_evaluation(report.to_dict(), eval_dir)
    gate_counts: dict[str, int] = {}
    for gate in report.gates:
        gate_counts[gate.status] = gate_counts.get(gate.status, 0) + 1
    return {
        "tier": tier,
        "status": "complete",
        "passed": report.passed,
        "output": eval_path.as_posix(),
        "gate_counts": gate_counts,
        "detail": "Evaluation completed against holdout tape truth.",
    }


def _load_optional_floorplan(
    path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"Missing {path.as_posix()}"
    try:
        return load_floorplan(path), None
    except CozmoFloorPlanError as exc:
        return None, str(exc)


def _report(
    manifest: WalkinManifest,
    *,
    status: str,
    inputs: list[dict[str, Any]],
    observed: tuple[str, ...],
    collisions: tuple[str, ...],
    runs: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    pending_inputs: list[str] | None = None,
    selected_tiers: tuple[str, ...] = TIERS,
) -> dict[str, Any]:
    return {
        "version": WALKIN_SCHEMA_VERSION,
        "walkin_id": manifest.walkin_id,
        "room_id": manifest.room_id,
        "status": status,
        "selected_tiers": list(selected_tiers),
        "capture_root": manifest.root.as_posix(),
        "observed_rooms": list(observed),
        "forbidden_collisions": list(collisions),
        "pending_inputs": pending_inputs or [],
        "inputs": inputs,
        "runs": runs,
        "evaluations": evaluations,
    }


def _write_report(report: dict[str, Any], output: Path) -> None:
    write_json_atomic(report, output / WALKIN_REPORT_NAME)
    write_text_atomic(render_walkin_summary(report), output / WALKIN_SUMMARY_NAME)


def _pending_evaluation(tier: str, detail: str) -> dict[str, Any]:
    return {
        "tier": tier,
        "status": "pending",
        "passed": None,
        "detail": detail,
    }


def _next_action(tier: str, plan: dict[str, Any]) -> str:
    if plan.get("rooms") and plan.get("walls"):
        return "Geometry emitted; evaluate against laser/tape truth."
    if tier == "photos":
        return "Recapture eight sharp stills with 60%+ overlap and shared doorway views."
    if tier == "video":
        return "Rewalk slowly; pause at corners and keep floor, ceiling, and both wall pairs visible."
    if tier == "lidar":
        return "Repeat one slow perimeter scan with every wall, opening, floor band, and ceiling covered."
    return "Inspect the structured warning before recapture."


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
