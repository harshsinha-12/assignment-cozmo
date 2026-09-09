"""Status semantics for auditable claims-agent fallback paths."""

from typing import Any


def record_fallback(
    document: dict[str, Any],
    message: str,
    *,
    degrade_status: bool,
) -> dict[str, Any]:
    """Record fallback use and optionally mark an otherwise healthy run partial.

    Explicit deterministic mode is a supported execution path, so successful
    completion keeps the reconstruction status. Automatic fallback represents
    missing configuration or provider failure and remains degraded.
    """

    warnings = document.setdefault("warnings", [])
    if not any(item.get("code") == "agent_fallback" for item in warnings):
        warnings.append({"code": "agent_fallback", "message": message})
    if degrade_status and document.get("status") == "ok":
        document["status"] = "partial"
    return document
