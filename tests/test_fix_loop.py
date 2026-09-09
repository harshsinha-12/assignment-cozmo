import json
import shutil
from pathlib import Path

import pytest

from cozmo_floorplan.fix_loop.verify import FixLoopBundleError, verify_fix_loop_bundle
from cozmo_floorplan.schema import validate_floorplan

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "data" / "fix-loop"


def test_frozen_before_bundle_is_valid_and_records_a_real_failure():
    manifest = verify_fix_loop_bundle(BUNDLE)
    prediction = json.loads((BUNDLE / "before" / "floorplan.json").read_text(encoding="utf-8"))
    report = json.loads((BUNDLE / "before" / "eval.json").read_text(encoding="utf-8"))
    yield_gate = next(gate for gate in report["gates"] if gate["name"] == "pipeline_yield")

    validate_floorplan(prediction)
    assert manifest["before"]["source_commit"].startswith("523ceea")
    assert manifest["after"] is None
    assert yield_gate["status"] == "fail"
    assert yield_gate["metrics"] == {"prediction_status": "partial"}


def test_frozen_before_bundle_detects_artifact_tampering(tmp_path):
    copy = tmp_path / "fix-loop"
    shutil.copytree(BUNDLE, copy)
    with (copy / "before" / "eval.json").open("a", encoding="utf-8") as handle:
        handle.write("\n")

    with pytest.raises(FixLoopBundleError, match="Checksum mismatch"):
        verify_fix_loop_bundle(copy)
