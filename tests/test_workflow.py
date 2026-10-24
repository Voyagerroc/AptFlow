import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aptflow import load_bundle, render


class WorkflowTests(unittest.TestCase):
    def write(self, directory, evidence_ids):
        path = Path(directory) / "bundle.json"
        path.write_text(json.dumps({"evidence": [{"id": "source", "url": "https://example.com"}],
                                    "scenes": [{"title": "Demo", "body": "Evidence", "seconds": 1,
                                                "evidence_ids": evidence_ids}]}), encoding="utf-8")
        return path

    def test_unknown_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "known evidence"):
                load_bundle(self.write(directory, ["invented"]))

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = self.write(directory, ["source"])
            destination = Path(directory) / "previous-run"
            destination.mkdir()
            marker = destination / "precious.txt"
            marker.write_text("keep", encoding="utf-8")
            font = Path(directory) / "test-font.ttf"
            font.write_bytes(b"not-read-in-this-test")
            with patch("aptflow_core.media.shutil.which", return_value="fake-tool"):
                with self.assertRaises(FileExistsError):
                    render(bundle, destination, font)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
