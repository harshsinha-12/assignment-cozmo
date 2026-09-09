"""Discover and validate per-room photo evidence."""

from dataclasses import dataclass
from pathlib import Path

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.recon.photos_config import (
    DEFAULT_PHOTO_INGEST,
    PHOTO_EXTENSIONS,
    PhotoIngestConfig,
)
from cozmo_floorplan.utils.images import load_display_oriented_bgr


@dataclass(frozen=True, slots=True)
class PhotoFrame:
    path: Path
    width_px: int
    height_px: int


@dataclass(frozen=True, slots=True)
class PhotoRoom:
    identifier: str
    frames: tuple[PhotoFrame, ...]


def load_photo_rooms(
    photos_dir: Path,
    *,
    config: PhotoIngestConfig = DEFAULT_PHOTO_INGEST,
) -> tuple[PhotoRoom, ...]:
    """Return stable room/frame metadata after decoding every supported image."""

    room_dirs = sorted(
        (
            path
            for path in photos_dir.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        ),
        key=lambda path: path.name.lower(),
    )
    if not room_dirs:
        raise ReconstructionError(
            "No room folders found in photos/. Add photos/<room_id>/ with 2 to 8 images.",
            warning_code="incomplete_scan",
        )

    return tuple(_load_room(room_dir, config) for room_dir in room_dirs)


def _load_room(room_dir: Path, config: PhotoIngestConfig) -> PhotoRoom:
    paths = sorted(
        (
            path
            for path in room_dir.iterdir()
            if path.is_file() and path.suffix.lower() in PHOTO_EXTENSIONS
        ),
        key=lambda path: path.name.lower(),
    )
    count = len(paths)
    if not config.min_photos_per_room <= count <= config.max_photos_per_room:
        raise ReconstructionError(
            (
                f"Photo room {room_dir.name!r} contains {count} supported images; "
                f"need {config.min_photos_per_room} to {config.max_photos_per_room}."
            ),
            warning_code="incomplete_scan",
        )
    frames = tuple(_inspect_photo(path, config) for path in paths)
    return PhotoRoom(identifier=room_dir.name, frames=frames)


def _inspect_photo(path: Path, config: PhotoIngestConfig) -> PhotoFrame:
    image = load_display_oriented_bgr(path)
    if image is None:
        raise ReconstructionError(
            f"Could not decode photo {path.name!r} in room {path.parent.name!r}.",
            warning_code="incomplete_scan",
        )
    height, width = image.shape[:2]
    if min(width, height) < config.min_edge_px:
        raise ReconstructionError(
            (
                f"Photo {path.name!r} in room {path.parent.name!r} is {width}x{height}; "
                f"each edge must be at least {config.min_edge_px} px."
            ),
            warning_code="incomplete_scan",
        )
    return PhotoFrame(path=path, width_px=int(width), height_px=int(height))
