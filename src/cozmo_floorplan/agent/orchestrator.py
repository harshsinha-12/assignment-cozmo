"""Choose a transactional live or fallback claims-enrichment path."""

import copy
from pathlib import Path
from typing import Any

from cozmo_floorplan.agent.config import AgentConfig
from cozmo_floorplan.agent.fallback_agent import run_fallback_agent
from cozmo_floorplan.agent.models import AgentRun
from cozmo_floorplan.agent.observations import load_damage_observations
from cozmo_floorplan.agent.openai_agent import OpenAIResponsesAgent, ResponseTransport
from cozmo_floorplan.agent.status_policy import record_fallback
from cozmo_floorplan.errors import AgentError
from cozmo_floorplan.io.job import Job
from cozmo_floorplan.schema import validate_floorplan
from cozmo_floorplan.utils.env import load_env_file


def enrich_floorplan(
    job: Job,
    document: dict[str, Any],
    *,
    config: AgentConfig | None = None,
    transport: ResponseTransport | None = None,
) -> dict[str, Any]:
    """Enrich a reconstructed plan, rolling back partial provider mutations on failure."""

    if document.get("status") == "failed":
        return document
    try:
        observations = load_damage_observations(job.root)
    except AgentError as exc:
        return record_fallback(
            document,
            f"Claims observations were skipped: {exc}",
            degrade_status=True,
        )
    if not observations:
        return document

    if config is None:
        load_env_file(Path.cwd() / ".env")
        config = AgentConfig.from_environment()

    live_requested = config.mode == "live" or (config.mode == "auto" and config.api_key is not None)
    if live_requested and config.api_key:
        try:
            run = OpenAIResponsesAgent(config, transport).run(job, copy.deepcopy(document), observations)
            return _finalize(run)
        except AgentError as exc:
            fallback = run_fallback_agent(job, copy.deepcopy(document), observations)
            fallback_document = _finalize(fallback)
            return record_fallback(
                fallback_document,
                f"Live claims agent failed; used rules: {exc}",
                degrade_status=True,
            )

    fallback = run_fallback_agent(job, copy.deepcopy(document), observations)
    fallback_document = _finalize(fallback)
    explicit_fallback = config.mode == "fallback"
    reason = (
        "Agent mode requested deterministic fallback"
        if explicit_fallback
        else "No OPENAI_API_KEY; used deterministic claims tools"
    )
    return record_fallback(
        fallback_document,
        reason,
        degrade_status=not explicit_fallback,
    )


def _finalize(run: AgentRun) -> dict[str, Any]:
    notes = run.document["provenance"].get("notes", "").rstrip()
    model = f" model={run.model}" if run.model else ""
    audit = f"Claims agent: mode={run.mode} provider={run.provider}{model} tool_calls={run.tool_calls}."
    run.document["provenance"]["notes"] = f"{notes} {audit}".strip()
    validate_floorplan(run.document)
    return run.document
