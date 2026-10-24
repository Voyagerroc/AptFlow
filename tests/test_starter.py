import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aptflow_core.config import read_config
from aptflow_core.workflow import plan, run


ROOT = Path(__file__).resolve().parents[1]


class StarterTests(unittest.TestCase):
    def config(self):
        return read_config(ROOT / "aptflow_core" / "demo-config.json")

    def test_demo_runs_without_accounts_or_network(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            with patch("socket.socket", side_effect=AssertionError("Network is forbidden")):
                config = self.config()
                self.assertTrue(plan(config)["ready"])
                result = run(config, Path(directory) / "demo")
            self.assertEqual(result["status"], "demo_completed")
            self.assertEqual(result["external_calls"], 0)
            self.assertFalse(result["video_generated"])
            bundle = json.loads((Path(directory) / "demo" / "storyboard.json").read_text())
            self.assertTrue(bundle["synthetic"])

    def test_unimplemented_live_fails_before_creating_output(self):
        config = read_config(ROOT / "config" / "live.example.json")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "never-created"
            with self.assertRaisesRegex(ValueError, "Preflight"):
                run(config, output)
            self.assertFalse(output.exists())

    def test_doctor_never_exposes_credentials(self):
        config = read_config(ROOT / "config" / "live.example.json")
        with patch.dict(os.environ, {"TINYFISH_API_KEY": "private-sentinel-credential"}):
            report = json.dumps(plan(config))
        self.assertNotIn("private-sentinel-credential", report)
        self.assertFalse(plan(config)["ready"])

    def test_demo_rejects_live_adapter_selection(self):
        config = self.config()
        config["tools"]["video"]["adapter"] = "heygen"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "only mock"):
                read_config(path)

    def test_optional_memory_can_be_disabled(self):
        config = copy.deepcopy(self.config())
        config["tools"]["memory"]["enabled"] = False
        with tempfile.TemporaryDirectory() as directory:
            result = run(config, Path(directory) / "run")
        self.assertEqual(result["stages"][0]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
