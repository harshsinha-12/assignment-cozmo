"""Verify frozen fix-loop evidence against its manifest."""

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from cozmo_floorplan.fix_loop.config import MANIFEST_FILENAME, REQUIRED_BEFORE_ARTIFACTS


class FixLoopBundleError(ValueError):
    """A frozen artifact is missing, unsafe, or inconsistent with its manifest."""


def verify_fix_loop_bundle(root: str | Path) -> dict[str, Any]:
    """Validate artifact hashes and the declared failing gate."""

    bundle_root = Path(root).resolve()
    manifest = _read_json(bundle_root / MANIFEST_FILENAME)
    artifacts = manifest.get("before", {}).get("artifacts")
    if not isinstance(artifacts, list):
        raise FixLoopBundleError("Manifest before.artifacts must be an array")

    declared_paths: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise FixLoopBundleError("Every artifact entry must be an object")
        relative = artifact.get("path")
        expected_hash = artifact.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            raise FixLoopBundleError("Every artifact needs string path and sha256 fields")
        path = (bundle_root / relative).resolve()
        if not path.is_relative_to(bundle_root):
            raise FixLoopBundleError(f"Artifact escapes bundle root: {relative}")
        if not path.is_file():
            raise FixLoopBundleError(f"Missing frozen artifact: {relative}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise FixLoopBundleError(f"Checksum mismatch for {relative}")
        declared_paths.add(relative)

    missing = REQUIRED_BEFORE_ARTIFACTS - declared_paths
    if missing:
        raise FixLoopBundleError(f"Manifest omits required artifacts: {sorted(missing)}")

    target = manifest.get("target_gate")
    if not isinstance(target, dict):
        raise FixLoopBundleError("Manifest target_gate must be an object")
    report = _read_json(bundle_root / "before" / "eval.json")
    gate = next(
        (item for item in report.get("gates", []) if item.get("name") == target.get("name")),
        None,
    )
    if gate is None:
        raise FixLoopBundleError("Target gate is absent from before/eval.json")
    if gate.get("status") != target.get("before_status"):
        raise FixLoopBundleError("Target gate status disagrees with the manifest")
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify frozen fix-loop artifacts.")
    parser.add_argument("bundle", type=Path, help="Directory containing manifest.json.")
    args = parser.parse_args(argv)
    try:
        manifest = verify_fix_loop_bundle(args.bundle)
    except FixLoopBundleError as exc:
        print(f"invalid fix-loop bundle: {exc}")
        return 1
    target = manifest["target_gate"]
    print(f"valid fix-loop bundle: {target['name']}={target['before_status']}")
    return 0


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FixLoopBundleError(f"Could not read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FixLoopBundleError(f"Expected a JSON object: {path}")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
