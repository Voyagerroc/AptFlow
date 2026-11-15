import copy
import json
import tempfile
import unittest
from pathlib import Path

from aptflow_core.config import read_config


class ConfigTests(unittest.TestCase):
    def config(self):
        return {
            "schema_version": 1,
            "mode": "demo",
            "tools": {
                role: {"adapter": "mock", "enabled": True}
                for role in ("memory", "research", "script", "video")
            },
        }

    def read(self, config, encoding="utf-8"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config), encoding=encoding)
            return read_config(path)

    def test_valid_demo_config(self):
        for encoding in ("utf-8", "utf-8-sig"):
            for memory_enabled in (True, False):
                with self.subTest(encoding=encoding, memory_enabled=memory_enabled):
                    config = self.config()
                    config["tools"]["memory"]["enabled"] = memory_enabled
                    self.assertEqual(self.read(config, encoding), config)

    def test_exact_fields(self):
        root = self.config()
        containers = [((), root, "Config must contain only")]
        containers.append((("tools",), root["tools"], "Configure memory, research, script and video"))
        for role in root["tools"]:
            containers.append((("tools", role), root["tools"][role],
                               f"{role}: only adapter and enabled are supported"))
        for path, fields, message in containers:
            for field in (*fields, "extra"):
                with self.subTest(path=path, field=field):
                    config = copy.deepcopy(root)
                    target = config
                    for key in path:
                        target = target[key]
                    if field == "extra":
                        target[field] = None
                    else:
                        del target[field]
                    with self.assertRaisesRegex(ValueError, message):
                        self.read(config)

    def test_invalid_values(self):
        cases = [
            (("schema_version",), value, "Supported schema_version is 1")
            for value in (True, False, "1", 0, 2)
        ]
        cases.append((("mode",), "invalid", "mode must be demo or live"))
        for role in self.config()["tools"]:
            cases.extend([
                (("tools", role, "adapter"), "unknown", f"{role}: unknown adapter"),
                (("tools", role, "adapter"), None, f"{role}: unknown adapter"),
                (("tools", role, "adapter"), "tinyfish" if role != "research" else "heygen",
                 f"{role}: unknown adapter"),
            ])
            for enabled in (0, 1, "true", None):
                cases.append((("tools", role, "enabled"), enabled,
                              f"{role}: enabled must be boolean"))
            if role != "memory":
                cases.append((("tools", role, "enabled"), False,
                              f"{role} is required; only memory is optional"))
        for path, value, message in cases:
            with self.subTest(path=path, value=value):
                config = self.config()
                target = config
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.read(config)

    def test_demo_rejects_enabled_live_adapters(self):
        for role, adapter in (("memory", "notebooklm"), ("research", "tinyfish"),
                              ("script", "reasoning-model"), ("video", "heygen")):
            with self.subTest(role=role):
                config = self.config()
                config["tools"][role]["adapter"] = adapter
                with self.assertRaisesRegex(ValueError, "Demo mode allows only mock adapters"):
                    self.read(config)


if __name__ == "__main__":
    unittest.main()
