"""Run every available tier and emit an honest final benchmark status bundle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cozmo_floorplan.benchmark.config import (
    BENCHMARK_REPORT_NAME,
    BENCHMARK_SCHEMA_VERSION,
    BENCHMARK_SUMMARY_NAME,
    TIERS,
)
from cozmo_floorplan.benchmark.manifest import load_benchmark_manifest
from cozmo_floorplan.benchmark.readiness import audit_benchmark_inputs
from cozmo_floorplan.benchmark.report import render_benchmark_summary
from cozmo_floorplan.config import ABLATION_OFF_FILENAME
from cozmo_floorplan.errors import CozmoFloorPlanError
from cozmo_floorplan.eval.evaluator import evaluate_floorplans
from cozmo_floorplan.eval.io import load_floorplan, write_evaluation
from cozmo_floorplan.io.artifacts import write_run_artifacts
from cozmo_floorplan.io.output import write_json_atomic, write_text_atomic
from cozmo_floorplan.pipeline import run_job_with_ablation
from cozmo_floorplan.schema import validate_floorplan


def run_benchmark(capture_root: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Run present inputs and label absent evidence pending in one report."""

    manifest = load_benchmark_manifest(capture_root)
    output = Path(output_dir).resolve()
    inputs = audit_benchmark_inputs(manifest)
    runs: list[dict[str, Any]] = []
    plans: dict[str, dict[str, Any]] = {}
    repeats: dict[str, dict[str, Any]] = {}
    ablations: dict[str, dict[str, Any]] = {}

    for tier in TIERS:
        result, plan, ablation = _run_available_job(
            tier, manifest.jobs[tier], output / tier
        )
        runs.append(result)
        if plan is not None:
            plans[tier] = plan
        if ablation is not None:
            ablations[tier] = ablation

    for tier, path in sorted(manifest.repeats.items()):
        result, plan, _ablation = _run_available_job(
            f"repeat_{tier}", path, output / f"repeat-{tier}"
        )
        runs.append(result)
        if plan is not None:
            repeats[tier] = plan

    truth, truth_error = _load_optional_floorplan(manifest.truth)
    incumbent, incumbent_error = _load_optional_floorplan(manifest.incumbent)
    evaluations: list[dict[str, Any]] = []
    for tier in TIERS:
        prediction = plans.get(tier)
        if prediction is None:
            evaluations.append(
                _pending_evaluation(tier, "Tier prediction is not available.")
            )
            continue
        if truth is None:
            detail = truth_error or "Ground truth is not available."
            evaluations.append(_pending_evaluation(tier, detail))
            continue
        report = evaluate_floorplans(
            prediction,
            truth,
            repeat_prediction=repeats.get(tier),
            ablation_off_prediction=ablations.get(tier),
            incumbent_prediction=incumbent if tier == "lidar" else None,
        )
        eval_dir = output / tier
        eval_path = write_evaluation(report.to_dict(), eval_dir)
        gate_counts: dict[str, int] = {}
        for gate in report.gates:
            gate_counts[gate.status] = gate_counts.get(gate.status, 0) + 1
        detail = "Evaluation completed."
        if tier == "lidar" and incumbent is None:
            detail += f" Incumbent pending: {incumbent_error}"
        evaluations.append(
            {
                "tier": tier,
                "status": "complete",
                "passed": report.passed,
                "output": eval_path.as_posix(),
                "gate_counts": gate_counts,
                "detail": detail,
            }
        )

    pending_inputs = [item["id"] for item in inputs if item["status"] == "pending"]
    report_document: dict[str, Any] = {
        "version": BENCHMARK_SCHEMA_VERSION,
        "benchmark_id": manifest.benchmark_id,
        "status": "pending_inputs" if pending_inputs else "complete",
        "capture_root": manifest.root.as_posix(),
        "pending_inputs": pending_inputs,
        "inputs": inputs,
        "runs": runs,
        "evaluations": evaluations,
    }
    write_json_atomic(report_document, output / BENCHMARK_REPORT_NAME)
    write_text_atomic(
        render_benchmark_summary(report_document), output / BENCHMARK_SUMMARY_NAME
    )
    return report_document


def _run_available_job(
    tier: str,
    job_path: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
    if not (job_path / "manifest.yaml").is_file():
        return (
            {
                "tier": tier,
                "status": "pending",
                "job": job_path.as_posix(),
                "detail": "Job manifest is not available.",
            },
            None,
            None,
        )
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
                "detail": str(exc),
            },
            None,
            None,
        )
    return (
        {
            "tier": tier,
            "status": "complete",
            "job": job_path.as_posix(),
            "pipeline_status": plan["status"],
            "output": artifacts.floorplan_json.as_posix(),
            "detail": "Artifacts generated; inspect pipeline_status and evaluation gates.",
        },
        plan,
        ablation,
    )


def _load_optional_floorplan(
    path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"Missing {path.as_posix()}"
    try:
        return load_floorplan(path), None
    except CozmoFloorPlanError as exc:
        return None, str(exc)


def _pending_evaluation(tier: str, detail: str) -> dict[str, Any]:
    return {
        "tier": tier,
        "status": "pending",
        "passed": None,
        "detail": detail,
    }
