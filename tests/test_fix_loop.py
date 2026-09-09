import json
import shutil
from pathlib import Path

import pytest

from cozmo_floorplan.fix_loop.verify import FixLoopBundleError, verify_fix_loop_bundle
from cozmo_floorplan.schema import validate_floorplan

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "data" / "fix-loop"


def test_frozen_bundle_records_the_predicted_fail_to_pass_delta():
    manifest = verify_fix_loop_bundle(BUNDLE)
    before = json.loads((BUNDLE / "before" / "floorplan.json").read_text(encoding="utf-8"))
    after = json.loads((BUNDLE / "after" / "floorplan.json").read_text(encoding="utf-8"))
    before_report = json.loads((BUNDLE / "before" / "eval.json").read_text(encoding="utf-8"))
    after_report = json.loads((BUNDLE / "after" / "eval.json").read_text(encoding="utf-8"))
    before_yield = next(gate for gate in before_report["gates"] if gate["name"] == "pipeline_yield")
    after_yield = next(gate for gate in after_report["gates"] if gate["name"] == "pipeline_yield")

    validate_floorplan(before)
    validate_floorplan(after)
    assert manifest["before"]["source_commit"].startswith("523ceea")
    assert manifest["after"]["source_commit"].startswith("68acdf6")
    assert before_yield["status"] == "fail"
    assert before_yield["metrics"] == {"prediction_status": "partial"}
    assert after_yield["status"] == "pass"
    assert after_yield["metrics"] == {"prediction_status": "ok"}


def test_frozen_before_bundle_detects_artifact_tampering(tmp_path):
    copy = tmp_path / "fix-loop"
    shutil.copytree(BUNDLE, copy)
    with (copy / "before" / "eval.json").open("a", encoding="utf-8") as handle:
        handle.write("\n")

    with pytest.raises(FixLoopBundleError, match="Checksum mismatch"):
        verify_fix_loop_bundle(copy)


def test_frozen_after_bundle_detects_artifact_tampering(tmp_path):
    copy = tmp_path / "fix-loop"
    shutil.copytree(BUNDLE, copy)
    with (copy / "after" / "floorplan.json").open("a", encoding="utf-8") as handle:
        handle.write("\n")

    with pytest.raises(FixLoopBundleError, match="Checksum mismatch"):
        verify_fix_loop_bundle(copy)
