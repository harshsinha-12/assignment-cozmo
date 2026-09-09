import copy
import json
from pathlib import Path

import pytest

from cozmo_floorplan.agent.config import AgentConfig
from cozmo_floorplan.agent.observations import load_damage_observations
from cozmo_floorplan.agent.openai_agent import OpenAIResponsesAgent
from cozmo_floorplan.agent.orchestrator import enrich_floorplan
from cozmo_floorplan.agent.tools import FloorPlanTools
from cozmo_floorplan.errors import AgentError
from cozmo_floorplan.io.job import load_job
from cozmo_floorplan.recon.lidar import reconstruct_lidar
from cozmo_floorplan.schema import validate_floorplan

ROOT = Path(__file__).resolve().parents[1]
JOB_DIR = ROOT / "data" / "fixtures" / "roomplan_two_room"


def _inputs():
    job = load_job(JOB_DIR)
    document = reconstruct_lidar(job)
    observations = load_damage_observations(job.root)
    return job, document, observations


def test_fallback_uses_tools_and_copies_metric_extent(monkeypatch):
    job, document, observations = _inputs()
    config = AgentConfig(
        mode="fallback",
        api_key=None,
        model="gpt-5-mini",
        base_url="https://api.openai.com/v1",
    )

    enriched = enrich_floorplan(job, document, config=config)

    validate_floorplan(enriched)
    assert [item["class"] for item in enriched["damage"]] == ["water_stain", "impact_damage"]
    assert enriched["damage"][0]["extent"] == observations[0].extent
    assert enriched["scope"][0]["quantity"] == observations[0].extent
    assert enriched["concealed_flags"][0]["rule_id"] == "CONCEALED_WATER_MIGRATION_001"
    assert enriched["warnings"][-1]["code"] == "agent_fallback"
    assert "provider=deterministic-rules" in enriched["provenance"]["notes"]
    assert enriched["status"] == "ok"


def test_tools_reject_model_supplied_extent_and_unapproved_rule():
    job, document, observations = _inputs()
    tools = FloorPlanTools(job, document, observations)

    with pytest.raises(AgentError, match="Expected arguments"):
        tools.execute(
            "apply_damage",
            {
                "observation_id": observations[0].identifier,
                "damage_class": "water_stain",
                "confidence": 0.9,
                "extent": {"value": 999999, "unit": "cm2"},
            },
        )

    result = tools.execute(
        "apply_damage",
        {
            "observation_id": observations[0].identifier,
            "damage_class": "water_stain",
            "confidence": 0.9,
        },
    )
    with pytest.raises(AgentError, match="not allowed"):
        tools.execute(
            "fire_concealed_rule",
            {"damage_id": result["damage"]["id"], "rule_id": "MADE_UP_RULE"},
        )


def test_live_agent_executes_scripted_openai_function_calls():
    job, document, observations = _inputs()
    scripted_calls = [
        ("classify_damage", {"observation_id": "staged-water-stain"}),
        (
            "apply_damage",
            {"observation_id": "staged-water-stain", "damage_class": "water_stain", "confidence": 0.93},
        ),
        (
            "fire_concealed_rule",
            {"damage_id": "damage-staged-water-stain", "rule_id": "CONCEALED_WATER_MIGRATION_001"},
        ),
        (
            "add_scope_line",
            {"damage_id": "damage-staged-water-stain", "action": "remove affected material"},
        ),
        ("classify_damage", {"observation_id": "staged-impact"}),
        (
            "apply_damage",
            {"observation_id": "staged-impact", "damage_class": "impact_damage", "confidence": 0.9},
        ),
        (
            "add_scope_line",
            {"damage_id": "damage-staged-impact", "action": "repair affected material"},
        ),
    ]
    requests = []

    def transport(payload):
        requests.append(copy.deepcopy(payload))
        name, arguments = scripted_calls[len(requests) - 1]
        return {
            "id": f"response-{len(requests)}",
            "output": [
                {
                    "type": "function_call",
                    "call_id": f"call-{len(requests)}",
                    "name": name,
                    "arguments": json.dumps(arguments),
                }
            ],
        }

    config = AgentConfig(
        mode="live",
        api_key="test-key-not-sent",
        model="gpt-5-mini",
        base_url="https://api.openai.com/v1",
    )
    run = OpenAIResponsesAgent(config, transport).run(job, document, observations)

    validate_floorplan(run.document)
    assert run.mode == "live"
    assert run.tool_calls == 7
    assert len(run.document["damage"]) == 2
    assert requests[0]["tool_choice"] == "required"
    assert requests[1]["input"][-1]["type"] == "function_call_output"
    assert "previous_response_id" not in requests[1]
    assert requests[0]["store"] is False


def test_live_failure_rolls_back_then_runs_fallback():
    job, document, _ = _inputs()
    config = AgentConfig(
        mode="live",
        api_key="test-key-not-sent",
        model="gpt-5-mini",
        base_url="https://api.openai.com/v1",
    )

    def failing_transport(payload):
        raise AgentError("simulated provider outage")

    enriched = enrich_floorplan(job, document, config=config, transport=failing_transport)

    assert len(enriched["damage"]) == 2
    assert len({item["id"] for item in enriched["damage"]}) == 2
    assert enriched["warnings"][-1]["code"] == "agent_fallback"
    assert "simulated provider outage" in enriched["warnings"][-1]["message"]
    assert enriched["status"] == "partial"


def test_auto_mode_without_api_key_remains_degraded():
    job, document, _ = _inputs()
    config = AgentConfig(
        mode="auto",
        api_key=None,
        model="gpt-5-mini",
        base_url="https://api.openai.com/v1",
    )

    enriched = enrich_floorplan(job, document, config=config)

    assert enriched["status"] == "partial"
    assert enriched["warnings"][-1]["code"] == "agent_fallback"
