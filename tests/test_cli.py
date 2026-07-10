import csv
import json
import tempfile
import unittest
from pathlib import Path

from award_availability.cli import main


class CliTests(unittest.TestCase):
    def test_writes_ranked_csv_and_summary(self):
        payload = {
            "data": [
                {
                    "id": "sample-1",
                    "route_id": "route-1",
                    "date": "2030-04-12",
                    "program": "Example Rewards",
                    "currency": "USD",
                    "cabins": {"economy": {"available": True, "miles": 25000, "direct": True, "seats": 3, "taxes": 55}},
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            output_path = root / "output"
            exit_code = main([
                "--input", str(input_path),
                "--origin", "AAA",
                "--destination", "BBB",
                "--outdir", str(output_path),
            ])
            self.assertEqual(0, exit_code)
            with (output_path / "ranked_options.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual("25000", rows[0]["miles"])
            self.assertIn("AAA -> BBB", (output_path / "scan_summary.md").read_text())
