"""Runtime and claims-policy configuration for the agent layer."""

from dataclasses import dataclass
import os

OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
AGENT_MODE_ENV = "COZMO_AGENT_MODE"
AGENT_MODEL_ENV = "COZMO_AGENT_MODEL"
OPENAI_BASE_URL_ENV = "OPENAI_BASE_URL"

ALLOWED_DAMAGE_CLASSES = (
    "water_stain",
    "mold_like_growth",
    "impact_damage",
    "crack",
    "fire_soot",
    "other",
)

CLAIMS_POLICIES: dict[str, dict[str, str | None]] = {
    "water_stain": {
        "concealed_rule_id": "CONCEALED_WATER_MIGRATION_001",
        "scope_action": "remove affected material",
    },
    "mold_like_growth": {
        "concealed_rule_id": "CONCEALED_MICROBIAL_GROWTH_001",
        "scope_action": "clean and treat affected material",
    },
    "impact_damage": {
        "concealed_rule_id": None,
        "scope_action": "repair affected material",
    },
    "crack": {
        "concealed_rule_id": "CONCEALED_SUBSTRATE_CRACK_001",
        "scope_action": "repair affected material",
    },
    "fire_soot": {
        "concealed_rule_id": "CONCEALED_SMOKE_MIGRATION_001",
        "scope_action": "clean and seal affected material",
    },
    "other": {
        "concealed_rule_id": None,
        "scope_action": "inspect affected material",
    },
}


@dataclass(frozen=True, slots=True)
class AgentConfig:
    """Resolved settings for one claims-enrichment run."""

    mode: str
    api_key: str | None
    model: str
    base_url: str
    timeout_seconds: float = 30.0
    max_tool_rounds: int = 12

    @classmethod
    def from_environment(cls) -> "AgentConfig":
        mode = os.getenv(AGENT_MODE_ENV, "auto").strip().lower()
        if mode not in {"auto", "live", "fallback"}:
            mode = "auto"
        key = os.getenv(OPENAI_API_KEY_ENV, "").strip() or None
        return cls(
            mode=mode,
            api_key=key,
            model=os.getenv(AGENT_MODEL_ENV, "gpt-5-mini").strip() or "gpt-5-mini",
            base_url=os.getenv(OPENAI_BASE_URL_ENV, "https://api.openai.com/v1").rstrip("/"),
        )
