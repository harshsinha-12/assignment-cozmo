"""Deterministic serializable models for gate results."""

from dataclasses import dataclass, field
from typing import Any, Literal

from cozmo_floorplan.config import EVAL_REPORT_VERSION

GateStatus = Literal["pass", "fail", "missing_evidence", "not_applicable"]


@dataclass(frozen=True, slots=True)
class GateResult:
    """One scored or explicitly non-applicable evaluation gate."""

    name: str
    status: GateStatus
    threshold: str
    metrics: dict[str, Any] = field(default_factory=dict)
    detail: str = ""

    @property
    def passed(self) -> bool | None:
        if self.status == "not_applicable":
            return None
        return self.status == "pass"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "passed": self.passed,
            "threshold": self.threshold,
            "metrics": self.metrics,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Complete deterministic evaluation artifact."""

    tier: str
    prediction_status: str
    gates: tuple[GateResult, ...]
    summary: dict[str, Any]

    @property
    def passed(self) -> bool:
        applicable = [gate for gate in self.gates if gate.status != "not_applicable"]
        return bool(applicable) and all(gate.status == "pass" for gate in applicable)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": EVAL_REPORT_VERSION,
            "tier": self.tier,
            "prediction_status": self.prediction_status,
            "passed": self.passed,
            "summary": self.summary,
            "gates": [gate.to_dict() for gate in self.gates],
        }
