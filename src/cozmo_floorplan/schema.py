"""Load and validate documents against the canonical FloorPlan schema."""

import json
from functools import lru_cache
from typing import Any

from jsonschema import Draft202012Validator

from cozmo_floorplan.errors import OutputValidationError
from cozmo_floorplan.utils.paths import resolve_schema_path


@lru_cache(maxsize=1)
def floorplan_validator() -> Draft202012Validator:
    """Load and compile the canonical schema once per process."""

    schema_path = resolve_schema_path()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_floorplan(document: dict[str, Any]) -> None:
    """Raise one concise domain error if output violates the contract."""

    errors = sorted(floorplan_validator().iter_errors(document), key=lambda error: list(error.path))
    if not errors:
        return

    first = errors[0]
    location = ".".join(str(part) for part in first.absolute_path) or "<root>"
    raise OutputValidationError(
        f"FloorPlan output failed schema validation at {location}: {first.message}"
    )
