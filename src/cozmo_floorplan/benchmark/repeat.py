"""Validate declared same-room, same-tier benchmark repeat evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from cozmo_floorplan.benchmark.manifest import BenchmarkManifest


@dataclass(frozen=True, slots=True)
class RepeatEvidence:
    """One repeat job whose manifest links it to a primary job and room."""

    tier: str
    path: Path
    room_ids: tuple[str, ...]


def find_repeat_evidence(
    manifest: BenchmarkManifest,
) -> tuple[RepeatEvidence | None, str]:
    """Return the first valid repeat declared for any official capture tier."""

    problems: list[str] = []
    for tier, repeat_path in sorted(manifest.repeats.items()):
        evidence, problem = _validate_repeat(manifest, tier, repeat_path)
        if evidence is not None:
            return evidence, ""
        problems.append(f"{tier}: {problem}")
    if not problems:
        return None, "benchmark.yaml does not declare a repeat job"
    return None, "; ".join(problems)


def _validate_repeat(
    manifest: BenchmarkManifest,
    tier: str,
    repeat_path: Path,
) -> tuple[RepeatEvidence | None, str]:
    repeat_manifest = _read_yaml(repeat_path / "manifest.yaml")
    if repeat_manifest is None:
        return None, "manifest.yaml is missing or invalid"
    primary_manifest = _read_yaml(manifest.jobs[tier] / "manifest.yaml")
    if primary_manifest is None:
        return None, "primary manifest.yaml is missing or invalid"
    if repeat_manifest.get("tier") != tier:
        return None, f"manifest tier must be {tier!r}"
    if primary_manifest.get("tier") != tier:
        return None, f"primary manifest tier must be {tier!r}"
    primary_job_id = primary_manifest.get("job_id")
    if repeat_manifest.get("repeat_of_job_id") != primary_job_id:
        return None, "repeat_of_job_id must match the primary job_id"
    raw_room_ids = repeat_manifest.get("repeat_room_ids")
    if (
        not isinstance(raw_room_ids, list)
        or not raw_room_ids
        or any(not isinstance(item, str) or not item.strip() for item in raw_room_ids)
    ):
        return None, "repeat_room_ids must contain at least one room id"
    room_ids = tuple(dict.fromkeys(item.strip() for item in raw_room_ids))
    return RepeatEvidence(tier=tier, path=repeat_path, room_ids=room_ids), ""


def _read_yaml(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return None
    return value if isinstance(value, dict) else None
