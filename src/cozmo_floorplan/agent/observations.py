"""Read metric damage proposals supplied by capture/CV preprocessing."""

import json
from pathlib import Path
from typing import Any

from cozmo_floorplan.agent.config import ALLOWED_DAMAGE_CLASSES
from cozmo_floorplan.agent.models import DamageObservation
from cozmo_floorplan.config import AGENT_OBSERVATIONS_FILENAME
from cozmo_floorplan.errors import AgentError


def load_damage_observations(job_root: Path) -> tuple[DamageObservation, ...]:
    """Load the optional observation contract; an absent file means no claims work."""

    path = job_root / AGENT_OBSERVATIONS_FILENAME
    if not path.is_file():
        return ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AgentError(f"Could not read {AGENT_OBSERVATIONS_FILENAME}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("version") != "1.0":
        raise AgentError(f"{AGENT_OBSERVATIONS_FILENAME} must use version '1.0'")
    raw_observations = payload.get("observations")
    if not isinstance(raw_observations, list):
        raise AgentError(f"{AGENT_OBSERVATIONS_FILENAME} observations must be an array")
    observations = tuple(_parse_observation(item, index) for index, item in enumerate(raw_observations))
    identifiers = [item.identifier for item in observations]
    if len(identifiers) != len(set(identifiers)):
        raise AgentError("Damage observation ids must be unique")
    return observations


def _parse_observation(value: Any, index: int) -> DamageObservation:
    if not isinstance(value, dict):
        raise AgentError(f"Damage observation {index} must be an object")
    identifier = _string(value, "id", index)
    surface = value.get("surface")
    if not isinstance(surface, dict) or surface.get("kind") not in {"room", "wall", "opening", "floor", "ceiling"}:
        raise AgentError(f"Damage observation {identifier!r} has an invalid surface")
    surface_id = surface.get("id")
    if not isinstance(surface_id, str) or not surface_id:
        raise AgentError(f"Damage observation {identifier!r} needs a surface id")
    fallback_class = _string(value, "fallback_class", index)
    if fallback_class not in ALLOWED_DAMAGE_CLASSES:
        raise AgentError(f"Damage observation {identifier!r} has unsupported fallback_class {fallback_class!r}")
    extent = _measurement(value.get("extent"), identifier)
    refs = value.get("evidence_refs")
    if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref for ref in refs):
        raise AgentError(f"Damage observation {identifier!r} needs evidence_refs")
    confidence = value.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        raise AgentError(f"Damage observation {identifier!r} confidence must be between 0 and 1")
    region = _region(value.get("region"), identifier)
    return DamageObservation(
        identifier=identifier,
        surface={"kind": str(surface["kind"]), "id": surface_id},
        extent=extent,
        evidence_refs=tuple(refs),
        fallback_class=fallback_class,
        confidence=float(confidence),
        region=region,
    )


def _measurement(value: Any, identifier: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AgentError(f"Damage observation {identifier!r} needs a metric extent")
    if value.get("unit") not in {"cm", "cm2", "count"}:
        raise AgentError(f"Damage observation {identifier!r} extent must use cm, cm2, or count")
    number = value.get("value")
    interval = value.get("interval")
    if not isinstance(number, (int, float)) or isinstance(number, bool) or number < 0:
        raise AgentError(f"Damage observation {identifier!r} extent value must be non-negative")
    if not isinstance(interval, dict):
        raise AgentError(f"Damage observation {identifier!r} extent needs an interval")
    low, high, confidence = interval.get("low"), interval.get("high"), interval.get("confidence")
    if any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in (low, high, confidence)):
        raise AgentError(f"Damage observation {identifier!r} has an invalid extent interval")
    if low > number or number > high or not 0 < confidence <= 1:
        raise AgentError(f"Damage observation {identifier!r} extent interval does not contain its value")
    return {
        "value": float(number),
        "unit": value["unit"],
        "interval": {"low": float(low), "high": float(high), "confidence": float(confidence)},
        "method": str(value.get("method") or "damage_observation"),
        "evidence_refs": _measurement_refs(value.get("evidence_refs"), identifier),
    }


def _region(value: Any, identifier: str) -> tuple[tuple[float, float], ...] | None:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) < 3:
        raise AgentError(f"Damage observation {identifier!r} region needs at least three points")
    points: list[tuple[float, float]] = []
    for point in value:
        if (
            not isinstance(point, list)
            or len(point) != 2
            or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in point)
        ):
            raise AgentError(f"Damage observation {identifier!r} has an invalid region point")
        points.append((float(point[0]), float(point[1])))
    return tuple(points)


def _measurement_refs(value: Any, identifier: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise AgentError(f"Damage observation {identifier!r} extent evidence_refs must be strings")
    return list(dict.fromkeys(value))


def _string(value: dict[str, Any], key: str, index: int) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise AgentError(f"Damage observation {index} field {key!r} must be a non-empty string")
    return item.strip()
