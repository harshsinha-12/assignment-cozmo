"""Convert accepted calibrated video rooms into the shared FloorPlan IR."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path
from typing import Any

from cozmo_floorplan.config import FLOORPLAN_SCHEMA_VERSION
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.video_config import (
    DEFAULT_VIDEO_OUTPUT,
    HANDHELD_VIDEO_OUTPUT,
    VideoOutputConfig,
)
from cozmo_floorplan.recon.video_measurements import (
    video_area,
    video_length,
    video_opening_length,
)
from cozmo_floorplan.recon.video_native_scale import NATIVE_SCALE_SOURCE
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
    gravity_source: str = "device"
    openings: tuple[Record3DOpeningCandidate, ...] = ()


def build_video_floorplan(
    job: Job,
    reconstructions: tuple[VideoRoomReconstruction, ...],
    *,
    config: VideoOutputConfig | None = None,
    incomplete_rooms: tuple[str, ...] = (),
) -> FloorPlan:
    """Build partial rooms from one sidecar world or independently scaled native rooms."""

    if not reconstructions:
        raise ValueError("video FloorPlan conversion requires at least one room")
    scale_sources = {item.scale_source for item in reconstructions}
    world_frames = {item.world_frame_id for item in reconstructions}
    sidecar_scales = {"arkit_poses", "arcore_poses"}
    independent = False
    if scale_sources <= sidecar_scales:
        if len(world_frames) != 1:
            raise ValueError("video room sidecars must share one world_frame_id")
        output = config or DEFAULT_VIDEO_OUTPUT
        gravity_source = "device"
        origin_frame = f"video-world:{next(iter(world_frames))}"
        placement_note = (
            f"All rooms declare shared world frame {next(iter(world_frames))!r}."
        )
    elif scale_sources == {NATIVE_SCALE_SOURCE}:
        independent = True
        output = config or HANDHELD_VIDEO_OUTPUT
        gravity_source = "assumed"
        origin_frame = "native-video-independent-bookkeeping"
        placement_note = (
            "Native rooms use a disclosed handheld-height prior and independent "
            "bookkeeping placement; they are not cross-registered."
        )
    else:
        raise ValueError("video rooms must share one supported metric scale_source")

    rooms: list[dict[str, Any]] = []
    walls: list[dict[str, Any]] = []
    openings: list[dict[str, Any]] = []
    audit: list[str] = []
    cursor_x = 0.0
    gap_cm = 200.0
    for reconstruction in reconstructions:
        video_ref = reconstruction.source.relative_to(job.root).as_posix()
        sidecar_ref = reconstruction.pose_sidecar.relative_to(job.root).as_posix()
        evidence_ref = f"{video_ref}#{sidecar_ref}:sparse-manhattan"
        room_id = reconstruction.source.stem
        polygon_cm = [
            [_clean(x_m * 100.0), _clean(z_m * 100.0)]
            for x_m, z_m in reconstruction.room.polygon_xz_m
        ]
        if independent:
            min_x = min(point[0] for point in polygon_cm)
            max_x = max(point[0] for point in polygon_cm)
            shift = cursor_x - min_x
            polygon_cm = [[point[0] + shift, point[1]] for point in polygon_cm]
            cursor_x += max_x - min_x + gap_cm
        rooms.append(
            {
                "id": room_id,
                "label": room_id.replace("-", " "),
                "polygon": polygon_cm,
                "ceiling_height": video_length(
                    reconstruction.room.ceiling_height_m * 100.0,
                    f"{evidence_ref}:floor-ceiling",
                    ceiling=True,
                    config=output,
                ),
                "area": video_area(
                    reconstruction.room.width_m
                    * reconstruction.room.depth_m
                    * 10_000.0,
                    f"{evidence_ref}:polygon",
                    config=output,
                ),
                "confidence": output.confidence,
            }
        )
        room_walls = _build_walls(room_id, polygon_cm, evidence_ref, output)
        walls.extend(room_walls)
        openings.extend(
            _build_openings(
                room_id,
                reconstruction.openings,
                room_walls,
                evidence_ref,
                output,
            )
        )
        audit.append(
            f"{reconstruction.source.name}: {reconstruction.sampled_frames} samples, "
            f"{reconstruction.accepted_pair_count} triangulated pairs, "
            f"{reconstruction.metric_voxel_count} metric voxels, "
            f"{len(reconstruction.openings)} occupancy openings"
        )

    if not independent:
        openings = _associate_shared_world_openings(openings, walls)

    opening_note = (
        f"{len(openings)} occupancy-supported opening candidate(s). "
        if openings
        else "No occupancy-supported openings were found. "
    )
    shared_links = sum(
        1 for opening in openings if len(opening.get("connects_room_ids", [])) == 2
    )
    warnings: list[dict[str, Any]] = [
        {
            "code": "low_confidence",
            "message": (
                "Video room intervals are candidate-stage engineering bounds, not "
                "the official ±3% wall gate. They remain uncalibrated until "
                "tape/laser ground truth is supplied. "
                + opening_note
                + (
                    "Shared-world openings may constrain stitch; independent native "
                    "rooms are not overlaid."
                )
            ),
            "refs": [
                item.source.relative_to(job.root).as_posix() for item in reconstructions
            ],
        }
    ]
    if incomplete_rooms:
        warnings.append(
            {
                "code": "low_confidence",
                "message": (
                    "Some walkthroughs did not support a complete room and were "
                    "omitted rather than dimensioned: "
                    + "; ".join(incomplete_rooms)
                ),
                "refs": [
                    item.source.relative_to(job.root).as_posix()
                    for item in reconstructions
                ],
            }
        )
    if len(reconstructions) > 1 and (independent or shared_links == 0):
        warnings.append(
            {
                "code": "disconnected_rooms",
                "message": (
                    "Video rooms are not opening-registered; adjacency and drift "
                    "correction are not claimed."
                    if independent
                    else (
                        "Video rooms share an exported world frame, but no common "
                        "opening association proves adjacency or drift correction yet."
                    )
                ),
                "refs": [
                    item.pose_sidecar.relative_to(job.root).as_posix()
                    for item in reconstructions
                ],
            }
        )
    scale_source = next(iter(scale_sources))
    return {
        "version": FLOORPLAN_SCHEMA_VERSION,
        "units": "cm",
        "status": "partial",
        "warnings": warnings,
        "floor_id": job.job_id,
        "origin": {"frame": origin_frame, "up": [0, 1, 0]},
        "rooms": rooms,
        "walls": walls,
        "openings": openings,
        "damage": [],
        "concealed_flags": [],
        "scope": [],
        "provenance": {
            "tier": "video",
            "scale_source": scale_source,
            "gravity_source": gravity_source,
            "pipeline": (
                "cozmo-floorplan/video-handheld-height-sparse-manhattan-v1"
                if independent
                else "cozmo-floorplan/video-calibrated-sparse-manhattan-v1"
            ),
            "inputs": list(job.input_refs),
            "notes": (
                f"{placement_note} {opening_note}"
                "Cross-room constraints are created only from shared-world opening "
                "pairs; the official ±3% wall gate is not claimed from these intervals. "
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


def _build_openings(
    room_id: str,
    candidates: tuple[Record3DOpeningCandidate, ...],
    walls: list[dict[str, Any]],
    evidence_ref: str,
    config: VideoOutputConfig,
) -> list[dict[str, Any]]:
    openings: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        candidate_ref = f"{evidence_ref}:opening:{index + 1}"
        openings.append(
            {
                "id": f"{room_id}-opening-{index + 1}",
                "kind": candidate.kind,
                "wall_id": walls[candidate.wall_index]["id"],
                "width": video_opening_length(
                    candidate.width_m * 100.0,
                    candidate_ref,
                    half_width_cm=config.opening_width_half_width_cm,
                    config=config,
                ),
                "height": video_opening_length(
                    candidate.height_m * 100.0,
                    candidate_ref,
                    half_width_cm=config.opening_height_half_width_cm,
                    config=config,
                ),
                "offset_along_wall": video_opening_length(
                    candidate.offset_m * 100.0,
                    candidate_ref,
                    half_width_cm=config.opening_width_half_width_cm,
                    config=config,
                ),
                "connects_room_ids": [room_id],
                "confidence": config.opening_confidence,
            }
        )
    return openings


def _associate_shared_world_openings(
    openings: list[dict[str, Any]],
    walls: list[dict[str, Any]],
    *,
    max_center_gap_cm: float = 80.0,
    max_width_delta_cm: float = 25.0,
) -> list[dict[str, Any]]:
    """Link same-kind openings that coincide in one exported world frame."""

    if len(openings) < 2:
        return openings
    walls_by_id = {str(wall["id"]): wall for wall in walls}
    used: set[int] = set()
    for left_index, left in enumerate(openings):
        if left_index in used:
            continue
        best: tuple[float, int] | None = None
        for right_index, right in enumerate(openings):
            if right_index <= left_index or right_index in used:
                continue
            if left["kind"] != right["kind"]:
                continue
            if set(left["connects_room_ids"]) & set(right["connects_room_ids"]):
                continue
            if abs(left["width"]["value"] - right["width"]["value"]) > max_width_delta_cm:
                continue
            gap = hypot(
                *(
                    left_coord - right_coord
                    for left_coord, right_coord in zip(
                        _opening_center_cm(left, walls_by_id),
                        _opening_center_cm(right, walls_by_id),
                        strict=True,
                    )
                )
            )
            if gap > max_center_gap_cm:
                continue
            if best is None or gap < best[0]:
                best = (gap, right_index)
        if best is None:
            continue
        right = openings[best[1]]
        connected = sorted(
            {*left["connects_room_ids"], *right["connects_room_ids"]}
        )
        left["connects_room_ids"] = connected
        right["connects_room_ids"] = connected
        used.add(left_index)
        used.add(best[1])
    return openings


def _opening_center_cm(
    opening: dict[str, Any],
    walls_by_id: dict[str, dict[str, Any]],
) -> tuple[float, float]:
    wall = walls_by_id[str(opening["wall_id"])]
    start_x, start_y = float(wall["a"][0]), float(wall["a"][1])
    delta_x = float(wall["b"][0]) - start_x
    delta_y = float(wall["b"][1]) - start_y
    length = hypot(delta_x, delta_y)
    if length <= 1e-9:
        return (start_x, start_y)
    offset = float(opening["offset_along_wall"]["value"]) + (
        float(opening["width"]["value"]) / 2.0
    )
    ratio = max(0.0, min(1.0, offset / length))
    return (start_x + ratio * delta_x, start_y + ratio * delta_y)


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
