"""Keep public capture templates aligned with the job loader contract."""

from pathlib import Path

import pytest

from cozmo_floorplan.io.job import load_job


TEMPLATE_ROOT = Path(__file__).parents[1] / "data" / "templates"


@pytest.mark.parametrize("tier", ("photos", "video", "lidar"))
def test_capture_template_loads_as_its_declared_tier(tier: str) -> None:
    job = load_job(TEMPLATE_ROOT / tier)

    assert job.tier == tier
    assert job.job_id == f"replace-me-{tier}"
    assert job.device and job.device.startswith("replace-me-")
    assert (job.root / tier).is_dir()


def test_templates_require_separate_job_ids() -> None:
    jobs = [load_job(TEMPLATE_ROOT / tier) for tier in ("photos", "video", "lidar")]

    assert len({job.job_id for job in jobs}) == len(jobs)
