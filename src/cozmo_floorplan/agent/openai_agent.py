"""OpenAI Responses API function-calling loop for claims decisions."""

import json
from typing import Any, Callable
from urllib import error, request

from cozmo_floorplan.agent.config import AgentConfig
from cozmo_floorplan.agent.images import image_inputs
from cozmo_floorplan.agent.models import AgentRun, DamageObservation
from cozmo_floorplan.agent.prompts import SYSTEM_INSTRUCTIONS, build_agent_context
from cozmo_floorplan.agent.tool_definitions import tool_definitions
from cozmo_floorplan.agent.tools import FloorPlanTools
from cozmo_floorplan.errors import AgentError
from cozmo_floorplan.io.job import Job

ResponseTransport = Callable[[dict[str, Any]], dict[str, Any]]


class OpenAIResponsesAgent:
    """Run strict local tools selected by a public OpenAI vision model."""

    def __init__(self, config: AgentConfig, transport: ResponseTransport | None = None) -> None:
        if not config.api_key:
            raise AgentError("OpenAI live mode requires OPENAI_API_KEY")
        self.config = config
        self.transport = transport or self._send

    def run(
        self,
        job: Job,
        document: dict[str, Any],
        observations: tuple[DamageObservation, ...],
    ) -> AgentRun:
        tools = FloorPlanTools(job, document, observations)
        content: list[dict[str, Any]] = [
            {"type": "input_text", "text": build_agent_context(document, observations)},
            *image_inputs(job.root, observations),
        ]
        conversation: list[dict[str, Any]] = [{"role": "user", "content": content}]
        payload: dict[str, Any] = {
            "model": self.config.model,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": conversation,
            "tools": tool_definitions(),
            "tool_choice": "required",
            "parallel_tool_calls": False,
            "store": False,
        }
        for _ in range(self.config.max_tool_rounds):
            response = self.transport(payload)
            calls = _function_calls(response)
            if not calls:
                break
            outputs = []
            for call in calls:
                result = _execute_call(tools, call)
                outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call["call_id"],
                        "output": json.dumps(result, sort_keys=True),
                    }
                )
            conversation.extend(calls)
            conversation.extend(outputs)
            payload = {
                "model": self.config.model,
                "instructions": SYSTEM_INSTRUCTIONS,
                "input": conversation,
                "tools": tool_definitions(),
                "tool_choice": "required" if not tools.is_complete() else "auto",
                "parallel_tool_calls": False,
                "store": False,
            }
            if tools.is_complete():
                return AgentRun(
                    document=document,
                    mode="live",
                    provider="openai-responses",
                    model=self.config.model,
                    tool_calls=len(tools.call_log),
                )
        raise AgentError("OpenAI agent stopped before every observation produced damage and scope")

    def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        api_request = request.Request(
            f"{self.config.base_url}/responses",
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(api_request, timeout=self.config.timeout_seconds) as response:
                value = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise AgentError(f"OpenAI Responses API request failed: {_http_error_message(exc)}") from exc
        except (error.URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise AgentError(f"OpenAI Responses API request failed: {exc}") from exc
        if not isinstance(value, dict):
            raise AgentError("OpenAI Responses API returned a non-object response")
        if value.get("error"):
            raise AgentError("OpenAI Responses API returned an error response")
        return value


def _function_calls(response: dict[str, Any]) -> list[dict[str, str]]:
    output = response.get("output")
    if not isinstance(output, list):
        raise AgentError("OpenAI response output must be an array")
    calls: list[dict[str, str]] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "function_call":
            continue
        name, call_id, arguments = item.get("name"), item.get("call_id"), item.get("arguments")
        if not all(isinstance(value, str) and value for value in (name, call_id, arguments)):
            raise AgentError("OpenAI function call is missing name, call_id, or arguments")
        calls.append(
            {
                "type": "function_call",
                "name": name,
                "call_id": call_id,
                "arguments": arguments,
            }
        )
    return calls


def _execute_call(tools: FloorPlanTools, call: dict[str, str]) -> dict[str, Any]:
    try:
        arguments = json.loads(call["arguments"])
        if not isinstance(arguments, dict):
            raise ValueError("arguments must decode to an object")
        return {"ok": True, "result": tools.execute(call["name"], arguments)}
    except (AgentError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def _http_error_message(exc: error.HTTPError) -> str:
    """Extract the provider's public error message without logging request headers."""

    try:
        payload = json.loads(exc.read().decode("utf-8"))
        message = payload.get("error", {}).get("message")
    except (AttributeError, UnicodeError, json.JSONDecodeError):
        message = None
    return str(message) if message else f"HTTP {exc.code}"
