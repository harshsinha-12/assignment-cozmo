from cozmo_floorplan.agent.status_policy import record_fallback


def _document(status: str = "ok") -> dict:
    return {"status": status, "warnings": []}


def test_explicit_fallback_is_audited_without_degrading_healthy_status():
    document = record_fallback(
        _document(),
        "Agent mode requested deterministic fallback",
        degrade_status=False,
    )

    assert document["status"] == "ok"
    assert document["warnings"] == [
        {
            "code": "agent_fallback",
            "message": "Agent mode requested deterministic fallback",
        }
    ]


def test_automatic_fallback_degrades_healthy_status():
    document = record_fallback(
        _document(),
        "No OPENAI_API_KEY; used deterministic claims tools",
        degrade_status=True,
    )

    assert document["status"] == "partial"


def test_fallback_never_upgrades_an_existing_partial_status():
    document = record_fallback(
        _document("partial"),
        "Agent mode requested deterministic fallback",
        degrade_status=False,
    )

    assert document["status"] == "partial"
