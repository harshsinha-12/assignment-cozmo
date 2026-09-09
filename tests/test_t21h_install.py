"""T21h cable-install path does not require a paid Apple Developer team."""

from pathlib import Path
import os
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install-cozmo-capture.sh"
ROUTE1 = ROOT / "docs" / "capture-route-route1.md"
ROUTE2 = ROOT / "docs" / "capture-route.md"
IOS_README = ROOT / "ios" / "CozmoCapture" / "README.md"


def test_install_script_help_and_dry_run_do_not_need_a_phone() -> None:
    help_run = subprocess.run(
        ["bash", str(SCRIPT), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    dry_run = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "DEVELOPMENT_TEAM": "PH4KQ4LY92"},
    )

    assert help_run.returncode == 0, help_run.stderr
    assert "Personal Team" in help_run.stdout
    assert "99" in help_run.stdout
    assert dry_run.returncode == 0, dry_run.stderr + dry_run.stdout
    assert "elapsed_s=" in dry_run.stdout
    assert "PH4KQ4LY92" in dry_run.stdout


def test_route1_card_is_the_ten_minute_dev_build_not_testflight() -> None:
    card = ROUTE1.read_text(encoding="utf-8")
    scored = ROUTE2.read_text(encoding="utf-8")
    ios_readme = IOS_README.read_text(encoding="utf-8")

    assert "10" in card
    assert "install-cozmo-capture.sh" in card
    assert "Apple Developer Program" in card
    assert "docs/capture-route.md" in card
    assert scored.startswith("# Capture route (Route 2)")
    assert "TestFlight is not used" in ios_readme or "not used" in ios_readme.lower()
