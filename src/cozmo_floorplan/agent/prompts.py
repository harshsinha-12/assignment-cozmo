"""Versioned instructions and context assembly for the claims agent."""

import json
from typing import Any

from cozmo_floorplan.agent.config import CLAIMS_POLICIES
from cozmo_floorplan.agent.models import DamageObservation

AGENT_PROMPT_VERSION = "claims-agent-v1"

SYSTEM_INSTRUCTIONS = """You are the claims-enrichment stage of a floor-plan pipeline.
Use only the supplied function tools. Never state, calculate, estimate, or copy a centimetre quantity yourself.
For every observation: call classify_damage, choose the most defensible allowed class from the visual evidence,
then call apply_damage. Use the returned policy to call fire_concealed_rule when a rule applies and add_scope_line
with exactly the allowed action. Tools validate surfaces, own metric extents, and write the output document.
Do not create cause-of-loss findings, moisture readings, depreciation, or estimating-system item codes.
Finish only after every observation has one damage region and one scope line.
"""


def build_agent_context(document: dict[str, Any], observations: tuple[DamageObservation, ...]) -> str:
    """Serialize non-secret plan and observation context for the model."""

    payload = {
        "prompt_version": AGENT_PROMPT_VERSION,
        "job": {
            "floor_id": document.get("floor_id"),
            "tier": document.get("provenance", {}).get("tier"),
            "room_ids": [room["id"] for room in document.get("rooms", [])],
            "wall_ids": [wall["id"] for wall in document.get("walls", [])],
            "opening_ids": [opening["id"] for opening in document.get("openings", [])],
        },
        "observations": [
            {
                "id": observation.identifier,
                "surface": observation.surface,
                "evidence_refs": list(observation.evidence_refs),
                "allowed_classes": list(CLAIMS_POLICIES),
            }
            for observation in observations
        ],
    }
    return json.dumps(payload, sort_keys=True)
