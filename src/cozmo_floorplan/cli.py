"""Argument parsing and process-level error handling for the local CLI."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from cozmo_floorplan.config import ABLATION_OFF_FILENAME, ExitCode
from cozmo_floorplan.benchmark import run_benchmark
from cozmo_floorplan.walkin import run_walkin
from cozmo_floorplan.errors import CozmoFloorPlanError, JobLoadError
from cozmo_floorplan.eval.evaluator import evaluate_floorplans
from cozmo_floorplan.eval.io import load_floorplan, write_evaluation
from cozmo_floorplan.floorplan import build_failed_floorplan
from cozmo_floorplan.io.artifacts import ArtifactPaths, write_run_artifacts
from cozmo_floorplan.io.output import write_json_atomic
from cozmo_floorplan.pipeline import run_job_with_ablation
from cozmo_floorplan.schema import validate_floorplan


def build_parser() -> argparse.ArgumentParser:
    """Build the public command parser without running it."""

    parser = argparse.ArgumentParser(
        prog="python -m cozmo_floorplan",
        description="Convert one local phone-capture job into FloorPlan artifacts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser(
        "run", help="Process one job directory or Cozmo Capture ZIP."
    )
    run_parser.add_argument(
        "job",
        type=Path,
        help="Directory containing manifest.yaml, or a Cozmo Capture .zip export.",
    )
    run_parser.add_argument("--out", type=Path, required=True, help="Directory for floorplan.json and later artifacts.")
    run_parser.add_argument(
        "--no-drift-correction",
        action="store_true",
        help="Emit poses-as-is geometry (the regenerable drift ablation).",
    )
    eval_parser = subparsers.add_parser("eval", help="Evaluate a FloorPlan against ground truth.")
    eval_parser.add_argument("--pred", type=Path, required=True, help="Predicted floorplan.json.")
    eval_parser.add_argument("--truth", type=Path, required=True, help="Ground-truth FloorPlan JSON.")
    eval_parser.add_argument("--out", type=Path, required=True, help="Directory for eval.json.")
    eval_parser.add_argument(
        "--repeat",
        type=Path,
        help="Optional second prediction of the same room for repeatability.",
    )
    eval_parser.add_argument(
        "--ablation-off",
        type=Path,
        help="Optional correction-disabled prediction for the drift ablation.",
    )
    eval_parser.add_argument(
        "--incumbent",
        type=Path,
        help="Optional normalized Polycam or magicplan FloorPlan for head-to-head scoring.",
    )
    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Run all available capture tiers and report missing evidence.",
    )
    benchmark_parser.add_argument(
        "capture_root",
        type=Path,
        help="Directory containing benchmark.yaml and tier job directories.",
    )
    benchmark_parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Directory for tier artifacts and benchmark status files.",
    )
    walkin_parser = subparsers.add_parser(
        "walkin",
        help="Time a cold holdout room on all three capture tiers.",
    )
    walkin_parser.add_argument(
        "capture_root",
        type=Path,
        help="Directory containing walkin.yaml and per-tier holdout jobs.",
    )
    walkin_parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Directory for timed tier artifacts and walk-in status files.",
    )
    walkin_parser.add_argument(
        "--tier",
        choices=("all", "photos", "video", "lidar"),
        default="all",
        help="Run all rehearsal tiers or only the evaluator-selected tier.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the CLI and return a stable process exit code."""

    args = build_parser().parse_args(argv)
    if args.command == "run":
        return _run_command(args.job, args.out, drift_correction=not args.no_drift_correction)
    if args.command == "eval":
        return _eval_command(
            args.pred,
            args.truth,
            args.out,
            args.repeat,
            args.ablation_off,
            args.incumbent,
        )
    if args.command == "benchmark":
        return _benchmark_command(args.capture_root, args.out)
    if args.command == "walkin":
        return _walkin_command(args.capture_root, args.out, tier=args.tier)
    return int(ExitCode.INTERNAL_ERROR)


