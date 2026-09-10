"""Identify walk-in rooms and refuse a recapture of the scored benchmark."""

from __future__ import annotations

from pathlib import Path

from cozmo_floorplan.errors import JobLoadError
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.recon.photos_config import PHOTO_EXTENSIONS
from cozmo_floorplan.walkin.manifest import WalkinManifest, is_placeholder


def normalize_room_id(value: str) -> str:
    """Collapse labels so 'My Room' and 'my_room' match 'my-room'."""

    return "-".join(value.strip().lower().replace("_", " ").replace("/", " ").split())


def collect_observed_room_ids(
    manifest: WalkinManifest,
    tiers: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Return unique normalized room ids visible in the walk-in folder."""

    observed: list[str] = []
    if not is_placeholder(manifest.room_id):
        _append_unique(observed, manifest.room_id)
    selected = tiers or tuple(manifest.jobs)
    for tier in selected:
        job_path = manifest.jobs[tier]
        for room_id in _job_room_ids(job_path):
            _append_unique(observed, room_id)
    return tuple(observed)


def forbidden_collisions(
    manifest: WalkinManifest,
    tiers: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Return observed room ids that belong to the existing benchmark."""

    forbidden = {normalize_room_id(item) for item in manifest.forbidden_room_ids}
    return tuple(
        room_id
        for room_id in collect_observed_room_ids(manifest, tiers)
        if room_id in forbidden
    )


def _job_room_ids(job_path: Path) -> tuple[str, ...]:
    rooms: list[str] = []
    manifest_path = job_path / "manifest.yaml"
    if manifest_path.is_file():
        try:
            job = load_job(job_path)
        except JobLoadError:
            job = None
        if job is not None:
            listed = job.manifest.get("rooms")
            if isinstance(listed, list):
                for item in listed:
                    if isinstance(item, str) and item.strip() and not is_placeholder(item):
                        _append_unique(rooms, item)
    photos_dir = job_path / "photos"
    if photos_dir.is_dir():
        for path in sorted(photos_dir.iterdir(), key=lambda item: item.name.lower()):
            if not path.is_dir() or path.name.startswith("."):
                continue
            if any(
                child.is_file() and child.suffix.lower() in PHOTO_EXTENSIONS
                for child in path.iterdir()
            ):
                _append_unique(rooms, path.name)
    return tuple(rooms)


def _append_unique(values: list[str], raw: str) -> None:
    normalized = normalize_room_id(raw)
    if normalized and normalized not in values:
        values.append(normalized)
