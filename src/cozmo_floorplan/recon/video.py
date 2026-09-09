"""Video-tier adapter from walkthrough evidence to conservative metric rooms."""

import numpy as np

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.video import (
    SampledVideo,
    find_pose_sidecar,
    find_video_files,
    sample_video,
)
from cozmo_floorplan.io.video_poses import MetricPoseSidecar, load_metric_pose_sidecar
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_INGEST,
    DEFAULT_VIDEO_TRACKING,
    POSE_SIDECAR_NAMES,
    VideoIngestConfig,
    VideoTrackingConfig,
)
from cozmo_floorplan.recon.video_tracks import analyze_video_tracks
from cozmo_floorplan.recon.video_floorplan import (
    VideoRoomReconstruction,
    build_video_floorplan,
)
from cozmo_floorplan.recon.video_native_scale import (
    NATIVE_SCALE_SOURCE,
    apply_handheld_height_scale,
    build_native_unit_sidecar,
    estimate_handheld_height_scale,
)
from cozmo_floorplan.recon.video_pose_alignment import (
    MetricSegmentAlignment,
    align_trajectory_to_metric_poses,
)
from cozmo_floorplan.recon.video_trajectory import recover_scale_free_trajectory
from cozmo_floorplan.recon.video_trajectory import VideoTrajectoryDiagnostics
from cozmo_floorplan.recon.video_rooms import fit_video_room_candidate
from cozmo_floorplan.recon.video_triangulation import (
    triangulate_aligned_video_segments,
)


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
    geometry_rejections: list[str] = []
    reconstructions: list[VideoRoomReconstruction] = []
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
        # The aggregate ratio is a capture-health signal, not a reconstruction
        # veto. A locally connected, pair-gated trajectory can still be valid
        # when long pans make most sampled pairs homography-dominant.
        if tracks.eligible_pairs == 0:
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
                metric_sidecar = build_native_unit_sidecar(sampled, trajectory)
                native_scale = metric_sidecar is not None
                alignment_note = (
                    "metric_alignment=native-height-prior"
                    if native_scale
                    else "metric_alignment=not-available"
                )
            else:
                native_scale = False
            if metric_sidecar is not None:
                alignment = align_trajectory_to_metric_poses(
                    sampled,
                    trajectory,
                    metric_sidecar,
                )
                rejected_alignments = _format_alignment_rejections(alignment.segments)
                if not native_scale:
                    alignment_note = (
                        f"metric_alignment={alignment.aligned_segment_count}/"
                        f"{len(alignment.segments)} segments, "
                        f"alignment_rejects={rejected_alignments}"
                    )
                else:
                    alignment_note += (
                        f", segments={alignment.aligned_segment_count}/"
                        f"{len(alignment.segments)}, "
                        f"alignment_rejects={rejected_alignments}"
                    )
                cloud = triangulate_aligned_video_segments(
                    sampled,
                    trajectory,
                    alignment,
                    metric_sidecar,
                    tracking_config=tracking_config,
                )
                if cloud is None:
                    alignment_note += ", triangulation=not-calibrated"
                    geometry_rejections.append(
                        f"{sampled.identifier}: calibrated triangulation was unavailable"
                    )
                else:
                    camera_positions = _accepted_camera_positions(
                        sampled, trajectory, alignment.segments, metric_sidecar
                    )
                    points = cloud.points_m
                    if native_scale:
                        height_scale = estimate_handheld_height_scale(
                            camera_positions, points
                        )
                        if height_scale is None:
                            alignment_note += (
                                f", triangulation={len(cloud.points_m)} voxels/"
                                f"{cloud.accepted_pairs}/{cloud.attempted_pairs} pairs, "
                                "native_scale=no-floor"
                            )
                            camera_positions = np.empty((0, 3))
                            points = None
                            geometry_rejections.append(
                                f"{sampled.identifier}: triangulated points did not "
                                "support a floor-relative camera-height scale"
                            )
                        else:
                            metric_sidecar, points = apply_handheld_height_scale(
                                metric_sidecar, points, height_scale
                            )
                            camera_positions = np.asarray(
                                [pose.position_m for pose in metric_sidecar.poses],
                                dtype=np.float64,
                            )
                            alignment_note += (
                                f", triangulation={len(points)} voxels/"
                                f"{cloud.accepted_pairs}/{cloud.attempted_pairs} pairs, "
                                f"native_scale={height_scale.scale_m_per_unit:.3f}m/unit"
                            )
                    if points is not None and len(camera_positions):
                        try:
                            room = fit_video_room_candidate(points, camera_positions)
                        except ReconstructionError as exc:
                            geometry_rejections.append(f"{sampled.identifier}: {exc}")
                            if "native_scale=" not in alignment_note:
                                alignment_note += (
                                    f", triangulation={len(points)} voxels/"
                                    f"{cloud.accepted_pairs}/{cloud.attempted_pairs} pairs, "
                                    "room=not-supported"
                                )
                            else:
                                alignment_note += ", room=not-supported"
                        else:
                            reconstructions.append(
                                VideoRoomReconstruction(
                                    source=source,
                                    pose_sidecar=metric_sidecar.source,
                                    world_frame_id=metric_sidecar.world_frame_id or "",
                                    scale_source=metric_sidecar.scale_source or "",
                                    gravity_source=(
                                        "assumed"
                                        if metric_sidecar.scale_source == NATIVE_SCALE_SOURCE
                                        else "device"
                                    ),
                                    room=room,
                                    sampled_frames=len(sampled.frames),
                                    metric_voxel_count=len(points),
                                    accepted_pair_count=cloud.accepted_pairs,
                                )
                            )
                            alignment_note += (
                                f", room={room.width_m:.2f}x{room.depth_m:.2f}m"
                                if "native_scale=" in alignment_note
                                else (
                                    f", triangulation={len(points)} voxels/"
                                    f"{cloud.accepted_pairs}/{cloud.attempted_pairs} pairs, "
                                    f"room={room.width_m:.2f}x{room.depth_m:.2f}m"
                                )
                            )
            elif trajectory.segments:
                geometry_rejections.append(
                    f"{sampled.identifier}: no connected trajectory segment retained "
                    "at least three poses for native scale"
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
    if geometry_rejections:
        raise ReconstructionError(
            (
                "Metric video evidence did not support every complete room: "
                f"{'; '.join(geometry_rejections)}. Floor, ceiling, and two "
                "camera-bracketing wall pairs are required; partial planes are "
                f"not converted to dimensions. Diagnostics: {'; '.join(summaries)}"
            ),
            warning_code="low_confidence",
        )
    if len(reconstructions) == len(media):
        scale_sources = {item.scale_source for item in reconstructions}
        world_frames = {item.world_frame_id for item in reconstructions}
        if scale_sources <= {"arkit_poses", "arcore_poses"}:
            if len(world_frames) != 1 or "" in world_frames:
                raise ReconstructionError(
                    "Calibrated multi-video sidecars must declare the same non-empty "
                    "world_frame_id; unrelated room coordinates will not be overlaid.",
                    warning_code="disconnected_rooms",
                )
        elif scale_sources != {NATIVE_SCALE_SOURCE}:
            raise ReconstructionError(
                "Video rooms must share one supported metric scale_source; mixed "
                "ARKit/native priors will not be overlaid.",
                warning_code="disconnected_rooms",
            )
        return build_video_floorplan(job, tuple(reconstructions))
    raise ReconstructionError(
        (
            f"Sampled {len(media)} room walkthrough(s) at {config.sample_fps:g} Hz "
            f"({'; '.join(summaries)}).{sidecar_warning} "
            "Video FloorPlan conversion requires v1.2 calibrated pose sidecars "
            "or a floor-supported handheld-height prior, plus complete "
            "camera-bracketing room surfaces. Centimetres will not be inferred "
            "from native Camera-app video without that evidence."
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


def _accepted_camera_positions(
    video: SampledVideo,
    trajectory: VideoTrajectoryDiagnostics,
    segments: tuple[MetricSegmentAlignment, ...],
    sidecar: MetricPoseSidecar,
) -> np.ndarray:
    accepted_ids = {item.segment_id for item in segments if item.accepted}
    source_indices = {
        video.source_frame_indices[pose.frame_index]
        for segment in trajectory.segments
        if segment.segment_id in accepted_ids
        for pose in segment.poses
    }
    return np.asarray(
        [
            pose.position_m
            for pose in sidecar.poses
            if pose.source_frame_index in source_indices
        ],
        dtype=np.float64,
    )
