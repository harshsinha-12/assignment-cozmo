import sys
from pathlib import Path

import pytest

from cozmo_floorplan.reproduction.commands import ReproductionCommandError, run_expected
from cozmo_floorplan.reproduction.runner import reproduce_synthetic
from cozmo_floorplan.reproduction.verify import verify_reproduction_artifacts

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_reproduction_runs_and_verifies(tmp_path):
    output = tmp_path / "output"

    elapsed = reproduce_synthetic(ROOT, output)
    result = verify_reproduction_artifacts(output)

    assert elapsed >= 0
    assert result["plan"]["status"] == "ok"
    assert result["report"]["passed"] is False


def test_reproduction_command_rejects_unexpected_exit():
    with pytest.raises(ReproductionCommandError, match="Expected exit 0, got 7"):
        run_expected(
            [sys.executable, "-c", "raise SystemExit(7)"],
            cwd=ROOT,
            expected_exit=0,
        )
