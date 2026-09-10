"""Photo-tier adapter: overlap graph, then incremental SfM when connected."""

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.photos import load_photo_rooms
from cozmo_floorplan.recon.photo_floorplan import build_photo_floorplan
from cozmo_floorplan.recon.photo_overlap import analyze_photo_overlap
from cozmo_floorplan.recon.photo_sfm import reconstruct_photo_room
from cozmo_floorplan.recon.photos_config import (
    DEFAULT_PHOTO_INGEST,
    DEFAULT_PHOTO_OVERLAP,
    DEFAULT_PHOTO_OUTPUT,
    DEFAULT_PHOTO_SFM,
    PhotoIngestConfig,
    PhotoOverlapConfig,
    PhotoOutputConfig,
    PhotoSfmConfig,
)


def reconstruct_photos(
    job: Job,
    *,
    config: PhotoIngestConfig = DEFAULT_PHOTO_INGEST,
    overlap_config: PhotoOverlapConfig = DEFAULT_PHOTO_OVERLAP,
    sfm_config: PhotoSfmConfig = DEFAULT_PHOTO_SFM,
    output_config: PhotoOutputConfig = DEFAULT_PHOTO_OUTPUT,
) -> dict:
    """Emit metric rooms from a connected overlap graph; refuse disconnected stills."""

    rooms = load_photo_rooms(job.root / "photos", config=config)
    counts = ", ".join(f"{room.identifier}={len(room.frames)}" for room in rooms)
    total = sum(len(room.frames) for room in rooms)
    overlap = analyze_photo_overlap(rooms, config=overlap_config)
    connectivity_parts = []
    for room in overlap.rooms:
        isolated = [group[0] for group in room.components if len(group) == 1]
        isolated_note = f", isolated={','.join(isolated)}" if isolated else ""
        connectivity_parts.append(
            f"{room.identifier}: edges={room.eligible_edges}/{room.possible_edges}, "
            f"components={room.component_count}{isolated_note}"
        )
    connectivity = "; ".join(connectivity_parts)
    disconnected = [room.identifier for room in overlap.rooms if not room.connected]
    cross_pair_count = len(rooms) * (len(rooms) - 1) // 2
    candidate_pairs = ",".join(
        f"{item.left_room}<->{item.right_room}"
        for item in overlap.cross_room_candidates
    )
    cross_note = (
        f"cross-room candidates={len(overlap.cross_room_candidates)}/"
        f"{cross_pair_count} room pairs"
        + (f" ({candidate_pairs})" if candidate_pairs else "")
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

    reconstructions = []
    incomplete: list[str] = []
    rooms_by_id = {room.identifier: room for room in rooms}
    for connectivity_room in overlap.rooms:
        try:
            reconstructions.append(
                reconstruct_photo_room(
                    rooms_by_id[connectivity_room.identifier],
                    overlap_config=overlap_config,
                    sfm_config=sfm_config,
                )
            )
        except ReconstructionError as exc:
            incomplete.append(f"{connectivity_room.identifier}: {exc}")
    if not reconstructions:
        raise ReconstructionError(
            (
                f"Validated {total} decodable photos across {len(rooms)} room "
                f"folders ({counts}); overlap graph is eligible ({connectivity}; "
                f"{cross_note}), but metric SfM did not recover a floor-supported "
                f"room: {'; '.join(incomplete)}. Centimetres will not be guessed."
            ),
            warning_code="low_confidence",
        )
    return build_photo_floorplan(
        job,
        tuple(reconstructions),
        config=output_config,
        incomplete_rooms=tuple(incomplete),
        overlap_note=f"Overlap {connectivity}; {cross_note}. ",
    )
