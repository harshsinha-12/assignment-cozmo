"""Materialize the official 2-still walk-in floor from a full photo job."""

from __future__ import annotations

import shutil
from pathlib import Path

from cozmo_floorplan.config import MANIFEST_FILENAME
from cozmo_floorplan.recon.photos_config import (
    DEFAULT_PHOTO_INGEST,
    PHOTO_EXTENSIONS,
)


def materialize_two_photo_job(source_job: Path, destination_job: Path) -> Path | None:
    """Copy the photo job with at most two stills per room.

    Returns the destination when every discovered room has enough images to
    exercise the official 2–8 floor. Returns None when the source is not a
    photo job or a room would fall below two stills.
    """

    photos_dir = source_job / "photos"
    manifest = source_job / MANIFEST_FILENAME
    if not photos_dir.is_dir() or not manifest.is_file():
        return None

    rooms: list[tuple[Path, list[Path]]] = []
    for room_dir in sorted(photos_dir.iterdir(), key=lambda path: path.name.lower()):
        if not room_dir.is_dir() or room_dir.name.startswith("."):
            continue
        images = sorted(
            (
                path
                for path in room_dir.iterdir()
                if path.is_file() and path.suffix.lower() in PHOTO_EXTENSIONS
            ),
            key=lambda path: path.name.lower(),
        )
        if len(images) < DEFAULT_PHOTO_INGEST.min_photos_per_room:
            return None
        rooms.append((room_dir, images[: DEFAULT_PHOTO_INGEST.min_photos_per_room]))
    if not rooms:
        return None

    if destination_job.exists():
        shutil.rmtree(destination_job)
    dest_photos = destination_job / "photos"
    dest_photos.mkdir(parents=True)
    shutil.copy2(manifest, destination_job / MANIFEST_FILENAME)
    for room_dir, images in rooms:
        dest_room = dest_photos / room_dir.name
        dest_room.mkdir()
        for image in images:
            shutil.copy2(image, dest_room / image.name)
    return destination_job
