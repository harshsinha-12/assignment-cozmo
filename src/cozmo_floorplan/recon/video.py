"""Video-tier adapter: ingest walkthroughs honestly until metric VO exists."""

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.video import find_pose_sidecar, find_video_files, sample_video_frames
from cozmo_floorplan.recon.video_config import DEFAULT_VIDEO_INGEST, VideoIngestConfig


def reconstruct_video(
    job: Job,
    *,
    config: VideoIngestConfig = DEFAULT_VIDEO_INGEST,
) -> dict:
    """Sample a walkthrough. Do not emit centimetres without a metric camera prior."""

    video_dir = job.root / "video"
    media = find_video_files(video_dir)
    if not media:
        raise ReconstructionError(
            "No MP4/MOV walkthrough found in video/. Add one file, then rerun.",
            warning_code="incomplete_scan",
        )

    source = media[0]
    try:
        frames = sample_video_frames(source, config=config)
    except OSError as exc:
        raise ReconstructionError(str(exc), warning_code="incomplete_scan") from exc

    if len(frames) < config.min_frames:
        raise ReconstructionError(
            f"{source.name} yielded {len(frames)} sampled frames; need at least {config.min_frames}.",
            warning_code="incomplete_scan",
        )

    sidecar = find_pose_sidecar(video_dir)
    relative = source.relative_to(job.root).as_posix()
    extra = f" Pose sidecar: {sidecar.relative_to(job.root).as_posix()}." if sidecar else ""
    raise ReconstructionError(
        (
            f"Sampled {len(frames)} frames from {relative} at {config.sample_fps:g} Hz."
            f"{extra} Metric video reconstruction is not implemented yet; "
            "centimetres will not be guessed from an uncalibrated walkthrough."
        ),
        warning_code="unsupported_tier",
    )
