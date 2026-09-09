"""Load the path-only walk-in manifest without escaping its capture root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from cozmo_floorplan.walkin.config import (
    DEFAULT_FORBIDDEN_ROOM_IDS,
    DEFAULT_JOB_PATHS,
    DEFAULT_ROOM_ID,
    DEFAULT_TRUTH_PATH,
    PLACEHOLDER_PREFIX,
    TIERS,
    WALKIN_MANIFEST_NAME,
    WALKIN_SCHEMA_VERSION,
)


@dataclass(frozen=True, slots=True)
class WalkinManifest:
    """Resolved walk-in inputs rooted beneath one private capture directory."""

    root: Path
    walkin_id: str
    room_id: str
    forbidden_room_ids: tuple[str, ...]
    manifest_path: Path
    manifest_present: bool
    jobs: dict[str, Path]
    truth: Path


def load_walkin_manifest(capture_root: str | Path) -> WalkinManifest:
    """Load walkin.yaml, or use documented paths while marking it pending."""

    root = Path(capture_root).resolve()
    manifest_path = root / WALKIN_MANIFEST_NAME
    if manifest_path.is_file():
        try:
            document = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise ValueError(f"Could not read {manifest_path}: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError("walkin.yaml must contain a YAML mapping")
        if document.get("schema_version") != WALKIN_SCHEMA_VERSION:
            raise ValueError(
                f"walkin.yaml requires schema_version={WALKIN_SCHEMA_VERSION!r}"
            )
        walkin_id = _nonempty(document.get("walkin_id"), "walkin_id")
        room_id = _nonempty(document.get("room_id"), "room_id")
        raw_jobs = document.get("jobs")
        if not isinstance(raw_jobs, dict):
            raise ValueError("walkin.yaml requires a jobs mapping")
        jobs = {
            tier: _resolve_beneath(root, _nonempty(raw_jobs.get(tier), f"jobs.{tier}"))
            for tier in TIERS
        }
        truth = _resolve_beneath(
            root, _nonempty(document.get("ground_truth"), "ground_truth")
        )
        forbidden = _forbidden_ids(document.get("forbidden_room_ids"))
        present = True
    else:
        walkin_id = root.name or "walkin"
        room_id = DEFAULT_ROOM_ID
        jobs = {
            tier: _resolve_beneath(root, relative)
            for tier, relative in DEFAULT_JOB_PATHS.items()
        }
        truth = _resolve_beneath(root, DEFAULT_TRUTH_PATH)
        forbidden = tuple(DEFAULT_FORBIDDEN_ROOM_IDS)
        present = False
    return WalkinManifest(
        root=root,
        walkin_id=walkin_id,
        room_id=room_id,
        forbidden_room_ids=forbidden,
        manifest_path=manifest_path,
        manifest_present=present,
        jobs=jobs,
        truth=truth,
    )


def is_placeholder(value: str) -> bool:
    """Return True when a manifest string is still a template token."""

    return value.strip().lower().startswith(PLACEHOLDER_PREFIX)


def _forbidden_ids(raw: object) -> tuple[str, ...]:
    extras: list[str] = []
    if raw is not None:
        if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
            raise ValueError("walkin.yaml forbidden_room_ids must be a list of strings")
        extras = [_nonempty(item, "forbidden_room_ids[]") for item in raw]
    merged = list(DEFAULT_FORBIDDEN_ROOM_IDS)
    for item in extras:
        if item not in merged:
            merged.append(item)
    return tuple(merged)


def _resolve_beneath(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Walk-in path escapes capture root: {relative}") from exc
    return candidate


def _nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"walkin.yaml field {label!r} must be a non-empty string")
    return value.strip()
