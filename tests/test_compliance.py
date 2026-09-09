from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "docs" / "compliance-matrix.md"
ALLOWED_STATUSES = ("missing", "partial", "done", "doing")


def test_compliance_matrix_has_every_unique_requirement_and_valid_status():
    rows = [
        line
        for line in MATRIX_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("| R") and line.split("|", maxsplit=2)[1].strip()[1:].isdigit()
    ]
    parsed = [tuple(cell.strip() for cell in row.strip("|").split("|")) for row in rows]
    identifiers = [cells[0] for cells in parsed]
    statuses = [cells[-1] for cells in parsed]

    assert identifiers == [f"R{index}" for index in range(1, 28)]
    assert len(identifiers) == len(set(identifiers))
    assert all(status.startswith(ALLOWED_STATUSES) for status in statuses)
