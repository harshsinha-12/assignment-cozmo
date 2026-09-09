"""Semantic readiness checks for benchmark truth and claims evidence."""

from __future__ import annotations

from pathlib import Path

from cozmo_floorplan.agent.observations import load_damage_observations
from cozmo_floorplan.errors import AgentError, CozmoFloorPlanError
from cozmo_floorplan.eval.io import load_floorplan


def floorplan_evidence_ready(
    path: Path, *, minimum_rooms: int = 0
) -> tuple[bool, str]:
    """Validate a FloorPlan evidence file and its minimum room coverage."""

    if not path.is_file():
        return False, f"missing {path.name}"
    try:
        document = load_floorplan(path)
    except CozmoFloorPlanError as exc:
        return False, str(exc)
    room_count = len(document.get("rooms", []))
    if room_count < minimum_rooms:
        return False, f"contains {room_count} room(s); at least {minimum_rooms} required"
    return True, ""


def find_damage_evidence(job_paths: list[Path]) -> tuple[Path | None, str]:
    """Find two-class staged damage evidence with resolvable local image refs."""

    problems: list[str] = []
    for job_path in job_paths:
        observation_path = job_path / "damage_observations.json"
        if not observation_path.is_file():
            continue
        try:
            observations = load_damage_observations(job_path)
        except AgentError as exc:
            problems.append(f"{job_path.name}: {exc}")
            continue
        classes = {item.fallback_class for item in observations}
        if len(classes) < 2:
            problems.append(f"{job_path.name}: fewer than two damage classes")
            continue
        missing_refs = sorted(
            {
                ref
                for item in observations
                for ref in item.evidence_refs
                if not (job_path / ref).is_file()
            }
        )
        if missing_refs:
            problems.append(
                f"{job_path.name}: missing evidence refs {', '.join(missing_refs)}"
            )
            continue
        return observation_path, ""
    return None, "; ".join(problems) or "no damage_observations.json found"
