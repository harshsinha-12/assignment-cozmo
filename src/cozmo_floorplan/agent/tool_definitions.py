"""OpenAI-compatible strict function schemas for FloorPlan claims tools."""

from typing import Any

from cozmo_floorplan.agent.config import ALLOWED_DAMAGE_CLASSES, CLAIMS_POLICIES


def tool_definitions() -> list[dict[str, Any]]:
    """Return fresh tool schemas so callers cannot mutate shared constants."""

    actions = sorted({str(policy["scope_action"]) for policy in CLAIMS_POLICIES.values()})
    return [
        _tool("get_plan", "Read plan geometry and measured quantities.", {}, []),
        _tool(
            "get_surface",
            "Read one surface and its tool-owned measurements.",
            {
                "kind": {"type": "string", "enum": ["room", "wall", "opening", "floor", "ceiling"]},
                "id": {"type": "string"},
            },
            ["kind", "id"],
        ),
        _tool(
            "list_frames",
            "List local evidence references associated with damage observations.",
            {"room_id": {"type": ["string", "null"]}},
            ["room_id"],
        ),
        _tool(
            "classify_damage",
            "Read one pre-mapped metric observation before selecting its visual damage class.",
            {"observation_id": {"type": "string"}},
            ["observation_id"],
        ),
        _tool(
            "apply_damage",
            "Apply a visual class to an observation. Extent and region are copied from the metric observation, never supplied by the model.",
            {
                "observation_id": {"type": "string"},
                "damage_class": {"type": "string", "enum": list(ALLOWED_DAMAGE_CLASSES)},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            ["observation_id", "damage_class", "confidence"],
        ),
        _tool(
            "fire_concealed_rule",
            "Apply the configured concealed-damage rule for an already-applied damage region.",
            {
                "damage_id": {"type": "string"},
                "rule_id": {
                    "type": "string",
                    "enum": sorted(
                        str(policy["concealed_rule_id"])
                        for policy in CLAIMS_POLICIES.values()
                        if policy["concealed_rule_id"] is not None
                    ),
                },
            },
            ["damage_id", "rule_id"],
        ),
        _tool(
            "add_scope_line",
            "Add a permitted action whose quantity is copied from the damage extent.",
            {
                "damage_id": {"type": "string"},
                "action": {"type": "string", "enum": actions},
            },
            ["damage_id", "action"],
        ),
    ]


def _tool(
    name: str,
    description: str,
    properties: dict[str, Any],
    required: list[str],
) -> dict[str, Any]:
    return {
        "type": "function",
        "name": name,
        "description": description,
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }
