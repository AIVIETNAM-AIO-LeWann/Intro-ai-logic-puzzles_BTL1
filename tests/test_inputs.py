import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import benchmark
from logic_lab.__main__ import main
from logic_lab.inputs import load_levels, make_problem, suite_levels, validate_level
from logic_lab.search import search
from test_logic import valid_pipes, valid_akari


class InputTests(unittest.TestCase):
    def test_examples_include_solved_and_proven_unsat(self):
        levels = load_levels(Path(__file__).resolve().parents[1] / "inputs/examples.json")
        for algorithm in ("dfs", "greedy"):
            self.assertEqual([search(make_problem(l), algorithm)["status"] for l in levels],
                             ["solved", "solved", "unsat"])

    def test_malformed_structures_are_rejected(self):
        base = {"game": "pipes", "rows": 2, "cols": 2, "tiles": [1, 3, 4, 6]}
        for changes in ({"rows": True}, {"rows": 0}, {"cols": 21}, {"tiles": [1]},
                        {"tiles": [1, 3, 4, False]}, {"id": []}, {"game": "bad"},
                        {"game": "lightup", "board": ["..", ".5"]},
                        {"game": "lightup", "board": ["..", "."]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_level({**base, **changes})

    def test_extended_suite_solutions_match_independent_oracles(self):
        levels = suite_levels("extended")
        self.assertEqual(len(levels), 26)
        self.assertEqual(len({l["id"] for l in levels}), 26)
        self.assertFalse(any("_witness" in l for l in levels))
        for level in levels[8:]:
            for algorithm in ("dfs", "greedy"):
                with self.subTest(level=level["id"], algorithm=algorithm):
                    result = search(make_problem(level), algorithm, timeout=2)
                    self.assertEqual(result["status"], "solved")
                    answer = result["solution"]
                    self.assertTrue(valid_pipes(level, answer["tiles"]) if level["game"] == "pipes"
                                    else valid_akari(level["board"], set(answer["bulbs"])))

    def test_cli_output_and_limit_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "answer.json"
            self.assertEqual(main(["--level", "lightup-3", "--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))[0]["status"], "solved")
            self.assertEqual(main(["--level", "pipes-3", "--max-nodes", "0", "--output", str(output)]), 2)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))[0]["status"], "limit")

    def test_benchmark_exports_inputs_raw_measurements_and_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bench.json"
            source = Path(directory) / "inputs.json"
            source.write_text(json.dumps({"id": "unsat", "game": "lightup", "rows": 1,
                                          "cols": 2, "board": ["0."]}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                benchmark.main(["--input", str(source), "--repeat", "2", "--output", str(output)])
            data = json.loads(output.read_text(encoding="utf-8"))
            canonical = json.dumps(data["inputs"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            self.assertEqual(data["inputs_sha256"], hashlib.sha256(canonical.encode("utf-8")).hexdigest())
            self.assertEqual(len(data["results"]), 2)
            for row in data["results"]:
                self.assertEqual(row["statuses"], ["unsat", "unsat"])
                self.assertEqual(row["solved_runs"], 0)
                self.assertIsNone(row["solutions_verified"])
                self.assertEqual(row["memory_status"], "unsat")
                self.assertEqual(row["frontier_peak"], 0)
                self.assertEqual(len(row["runs_metrics"]), 2)
            self.assertTrue(output.with_suffix(".csv").exists())
