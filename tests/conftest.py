import pytest


@pytest.fixture(autouse=True)
def force_deterministic_agent_mode(monkeypatch):
    """Unit tests never spend API credits or depend on a developer's local key."""

    monkeypatch.setenv("COZMO_AGENT_MODE", "fallback")
