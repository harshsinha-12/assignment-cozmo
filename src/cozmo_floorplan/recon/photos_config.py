"""Immutable limits for photo-folder ingest."""

from dataclasses import dataclass


PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


@dataclass(frozen=True, slots=True)
class PhotoIngestConfig:
    min_photos_per_room: int = 2
    max_photos_per_room: int = 8
    min_edge_px: int = 64


DEFAULT_PHOTO_INGEST = PhotoIngestConfig()
