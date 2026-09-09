"""Video-tier adapter: ingest walkthroughs honestly until metric VO exists."""

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.video import find_pose_sidecar, find_video_files, sample_video
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_INGEST,
    POSE_SIDECAR_NAMES,
    VideoIngestConfig,
)


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

    summaries: list[str] = []
    for source in media:
        try:
            sampled = sample_video(source, config=config)
        except OSError as exc:
            raise ReconstructionError(str(exc), warning_code="incomplete_scan") from exc
        if len(sampled.frames) < config.min_frames:
            raise ReconstructionError(
                f"{source.name} yielded {len(sampled.frames)} sampled frames; "
                f"need at least {config.min_frames}.",
                warning_code="incomplete_scan",
            )
        sidecar = find_pose_sidecar(
            video_dir,
            video_stem=source.stem,
            allow_global=len(media) == 1,
        )
        relative = source.relative_to(job.root).as_posix()
        sidecar_note = (
            f", poses={sidecar.relative_to(job.root).as_posix()}" if sidecar else ""
        )
        metadata = sampled.metadata
        summaries.append(
            f"{sampled.identifier}: {len(sampled.frames)} samples from {relative}, "
            f"{metadata.display_size_px[0]}x{metadata.display_size_px[1]} display, "
            f"rotation={metadata.rotation_degrees_clockwise}deg clockwise, "
            f"duration={metadata.duration_s:.2f}s{sidecar_note}"
        )

    global_sidecar = find_pose_sidecar(video_dir, allow_global=True)
    ambiguous_sidecar = (
        len(media) > 1
        and global_sidecar is not None
        and global_sidecar.name in POSE_SIDECAR_NAMES
    )
    sidecar_warning = (
        " A global pose sidecar is ambiguous for multiple videos; use "
        "<video-stem>.poses.json."
        if ambiguous_sidecar
        else ""
    )
    raise ReconstructionError(
        (
            f"Sampled {len(media)} room walkthrough(s) at {config.sample_fps:g} Hz "
            f"({'; '.join(summaries)}).{sidecar_warning} "
            "Metric video reconstruction is not implemented yet; "
            "centimetres will not be guessed from an uncalibrated walkthrough."
        ),
        warning_code="unsupported_tier",
    )
