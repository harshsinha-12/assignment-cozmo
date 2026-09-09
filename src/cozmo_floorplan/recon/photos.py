"""Photo-tier adapter: validate room folders until metric SfM exists."""

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.photos import load_photo_rooms
from cozmo_floorplan.recon.photo_overlap import analyze_photo_overlap
from cozmo_floorplan.recon.photos_config import (
    DEFAULT_PHOTO_INGEST,
    DEFAULT_PHOTO_OVERLAP,
    PhotoIngestConfig,
    PhotoOverlapConfig,
)


def reconstruct_photos(
    job: Job,
    *,
    config: PhotoIngestConfig = DEFAULT_PHOTO_INGEST,
    overlap_config: PhotoOverlapConfig = DEFAULT_PHOTO_OVERLAP,
) -> dict:
    """Validate photo evidence and overlap without fabricating metric geometry."""

    rooms = load_photo_rooms(job.root / "photos", config=config)
    counts = ", ".join(f"{room.identifier}={len(room.frames)}" for room in rooms)
    total = sum(len(room.frames) for room in rooms)
    overlap = analyze_photo_overlap(rooms, config=overlap_config)
    connectivity = "; ".join(
        f"{room.identifier}: edges={room.eligible_edges}/{room.possible_edges}, "
        f"components={room.component_count}"
        for room in overlap.rooms
    )
    disconnected = [room.identifier for room in overlap.rooms if not room.connected]
    cross_pair_count = len(rooms) * (len(rooms) - 1) // 2
    cross_note = (
        f"cross-room candidates={len(overlap.cross_room_candidates)}/"
        f"{cross_pair_count} room pairs"
    )
    if disconnected:
        raise ReconstructionError(
            (
                f"Validated {total} decodable photos across {len(rooms)} room "
                f"folders ({counts}), but the overlap graph is disconnected for "
                f"{', '.join(disconnected)} ({connectivity}; {cross_note}). "
                "Reshoot intermediate views with 60%+ overlap. Centimetres will "
                "not be guessed."
            ),
            warning_code="insufficient_overlap",
        )
    if len(rooms) > 1 and not overlap.cross_room_candidates:
        raise ReconstructionError(
            (
                f"Validated {total} decodable photos across {len(rooms)} room "
                f"folders ({counts}); each room graph is connected ({connectivity}), "
                f"but {cross_note}. Add doorway/connector views shared by adjacent "
                "rooms. Centimetres will not be guessed."
            ),
            warning_code="insufficient_overlap",
        )
    raise ReconstructionError(
        (
            f"Validated {total} decodable photos across {len(rooms)} room folders "
            f"({counts}); overlap graph is eligible ({connectivity}; {cross_note}). "
            "Metric SfM, adjacency verification, and scale are not implemented yet; "
            "centimetres will not be guessed."
        ),
        warning_code="unsupported_tier",
    )
