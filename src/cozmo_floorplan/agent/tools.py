"""Validated read/write tools; this is the only claims mutation boundary."""

import copy
from typing import Any, Callable

from cozmo_floorplan.agent.config import ALLOWED_DAMAGE_CLASSES, CLAIMS_POLICIES
from cozmo_floorplan.agent.models import DamageObservation
from cozmo_floorplan.errors import AgentError
from cozmo_floorplan.io.job import Job

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


class FloorPlanTools:
    """Execute strict tool calls against one private FloorPlan working copy."""

    def __init__(
        self,
        job: Job,
        document: dict[str, Any],
        observations: tuple[DamageObservation, ...],
    ) -> None:
        self.job = job
        self.document = document
        self.observations = {item.identifier: item for item in observations}
        self.call_log: list[dict[str, Any]] = []

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatch one known tool and return a JSON-serializable result."""

        handlers: dict[str, ToolHandler] = {
            "get_plan": self._get_plan,
            "get_surface": self._get_surface,
            "list_frames": self._list_frames,
            "classify_damage": self._classify_damage,
            "apply_damage": self._apply_damage,
            "fire_concealed_rule": self._fire_concealed_rule,
            "add_scope_line": self._add_scope_line,
        }
        handler = handlers.get(name)
        if handler is None:
            raise AgentError(f"Unknown agent tool {name!r}")
        try:
            result = handler(arguments)
        except (KeyError, TypeError, ValueError) as exc:
            raise AgentError(f"Invalid arguments for {name}: {exc}") from exc
        self.call_log.append({"name": name, "arguments": copy.deepcopy(arguments)})
        return result

    def is_complete(self) -> bool:
        """Require one damage and scope item for every supplied observation."""

        damage_ids = {item["id"] for item in self.document["damage"]}
        scoped_damage_ids = {
            damage_id
            for line in self.document["scope"]
            for damage_id in line.get("damage_ids", [])
        }
        expected = {self._damage_id(identifier) for identifier in self.observations}
        return expected <= damage_ids and expected <= scoped_damage_ids

    def _get_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, set())
        return copy.deepcopy(
            {
                "rooms": self.document["rooms"],
                "walls": self.document["walls"],
                "openings": self.document["openings"],
                "stitch": self.document.get("stitch"),
            }
        )

    def _get_surface(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, {"kind", "id"})
        return copy.deepcopy(self._surface(str(arguments["kind"]), str(arguments["id"])))

    def _list_frames(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, {"room_id"})
        room_id = arguments["room_id"]
        refs = sorted(
            {
                reference
                for observation in self.observations.values()
                if room_id is None or room_id in self._surface_room_ids(observation)
                for reference in observation.evidence_refs
            }
        )
        return {"evidence_refs": refs}

    def _classify_damage(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, {"observation_id"})
        observation = self._observation(str(arguments["observation_id"]))
        self._surface(observation.surface["kind"], observation.surface["id"])
        return {
            "observation_id": observation.identifier,
            "surface": observation.surface,
            "evidence_refs": list(observation.evidence_refs),
            "allowed_classes": list(ALLOWED_DAMAGE_CLASSES),
            "local_classifier_candidate": observation.fallback_class,
            "local_classifier_confidence": observation.confidence,
            "metric_extent_owned_by_tool": True,
        }

    def _apply_damage(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, {"observation_id", "damage_class", "confidence"})
        observation = self._observation(str(arguments["observation_id"]))
        damage_class = str(arguments["damage_class"])
        confidence = float(arguments["confidence"])
        if damage_class not in ALLOWED_DAMAGE_CLASSES:
            raise AgentError(f"Unsupported damage class {damage_class!r}")
        if not 0 <= confidence <= 1:
            raise AgentError("Damage confidence must be between 0 and 1")
        self._surface(observation.surface["kind"], observation.surface["id"])
        identifier = self._damage_id(observation.identifier)
        if any(item["id"] == identifier for item in self.document["damage"]):
            raise AgentError(f"Damage {identifier!r} already exists")
        damage = {
            "id": identifier,
            "surface": copy.deepcopy(observation.surface),
            "class": damage_class,
            "extent": copy.deepcopy(observation.extent),
            "evidence_refs": list(observation.evidence_refs),
            "confidence": confidence,
        }
        if observation.region is not None:
            damage["region"] = [list(point) for point in observation.region]
        self.document["damage"].append(damage)
        policy = CLAIMS_POLICIES[damage_class]
        return {
            "damage": copy.deepcopy(damage),
            "allowed_concealed_rule_id": policy["concealed_rule_id"],
            "allowed_scope_action": policy["scope_action"],
            "quantity_owned_by_tool": True,
        }

    def _fire_concealed_rule(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, {"damage_id", "rule_id"})
        damage = self._damage(str(arguments["damage_id"]))
        rule_id = str(arguments["rule_id"])
        allowed_rule = CLAIMS_POLICIES[damage["class"]]["concealed_rule_id"]
        if allowed_rule is None or rule_id != allowed_rule:
            raise AgentError(f"Rule {rule_id!r} is not allowed for damage class {damage['class']!r}")
        identifier = f"concealed-{damage['id']}"
        if any(item["id"] == identifier for item in self.document["concealed_flags"]):
            raise AgentError(f"Concealed flag {identifier!r} already exists")
        flag = {
            "id": identifier,
            "surface": copy.deepcopy(damage["surface"]),
            "rule_id": rule_id,
            "status": "suspected",
            "damage_ids": [damage["id"]],
            "evidence_refs": list(damage["evidence_refs"]),
            "notes": "Rule-selected inspection flag; not a confirmed concealed condition.",
        }
        self.document["concealed_flags"].append(flag)
        return {"concealed_flag": copy.deepcopy(flag)}

    def _add_scope_line(self, arguments: dict[str, Any]) -> dict[str, Any]:
        self._expect_keys(arguments, {"damage_id", "action"})
        damage = self._damage(str(arguments["damage_id"]))
        action = str(arguments["action"])
        allowed_action = CLAIMS_POLICIES[damage["class"]]["scope_action"]
        if action != allowed_action:
            raise AgentError(f"Action {action!r} is not allowed for damage class {damage['class']!r}")
        identifier = f"scope-{damage['id']}"
        if any(item["id"] == identifier for item in self.document["scope"]):
            raise AgentError(f"Scope line {identifier!r} already exists")
        flag_ids = [
            item["id"]
            for item in self.document["concealed_flags"]
            if damage["id"] in item.get("damage_ids", [])
        ]
        line = {
            "id": identifier,
            "surface": copy.deepcopy(damage["surface"]),
            "action": action,
            "quantity": copy.deepcopy(damage["extent"]),
            "quantity_source": "damage_extent",
            "damage_ids": [damage["id"]],
            "concealed_flag_ids": flag_ids,
            "notes": "Quantity copied from the metric damage observation by tool execution.",
        }
        self.document["scope"].append(line)
        return {"scope_line": copy.deepcopy(line), "quantity_owned_by_tool": True}

    def _surface(self, kind: str, identifier: str) -> dict[str, Any]:
        collection = {
            "room": "rooms",
            "wall": "walls",
            "opening": "openings",
            "floor": "rooms",
            "ceiling": "rooms",
        }.get(kind)
        if collection is None:
            raise AgentError(f"Unsupported surface kind {kind!r}")
        for item in self.document[collection]:
            if item["id"] == identifier:
                return item
        raise AgentError(f"Surface {kind}:{identifier} does not exist")

    def _observation(self, identifier: str) -> DamageObservation:
        try:
            return self.observations[identifier]
        except KeyError as exc:
            raise AgentError(f"Unknown damage observation {identifier!r}") from exc

    def _surface_room_ids(self, observation: DamageObservation) -> set[str]:
        kind = observation.surface["kind"]
        surface = self._surface(kind, observation.surface["id"])
        if kind in {"room", "floor", "ceiling"}:
            return {surface["id"]}
        return set(surface.get("room_ids", []))

    def _damage(self, identifier: str) -> dict[str, Any]:
        for damage in self.document["damage"]:
            if damage["id"] == identifier:
                return damage
        raise AgentError(f"Unknown damage {identifier!r}")

    @staticmethod
    def _expect_keys(arguments: dict[str, Any], expected: set[str]) -> None:
        if set(arguments) != expected:
            raise AgentError(f"Expected arguments {sorted(expected)}, received {sorted(arguments)}")

    @staticmethod
    def _damage_id(observation_id: str) -> str:
        return f"damage-{observation_id}"
