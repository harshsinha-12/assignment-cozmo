"""Convert accepted calibrated video rooms into the shared FloorPlan IR."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path
from typing import Any

from cozmo_floorplan.config import FLOORPLAN_SCHEMA_VERSION
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.recon.video_config import DEFAULT_VIDEO_OUTPUT, VideoOutputConfig
from cozmo_floorplan.recon.video_measurements import video_area, video_length
from cozmo_floorplan.recon.video_rooms import VideoRoomCandidate

FloorPlan = dict[str, Any]


@dataclass(frozen=True, slots=True)
class VideoRoomReconstruction:
    """Output evidence for one calibrated room walkthrough."""

    source: Path
    pose_sidecar: Path
    world_frame_id: str
    scale_source: str
    room: VideoRoomCandidate
    sampled_frames: int
    metric_voxel_count: int
    accepted_pair_count: int


def build_video_floorplan(
    job: Job,
    reconstructions: tuple[VideoRoomReconstruction, ...],
    *,
    config: VideoOutputConfig = DEFAULT_VIDEO_OUTPUT,
) -> FloorPlan:
    """Build partial rooms only when every sidecar names one shared world frame."""

    if not reconstructions:
        raise ValueError("video FloorPlan conversion requires at least one room")
    world_frames = {item.world_frame_id for item in reconstructions}
    if len(world_frames) != 1:
        raise ValueError("video room sidecars must share one world_frame_id")
    scale_sources = {item.scale_source for item in reconstructions}
    if len(scale_sources) != 1 or not scale_sources <= {
        "arkit_poses",
        "arcore_poses",
    }:
        raise ValueError("video rooms must share one supported metric scale_source")

    rooms: list[dict[str, Any]] = []
    walls: list[dict[str, Any]] = []
    audit: list[str] = []
    for reconstruction in reconstructions:
        video_ref = reconstruction.source.relative_to(job.root).as_posix()
        sidecar_ref = reconstruction.pose_sidecar.relative_to(job.root).as_posix()
        evidence_ref = f"{video_ref}#{sidecar_ref}:sparse-manhattan"
        room_id = reconstruction.source.stem
        polygon_cm = [
            [_clean(x_m * 100.0), _clean(z_m * 100.0)]
            for x_m, z_m in reconstruction.room.polygon_xz_m
        ]
        rooms.append(
            {
                "id": room_id,
                "label": room_id.replace("-", " "),
                "polygon": polygon_cm,
                "ceiling_height": video_length(
                    reconstruction.room.ceiling_height_m * 100.0,
                    f"{evidence_ref}:floor-ceiling",
                    ceiling=True,
                    config=config,
                ),
                "area": video_area(
                    reconstruction.room.width_m
                    * reconstruction.room.depth_m
                    * 10_000.0,
                    f"{evidence_ref}:polygon",
                    config=config,
                ),
                "confidence": config.confidence,
            }
        )
        walls.extend(_build_walls(room_id, polygon_cm, evidence_ref, config))
        audit.append(
            f"{reconstruction.source.name}: {reconstruction.sampled_frames} samples, "
            f"{reconstruction.accepted_pair_count} triangulated pairs, "
            f"{reconstruction.metric_voxel_count} metric voxels"
        )

    warnings: list[dict[str, Any]] = [
        {
            "code": "low_confidence",
            "message": (
                "Video room intervals are candidate-stage engineering bounds and "
                "remain uncalibrated until tape/laser ground truth is supplied. "
                "Opening detection is not yet supported by this video path."
            ),
            "refs": [
                item.source.relative_to(job.root).as_posix() for item in reconstructions
            ],
        }
    ]
    if len(reconstructions) > 1:
        warnings.append(
            {
                "code": "disconnected_rooms",
                "message": (
                    "Video rooms share an exported world frame, but no common opening "
                    "association proves adjacency or drift correction yet."
                ),
                "refs": [
                    item.pose_sidecar.relative_to(job.root).as_posix()
                    for item in reconstructions
                ],
            }
        )
    world_frame_id = next(iter(world_frames))
    scale_source = next(iter(scale_sources))
    return {
        "version": FLOORPLAN_SCHEMA_VERSION,
        "units": "cm",
        "status": "partial",
        "warnings": warnings,
        "floor_id": job.job_id,
        "origin": {"frame": f"video-world:{world_frame_id}", "up": [0, 1, 0]},
        "rooms": rooms,
        "walls": walls,
        "openings": [],
        "damage": [],
        "concealed_flags": [],
        "scope": [],
        "provenance": {
            "tier": "video",
            "scale_source": scale_source,
            "gravity_source": "device",
            "pipeline": "cozmo-floorplan/video-calibrated-sparse-manhattan-v1",
            "inputs": list(job.input_refs),
            "notes": (
                f"All rooms declare shared world frame {world_frame_id!r}. "
                "No openings or cross-room constraints were invented. "
                + "; ".join(audit)
            ),
        },
    }


def _build_walls(
    room_id: str,
    polygon_cm: list[list[float]],
    evidence_ref: str,
    config: VideoOutputConfig,
) -> list[dict[str, Any]]:
    walls: list[dict[str, Any]] = []
    for index, start in enumerate(polygon_cm):
        end = polygon_cm[(index + 1) % len(polygon_cm)]
        length_cm = hypot(end[0] - start[0], end[1] - start[1])
        walls.append(
            {
                "id": f"{room_id}-wall-{index + 1}",
                "room_ids": [room_id],
                "a": start,
                "b": end,
                "length": video_length(
                    length_cm,
                    f"{evidence_ref}:wall:{index + 1}",
                    config=config,
                ),
                "confidence": config.confidence,
            }
        )
    return walls


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
