"""Subprocess utility with explicit exit-code contracts."""

import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path


class ReproductionCommandError(RuntimeError):
    """A reproduction command returned an unexpected exit code."""


def run_expected(
    command: Sequence[str],
    *,
    cwd: Path,
    expected_exit: int,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a visible command and enforce its documented exit code."""

    print("+", " ".join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
    )
    if completed.returncode != expected_exit:
        raise ReproductionCommandError(
            f"Expected exit {expected_exit}, got {completed.returncode}: {' '.join(command)}"
        )
    return completed
