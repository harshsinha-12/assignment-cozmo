"""Convert accepted photo SfM rooms into the shared FloorPlan IR."""

from __future__ import annotations

from math import hypot
from typing import Any

from cozmo_floorplan.config import FLOORPLAN_SCHEMA_VERSION
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.recon.photos_config import DEFAULT_PHOTO_OUTPUT, PhotoOutputConfig
from cozmo_floorplan.recon.photo_sfm import PhotoRoomReconstruction
from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.video_config import VideoOutputConfig
from cozmo_floorplan.recon.video_measurements import (
    video_area,
    video_length,
    video_opening_length,
)
from cozmo_floorplan.recon.video_openings import detect_video_openings

FloorPlan = dict[str, Any]


def build_photo_floorplan(
    job: Job,
    reconstructions: tuple[PhotoRoomReconstruction, ...],
    *,
    config: PhotoOutputConfig = DEFAULT_PHOTO_OUTPUT,
    incomplete_rooms: tuple[str, ...] = (),
    overlap_note: str = "",
) -> FloorPlan:
    """Place independently scaled photo rooms; do not overlay unrelated SfM frames."""

    if not reconstructions:
        raise ValueError("photo FloorPlan conversion requires at least one room")
    output = _as_video_output(config)
    rooms: list[dict[str, Any]] = []
    walls: list[dict[str, Any]] = []
    openings: list[dict[str, Any]] = []
    audit: list[str] = []
    cursor_x = 0.0
    gap_cm = 200.0
    for reconstruction in reconstructions:
        evidence_ref = f"photos/{reconstruction.identifier}:sfm-manhattan"
        polygon_cm = [
            [_clean(x_m * 100.0), _clean(z_m * 100.0)]
            for x_m, z_m in reconstruction.room.polygon_xz_m
        ]
        min_x = min(point[0] for point in polygon_cm)
        max_x = max(point[0] for point in polygon_cm)
        shift = cursor_x - min_x
        polygon_cm = [[point[0] + shift, point[1]] for point in polygon_cm]
        cursor_x += max_x - min_x + gap_cm
        rooms.append(
            {
                "id": reconstruction.identifier,
                "label": reconstruction.identifier.replace("-", " "),
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
        room_walls = _build_walls(
            reconstruction.identifier, polygon_cm, evidence_ref, output
        )
        walls.extend(room_walls)
        detected = detect_video_openings(
            reconstruction.points_m, reconstruction.room
        )
        openings.extend(
            _build_openings(
                reconstruction.identifier,
                detected,
                room_walls,
                evidence_ref,
                output,
            )
        )
        audit.append(
            f"{reconstruction.identifier}: {reconstruction.registered_cameras}/"
            f"{reconstruction.image_count} cameras, "
            f"{reconstruction.triangulated_points} voxels, "
            f"{len(detected)} occupancy openings"
        )

    opening_note = (
        f"{len(openings)} occupancy-supported opening candidate(s). "
        if openings
        else "No occupancy-supported openings were found. "
    )
    warnings: list[dict[str, Any]] = [
        {
            "code": "low_confidence",
            "message": (
                "Photo room intervals use a disclosed 1.45 m handheld-height prior "
                "and assumed intrinsics. They are not the official ±8% wall gate. "
                + opening_note
                + "Independent rooms are not cross-registered."
            ),
            "refs": [f"photos/{item.identifier}" for item in reconstructions],
        }
    ]
    if incomplete_rooms:
        warnings.append(
            {
                "code": "low_confidence",
                "message": (
                    "Some connected photo rooms did not support metric SfM and "
                    "were omitted: " + "; ".join(incomplete_rooms)
                ),
                "refs": [f"photos/{item.identifier}" for item in reconstructions],
            }
        )
    if len(reconstructions) > 1:
        warnings.append(
            {
                "code": "disconnected_rooms",
                "message": (
                    "Photo rooms are independently scaled; adjacency and drift "
                    "correction are not claimed from stills without a shared "
                    "metric frame."
                ),
                "refs": [f"photos/{item.identifier}" for item in reconstructions],
            }
        )
    return {
        "version": FLOORPLAN_SCHEMA_VERSION,
        "units": "cm",
        "status": "partial",
        "warnings": warnings,
        "floor_id": job.job_id,
        "origin": {"frame": "photo-sfm-independent-bookkeeping", "up": [0, 1, 0]},
        "rooms": rooms,
        "walls": walls,
        "openings": openings,
        "damage": [],
        "concealed_flags": [],
        "scope": [],
        "provenance": {
            "tier": "photos",
            "scale_source": "known_length",
            "gravity_source": "assumed",
            "pipeline": "cozmo-floorplan/photo-incremental-sfm-handheld-height-v1",
            "inputs": list(job.input_refs),
            "notes": (
                "Connected overlap graphs advance to incremental SfM. Scale is the "
                "disclosed 1.45 m handheld-height prior after a floor band. "
                + overlap_note
                + opening_note
                + "; ".join(audit)
            ),
        },
    }


def _as_video_output(config: PhotoOutputConfig) -> VideoOutputConfig:
    return VideoOutputConfig(
        confidence=config.confidence,
        minimum_length_half_width_cm=config.minimum_length_half_width_cm,
        length_relative_half_width=config.length_relative_half_width,
        minimum_ceiling_half_width_cm=config.minimum_ceiling_half_width_cm,
        area_relative_half_width=config.area_relative_half_width,
        opening_confidence=config.opening_confidence,
        opening_width_half_width_cm=config.opening_width_half_width_cm,
        opening_height_half_width_cm=config.opening_height_half_width_cm,
        method=config.method,
    )


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


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded
