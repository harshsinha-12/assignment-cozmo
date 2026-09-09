"""Video-tier adapter: ingest walkthroughs honestly until metric VO exists."""

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.video import find_pose_sidecar, find_video_files, sample_video
from cozmo_floorplan.io.video_poses import load_metric_pose_sidecar
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_INGEST,
    DEFAULT_VIDEO_TRACKING,
    POSE_SIDECAR_NAMES,
    VideoIngestConfig,
    VideoTrackingConfig,
)
from cozmo_floorplan.recon.video_tracks import analyze_video_tracks
from cozmo_floorplan.recon.video_pose_alignment import (
    MetricSegmentAlignment,
    align_trajectory_to_metric_poses,
)
from cozmo_floorplan.recon.video_trajectory import recover_scale_free_trajectory


def reconstruct_video(
    job: Job,
    *,
    config: VideoIngestConfig = DEFAULT_VIDEO_INGEST,
    tracking_config: VideoTrackingConfig = DEFAULT_VIDEO_TRACKING,
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
    rejected: list[str] = []
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
        metric_sidecar = None
        if sidecar is not None:
            try:
                metric_sidecar = load_metric_pose_sidecar(sidecar)
            except ValueError as exc:
                raise ReconstructionError(
                    str(exc),
                    warning_code="incomplete_scan",
                ) from exc
        relative = source.relative_to(job.root).as_posix()
        sidecar_note = (
            f", poses={sidecar.relative_to(job.root).as_posix()}"
            f", metric_poses={len(metric_sidecar.poses)}"
            if sidecar and metric_sidecar
            else ""
        )
        metadata = sampled.metadata
        tracks = analyze_video_tracks(sampled, config=tracking_config)
        if not tracks.accepted_for_relative_vo:
            rejected.append(sampled.identifier)
            trajectory_note = "trajectory=not-attempted"
            alignment_note = "metric_alignment=not-attempted"
        else:
            trajectory = recover_scale_free_trajectory(
                sampled,
                tracking_config=tracking_config,
            )
            if not trajectory.segments:
                rejected.append(sampled.identifier)
            trajectory_note = (
                f"trajectory={trajectory.accepted_edges}/"
                f"{trajectory.attempted_edges} edges, "
                f"segments={len(trajectory.segments)}, "
                f"breaks={trajectory.segment_breaks}, "
                f"restarts={trajectory.segment_restarts}, "
                f"focal_prior={trajectory.assumed_focal_length_px:.1f}px"
            )
            if metric_sidecar is None:
                alignment_note = "metric_alignment=not-available"
            else:
                alignment = align_trajectory_to_metric_poses(
                    sampled,
                    trajectory,
                    metric_sidecar,
                )
                rejected_alignments = _format_alignment_rejections(alignment.segments)
                alignment_note = (
                    f"metric_alignment={alignment.aligned_segment_count}/"
                    f"{len(alignment.segments)} segments, "
                    f"alignment_rejects={rejected_alignments}"
                )
        summaries.append(
            f"{sampled.identifier}: {len(sampled.frames)} samples from {relative}, "
            f"{metadata.display_size_px[0]}x{metadata.display_size_px[1]} display, "
            f"rotation={metadata.rotation_degrees_clockwise}deg clockwise, "
            f"duration={metadata.duration_s:.2f}s, "
            f"tracks={tracks.eligible_pairs}/{tracks.analyzed_pairs}, "
            f"median_keypoints={tracks.median_keypoints:.0f}, "
            f"median_matches={tracks.median_matches:.0f}, "
            f"median_inliers={tracks.median_fundamental_inliers:.0f}, "
            f"median_motion={tracks.median_motion_px:.2f}px, "
            f"median_parallax={tracks.median_parallax_px:.2f}px, "
            f"coverage={tracks.median_coverage_fraction:.1%}, "
            f"rejects={_format_rejections(tracks.rejection_reason_counts)}, "
            f"{trajectory_note}, {alignment_note}"
            f"{sidecar_note}"
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
    if rejected:
        raise ReconstructionError(
            (
                f"Feature-track diagnostics rejected {len(rejected)} room "
                f"walkthrough(s): {', '.join(rejected)} "
                f"({'; '.join(summaries)}). Re-walk with slower translation, "
                f"visible texture, and less motion blur before relative VO."
                f"{sidecar_warning} Centimetres will not be guessed."
            ),
            warning_code="insufficient_overlap",
        )
    raise ReconstructionError(
        (
            f"Sampled {len(media)} room walkthrough(s) at {config.sample_fps:g} Hz "
            f"({'; '.join(summaries)}).{sidecar_warning} "
            "Video room-surface extraction is not implemented yet; centimetres "
            "will not be emitted until metric pose alignment and geometry both "
            "succeed."
        ),
        warning_code="unsupported_tier",
    )


def _format_rejections(counts: tuple[tuple[str, int], ...]) -> str:
    return "|".join(f"{reason}:{count}" for reason, count in counts) or "none"


def _format_alignment_rejections(
    segments: tuple[MetricSegmentAlignment, ...],
) -> str:
    counts: dict[str, int] = {}
    for segment in segments:
        if segment.rejection_reason:
            counts[segment.rejection_reason] = (
                counts.get(segment.rejection_reason, 0) + 1
            )
    return (
        "|".join(f"{reason}:{count}" for reason, count in sorted(counts.items()))
        or "none"
    )
