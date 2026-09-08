"""Deterministic no-network claims agent using the exact live tool boundary."""

from typing import Any

from cozmo_floorplan.agent.config import CLAIMS_POLICIES
from cozmo_floorplan.agent.models import AgentRun, DamageObservation
from cozmo_floorplan.agent.tools import FloorPlanTools
from cozmo_floorplan.io.job import Job


def run_fallback_agent(
    job: Job,
    document: dict[str, Any],
    observations: tuple[DamageObservation, ...],
) -> AgentRun:
    """Apply observation hints and policy tables through normal validated tools."""

    tools = FloorPlanTools(job, document, observations)
    for observation in observations:
        tools.execute("classify_damage", {"observation_id": observation.identifier})
        damage_result = tools.execute(
            "apply_damage",
            {
                "observation_id": observation.identifier,
                "damage_class": observation.fallback_class,
                "confidence": observation.confidence,
            },
        )
        damage_id = damage_result["damage"]["id"]
        policy = CLAIMS_POLICIES[observation.fallback_class]
        if policy["concealed_rule_id"] is not None:
            tools.execute(
                "fire_concealed_rule",
                {"damage_id": damage_id, "rule_id": policy["concealed_rule_id"]},
            )
        tools.execute(
            "add_scope_line",
            {"damage_id": damage_id, "action": policy["scope_action"]},
        )
    return AgentRun(
        document=document,
        mode="fallback",
        provider="deterministic-rules",
        model=None,
        tool_calls=len(tools.call_log),
    )
