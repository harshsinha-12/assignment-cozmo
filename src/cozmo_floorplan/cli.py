"""Argument parsing and process-level error handling for the local CLI."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from cozmo_floorplan.config import ExitCode, OUTPUT_FILENAME
from cozmo_floorplan.errors import CozmoFloorPlanError, JobLoadError
from cozmo_floorplan.floorplan import build_failed_floorplan
from cozmo_floorplan.io.output import write_floorplan, write_json_atomic
from cozmo_floorplan.pipeline import run_job


def build_parser() -> argparse.ArgumentParser:
    """Build the public command parser without running it."""

    parser = argparse.ArgumentParser(
        prog="python -m cozmo_floorplan",
        description="Convert one local phone-capture job into FloorPlan artifacts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Process one job directory.")
    run_parser.add_argument("job", type=Path, help="Directory containing manifest.yaml and capture files.")
    run_parser.add_argument("--out", type=Path, required=True, help="Directory for floorplan.json and later artifacts.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the CLI and return a stable process exit code."""

    args = build_parser().parse_args(argv)
    if args.command == "run":
        return _run_command(args.job, args.out)
    return int(ExitCode.INTERNAL_ERROR)


def _run_command(job_dir: Path, out_dir: Path) -> int:
    try:
        document = run_job(job_dir)
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
        output_path = write_floorplan(document, out_dir)
    except CozmoFloorPlanError as exc:
        return _write_last_resort_failure(job_dir, out_dir, str(exc))
    except Exception as exc:
        return _write_last_resort_failure(job_dir, out_dir, f"Unexpected output error: {exc}")

    _print_result(document["status"], output_path)
    return int(ExitCode.OK if document["status"] == "ok" else ExitCode.STRUCTURED_FAILURE)


def _write_last_resort_failure(job_dir: Path, out_dir: Path, message: str) -> int:
    document = build_failed_floorplan(
        job_id=job_dir.name or "unknown_job",
        tier="mixed",
        warning_code="other",
        message=message,
    )
    try:
        output_path = write_json_atomic(document, out_dir / OUTPUT_FILENAME)
    except OSError as write_error:
        print(f"failed: could not write structured output: {write_error}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)

    _print_result(document["status"], output_path)
    return int(ExitCode.INTERNAL_ERROR)


def _print_result(status: str, output_path: Path) -> None:
    print(f"status={status} output={output_path}")
