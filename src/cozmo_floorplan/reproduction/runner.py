"""Run and verify the public synthetic end-to-end workflow."""

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from time import perf_counter

from cozmo_floorplan.fix_loop.verify import verify_fix_loop_bundle
from cozmo_floorplan.reproduction.commands import run_expected
from cozmo_floorplan.reproduction.config import (
    FIX_LOOP_RELATIVE,
    FIXTURE_RELATIVE,
    TRUTH_RELATIVE,
)
from cozmo_floorplan.reproduction.verify import verify_reproduction_artifacts


def reproduce_synthetic(repo_root: str | Path, output_dir: str | Path) -> float:
    """Regenerate the synthetic plan/eval, verify gates and frozen fix evidence."""

    repo = Path(repo_root).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["COZMO_AGENT_MODE"] = "fallback"
    source_path = str(repo / "src")
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        f"{source_path}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else source_path
    )
    started = perf_counter()

    run_expected(
        [
            sys.executable,
            "-m",
            "cozmo_floorplan",
            "run",
            str(repo / FIXTURE_RELATIVE),
            "--out",
            str(output),
        ],
        cwd=repo,
        expected_exit=0,
        env=environment,
    )
    run_expected(
        [
            sys.executable,
            "-m",
            "cozmo_floorplan",
            "eval",
            "--pred",
            str(output / "floorplan.json"),
            "--truth",
            str(repo / TRUTH_RELATIVE),
            "--ablation-off",
            str(output / "floorplan.ablation-off.json"),
            "--out",
            str(output),
        ],
        cwd=repo,
        expected_exit=3,
        env=environment,
    )
    verify_reproduction_artifacts(output)
    verify_fix_loop_bundle(repo / FIX_LOOP_RELATIVE)
    elapsed = perf_counter() - started
    print(f"synthetic reproduction: pass ({elapsed:.2f}s) output={output}")
    return elapsed


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate verified synthetic artifacts.")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=Path("out/reproduction"))
    args = parser.parse_args(argv)
    reproduce_synthetic(args.repo, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
