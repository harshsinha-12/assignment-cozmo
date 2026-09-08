"""Path discovery helpers for repository-local runtime assets."""

import os
from pathlib import Path

from cozmo_floorplan.config import SCHEMA_ENV_VAR
from cozmo_floorplan.errors import SchemaLocationError

SCHEMA_RELATIVE_PATH = Path("docs/schemas/floorplan.schema.json")


def find_repository_root(start: Path | None = None) -> Path:
    """Find the nearest parent containing the canonical schema."""

    candidate = (start or Path(__file__)).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if (directory / SCHEMA_RELATIVE_PATH).is_file():
            return directory

    raise SchemaLocationError(
        f"Could not find {SCHEMA_RELATIVE_PATH}; set {SCHEMA_ENV_VAR} to its path."
    )


def resolve_schema_path() -> Path:
    """Resolve the schema from an override or the current repository."""

    override = os.environ.get(SCHEMA_ENV_VAR)
    if override:
        path = Path(override).resolve()
        if not path.is_file():
            raise SchemaLocationError(f"{SCHEMA_ENV_VAR} does not point to a file: {path}")
        return path

    return find_repository_root() / SCHEMA_RELATIVE_PATH
