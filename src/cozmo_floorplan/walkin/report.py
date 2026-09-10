"""Render the walk-in status artifact into a concise operator checklist."""

from __future__ import annotations

from typing import Any


def render_walkin_summary(report: dict[str, Any]) -> str:
    """Return deterministic Markdown alongside walkin-status.json."""

    collisions = report.get("forbidden_collisions") or []
    collision_text = ", ".join(f"`{item}`" for item in collisions) or "none"
    lines = [
        f"# Walk-in rehearsal — {report['walkin_id']}",
        "",
        f"Overall: **{report['status']}**",
        f"Selected tiers: {_join(report.get('selected_tiers'))}",
        f"Declared room: `{report['room_id']}`",
        f"Observed rooms: {_join(report.get('observed_rooms'))}",
        f"Benchmark-room collisions: {collision_text}",
        "",
        "This is a cold holdout. Do not drop drawing-room, my-room, pooja-room, or",
        "connector media here. Follow `docs/capture-route.md`, then run the public",
        "`python -m cozmo_floorplan run` command while taping the room.",
        "",
        "## Required inputs",
        "",
        "| Input | Status | Path | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["inputs"]:
        lines.append(
            f"| {item['id']} | {item['status']} | `{item['path']}` | {item['detail']} |"
        )
    lines.extend(
        [
            "",
            "## Timed tier runs",
            "",
            "| Tier | Status | Pipeline | Geometry ready | Seconds | Output |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for item in report["runs"]:
        elapsed = item.get("elapsed_s")
        elapsed_text = f"{elapsed:.3f}" if isinstance(elapsed, (int, float)) else ""
        lines.append(
            f"| {item['tier']} | {item['status']} | "
            f"{item.get('pipeline_status', 'pending')} | "
            f"{item.get('geometry_ready', False)} | {elapsed_text} | "
            f"`{item.get('output', '')}` |"
        )
    lines.extend(
        [
            "",
            "## Immediate actions",
            "",
            "| Tier | Warning codes | Next action |",
            "| --- | --- | --- |",
        ]
    )
    for item in report["runs"]:
        warnings = ", ".join(item.get("warning_codes", [])) or "none"
        lines.append(
            f"| {item['tier']} | {warnings} | "
            f"{item.get('next_action', item.get('detail', 'Inspect output.'))} |"
        )
    lines.extend(
        [
            "",
            "## Evaluations",
            "",
            "| Tier | Status | Passing | Detail |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in report["evaluations"]:
        lines.append(
            f"| {item['tier']} | {item['status']} | "
            f"{item.get('passed', 'pending')} | {item['detail']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _join(values: object) -> str:
    if not isinstance(values, list) or not values:
        return "none"
    return ", ".join(f"`{item}`" for item in values)
