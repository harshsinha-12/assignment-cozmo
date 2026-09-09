"""Render the benchmark status artifact into a concise human checklist."""

from __future__ import annotations

from typing import Any


def render_benchmark_summary(report: dict[str, Any]) -> str:
    """Return deterministic Markdown alongside benchmark-status.json."""

    lines = [
        f"# Benchmark status — {report['benchmark_id']}",
        "",
        f"Overall: **{report['status']}**",
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
            "## Tier runs",
            "",
            "| Tier | Status | Pipeline status | Output |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in report["runs"]:
        lines.append(
            f"| {item['tier']} | {item['status']} | "
            f"{item.get('pipeline_status', 'pending')} | `{item.get('output', '')}` |"
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
