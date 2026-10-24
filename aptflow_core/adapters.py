"""Provider boundaries. Live providers are deliberately unimplemented."""
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class AdapterSpec:
    role: str
    name: str
    implemented: bool
    required_env: tuple[str, ...] = ()


SPECS = {
    ("memory", "mock"): AdapterSpec("memory", "mock", True),
    ("research", "mock"): AdapterSpec("research", "mock", True),
    ("script", "mock"): AdapterSpec("script", "mock", True),
    ("video", "mock"): AdapterSpec("video", "mock", True),
    ("memory", "notebooklm"): AdapterSpec("memory", "notebooklm", False, ("NOTEBOOKLM_NOTEBOOK_ID",)),
    ("research", "tinyfish"): AdapterSpec("research", "tinyfish", False, ("TINYFISH_API_KEY",)),
    ("script", "reasoning-model"): AdapterSpec("script", "reasoning-model", False, ("MODEL_API_KEY", "MODEL_NAME", "MODEL_BASE_URL")),
    ("video", "heygen"): AdapterSpec("video", "heygen", False, ("HEYGEN_API_KEY", "HEYGEN_AVATAR_ID", "HEYGEN_VOICE_ID")),
}


class Adapter(Protocol):
    """Implement this boundary for a provider. Never return secrets."""

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class MockAdapter:
    """Deterministic, synthetic outputs. No network or user-account access."""

    def __init__(self, role: str):
        self.role = role

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.role == "memory":
            return {"synthetic": True, "summary": "Fictional demo brand; no personal memory loaded."}
        if self.role == "research":
            return {"synthetic": True, "evidence": [{
                "id": "demo", "url": "https://example.com/",
                "finding": "Synthetic fixture, not a fetched source or verified product claim."}]}
        if self.role == "script":
            return {"synthetic": True, "scenes": [
                {"title": "Your goal, your tools", "body": "An account-free starter workflow. Replace mock adapters with your own integrations.", "seconds": 5, "evidence_ids": ["demo"]},
                {"title": "Bring your configuration", "body": "Choose providers and keep credentials in your own environment. This example uses only synthetic data.", "seconds": 5, "evidence_ids": ["demo"]},
                {"title": "Inspect every result", "body": "The mock video step exports a storyboard. Optional FFmpeg rendering is a separate local command.", "seconds": 5, "evidence_ids": ["demo"]}]}
        if self.role == "video":
            return {"synthetic": True, "kind": "storyboard", "video_generated": False,
                    "scenes": payload["script"]["scenes"], "evidence": payload["research"]["evidence"]}
        raise ValueError(f"Unsupported mock role: {self.role}")


def create_adapter(role: str, name: str) -> Adapter:
    spec = SPECS[(role, name)]
    if not spec.implemented:
        raise NotImplementedError(f"{role}/{name}: implement this adapter before live use")
    return MockAdapter(role)
