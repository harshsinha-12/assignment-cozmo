"""Photo-tier adapter: validate room folders until metric SfM exists."""

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.io.photos import load_photo_rooms
from cozmo_floorplan.recon.photos_config import DEFAULT_PHOTO_INGEST, PhotoIngestConfig


def reconstruct_photos(
    job: Job,
    *,
    config: PhotoIngestConfig = DEFAULT_PHOTO_INGEST,
) -> dict:
    """Validate photo evidence without fabricating scale or room geometry."""

    rooms = load_photo_rooms(job.root / "photos", config=config)
    counts = ", ".join(f"{room.identifier}={len(room.frames)}" for room in rooms)
    total = sum(len(room.frames) for room in rooms)
    raise ReconstructionError(
        (
            f"Validated {total} decodable photos across {len(rooms)} room folders ({counts}). "
            "Metric photo reconstruction and cross-room adjacency are not implemented yet; "
            "centimetres will not be guessed without SfM and a declared scale source."
        ),
        warning_code="unsupported_tier",
    )
