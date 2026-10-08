import copy
import unittest
from unittest.mock import patch
from logic_lab import service
from logic_lab.levels import BY_ID
from logic_lab.games.pipes import Pipes, orientations


class DemoTests(unittest.TestCase):
    def test_wrong_lightup_move_can_be_relaxed_without_changing_input(self):
        data = {"level": "lightup-3", "state": {"bulbs": [1], "crosses": []}}
        original = copy.deepcopy(data)
        self.assertEqual(service.solve(data, trace=True)["status"], "unsat")
        for algorithm in ("dfs", "greedy"):
            result = service.solve({**data, "scope": "original", "algorithm": algorithm}, trace=True)
            self.assertEqual(result["status"], "solved")
            self.assertTrue(result["trace"])
            self.assertNotIn(1, result["solution"]["bulbs"])
        self.assertEqual(data, original)

    def test_wrong_pipes_move_can_be_relaxed(self):
        level = BY_ID["pipes-3"]
        tiles = level["_witness"]["tiles"][:]
        tiles[0] = next(v for v in orientations(tiles[0]) if v not in Pipes(level).options[0])
        data = {"level": level["id"], "state": {"tiles": tiles, "fixed": [0]}}
        self.assertEqual(service.solve(data)["status"], "unsat")
        for algorithm in ("dfs", "greedy"):
            result = service.solve({**data, "scope": "original", "algorithm": algorithm}, trace=True)
            self.assertEqual(result["status"], "solved")
            self.assertTrue(Pipes(level).check(result["solution"]["tiles"])["solved"])
            self.assertTrue(result["trace"])

    def test_current_scope_preserves_valid_player_choice(self):
        result = service.solve({"level": "lightup-3", "state": {"bulbs": [2]}})
        self.assertEqual(set(result["solution"]["bulbs"]), {2, 6})
        self.assertEqual(result["scope"], "current")

    def test_limit_stays_limit_and_does_not_silently_relax(self):
        with patch('logic_lab.service.search', return_value={"status": "limit"}) as mocked:
            result = service.solve({"level": "lightup-3", "state": {}})
            self.assertEqual(result["status"], "limit")
            self.assertEqual(mocked.call_count, 1)

    def test_invalid_scope_rejected(self):
        with self.assertRaises(ValueError):
            service.solve({"level": "lightup-3", "scope": "bad"})
