"""Inspect and extract Cozmo Capture job ZIPs into the CLI job-folder contract."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import yaml

from cozmo_floorplan.config import MANIFEST_FILENAME, TIER_INPUT_DIRECTORIES
from cozmo_floorplan.errors import JobLoadError

LIDAR_DIRECTORY = TIER_INPUT_DIRECTORIES["lidar"]
ROOMPLAN_MEMBER = f"{LIDAR_DIRECTORY}/roomplan.json"
_SKIP_PREFIXES = ("__MACOSX/",)
_SKIP_NAMES = {".DS_Store"}


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
    if ROOMPLAN_MEMBER not in members:
        raise JobLoadError(f"Capture ZIP is missing {ROOMPLAN_MEMBER}: {archive_path}")

    with ZipFile(archive_path) as archive:
        mapping = _logical_index(archive)
        manifest = _load_manifest(archive.read(mapping[MANIFEST_FILENAME]), archive_path)
        job_id = manifest.get("job_id")
        if not isinstance(job_id, str) or not job_id.strip():
            raise JobLoadError(
                f"Capture ZIP manifest job_id must be a non-empty string: {archive_path}"
            )
        tier = str(manifest.get("tier", "")).strip().lower()
        if tier != "lidar":
            raise JobLoadError(
                f"Capture ZIP manifest tier must be 'lidar', not {tier!r}: {archive_path}",
                warning_code="unsupported_tier",
            )
        try:
            plan = json.loads(archive.read(mapping[ROOMPLAN_MEMBER]).decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise JobLoadError(
                f"Capture ZIP {ROOMPLAN_MEMBER} is not valid JSON: {archive_path}"
            ) from exc
        rooms = plan.get("rooms") if isinstance(plan, dict) else None
        if not isinstance(rooms, list) or not rooms:
            raise JobLoadError(f"Capture ZIP {ROOMPLAN_MEMBER} has no rooms: {archive_path}")


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
    if root in {MANIFEST_FILENAME, LIDAR_DIRECTORY}:
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
