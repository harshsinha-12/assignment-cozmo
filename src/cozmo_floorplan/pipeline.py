"""Top-level orchestration boundary shared by the CLI and future callers."""

from pathlib import Path
from typing import Any

from cozmo_floorplan.agent import enrich_floorplan
from cozmo_floorplan.floorplan import build_failed_floorplan
from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job, load_job
from cozmo_floorplan.recon.lidar import reconstruct_lidar
from cozmo_floorplan.recon.photos import reconstruct_photos
from cozmo_floorplan.recon.video import reconstruct_video
from cozmo_floorplan.stitch import apply_drift_correction

FloorPlan = dict[str, Any]


def run_job(job_dir: str | Path, *, drift_correction: bool = True) -> FloorPlan:
    """Run one job and return the primary FloorPlan document."""

    document, _ablation = run_job_with_ablation(
        job_dir, drift_correction=drift_correction
    )
    return document


def run_job_with_ablation(
    job_dir: str | Path,
    *,
    drift_correction: bool = True,
) -> tuple[FloorPlan, FloorPlan | None]:
    """Return the primary document plus a poses-as-is ablation when correction ran."""

    job = load_job(job_dir)
    return run_loaded_job(job, drift_correction=drift_correction)


def run_loaded_job(
    job: Job, *, drift_correction: bool = True
) -> tuple[FloorPlan, FloorPlan | None]:
    """Dispatch a normalized job to its capture-tier adapter."""

    if job.tier == "lidar":
        try:
            raw = reconstruct_lidar(job)
        except ReconstructionError as exc:
            return _structured_failure(job, exc), None
        ablation_off = apply_drift_correction(raw, enabled=False)
        corrected = (
            apply_drift_correction(raw, enabled=True)
            if drift_correction
            else ablation_off
        )
        primary = enrich_floorplan(job, corrected)
        if drift_correction and corrected.get("stitch"):
            return primary, ablation_off
        return primary, None

    if job.tier == "video":
        try:
            raw = reconstruct_video(job)
        except ReconstructionError as exc:
            return _structured_failure(job, exc), None
        ablation_off = apply_drift_correction(raw, enabled=False)
        corrected = (
            apply_drift_correction(raw, enabled=True)
            if drift_correction
            else ablation_off
        )
        primary = enrich_floorplan(job, corrected)
        if drift_correction and corrected.get("stitch"):
            return primary, ablation_off
        return primary, None

    if job.tier == "photos":
        try:
            reconstruct_photos(job)
        except ReconstructionError as exc:
            return _structured_failure(job, exc), None

    failed = build_failed_floorplan(
        job_id=job.job_id,
        tier=job.tier,
        warning_code="unsupported_tier",
        message=f"The {job.tier!r} reconstruction adapter is not implemented yet.",
        input_refs=job.input_refs,
    )
    return failed, None


def _structured_failure(job: Job, exc: ReconstructionError) -> FloorPlan:
    return build_failed_floorplan(
        job_id=job.job_id,
        tier=job.tier,
        warning_code=exc.warning_code,
        message=str(exc),
        input_refs=job.input_refs,
    )
