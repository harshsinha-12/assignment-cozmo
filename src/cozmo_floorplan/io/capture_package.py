"""Inspect and extract Cozmo Capture job ZIPs into the CLI job-folder contract."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import yaml

from cozmo_floorplan.config import MANIFEST_FILENAME, SUPPORTED_TIERS, TIER_INPUT_DIRECTORIES
from cozmo_floorplan.errors import JobLoadError
from cozmo_floorplan.recon.photos_config import PHOTO_EXTENSIONS
from cozmo_floorplan.recon.video_config import VIDEO_EXTENSIONS

LIDAR_DIRECTORY = TIER_INPUT_DIRECTORIES["lidar"]
PHOTO_DIRECTORY = TIER_INPUT_DIRECTORIES["photos"]
VIDEO_DIRECTORY = TIER_INPUT_DIRECTORIES["video"]
ROOMPLAN_MEMBER = f"{LIDAR_DIRECTORY}/roomplan.json"
_SKIP_PREFIXES = ("__MACOSX/",)
_SKIP_NAMES = {".DS_Store"}
_JOB_ROOT_NAMES = frozenset(
    {MANIFEST_FILENAME, *TIER_INPUT_DIRECTORIES.values()}
)
_PHOTO_SUFFIXES = frozenset(PHOTO_EXTENSIONS)
_VIDEO_SUFFIXES = frozenset(VIDEO_EXTENSIONS)


def inspect_capture_zip(path: str | Path) -> tuple[str, ...]:
    """Return logical member paths after stripping a single wrapper folder."""

    archive_path = Path(path)
    try:
        with ZipFile(archive_path) as archive:
            kept = _kept_members(archive.namelist())
    except (OSError, BadZipFile) as exc:
        raise JobLoadError(f"Capture ZIP could not be read: {archive_path}") from exc
    prefix = _wrapper_prefix(kept)
    return tuple(sorted(name[len(prefix) :] for name in kept if name[len(prefix) :]))


def validate_capture_zip(path: str | Path) -> None:
    """Reject incomplete Cozmo Capture archives before extraction."""

    archive_path = Path(path)
    members = set(inspect_capture_zip(archive_path))
    if MANIFEST_FILENAME not in members:
        raise JobLoadError(f"Capture ZIP is missing {MANIFEST_FILENAME}: {archive_path}")

    with ZipFile(archive_path) as archive:
        mapping = _logical_index(archive)
        manifest = _load_manifest(archive.read(mapping[MANIFEST_FILENAME]), archive_path)
        job_id = manifest.get("job_id")
        if not isinstance(job_id, str) or not job_id.strip():
            raise JobLoadError(
                f"Capture ZIP manifest job_id must be a non-empty string: {archive_path}"
            )
        tier = str(manifest.get("tier", "")).strip().lower()
        if tier not in SUPPORTED_TIERS:
            choices = ", ".join(sorted(SUPPORTED_TIERS))
            raise JobLoadError(
                f"Capture ZIP manifest tier must be one of {choices}, not {tier!r}: {archive_path}",
                warning_code="unsupported_tier",
            )
        if tier == "lidar":
            _validate_lidar_members(archive, mapping, members, archive_path)
        elif tier == "photos":
            _validate_photo_members(members, archive_path)
        elif tier == "video":
            _validate_video_members(members, archive_path)
        else:
            raise JobLoadError(
                f"Capture ZIP tier {tier!r} is not a Cozmo Capture export: {archive_path}",
                warning_code="unsupported_tier",
            )


def open_job_directory(path: str | Path, unpack_root: str | Path | None = None) -> Path:
    """Return a job folder, extracting a Cozmo Capture ZIP when needed."""

    source = Path(path)
    if source.is_file() and source.suffix.lower() == ".zip":
        if unpack_root is None:
            raise JobLoadError(f"Capture ZIP extract destination is required: {source}")
        return extract_capture_zip(source, unpack_root)
    if source.is_file():
        raise JobLoadError(f"Job path must be a directory or .zip: {source}")
    return source


def extract_capture_zip(path: str | Path, destination: str | Path) -> Path:
    """Extract a valid capture ZIP into a job folder and return that folder."""

    archive_path = Path(path)
    validate_capture_zip(archive_path)
    job_root = Path(destination)
    job_root.mkdir(parents=True, exist_ok=True)
    root_resolved = job_root.resolve()

    with ZipFile(archive_path) as archive:
        for logical, member in _logical_index(archive).items():
            target = (job_root / logical).resolve()
            if not target.is_relative_to(root_resolved):
                raise JobLoadError(f"Capture ZIP member escapes destination: {member}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(member))
    return job_root


def _validate_lidar_members(
    archive: ZipFile,
    mapping: dict[str, str],
    members: set[str],
    archive_path: Path,
) -> None:
    if ROOMPLAN_MEMBER not in members:
        raise JobLoadError(f"Capture ZIP is missing {ROOMPLAN_MEMBER}: {archive_path}")
    try:
        plan = json.loads(archive.read(mapping[ROOMPLAN_MEMBER]).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise JobLoadError(
            f"Capture ZIP {ROOMPLAN_MEMBER} is not valid JSON: {archive_path}"
        ) from exc
    rooms = plan.get("rooms") if isinstance(plan, dict) else None
    if not isinstance(rooms, list) or not rooms:
        raise JobLoadError(f"Capture ZIP {ROOMPLAN_MEMBER} has no rooms: {archive_path}")


def _validate_photo_members(members: set[str], archive_path: Path) -> None:
    counts: dict[str, int] = {}
    for member in members:
        path = Path(member)
        if path.parts[:1] != (PHOTO_DIRECTORY,) or len(path.parts) < 3:
            continue
        if path.suffix.lower() not in _PHOTO_SUFFIXES:
            continue
        counts[path.parts[1]] = counts.get(path.parts[1], 0) + 1
    if not counts:
        raise JobLoadError(
            f"Capture ZIP is missing {PHOTO_DIRECTORY}/<room> images: {archive_path}"
        )
    for room, count in sorted(counts.items()):
        if not 2 <= count <= 8:
            raise JobLoadError(
                f"Capture ZIP photo room {room!r} has {count} images; need 2 to 8: {archive_path}"
            )


def _validate_video_members(members: set[str], archive_path: Path) -> None:
    videos = [
        member
        for member in members
        if Path(member).parts[:1] == (VIDEO_DIRECTORY,)
        and Path(member).suffix.lower() in _VIDEO_SUFFIXES
    ]
    if not videos:
        raise JobLoadError(f"Capture ZIP is missing {VIDEO_DIRECTORY} walkthroughs: {archive_path}")


def _kept_members(names: list[str]) -> list[str]:
    kept: list[str] = []
    for name in names:
        if name.endswith("/") or name in _SKIP_NAMES:
            continue
        if any(name.startswith(prefix) for prefix in _SKIP_PREFIXES):
            continue
        leaf = name.rsplit("/", 1)[-1]
        if leaf in _SKIP_NAMES:
            continue
        kept.append(name)
    return kept


def _wrapper_prefix(names: list[str]) -> str:
    if not names:
        return ""
    firsts = {name.split("/", 1)[0] for name in names}
    if len(firsts) != 1:
        return ""
    root = next(iter(firsts))
    if root in _JOB_ROOT_NAMES:
        return ""
    if not all(name.startswith(f"{root}/") for name in names):
        return ""
    return f"{root}/"


def _logical_index(archive: ZipFile) -> dict[str, str]:
    kept = _kept_members(archive.namelist())
    prefix = _wrapper_prefix(kept)
    return {name[len(prefix) :]: name for name in kept}


def _load_manifest(payload: bytes, archive_path: Path) -> dict:
    try:
        value = yaml.safe_load(payload.decode("utf-8"))
    except (UnicodeError, yaml.YAMLError) as exc:
        raise JobLoadError(f"Capture ZIP manifest is not valid YAML: {archive_path}") from exc
    if not isinstance(value, dict):
        raise JobLoadError(f"Capture ZIP manifest must contain a YAML mapping: {archive_path}")
    return value
