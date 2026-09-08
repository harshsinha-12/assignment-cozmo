"""Typed internal records shared by live and fallback agents."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DamageObservation:
    """Metric damage proposal produced before the language-model layer."""

    identifier: str
    surface: dict[str, str]
    extent: dict[str, Any]
    evidence_refs: tuple[str, ...]
    fallback_class: str
    confidence: float
    region: tuple[tuple[float, float], ...] | None = None


@dataclass(frozen=True, slots=True)
class AgentRun:
    """Result and audit metadata from one enrichment path."""

    document: dict[str, Any]
    mode: str
    provider: str
    model: str | None
    tool_calls: int
