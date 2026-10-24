"""Explicit stages with preflight, isolated run directories and honest status."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .adapters import SPECS, create_adapter
from .config import ROLES
from .media import load_bundle


def plan(config: dict) -> dict:
    stages = []
    for role in ROLES:
        tool = config["tools"][role]
        spec = SPECS[(role, tool["adapter"])]
        # Report variable names, never their values or the complete environment.
        stages.append({"role": role, "adapter": spec.name, "enabled": tool["enabled"],
                       "implemented": spec.implemented,
                       "missing_environment": [name for name in spec.required_env if not os.environ.get(name)] if tool["enabled"] else []})
    ready = all(not s["enabled"] or (s["implemented"] and not s["missing_environment"]) for s in stages)
    return {"mode": config["mode"], "ready": ready, "stages": stages,
            "note": "Live provider entries are extension stubs; setting credentials does not implement them."}


def run(config: dict, output: Path) -> dict:
    readiness = plan(config)
    if not readiness["ready"]:
        raise ValueError("Preflight failed: inspect plan/doctor; live adapters are extension stubs")
    output.mkdir(parents=True, exist_ok=False)
    report = {"status": "running", "mode": config["mode"], "synthetic": True,
              "external_calls": 0, "known_external_cost_usd": 0,
              "video_generated": False, "stages": [],
              "started_at": datetime.now(timezone.utc).isoformat()}
    context = {}
    try:
        for stage in readiness["stages"]:
            role = stage["role"]
            if not stage["enabled"]:
                report["stages"].append({"role": role, "status": "skipped"})
                continue
            result = create_adapter(role, stage["adapter"]).execute(context)
            context[role] = result
            report["stages"].append({"role": role, "adapter": stage["adapter"], "status": "mock_completed"})
        video = context["video"]
        bundle = {"schema_version": "0.1", "synthetic": True,
                  "evidence": video["evidence"], "scenes": video["scenes"]}
        bundle_path = output / "storyboard.json"
        bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        load_bundle(bundle_path)
        report.update(status="demo_completed", checks={"storyboard_structure": True},
                      outputs=["storyboard.json", "report.json"])
    except Exception:
        report["status"] = "failed"
        # Keep provider exception strings out of reports: they can contain credentials.
        raise RuntimeError("Workflow failed; inspect the failing adapter locally") from None
    finally:
        (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
