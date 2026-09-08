"""Persist validated JSON artifacts atomically."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from cozmo_floorplan.config import OUTPUT_FILENAME
from cozmo_floorplan.schema import validate_floorplan


def write_floorplan(document: dict[str, Any], out_dir: str | Path) -> Path:
    """Validate and atomically write ``floorplan.json``."""

    validate_floorplan(document)
    return write_json_atomic(document, Path(out_dir) / OUTPUT_FILENAME)


def write_json_atomic(document: dict[str, Any], destination: Path) -> Path:
    """Write JSON without exposing a partially-written artifact."""

    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, indent=2, sort_keys=True) + "\n"

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(payload)
            temporary_path = Path(handle.name)
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return destination
