"""Strict public configuration; credentials live in environment variables."""
import json
from pathlib import Path

from .adapters import SPECS


ROLES = ("memory", "research", "script", "video")


def read_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "mode", "tools"}:
        raise ValueError("Config must contain only schema_version, mode and tools; keep secrets in environment variables")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Supported schema_version is 1")
    if data["mode"] not in ("demo", "live"):
        raise ValueError("mode must be demo or live")
    if not isinstance(data["tools"], dict) or set(data["tools"]) != set(ROLES):
        raise ValueError("Configure memory, research, script and video")
    for role in ROLES:
        tool = data["tools"][role]
        if not isinstance(tool, dict) or set(tool) != {"adapter", "enabled"}:
            raise ValueError(f"{role}: only adapter and enabled are supported")
        if not isinstance(tool["adapter"], str) or (role, tool["adapter"]) not in SPECS:
            raise ValueError(f"{role}: unknown adapter")
        if type(tool["enabled"]) is not bool:
            raise ValueError(f"{role}: enabled must be boolean")
        if role != "memory" and not tool["enabled"]:
            raise ValueError(f"{role} is required; only memory is optional")
        if data["mode"] == "demo" and tool["enabled"] and tool["adapter"] != "mock":
            raise ValueError("Demo mode allows only mock adapters")
    return data
