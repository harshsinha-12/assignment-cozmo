"""Load and validate the public job-directory contract."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from cozmo_floorplan.config import (
    AGENT_OBSERVATIONS_FILENAME,
    MANIFEST_FILENAME,
    SUPPORTED_TIERS,
    TIER_INPUT_DIRECTORIES,
)
from cozmo_floorplan.errors import JobLoadError


@dataclass(frozen=True, slots=True)
class Job:
    """Normalized metadata needed by downstream reconstruction adapters."""

    root: Path
    job_id: str
    tier: str
    device: str | None
    manifest: dict[str, Any]
    input_refs: tuple[str, ...]


def load_job(job_dir: str | Path) -> Job:
    """Load a job folder and return a normalized immutable description."""

    root = Path(job_dir).resolve()
    if not root.is_dir():
        raise JobLoadError(f"Job directory does not exist: {root}")

    manifest_path = root / MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise JobLoadError(f"Missing required manifest: {manifest_path}")

    manifest = _read_manifest(manifest_path)
    job_id = _required_string(manifest, "job_id")
    tier = _required_string(manifest, "tier").lower()
    if tier not in SUPPORTED_TIERS:
        choices = ", ".join(sorted(SUPPORTED_TIERS))
        raise JobLoadError(
            f"Unsupported manifest tier {tier!r}; expected one of: {choices}",
            warning_code="unsupported_tier",
        )

    expected_input_dir = TIER_INPUT_DIRECTORIES.get(tier)
    if expected_input_dir and not (root / expected_input_dir).is_dir():
        raise JobLoadError(
            f"Tier {tier!r} requires a {expected_input_dir}/ directory in {root}"
        )

    device_value = manifest.get("device")
    device = str(device_value) if device_value is not None else None
    return Job(
        root=root,
        job_id=job_id,
        tier=tier,
        device=device,
        manifest=manifest,
        input_refs=_collect_input_refs(root, expected_input_dir),
    )


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise JobLoadError(f"Could not read manifest {path}: {exc}") from exc

    if not isinstance(value, dict):
        raise JobLoadError(f"Manifest must contain a YAML mapping: {path}")
    return value


def _required_string(manifest: dict[str, Any], key: str) -> str:
    value = manifest.get(key)
    if not isinstance(value, str) or not value.strip():
        raise JobLoadError(f"Manifest field {key!r} must be a non-empty string")
    return value.strip()


def _collect_input_refs(root: Path, input_dir_name: str | None) -> tuple[str, ...]:
    refs = [MANIFEST_FILENAME]
    if (root / AGENT_OBSERVATIONS_FILENAME).is_file():
        refs.append(AGENT_OBSERVATIONS_FILENAME)
    if input_dir_name:
        input_dir = root / input_dir_name
        refs.extend(
            path.relative_to(root).as_posix()
            for path in sorted(input_dir.rglob("*"))
            if path.is_file()
        )
    return tuple(refs)
