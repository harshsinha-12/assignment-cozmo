"""Load the path-only benchmark manifest without escaping its capture root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from cozmo_floorplan.benchmark.config import (
    BENCHMARK_MANIFEST_NAME,
    BENCHMARK_SCHEMA_VERSION,
    DEFAULT_INCUMBENT_PATH,
    DEFAULT_JOB_PATHS,
    DEFAULT_LIDAR_REPEAT_PATH,
    DEFAULT_TRUTH_PATH,
    TIERS,
)


@dataclass(frozen=True, slots=True)
class BenchmarkManifest:
    """Resolved benchmark inputs rooted beneath one private capture directory."""

    root: Path
    benchmark_id: str
    manifest_path: Path
    manifest_present: bool
    jobs: dict[str, Path]
    truth: Path
    repeats: dict[str, Path]
    incumbent: Path


def load_benchmark_manifest(capture_root: str | Path) -> BenchmarkManifest:
    """Load benchmark.yaml, or use documented paths while marking it pending."""

    root = Path(capture_root).resolve()
    manifest_path = root / BENCHMARK_MANIFEST_NAME
    if manifest_path.is_file():
        try:
            document = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise ValueError(f"Could not read {manifest_path}: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError("benchmark.yaml must contain a YAML mapping")
        if document.get("schema_version") != BENCHMARK_SCHEMA_VERSION:
            raise ValueError(
                f"benchmark.yaml requires schema_version={BENCHMARK_SCHEMA_VERSION!r}"
            )
        benchmark_id = _nonempty(document.get("benchmark_id"), "benchmark_id")
        raw_jobs = document.get("jobs")
        if not isinstance(raw_jobs, dict):
            raise ValueError("benchmark.yaml requires a jobs mapping")
        jobs = {
            tier: _resolve_beneath(root, _nonempty(raw_jobs.get(tier), f"jobs.{tier}"))
            for tier in TIERS
        }
        truth = _resolve_beneath(
            root, _nonempty(document.get("ground_truth"), "ground_truth")
        )
        raw_repeats = document.get("repeats", {})
        if not isinstance(raw_repeats, dict):
            raise ValueError("benchmark.yaml repeats must be a mapping")
        repeats = {
            tier: _resolve_beneath(root, _nonempty(path, f"repeats.{tier}"))
            for tier, path in raw_repeats.items()
            if tier in TIERS
        }
        incumbent = _resolve_beneath(
            root, _nonempty(document.get("incumbent"), "incumbent")
        )
        present = True
    else:
        benchmark_id = root.name or "benchmark"
        jobs = {
            tier: _resolve_beneath(root, relative)
            for tier, relative in DEFAULT_JOB_PATHS.items()
        }
        truth = _resolve_beneath(root, DEFAULT_TRUTH_PATH)
        repeats = {"lidar": _resolve_beneath(root, DEFAULT_LIDAR_REPEAT_PATH)}
        incumbent = _resolve_beneath(root, DEFAULT_INCUMBENT_PATH)
        present = False
    return BenchmarkManifest(
        root=root,
        benchmark_id=benchmark_id,
        manifest_path=manifest_path,
        manifest_present=present,
        jobs=jobs,
        truth=truth,
        repeats=repeats,
        incumbent=incumbent,
    )


def _resolve_beneath(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Benchmark path escapes capture root: {relative}") from exc
    return candidate


def _nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"benchmark.yaml field {label!r} must be a non-empty string")
    return value.strip()
