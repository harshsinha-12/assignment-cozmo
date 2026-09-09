"""Convert accepted Record3D room candidates into the shared FloorPlan IR."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path
from typing import Any

from cozmo_floorplan.config import FLOORPLAN_SCHEMA_VERSION
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.recon.record3d_config import (
    DEFAULT_RECORD3D_OUTPUT,
    Record3DOutputConfig,
)
from cozmo_floorplan.recon.record3d_measurements import (
    record3d_area,
    record3d_length,
)
from cozmo_floorplan.recon.record3d_openings import Record3DOpeningCandidate
from cozmo_floorplan.recon.record3d_planes import ManhattanRoomCandidate
from cozmo_floorplan.recon.record3d_uncertainty import Record3DUncertainty

FloorPlan = dict[str, Any]


@dataclass(frozen=True, slots=True)
class Record3DRoomReconstruction:
    """Output-relevant evidence from one independently stored archive."""

    source: Path
    room: ManhattanRoomCandidate
    openings: tuple[Record3DOpeningCandidate, ...]
    frame_count: int
    sampled_frame_count: int
    metric_voxel_count: int
    uncertainty: Record3DUncertainty | None = None


def build_record3d_floorplan(
    job: Job,
    reconstructions: tuple[Record3DRoomReconstruction, ...],
    *,
    config: Record3DOutputConfig = DEFAULT_RECORD3D_OUTPUT,
) -> FloorPlan:
    """Build partial metric geometry without inventing cross-archive adjacency."""

    rooms: list[dict[str, Any]] = []
    walls: list[dict[str, Any]] = []
    openings: list[dict[str, Any]] = []
    evidence_refs: list[str] = []
    audit_notes: list[str] = []
    for reconstruction in reconstructions:
        evidence_ref = reconstruction.source.relative_to(job.root).as_posix()
        evidence_refs.append(evidence_ref)
        room_id = reconstruction.source.stem
        polygon_cm = [
            [_clean(x_m * 100.0), _clean(z_m * 100.0)]
            for x_m, z_m in reconstruction.room.polygon_xz_m
        ]
        wall_half_widths = (
            reconstruction.uncertainty.polygon_wall_half_widths_cm
            if reconstruction.uncertainty
            else (config.wall_half_width_cm,) * 4
        )
        room_walls = _build_walls(
            room_id,
            polygon_cm,
            evidence_ref,
            wall_half_widths,
            config,
        )
        rooms.append(
            {
                "id": room_id,
                "label": room_id.replace("-", " "),
                "polygon": polygon_cm,
                "ceiling_height": record3d_length(
                    reconstruction.room.levels.ceiling_height_m * 100.0,
                    f"{evidence_ref}#horizontal-levels",
                    half_width_cm=(
                        reconstruction.uncertainty.ceiling_half_width_cm
                        if reconstruction.uncertainty
                        else config.ceiling_half_width_cm
                    ),
                    config=config,
                ),
                "area": record3d_area(
                    reconstruction.room.width_m
                    * reconstruction.room.depth_m
                    * 10_000.0,
                    f"{evidence_ref}#manhattan-polygon",
                    relative_half_width=(
                        reconstruction.uncertainty.area_relative_half_width
                        if reconstruction.uncertainty
                        else None
                    ),
                    config=config,
                ),
                "confidence": config.confidence,
            }
        )
        walls.extend(room_walls)
        openings.extend(
            _build_openings(
                room_id,
                reconstruction.openings,
                room_walls,
                evidence_ref,
                config,
            )
        )
        audit_notes.append(
            f"{reconstruction.source.name}: {reconstruction.frame_count} frames, "
            f"{reconstruction.sampled_frame_count} sampled, "
            f"{reconstruction.metric_voxel_count} metric voxels, "
            f"{len(reconstruction.openings)} supported opening candidates"
            + (
                ", support-conditioned conservative plane residual intervals"
                if reconstruction.uncertainty
                else ""
            )
        )

    warnings: list[dict[str, Any]] = [
        {
            "code": "low_confidence",
            "message": (
                "Record3D room intervals are conditioned on conservative raw-plane "
                "residuals and pass the current benchmark coverage policy, but lack "
                "independent holdout validation; opening intervals remain fixed candidates."
            ),
            "refs": evidence_refs,
        }
    ]
    if len(reconstructions) > 1:
        warnings.append(
            {
                "code": "disconnected_rooms",
                "message": (
                    "Separate Record3D archives retain their exported world-pose "
                    "coordinates, but no shared opening association was proven; "
                    "cross-archive registration remains unverified."
                ),
                "refs": evidence_refs,
            }
        )
    return {
        "version": FLOORPLAN_SCHEMA_VERSION,
        "units": "cm",
        "status": "partial",
        "warnings": warnings,
        "floor_id": job.job_id,
        "origin": {"frame": "record3d-world-xz", "up": [0, 1, 0]},
        "rooms": rooms,
        "walls": walls,
        "openings": openings,
        "damage": [],
        "concealed_flags": [],
        "scope": [],
        "provenance": {
            "tier": "lidar",
            "scale_source": "lidar",
            "gravity_source": "device",
            "pipeline": "cozmo-floorplan/record3d-r3d-v1+manhattan-candidates",
            "inputs": list(job.input_refs),
            "notes": (
                "Metric geometry comes from depth, intrinsics, and exported poses. "
                "No cross-archive transform was invented. " + "; ".join(audit_notes)
            ),
        },
    }


def _build_walls(
    room_id: str,
    polygon_cm: list[list[float]],
    evidence_ref: str,
    half_widths_cm: tuple[float, float, float, float],
    config: Record3DOutputConfig,
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
                "length": record3d_length(
                    length_cm,
                    f"{evidence_ref}#wall:{index + 1}",
                    half_width_cm=half_widths_cm[index],
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
    config: Record3DOutputConfig,
) -> list[dict[str, Any]]:
    openings: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        candidate_ref = f"{evidence_ref}#opening-candidate:{index + 1}"
        openings.append(
            {
                "id": f"{room_id}-opening-{index + 1}",
                "kind": candidate.kind,
                "wall_id": walls[candidate.wall_index]["id"],
                "width": record3d_length(
                    candidate.width_m * 100.0,
                    candidate_ref,
                    half_width_cm=config.opening_width_half_width_cm,
                    config=config,
                ),
                "height": record3d_length(
                    candidate.height_m * 100.0,
                    candidate_ref,
                    half_width_cm=config.opening_height_half_width_cm,
                    config=config,
                ),
                "offset_along_wall": record3d_length(
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