def _eval_command(
    prediction_path: Path,
    truth_path: Path,
    out_dir: Path,
    repeat_path: Path | None,
    ablation_off_path: Path | None,
    incumbent_path: Path | None,
) -> int:
    try:
        prediction = load_floorplan(prediction_path)
        truth = load_floorplan(truth_path)
        repeat = load_floorplan(repeat_path) if repeat_path else None
        ablation_off = load_floorplan(ablation_off_path) if ablation_off_path else None
        incumbent = load_floorplan(incumbent_path) if incumbent_path else None
        report = evaluate_floorplans(
            prediction,
            truth,
            repeat_prediction=repeat,
            ablation_off_prediction=ablation_off,
            incumbent_prediction=incumbent,
        )
        output_path = write_evaluation(report.to_dict(), out_dir)
    except CozmoFloorPlanError as exc:
        print(f"evaluation_error={exc}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)
    except Exception as exc:  # Defensive command boundary.
        print(f"evaluation_error=Unexpected evaluation error: {exc}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)

    print(f"passed={str(report.passed).lower()} output={output_path}")
    return int(ExitCode.OK if report.passed else ExitCode.EVALUATION_FAILED)


def _run_command(job_dir: Path, out_dir: Path, *, drift_correction: bool) -> int:
    ablation_off = None
    try:
        document, ablation_off = run_job_with_ablation(job_dir, drift_correction=drift_correction)
    except JobLoadError as exc:
        document = build_failed_floorplan(
            job_id=job_dir.name or "unknown_job",
            tier="mixed",
            warning_code=exc.warning_code,
            message=str(exc),
        )
    except CozmoFloorPlanError as exc:
        return _write_last_resort_failure(job_dir, out_dir, str(exc))
    except Exception as exc:  # Defensive CLI boundary: never return only a traceback.
        return _write_last_resort_failure(job_dir, out_dir, f"Unexpected pipeline error: {exc}")

    try:
        artifacts = write_run_artifacts(document, out_dir)
        if ablation_off is not None:
            validate_floorplan(ablation_off)
            write_json_atomic(ablation_off, Path(out_dir) / ABLATION_OFF_FILENAME)
    except CozmoFloorPlanError as exc:
        return _write_last_resort_failure(job_dir, out_dir, str(exc))
    except Exception as exc:
        return _write_last_resort_failure(job_dir, out_dir, f"Unexpected output error: {exc}")

    _print_result(document["status"], artifacts)
    return int(ExitCode.OK if document["status"] == "ok" else ExitCode.STRUCTURED_FAILURE)


def _benchmark_command(capture_root: Path, out_dir: Path) -> int:
    try:
        report = run_benchmark(capture_root, out_dir)
    except (CozmoFloorPlanError, OSError, ValueError) as exc:
        print(f"benchmark_error={exc}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)
    print(
        f"status={report['status']} pending={len(report['pending_inputs'])} "
        f"output={(out_dir.resolve() / 'benchmark-status.json')}"
    )
    return int(ExitCode.OK)


def _walkin_command(capture_root: Path, out_dir: Path, *, tier: str = "all") -> int:
    try:
        tiers = ("photos", "video", "lidar") if tier == "all" else (tier,)
        report = run_walkin(capture_root, out_dir, tiers=tiers)
    except (CozmoFloorPlanError, OSError, ValueError) as exc:
        print(f"walkin_error={exc}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)
    output = out_dir.resolve() / "walkin-status.json"
    print(
        f"status={report['status']} pending={len(report['pending_inputs'])} "
        f"output={output}"
    )
    if report["status"] == "invalid_holdout":
        return int(ExitCode.STRUCTURED_FAILURE)
    return int(ExitCode.OK)


def _write_last_resort_failure(job_dir: Path, out_dir: Path, message: str) -> int:
    document = build_failed_floorplan(
        job_id=job_dir.name or "unknown_job",
        tier="mixed",
        warning_code="other",
        message=message,
    )
    try:
        artifacts = write_run_artifacts(document, out_dir)
    except Exception as write_error:  # Last defensive boundary; do not emit only a traceback.
        print(f"failed: could not write structured output: {write_error}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)

    _print_result(document["status"], artifacts)
    return int(ExitCode.INTERNAL_ERROR)


def _print_result(status: str, artifacts: ArtifactPaths) -> None:
    print(
        f"status={status} json={artifacts.floorplan_json} svg={artifacts.floorplan_svg}"
    )
