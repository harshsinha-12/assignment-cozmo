"""Top-level orchestration boundary shared by the CLI and future callers."""

from pathlib import Path
from typing import Any

from cozmo_floorplan.floorplan import build_failed_floorplan
from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job, load_job
from cozmo_floorplan.recon.lidar import reconstruct_lidar


def run_job(job_dir: str | Path) -> dict[str, Any]:
    """Run one job; T13 intentionally returns a structured adapter failure."""

    job = load_job(job_dir)
    return run_loaded_job(job)


def run_loaded_job(job: Job) -> dict[str, Any]:
    """Dispatch a normalized job to its capture-tier adapter."""

    if job.tier == "lidar":
        try:
            return reconstruct_lidar(job)
        except ReconstructionError as exc:
            return build_failed_floorplan(
                job_id=job.job_id,
                tier=job.tier,
                warning_code=exc.warning_code,
                message=str(exc),
                input_refs=job.input_refs,
            )

    return build_failed_floorplan(
        job_id=job.job_id,
        tier=job.tier,
        warning_code="unsupported_tier",
        message=f"The {job.tier!r} reconstruction adapter is not implemented yet.",
        input_refs=job.input_refs,
    )
